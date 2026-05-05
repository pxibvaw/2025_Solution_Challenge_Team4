# REPLY/ QUESTION 파싱
# ai/logic/formatting.py
import json
import re


def parse_llm_response(raw: str) -> dict:
    """
    LLM 응답에서 reply + question JSON 파싱
    실패 시 fallback 반환
    """

    # 1. ```json ... ``` 블록 제거
    cleaned = re.sub(r"```json|```", "", raw).strip()

    # 2. JSON 파싱 시도
    try:
        parsed = json.loads(cleaned)
        reply = parsed.get("reply", "")
        question = parsed.get("question", "")

        if reply and question:
            return {"reply": reply, "question": question}

    except json.JSONDecodeError:
        pass

    # 3. fallback — 파싱 실패 시 기본값
    return {
        "reply": raw.strip(),
        "question": "조금 더 이야기해 주시겠어요?"
    }