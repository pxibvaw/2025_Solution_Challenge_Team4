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


def generate_reply(prompt: str, pool: str = "background") -> str:
    """
    Gemini 2.5 Flash에 프롬프트를 보내고 응답 텍스트를 반환.

    Args:
        prompt: LLM에 보낼 프롬프트 문자열
        pool:   "realtime" (인터뷰 응답) 또는 "background" (에피소드/자서전 등)
                기본값 "background" → 기존 호출 코드 변경 불필요.

    Returns:
        LLM 응답 텍스트
    """
    semaphore = _pools.get(pool, _pools["background"])

    semaphore.acquire()
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text
    finally:
        semaphore.release()
