# ai/app/api.py
import asyncio
from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends, APIRouter
from pydantic import BaseModel
from ai.app.schemas import (
    TurnRequest, TurnResponse,
    EndSessionRequest, EndSessionResponse,
    AutobiographyRequest, AutobiographyResponse,
    UserProfileContext,
)
from ai.app.orchestrator import handle_turn, end_session, mid_session_extraction
from ai.app.settings import settings
from ai.services.interview_service import get_history, should_mid_extract
from ai.services.episode_service import run_episode_pipeline
from ai.services.autobiography_service import generate_autobiography
from ai.services.memory_service import memory_service
from ai.clients.tts_google import text_to_speech
from ai.utils.cache import InMemoryCacheBackend

# ── FastAPI 앱 생성 ──────────────────────────────────────────
# 프로덕션: /docs, /redoc 비활성화 (보안)
app = FastAPI(
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None if settings.is_production else "/redoc",
)

# ── 캐시 ─────────────────────────────────────────────────────
# InMemoryCacheBackend: thread-safe TTLCache (cachetools 래핑)
# Redis 전환 시 → RedisCacheBackend로 import만 교체
_request_cache = InMemoryCacheBackend(maxsize=1000, ttl=60)        # idempotency: 60초 TTL
_session_profiles = InMemoryCacheBackend(maxsize=500, ttl=3600)    # profile: 1시간 TTL


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/turn", response_model=TurnResponse)
async def turn(req: TurnRequest, background_tasks: BackgroundTasks):
    cached = _request_cache.get(req.requestId)
    if cached is not None:
        return cached

    result = await asyncio.get_event_loop().run_in_executor(
        None,
        lambda: handle_turn(req.userText, profile=req.profile, session_id=req.sessionId)
    )

    # 세션별 profile 저장 (end_session 시 episode_service 전달용)
    _session_profiles.set(req.sessionId, req.profile)

    turn_index = len(get_history(req.sessionId))

    audio_b64 = await asyncio.get_event_loop().run_in_executor(
        None,
        lambda: text_to_speech(f"{result['reply']} {result['question']}")
    )

    response = TurnResponse(
        requestId=req.requestId,
        reply=result["reply"],
        question=result["question"],
        turnIndex=turn_index,
        audioContent=audio_b64
    )

    _request_cache.set(req.requestId, response)

    # 10턴마다 중간 추출 백그라운드 실행
    # 응답 반환 후 비동기로 처리 → 응답 지연 없음
    if should_mid_extract(req.sessionId):
        background_tasks.add_task(_run_mid_extraction, req.sessionId)

    return response


@app.post("/end-session", response_model=EndSessionResponse)
async def end_session_endpoint(req: EndSessionRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(
        _run_end_session,
        req.sessionId,
        req.userId,
    )

    return EndSessionResponse(
        sessionId=req.sessionId,
        saved=0,
        skipped=0
    )


@app.post("/autobiography", response_model=AutobiographyResponse)
async def autobiography(req: AutobiographyRequest):
    """
    자서전 생성 엔드포인트.

    FE 에피소드 페이지에서 선택한 에피소드로 자서전 생성.
    LLM 호출 N+3회 (N=챕터 수) — 동기 처리, 수십 초 소요 가능.
    """
    if not req.episodes:
        raise HTTPException(status_code=400, detail="에피소드가 없습니다.")

    try:
        result = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: generate_autobiography(req, profile=None)
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"자서전 생성 실패: {e}")


# ── 테스트 전용 엔드포인트 ─────────────────────────────────────
# 이중 방어:
#   1차: settings.is_production이면 라우터 자체를 등록하지 않음
#   2차: Dependency guard — 혹시 등록되더라도 프로덕션에서 404 반환

async def _require_test_env():
    """2차 안전장치 — 라우터가 실수로 등록되어도 프로덕션에서 차단."""
    if settings.is_production:
        raise HTTPException(status_code=404, detail="Not Found")

test_router = APIRouter(
    prefix="/test",
    tags=["test"],
    dependencies=[Depends(_require_test_env)],
)


class CleanupRequest(BaseModel):
    sessionId: str
    userId: str


@test_router.delete("/cleanup")
async def test_cleanup(req: CleanupRequest):
    """
    테스트 후 AI 서버 인메모리 데이터 정리.
    - 인메모리 캐시 (_request_cache, _session_profiles) 해당 세션 항목 제거
    - ChromaDB 해당 세션 메모리 삭제

    개발/테스트 환경에서만 사용 가능.
    프로덕션에서는 Dependency guard + 라우터 미등록으로 이중 차단.
    """
    cleaned = {}

    # 인메모리 캐시 정리
    session_id = req.sessionId
    removed_requests = _request_cache.clear_by_prefix(session_id)
    cleaned["request_cache"] = removed_requests

    _session_profiles.delete(session_id)
    cleaned["session_profiles"] = 1 if session_id else 0

    # ChromaDB 메모리 삭제
    try:
        deleted_count = memory_service.delete_by_session(session_id)
        cleaned["chromadb_memories"] = deleted_count
    except AttributeError:
        # memory_service에 delete_by_session 미구현 시
        cleaned["chromadb_memories"] = "not_supported"
    except Exception as e:
        cleaned["chromadb_memories"] = f"error: {e}"

    return {"cleaned": cleaned, "sessionId": session_id}


# 1차 방어: 프로덕션이 아닐 때만 라우터 등록
if not settings.is_production:
    app.include_router(test_router)


def _run_mid_extraction(session_id: str):
    result = mid_session_extraction(session_id)
    print(f"[mid-extraction] sessionId={session_id} saved={result['saved']} skipped={result['skipped']}")


def _run_end_session(session_id: str, user_id: str):
    """
    세션 종료 백그라운드 태스크.

    순서:
      1. orchestrator.end_session → 메모리 처리 + session_log 반환
      2. session_log 있을 때만 episode_pipeline 실행
      3. profile 캐시 정리
    """
    profile = _session_profiles.get(session_id)

    memory_result, session_log = end_session(session_id, user_id, profile)
    print(
        f"[end-session] sessionId={session_id} "
        f"saved={memory_result['saved']} skipped={memory_result['skipped']}"
    )

    if session_log:
        run_episode_pipeline(
            session_id=session_id,
            user_id=user_id,
            session_log=session_log,
            profile=profile,
            memory_service=memory_service,
        )

    # profile 캐시 정리
    _session_profiles.delete(session_id)