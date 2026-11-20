# ai/app/orchestrator.py
from ai.services.interview_service import (
    run_interview,
    get_history,
    reset_history,
    get_unextracted_turns,
    update_extracted_index,
)
from ai.services.memory_extractor import extract_facts
from ai.services.memory_importance import is_important
from ai.services.memory_deduplication import is_duplicate
from ai.services.memory_service import save_memory
from ai.services.memory_consolidation import run_consolidation
from ai.logic.guardrails import check_memory
from ai.memory.chroma_store import count_memories
from ai.app.schemas import UserProfileContext


def handle_turn(user_text: str, profile: UserProfileContext = None, session_id: str = "default") -> dict:
    # 중간 추출 트리거는 api.py BackgroundTasks에서 처리
    return run_interview(user_text, profile=profile, session_id=session_id)


def mid_session_extraction(session_id: str, user_id: str = "") -> dict:
    """
    미추출 턴만 추출해서 ChromaDB에 저장.
    api.py BackgroundTasks로 비동기 실행 → 응답 지연 없음.
    세션 중에도 오래된 기억을 ChromaDB에서 참조 가능.
    """
    new_turns = get_unextracted_turns(session_id)

    if not new_turns:
        return {"saved": 0, "skipped": 0}

    facts = extract_facts(new_turns)

    if not facts:
        update_extracted_index(session_id)
        return {"saved": 0, "skipped": 0}

    memory_count = count_memories()
    saved, skipped = 0, 0

    for fact in facts:
        important, score = is_important(fact, memory_count)
        if not important:
            skipped += 1
            continue
        if is_duplicate(fact):
            skipped += 1
            continue
        if not check_memory(fact):
            skipped += 1
            continue

        save_memory(fact, importance=score, session_id=session_id, user_id=user_id)
        saved += 1
        memory_count += 1

    update_extracted_index(session_id)
    return {"saved": saved, "skipped": skipped}


def process_memory_pipeline(session_id: str = "default", user_id: str = "") -> dict:
    """
    세션 종료 시 미추출 턴만 처리.
    중간 추출로 이미 저장된 턴은 재처리하지 않음.
    """
    remaining_turns = get_unextracted_turns(session_id)

    if not remaining_turns:
        return {"saved": 0, "skipped": 0, "reason": "all turns already extracted"}

    facts = extract_facts(remaining_turns)

    if not facts:
        return {"saved": 0, "skipped": 0, "reason": "no facts extracted"}

    memory_count = count_memories()
    saved, skipped = 0, 0

    for fact in facts:
        important, score = is_important(fact, memory_count)
        if not important:
            skipped += 1
            continue
        if is_duplicate(fact):
            skipped += 1
            continue
        if not check_memory(fact):
            skipped += 1
            continue

        save_memory(fact, importance=score, session_id=session_id, user_id=user_id)
        saved += 1
        memory_count += 1

    return {"saved": saved, "skipped": skipped}


def end_session(
    session_id: str,
    user_id: str,
    profile: UserProfileContext,
) -> tuple[dict, list[dict]]:
    """
    세션 종료 처리.

    순서:
      1. session_log 캡처 — reset_history 전에 반드시 먼저
      2. 남은 메모리 파이프라인 처리
      3. reset_history — 로그 즉시 해제
      4. (memory_result, session_log) 반환

    episode_service는 orchestrator가 직접 호출하지 않음.
    api.py에서 session_log를 받아 BackgroundTasks로 run_episode_pipeline 호출.
    → 책임 분리: orchestrator는 메모리+로그 관리, 에피소드 생성은 api.py 레이어

    Args:
        session_id:  종료할 세션 ID
        user_id:     사용자 ID (api.py → episode_service 전달용)
        profile:     UserProfileContext (api.py → episode_service 전달용)

    Returns:
        (memory_result, session_log)
        memory_result: {"saved": int, "skipped": int}
        session_log:   list[dict] — [{"user": ..., "ai": ...}, ...]
                       빈 세션이면 []
    """
    # Step 1: 로그 캡처 (reset_history 이전 필수)
    session_log = get_history(session_id)

    # Step 2: 남은 메모리 파이프라인
    memory_result = process_memory_pipeline(session_id, user_id=user_id)

    # Step 3: 로그 해제 (메모리 누수 방지)
    reset_history(session_id)

    # Step 4: consolidation
    if count_memories() > 50:
        run_consolidation()

    return memory_result, session_log