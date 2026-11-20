# ai/services/interview_service.py
from ai.services.memory_service import retrieve_memory
from ai.services.prompt_builder import build_prompt
from ai.clients.llm_gemini import generate_reply
from ai.logic.formatting import parse_llm_response
from ai.logic.guardrails import check_input, check_output
from ai.app.schemas import UserProfileContext

_sessions: dict[str, list] = {}         # sessionId → conversation_history
_extracted_index: dict[str, int] = {}   # sessionId → 마지막으로 추출 완료한 턴 인덱스

MAX_TURNS = 100           # 세션에 저장할 최대 턴 수
CONVERSATION_WINDOW = 15  # 매 턴 LLM 프롬프트에 넘길 최근 턴 수
MID_EXTRACTION_INTERVAL = 10  # 중간 추출 주기


def run_interview(user_text: str, profile: UserProfileContext = None, session_id: str = "default"):

    if session_id not in _sessions:
        _sessions[session_id] = []
        _extracted_index[session_id] = 0

    conversation_history = _sessions[session_id]

    # 0. 입력 필터
    deflect = check_input(user_text)
    if deflect:
        return deflect

    # 1. memory 검색
    memory = retrieve_memory(user_text)

    # 2. 최근 CONVERSATION_WINDOW 턴만 프롬프트에 사용
    recent_turns = conversation_history[-CONVERSATION_WINDOW:]
    conversation = "\n".join(
        f"User: {t['user']}\nAI: {t['ai']}"
        for t in recent_turns
    )

    # 3. prompt 생성
    prompt = build_prompt(
        user_text=user_text,
        memory=memory,
        conversation=conversation,
        profile=profile
    )

    # 4. LLM 호출 (realtime 풀: 사용자 대기 중이므로 최우선)
    raw_reply = generate_reply(prompt, pool="realtime")

    # 5. JSON 파싱
    parsed = parse_llm_response(raw_reply)

    # 6. 출력 필터
    parsed = check_output(parsed)

    # 7. 턴 저장
    conversation_history.append({
        "user": user_text,
        "ai": f"{parsed['reply']} {parsed['question']}"
    })

    # 8. 최대 턴 수 초과 시 가장 오래된 턴 제거 + 인덱스 조정
    if len(conversation_history) > MAX_TURNS:
        conversation_history.pop(0)
        if _extracted_index[session_id] > 0:
            _extracted_index[session_id] -= 1

    return parsed


def should_mid_extract(session_id: str) -> bool:
    """중간 추출 주기 도달 여부"""
    history = _sessions.get(session_id, [])
    extracted = _extracted_index.get(session_id, 0)
    return (len(history) - extracted) >= MID_EXTRACTION_INTERVAL


def get_unextracted_turns(session_id: str) -> list:
    """아직 추출되지 않은 새 턴만 반환"""
    history = _sessions.get(session_id, [])
    extracted = _extracted_index.get(session_id, 0)
    return history[extracted:]


def update_extracted_index(session_id: str):
    """추출 완료 후 인덱스를 현재 히스토리 끝으로 업데이트"""
    history = _sessions.get(session_id, [])
    _extracted_index[session_id] = len(history)


def get_history(session_id: str = "default") -> list:
    return _sessions.get(session_id, []).copy()


def reset_history(session_id: str = "default"):
    if session_id in _sessions:
        del _sessions[session_id]
    if session_id in _extracted_index:
        del _extracted_index[session_id]