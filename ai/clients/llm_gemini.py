# ai/clients/llm_gemini.py
"""
Gemini LLM 클라이언트 (Bulkhead 패턴 적용).

설계 근거:
  Bulkhead Pattern (Microsoft Resilience Patterns):
    태스크 유형별 독립 세마포어로 격리 → 백그라운드 부하가
    실시간 인터뷰 응답을 차단하지 않도록 보장.
  CONCUR (2025): Congestion-Based Concurrency Control for LLM.
  Google Gemini API Docs: client-side rate limiting 권장.

풀 구조:
  realtime  — handle_turn (사용자 대기 중, 최우선)
  background — 에피소드/메모리/자서전 (백그라운드)
"""
import logging
import os
import threading
import time

from google import genai
from ai.app.settings import settings

logger = logging.getLogger(__name__)

client = genai.Client(api_key=settings.GEMINI_API_KEY)


# ──────────────────────────────────────────────────────────────
# Bulkhead: 태스크 유형별 독립 세마포어
# ──────────────────────────────────────────────────────────────

_REALTIME_MAX = int(os.getenv("LLM_REALTIME_MAX_CONCURRENT", "5"))
_BACKGROUND_MAX = int(os.getenv("LLM_BACKGROUND_MAX_CONCURRENT", "5"))

_pools = {
    "realtime":   threading.Semaphore(_REALTIME_MAX),
    "background": threading.Semaphore(_BACKGROUND_MAX),
}


# ──────────────────────────────────────────────────────────────
# 응답 가드 (safety filter / 할당량 초과 / 일시적 네트워크)
# ──────────────────────────────────────────────────────────────
#
# Gemini는 safety filter 발동 시 response.text를 None으로 반환할 수 있고,
# 일시적 네트워크 오류로 빈 문자열이 올 수도 있다.
# 하위 파서(parse_llm_response, parse_llm_json)는 None/빈 문자열을 받으면
# AttributeError 또는 JSONDecodeError로 raw 500을 일으킨다.
#
# 정책:
#   1. None / 빈 문자열이면 1회 재시도 (0.8s backoff)
#   2. 그래도 실패하면 안내 메시지를 반환 (인터뷰 자체가 끊기지 않게)
#   3. 모든 실패는 warning 로그로 남겨 환각 튜닝 시 추적 가능

_EMPTY_RESPONSE_FALLBACK = (
    "죄송해요, 잠시 답을 떠올리지 못했어요. 같은 이야기를 다시 들려주실 수 있을까요?"
)


def _is_empty_response(text) -> bool:
    """Gemini 응답이 None이거나 공백만 있는지 판정."""
    return text is None or (isinstance(text, str) and not text.strip())


def _call_gemini(prompt: str):
    """단일 Gemini 호출. 예외는 None 반환으로 흡수."""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text
    except Exception as e:
        # exc_info=True: 스택트레이스까지 남겨 환각 튜닝 중 원인 추적 쉽게.
        logger.warning(f"[generate_reply] Gemini 호출 예외: {e}", exc_info=True)
        return None


def generate_reply(prompt: str, pool: str = "background") -> str:
    """
    Gemini 2.5 Flash에 프롬프트를 보내고 응답 텍스트를 반환.

    Args:
        prompt: LLM에 보낼 프롬프트 문자열
        pool:   "realtime" (인터뷰 응답) 또는 "background" (에피소드/자서전 등)
                기본값 "background" → 기존 호출 코드 변경 불필요.

    Returns:
        LLM 응답 텍스트. Gemini가 None/빈 문자열을 반환하면
        1회 재시도 후에도 실패 시 안내 메시지 fallback.
    """
    semaphore = _pools.get(pool, _pools["background"])

    semaphore.acquire()
    try:
        # 1차 호출
        text = _call_gemini(prompt)

        # 빈 응답이면 1회 재시도
        if _is_empty_response(text):
            time.sleep(0.8)
            text = _call_gemini(prompt)

        # 그래도 빈 응답이면 안내 메시지 fallback
        if _is_empty_response(text):
            logger.warning(
                "[generate_reply] Gemini가 빈/None 응답 "
                "(safety filter 또는 할당량 의심) — "
                f"pool={pool}, prompt_len={len(prompt)}"
            )
            return _EMPTY_RESPONSE_FALLBACK

        return text
    finally:
        semaphore.release()
