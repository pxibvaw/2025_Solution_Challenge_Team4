# ai/services/memory_extractor.py
import json
import re
from ai.clients.llm_gemini import generate_reply


EXTRACT_PROMPT = """
아래 대화에서 사용자에 대한 중요한 사실(fact)만 추출하세요.

추출 대상:
- 인물 (가족, 지인 이름 및 관계)
- 장소 (살았던 곳, 고향, 여행지)
- 직업 / 역할
- 사건 (중요한 경험, 기억)

규칙:
1. 사용자가 직접 말한 내용만 추출하세요
2. 추측하거나 덧붙이지 마세요
3. 각 fact는 1문장으로 간결하게 작성하세요
4. 추출할 내용이 없으면 반드시 빈 배열을 반환하세요
5. 반드시 아래 JSON 형식으로만 출력하세요

출력 형식:
{{
    "facts": [
        "추출된 fact 1",
        "추출된 fact 2"
    ]
}}

---

좋은 추출 예시:
대화:
User: 저 어릴 때 부산 영도에서 살았어요. 아버지가 어부셨거든요.
AI: 부산에서 사셨군요. 바다 가까이 사셨겠네요.
User: 네, 매일 아침 아버지 배 떠나는 거 봤어요.

출력:
{{
    "facts": [
        "사용자는 어릴 때 부산 영도에서 살았다.",
        "사용자의 아버지는 어부였다.",
        "사용자는 어린 시절 매일 아침 아버지의 배가 떠나는 것을 보았다."
    ]
}}

---

나쁜 추출 예시 (하면 안 되는 것):
대화:
User: 그냥 옛날 생각이 나요.
AI: 어떤 기억이 떠오르세요?

잘못된 출력:
{{
    "facts": [
        "사용자는 옛날을 그리워한다.",   ← 감정이지 fact가 아님
        "사용자는 과거에 관심이 많다."   ← 추측
    ]
}}

올바른 출력:
{{
    "facts": []   ← 구체적인 fact 없음
}}

---

대화:
{conversation}
"""


def _parse_facts(raw: str) -> list[str]:
    """LLM 응답에서 facts 리스트 파싱"""
    try:
        cleaned = re.sub(r"```json|```", "", raw).strip()
        parsed = json.loads(cleaned)
        facts = parsed.get("facts", [])
        return [f for f in facts if isinstance(f, str) and f.strip()]
    except json.JSONDecodeError:
        return []


def extract_facts(conversation_history: list) -> list[str]:
    """
    세션 전체 대화에서 facts 추출.

    Gemini 2.5 Flash 기준 100턴 × 200자 ≈ 14,000토큰.
    컨텍스트 1M 토큰의 1.4% 수준이므로 청킹 불필요.
    전체를 한 번에 넣어 추출 품질 최대화.
    """
    if not conversation_history:
        return []

    conversation = "\n".join(
        f"User: {t['user']}\nAI: {t['ai']}"
        for t in conversation_history
    )
    prompt = EXTRACT_PROMPT.format(conversation=conversation)
    raw = generate_reply(prompt)
    return _parse_facts(raw)