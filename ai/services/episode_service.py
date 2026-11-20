# ai/services/episode_service.py
"""
에피소드 생성 파이프라인 오케스트레이터.

처리 순서:
  1. memory_service.flush() → source_facts 스냅샷
  2. Spring Boot GET 기존 에피소드 (실패 시 빈 리스트 + warning)
  3. segmentor → MERGE / NEW 분리
  4. merger (MERGE 구간, 병렬)
  5. writer (NEW 구간, 병렬)
  6. needs_regeneration 선별 재생성 (1회 한정)
  7. Spring Boot POST (3회 지수 백오프 + 지터)
"""
import logging
import os
import random
import time

import httpx

from ai.app.schemas import EpisodeQuality, EpisodeGenerateResponse, UserProfileContext
from ai.app.settings import settings
from ai.services.episode_segmentor import segment_conversation
from ai.services.episode_writer import write_episodes, regenerate_episode
from ai.services.episode_merger import process_merges
from ai.utils.callback_retry import CircuitBreaker, CallbackOutbox

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────
# 서비스 설정 (하드코딩 없이 한 곳에서 관리)
# .env로 오버라이드 가능
# ──────────────────────────────────────────────────────────────

_SPRING_BOOT_BASE_URL = os.getenv("SPRING_BOOT_BASE_URL", "http://localhost:8080")

_CFG: dict = {
    # 재생성 기준
    "regen_always_types":       frozenset({"KEY_SCENE", "TURNING_POINT"}),
    "regen_richness_threshold": float(os.getenv("REGEN_RICHNESS_THRESHOLD", "0.50")),

    # Spring Boot 콜백 (POST)
    "callback_max_retries":     int(os.getenv("CALLBACK_MAX_RETRIES", "3")),
    "callback_base_delay":      float(os.getenv("CALLBACK_BASE_DELAY", "1.0")),
    "callback_max_delay":       float(os.getenv("CALLBACK_MAX_DELAY", "10.0")),
    "callback_timeout":         int(os.getenv("CALLBACK_TIMEOUT", "10")),

    # 기존 에피소드 조회 (GET)
    "fetch_retries":            int(os.getenv("FETCH_EPISODES_RETRIES", "2")),
    "fetch_timeout":            int(os.getenv("FETCH_EPISODES_TIMEOUT", "5")),

    # 병렬 처리
    "writer_max_workers":       int(os.getenv("WRITER_MAX_WORKERS", "5")),
    "merger_max_workers":       int(os.getenv("MERGER_MAX_WORKERS", "5")),
}

_EPISODES_POST_URL = f"{_SPRING_BOOT_BASE_URL}/api/ai/episodes"
_EPISODES_GET_URL  = f"{_SPRING_BOOT_BASE_URL}/api/episodes"


# ──────────────────────────────────────────────────────────────
# Circuit Breaker + Outbox (에피소드 유실 방지)
#
# 설계 근거:
#   Transactional Outbox Pattern (Netflix/Amazon):
#     콜백 실패 시 로컬 파일에 영속화 → 재시도.
#   Circuit Breaker (Microsoft Resilience Patterns):
#     Spring Boot 다운 시 무의미한 재시도 차단 → 즉시 fallback.
#   Startup Recovery:
#     서버 재시작 시 미전송 파일 자동 재전송.
# ──────────────────────────────────────────────────────────────

_OUTBOX_DIR = os.path.join(settings.CHROMA_PERSIST_PATH, "..", "failed_callbacks")

_circuit_breaker = CircuitBreaker(
    fail_max=int(os.getenv("CB_FAIL_MAX", "3")),
    reset_timeout=float(os.getenv("CB_RESET_TIMEOUT", "30.0")),
)

_callback_outbox = CallbackOutbox(
    outbox_dir=_OUTBOX_DIR,
    post_url=_EPISODES_POST_URL,
    max_retries=int(os.getenv("OUTBOX_MAX_RETRIES", "5")),
    base_delay=float(os.getenv("OUTBOX_BASE_DELAY", "2.0")),
    max_delay=float(os.getenv("OUTBOX_MAX_DELAY", "300.0")),
    timeout=_CFG["callback_timeout"],
)


def startup_recovery() -> dict:
    """
    서버 시작 시 호출: 미전송 콜백 파일 재전송.
    api.py의 @app.on_event("startup") 또는 lifespan에서 호출.
    """
    pending = _callback_outbox.get_pending_count()
    if pending == 0:
        return {"pending": 0, "recovered": {}}
    logger.info(f"[episode_service] Startup Recovery: {pending}개 미전송 콜백 발견")
    result = _callback_outbox.retry_all_pending()
    logger.info(f"[episode_service] Startup Recovery 완료: {result}")
    return {"pending": pending, "recovered": result}


def get_callback_health() -> dict:
    """
    /health 엔드포인트용: 콜백 상태 리포트.
    """
    return {
        "circuit_breaker_state": _circuit_breaker.state,
        "pending_callbacks": _callback_outbox.get_pending_count(),
    }


# ──────────────────────────────────────────────────────────────
# 경고 누적기
# ──────────────────────────────────────────────────────────────

class _WarningCollector:
    """파이프라인 단계별 경고를 누적해서 최종 payload에 포함."""

    def __init__(self) -> None:
        self._items: list[str] = []

    def add(self, msg: str) -> None:
        logger.warning(f"[episode_service] {msg}")
        self._items.append(msg)

    def get(self) -> list[str]:
        return self._items.copy()


# ──────────────────────────────────────────────────────────────
# 재생성 선별
# ──────────────────────────────────────────────────────────────

def _should_regenerate(episode: dict, quality_dict: dict) -> bool:
    """
    needs_regeneration=True인 에피소드 중 실제 재생성 대상 선별.

    KEY_SCENE / TURNING_POINT: 무조건 재생성 (핵심 기억, 품질 타협 불가)
    GENERAL_EVENT / LIFETIME_PERIOD: richness < threshold일 때만 재생성
    """
    ep_type = episode.get("type", "GENERAL_EVENT")

    if ep_type in _CFG["regen_always_types"]:
        return True

    try:
        richness = EpisodeQuality(**quality_dict).narrative_richness
    except Exception:
        richness = quality_dict.get("narrative_richness", 0.0)

    return richness < _CFG["regen_richness_threshold"]


# ──────────────────────────────────────────────────────────────
# HTTP 유틸리티
# ──────────────────────────────────────────────────────────────

def _backoff_delay(attempt: int) -> float:
    """지수 백오프 + 지터. thundering herd 방지."""
    raw = _CFG["callback_base_delay"] * (2 ** attempt) + random.uniform(0, 1)
    return min(raw, _CFG["callback_max_delay"])


def _fetch_existing_episodes(
    user_id: str,
    warnings: _WarningCollector,
) -> list[dict]:
    """
    Spring Boot에서 기존 에피소드 조회.
    실패 시 빈 리스트로 진행 + 중복 위험 경고.
    """
    for attempt in range(_CFG["fetch_retries"] + 1):
        try:
            resp = httpx.get(
                _EPISODES_GET_URL,
                params={"userId": user_id},
                timeout=_CFG["fetch_timeout"],
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            if attempt < _CFG["fetch_retries"]:
                time.sleep(_backoff_delay(attempt))
            else:
                warnings.add(
                    f"existing_episodes_fetch_failed: 기존 에피소드를 가져오지 못했습니다 ({e}). "
                    "모든 구간이 신규로 처리되어 중복 에피소드가 생성될 수 있습니다. "
                    "에피소드 페이지에서 확인 후 수동 정리가 필요합니다."
                )
                return []


def _post_callback(payload: dict) -> tuple[bool, str]:
    """
    에피소드 생성 결과를 Spring Boot에 전송.
    Circuit Breaker + 지수 백오프 재시도 + Outbox Fallback.

    흐름:
      1. Circuit Breaker 확인 → OPEN이면 즉시 Outbox 저장
      2. 최대 N회 지수 백오프 재시도
      3. 전부 실패 → Outbox에 저장 (에피소드 유실 방지)
      4. 성공/실패를 Circuit Breaker에 기록

    Returns: (success, reason)
    """
    # Circuit Breaker OPEN → 즉시 fallback
    if not _circuit_breaker.allow_request():
        reason = "circuit_breaker_open: Spring Boot 연결 불안정, Outbox에 저장"
        logger.warning(f"[episode_service] {reason}")
        _callback_outbox.save_failed(payload, reason)
        return False, reason

    for attempt in range(_CFG["callback_max_retries"]):
        try:
            resp = httpx.post(
                _EPISODES_POST_URL,
                json=payload,
                timeout=_CFG["callback_timeout"],
            )
            resp.raise_for_status()
            _circuit_breaker.record_success()
            return True, "success"
        except Exception as e:
            if attempt < _CFG["callback_max_retries"] - 1:
                wait = _backoff_delay(attempt)
                logger.warning(
                    f"[episode_service] 콜백 실패 attempt {attempt + 1}, "
                    f"{wait:.1f}s 후 재시도: {e}"
                )
                time.sleep(wait)
            else:
                _circuit_breaker.record_failure()
                reason = f"{_CFG['callback_max_retries']}회 모두 실패: {e}"
                # Outbox에 저장하여 에피소드 유실 방지
                _callback_outbox.save_failed(payload, reason)
                logger.error(
                    f"[episode_service] 콜백 최종 실패 → Outbox 저장: {reason}"
                )
                return False, reason

    return False, "max retries exceeded"


# ──────────────────────────────────────────────────────────────
# 세그먼트 / 에피소드 변환 유틸
# ──────────────────────────────────────────────────────────────

def _clean_segment(segment: dict) -> dict:
    """writer로 넘기기 전 내부 처리용 필드 제거 (예: _merge_skip_reason)."""
    return {k: v for k, v in segment.items() if not k.startswith("_")}


def _merge_segment_and_result(
    segment: dict,
    result: dict,
    session_id: str,
    source_facts: list[str],
) -> dict:
    """
    segmentor 메타데이터 + writer 출력 → Spring Boot 전송용 에피소드 dict.

    _prefix 필드는 내부 처리용 (재생성, 로그 등).
    _strip_internal_fields() 호출 후 외부 전송.
    """
    quality_dict = result.get("quality") or {}

    try:
        needs_regen = EpisodeQuality(**quality_dict).needs_regeneration
    except Exception:
        needs_regen = False

    return {
        # segmentor 메타데이터
        "turn_start":           segment.get("turn_start"),
        "turn_end":             segment.get("turn_end"),
        "title":                segment.get("title"),
        "type":                 segment.get("type", "GENERAL_EVENT"),
        "key_scene_type":       segment.get("key_scene_type"),
        "theme":                segment.get("theme", "기타"),
        "emotion_tone":         segment.get("emotion_tone", "중립"),
        "time_hint":            segment.get("time_hint"),
        "period_label":         segment.get("period_label"),
        "estimated_year_range": segment.get("estimated_year_range"),
        "location":             segment.get("location"),
        "persons":              segment.get("persons", []),
        "sensory":              segment.get("sensory"),

        # writer 출력
        "narrative":            result.get("narrative", ""),
        "quote":                result.get("quote"),
        "autobiography_hint":   result.get("autobiography_hint"),
        "life_value":           result.get("life_value"),
        "emotion_nuance":       result.get("emotion_nuance"),
        "quality":              quality_dict,

        # Episode 스키마 필수 필드
        "source_session_id":    session_id,
        "source_turn_range":    (segment.get("turn_start"), segment.get("turn_end")),
        "source_facts":         source_facts,
        "importance_score":     5.0,

        # 내부 처리용 (_prefix → Spring Boot 전송 전 제거)
        "_needs_regeneration":  needs_regen,
        "_failed_facts":        result.get("failed_facts", []),
        "_turns":               segment.get("turns", []),
    }


def _strip_internal_fields(episode: dict) -> dict:
    """Spring Boot 전송 전 _ prefix 내부 필드 제거."""
    return {k: v for k, v in episode.items() if not k.startswith("_")}


# ──────────────────────────────────────────────────────────────
# payload 조립
# ──────────────────────────────────────────────────────────────

def _build_callback_payload(
    session_id: str,
    user_id: str,
    new_episodes: list[dict],
    merged_episodes: list[dict],
    warnings: _WarningCollector,
) -> dict:
    """
    Spring Boot로 보낼 최종 payload.
    partial success 허용 — 에피소드 단위 추적 + warnings 포함.
    """
    weak_count = sum(
        1 for ep in new_episodes
        if _get_richness(ep.get("quality", {})) < _CFG["regen_richness_threshold"]
    )
    return {
        "sessionId":       session_id,
        "userId":          user_id,
        "newEpisodes":     new_episodes,
        "mergedEpisodes":  merged_episodes,
        "episodesCreated": len(new_episodes),
        "episodesMerged":  len(merged_episodes),
        "weakEpisodes":    weak_count,
        "warnings":        warnings.get(),
    }


def _get_richness(quality_dict: dict) -> float:
    """EpisodeQuality 활용 richness 계산. 실패 시 fallback."""
    try:
        return EpisodeQuality(**quality_dict).narrative_richness
    except Exception:
        return quality_dict.get("narrative_richness", 0.5)


# ──────────────────────────────────────────────────────────────
# 재생성 단계
# ──────────────────────────────────────────────────────────────

def _run_regeneration(
    episodes: list[dict],
    source_facts: list[str],
    warnings: _WarningCollector,
) -> list[dict]:
    """
    needs_regeneration=True이고 선별 기준 통과한 에피소드를 1회 재생성.
    실패 시 원본 유지.
    """
    result = []
    for ep in episodes:
        if not ep.get("_needs_regeneration") or not _should_regenerate(ep, ep.get("quality", {})):
            result.append(ep)
            continue

        logger.info(f"[episode_service] 재생성 시작: type={ep.get('type')}")
        try:
            regen = regenerate_episode(
                segment={
                    **ep,
                    "turns":   ep.get("_turns", []),
                    "type":    ep.get("type", "GENERAL_EVENT"),
                    "sensory": ep.get("sensory"),
                    "persons": ep.get("persons", []),
                },
                source_facts=source_facts,
                original_narrative=ep.get("narrative", ""),
                failed_facts=ep.get("_failed_facts", []),
            )
            if regen.get("narrative"):
                ep = {**ep, **regen, "_needs_regeneration": False}
                logger.info("[episode_service] 재생성 완료")
            else:
                warnings.add(f"regen_failed: 재생성 실패, 원본 유지 (type={ep.get('type')})")
        except Exception as e:
            warnings.add(f"regen_error: {e} (type={ep.get('type')})")

        result.append(ep)
    return result


# ──────────────────────────────────────────────────────────────
# 메인 함수
# ──────────────────────────────────────────────────────────────

def run_episode_pipeline(
    session_id: str,
    user_id: str,
    session_log: list[dict],
    profile: UserProfileContext,
    memory_service,
) -> EpisodeGenerateResponse:
    """
    에피소드 생성 파이프라인 전체 실행.
    orchestrator.py에서 백그라운드로 호출.

    Args:
        session_id:      종료된 세션 ID
        user_id:         사용자 ID
        session_log:     인터뷰 전체 대화 로그
        profile:         UserProfileContext
        memory_service:  ChromaDB 메모리 서비스 인스턴스
    """
    warnings = _WarningCollector()
    logger.info(f"[episode_service] 시작: session={session_id}, user={user_id}")

    # ── Step 1: source_facts 스냅샷 ──────────────────────────
    try:
        memory_service.flush(session_id)
        source_facts: list[str] = memory_service.get_facts_by_session(session_id)
        logger.info(f"[episode_service] source_facts: {len(source_facts)}개")
    except Exception as e:
        source_facts = []
        warnings.add(f"facts_fetch_failed: {e}")

    # ── Step 2: 기존 에피소드 조회 ───────────────────────────
    existing_episodes = _fetch_existing_episodes(user_id, warnings)
    logger.info(f"[episode_service] 기존 에피소드: {len(existing_episodes)}개")

    # ── Step 3: segmentor ────────────────────────────────────
    try:
        segments = segment_conversation(session_log, profile, existing_episodes)
    except Exception as e:
        warnings.add(f"segmentor_failed: {e}")
        segments = []

    if not segments:
        logger.warning("[episode_service] segments 없음, 파이프라인 종료")
        payload = _build_callback_payload(session_id, user_id, [], [], warnings)
        ok, reason = _post_callback(payload)
        if not ok:
            logger.error(f"[episode_service] 콜백 최종 실패: {reason}")
        return EpisodeGenerateResponse(
            sessionId=session_id,
            episodes_created=0,
            episodes_merged=0,
            weak_episodes=0,
        )

    # ── Step 4: merger (MERGE 구간 병렬) ─────────────────────
    new_segments, merged_episodes = process_merges(
        segments=segments,
        existing_episodes=existing_episodes,
        new_session_facts=source_facts,
        max_workers=_CFG["merger_max_workers"],
    )
    logger.info(
        f"[episode_service] merger 완료: "
        f"NEW {len(new_segments)}개, MERGED {len(merged_episodes)}개"
    )

    # ── Step 5: writer (NEW 구간 병렬) ───────────────────────
    clean_segments = [_clean_segment(s) for s in new_segments]
    write_results = write_episodes(
        segments=clean_segments,
        source_facts=source_facts,
        profile=profile,
        max_workers=_CFG["writer_max_workers"],
    )

    new_episodes = [
        _merge_segment_and_result(seg, res, session_id, source_facts)
        for seg, res in zip(clean_segments, write_results)
    ]

    # ── Step 6: 선별 재생성 (1회 한정) ──────────────────────
    new_episodes = _run_regeneration(new_episodes, source_facts, warnings)

    # ── Step 7: 내부 필드 제거 + Spring Boot POST ─────────────
    final_new    = [_strip_internal_fields(ep) for ep in new_episodes]
    final_merged = [_strip_internal_fields(ep) for ep in merged_episodes]

    payload = _build_callback_payload(session_id, user_id, final_new, final_merged, warnings)
    ok, reason = _post_callback(payload)

    if ok:
        logger.info(
            f"[episode_service] 완료: "
            f"created={len(final_new)}, merged={len(final_merged)}, "
            f"warnings={len(warnings.get())}"
        )
    else:
        logger.error(f"[episode_service] 콜백 최종 실패: {reason}")

    return EpisodeGenerateResponse(
        sessionId=session_id,
        episodes_created=len(final_new),
        episodes_merged=len(final_merged),
        weak_episodes=payload["weakEpisodes"],
    )