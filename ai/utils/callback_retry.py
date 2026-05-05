# ai/utils/callback_retry.py
"""
콜백 실패 시 로컬 파일 Fallback + Circuit Breaker + Startup Recovery.

설계 근거:
  Transactional Outbox Pattern (Netflix/Amazon):
    생성된 데이터를 먼저 영속화한 뒤 비동기 전송.
  Circuit Breaker (Microsoft Resilience Patterns):
    연속 실패 시 즉시 fallback으로 전환하여 무의미한 재시도 차단.
  StorySage (UIST 2025):
    Session Scribe 에이전트가 공유 데이터 구조에 먼저 영속화.

상태 머신:
  PENDING → SENDING → DELIVERED
                   ↘ FAILED (retry_count < max)
                        ↘ DEAD_LETTER (retry_count >= max)
"""
import json
import logging
import os
import random
import threading
import time
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────
# Circuit Breaker (경량 자체 구현 — pybreaker 의존성 제거)
# ──────────────────────────────────────────────────────────────

class CircuitBreaker:
    """
    Circuit Breaker: 연속 실패 시 회로 열어서 즉시 fallback.

    상태:
      CLOSED  — 정상 동작, 실패 카운트 누적
      OPEN    — 회로 열림, 모든 호출 즉시 차단
      HALF_OPEN — 테스트 1건 허용, 성공 시 CLOSED 복귀

    Args:
        fail_max:     OPEN 전환 임계값 (연속 실패 수)
        reset_timeout: OPEN → HALF_OPEN 전환 대기(초)
    """

    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

    def __init__(self, fail_max: int = 3, reset_timeout: float = 30.0):
        self._fail_max = fail_max
        self._reset_timeout = reset_timeout
        self._state = self.CLOSED
        self._fail_count = 0
        self._last_failure_time = 0.0
        self._lock = threading.Lock()

    @property
    def state(self) -> str:
        with self._lock:
            if self._state == self.OPEN:
                if time.time() - self._last_failure_time >= self._reset_timeout:
                    self._state = self.HALF_OPEN
            return self._state

    def allow_request(self) -> bool:
        """요청 허용 여부. OPEN이면 False."""
        s = self.state
        return s in (self.CLOSED, self.HALF_OPEN)

    def record_success(self) -> None:
        with self._lock:
            self._fail_count = 0
            self._state = self.CLOSED

    def record_failure(self) -> None:
        with self._lock:
            self._fail_count += 1
            self._last_failure_time = time.time()
            if self._fail_count >= self._fail_max:
                self._state = self.OPEN
                logger.warning(
                    f"[circuit_breaker] OPEN — 연속 {self._fail_count}회 실패, "
                    f"{self._reset_timeout}s 후 HALF_OPEN"
                )


# ──────────────────────────────────────────────────────────────
# Outbox: 파일 기반 Fallback 저장 + 재전송
# ──────────────────────────────────────────────────────────────

class CallbackOutbox:
    """
    파일 기반 Callback Outbox.

    실패한 payload를 JSON 파일로 저장, 백그라운드에서 재전송.
    상태 머신: PENDING → SENDING → DELIVERED / FAILED / DEAD_LETTER.

    Args:
        outbox_dir:   fallback 파일 저장 디렉토리
        post_url:     Spring Boot POST 엔드포인트
        max_retries:  최대 재시도 횟수
        base_delay:   지수 백오프 기본 대기(초)
        max_delay:    최대 대기(초)
        timeout:      HTTP 타임아웃(초)
    """

    def __init__(
        self,
        outbox_dir: str,
        post_url: str,
        max_retries: int = 5,
        base_delay: float = 2.0,
        max_delay: float = 300.0,
        timeout: int = 10,
    ):
        self._dir = Path(outbox_dir)
        self._dir.mkdir(parents=True, exist_ok=True)
        self._post_url = post_url
        self._max_retries = max_retries
        self._base_delay = base_delay
        self._max_delay = max_delay
        self._timeout = timeout

    def save_failed(self, payload: dict, reason: str) -> str:
        """
        실패한 payload를 JSON 파일로 저장.

        Returns: 저장된 파일 경로
        """
        session_id = payload.get("sessionId", "unknown")
        timestamp = int(time.time())
        filename = f"{session_id}_{timestamp}.json"
        filepath = self._dir / filename

        envelope = {
            "status": "PENDING",
            "retry_count": 0,
            "created_at": time.time(),
            "last_attempt": None,
            "last_error": reason,
            "payload": payload,
        }

        filepath.write_text(json.dumps(envelope, ensure_ascii=False, indent=2))
        logger.info(f"[callback_outbox] 저장됨: {filepath}")
        return str(filepath)

    def retry_all_pending(self) -> dict:
        """
        모든 PENDING/FAILED 파일을 스캔하여 재전송.
        Startup Recovery + 주기적 재시도 양쪽에서 호출.

        Returns: {"delivered": int, "failed": int, "dead_letter": int}
        """
        stats = {"delivered": 0, "failed": 0, "dead_letter": 0}

        for filepath in sorted(self._dir.glob("*.json")):
            try:
                envelope = json.loads(filepath.read_text())
            except (json.JSONDecodeError, OSError) as e:
                logger.error(f"[callback_outbox] 파일 읽기 실패: {filepath} — {e}")
                continue

            status = envelope.get("status")
            if status in ("DELIVERED", "DEAD_LETTER"):
                continue

            retry_count = envelope.get("retry_count", 0)
            if retry_count >= self._max_retries:
                envelope["status"] = "DEAD_LETTER"
                filepath.write_text(json.dumps(envelope, ensure_ascii=False, indent=2))
                # 확장자 변경: .json → .dead_letter.json
                dead_path = filepath.with_suffix(".dead_letter.json")
                filepath.rename(dead_path)
                stats["dead_letter"] += 1
                logger.warning(f"[callback_outbox] DEAD_LETTER: {dead_path}")
                continue

            # 재전송 시도
            envelope["status"] = "SENDING"
            envelope["retry_count"] = retry_count + 1
            envelope["last_attempt"] = time.time()

            try:
                resp = httpx.post(
                    self._post_url,
                    json=envelope["payload"],
                    timeout=self._timeout,
                )
                resp.raise_for_status()
                envelope["status"] = "DELIVERED"
                filepath.write_text(json.dumps(envelope, ensure_ascii=False, indent=2))
                stats["delivered"] += 1
                logger.info(f"[callback_outbox] 재전송 성공: {filepath.name}")
            except Exception as e:
                envelope["status"] = "FAILED"
                envelope["last_error"] = str(e)
                filepath.write_text(json.dumps(envelope, ensure_ascii=False, indent=2))
                stats["failed"] += 1

                # 지수 백오프 대기
                delay = min(
                    self._base_delay * (2 ** retry_count) + random.uniform(0, 1),
                    self._max_delay,
                )
                logger.warning(
                    f"[callback_outbox] 재전송 실패: {filepath.name} "
                    f"(attempt {envelope['retry_count']}/{self._max_retries}, "
                    f"next in {delay:.1f}s)"
                )
                time.sleep(delay)

        return stats

    def get_pending_count(self) -> int:
        """PENDING/FAILED 상태 파일 수. /health 리포트용."""
        count = 0
        for filepath in self._dir.glob("*.json"):
            if filepath.suffix == ".json" and ".dead_letter" not in filepath.name:
                try:
                    envelope = json.loads(filepath.read_text())
                    if envelope.get("status") in ("PENDING", "FAILED", "SENDING"):
                        count += 1
                except (json.JSONDecodeError, OSError):
                    count += 1
        return count
