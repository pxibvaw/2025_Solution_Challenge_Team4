# ai/logic/guardrails.py
import re

# ══════════════════════════════════════════════════════
# 입력 필터 (check_input)
# C-SSRS Level 2~5 명시적 표현만 즉시 차단
# Level 1~2 암묵적 표현은 interview_system.md (system prompt)에서 처리
#
# 설계 원칙:
#   - Level 2 (비특정 자살 사고): 명시적 표현만
#   - Level 3 (방법 생각): 방법 언급 포함 표현
#   - Level 4~5 (의도/계획): 구체적 수단 표현
#   - "우울해", "힘들어", "괴로워" 등 일반 감정 표현은 포함하지 않음
#     → LLM이 자연스럽게 공감하도록 위임
# ══════════════════════════════════════════════════════

# Level 2: 비특정 자살 사고 (명시적)
_LEVEL_2 = [
    "자살", "죽고 싶", "죽고싶",
    "살고 싶지 않", "살기 싫",
    "스스로 목숨", "스스로 죽",
]

# Level 1: wish to be dead — 수동적이지만 명시적
# "그냥 잠들어서 안 깨어났으면" 류
_LEVEL_1_EXPLICIT = [
    "안 깨어났으면", "잠들어서 안 깨어",
    "사라지고 싶", "없어지고 싶",
    "이 세상에서 사라",
]

# Level 3~5: 방법/계획/행동 의도 포함 (명시적)
_LEVEL_3_TO_5 = [
    "죽는 방법", "어떻게 죽",
    "목을 매", "목을 메",
    "약을 먹고 죽", "수면제를 먹고",
    "뛰어내리", "투신",
    "손목을 그", "손목을 긋",
    "번개탄",  # 한국 특이 수단
]

CRISIS_KEYWORDS = _LEVEL_2 + _LEVEL_1_EXPLICIT + _LEVEL_3_TO_5

# 기타 입력 필터
# 노인 대상 자서전 인터뷰에서 벗어난 주제
MEDICAL_KEYWORDS = [
    "처방해줘", "처방 받아야", "약 먹어야 하나",
    "진단해줘", "병원 가야 하나",
]
LEGAL_KEYWORDS = ["소송", "법원", "변호사", "계약서", "고소", "합의"]
FINANCIAL_KEYWORDS = ["주식", "투자", "코인", "대출", "보험료", "사기", "돈 빌려"]

# 주의: "암", "약", "병원" 단독은 제거
# 노인 사용자가 자연스럽게 건강 이야기를 할 수 있음
# → 처방/진단 요청처럼 명확히 의학 조언을 구하는 표현만 차단

DEFLECT_RESPONSES = {
    "crisis": {
        "reply": "그런 마음이 드셨군요. 많이 힘드셨겠어요. 혼자 두고 싶지 않아요. 힘드실 때는 자살예방상담전화 1393에 전화하시면 24시간 도움받으실 수 있어요.",
        "question": "지금 가까이 계신 가족분이나 지인이 있으신가요?"
    },
    "medical": {
        "reply": "건강 문제는 제가 잘 모르는 영역이에요. 가까운 병원이나 가족분께 여쭤보시면 좋겠어요.",
        "question": "오늘은 어떤 기억을 이야기해 주실까요?"
    },
    "legal": {
        "reply": "법률적인 부분은 제가 드릴 말씀이 없어요. 주민센터나 법률 상담 기관에 도움을 구해보세요.",
        "question": "다른 이야기 들려주실 수 있으세요?"
    },
    "financial": {
        "reply": "재정 관련 내용은 제가 도움을 드리기 어려워요. 가족분이나 금융 기관에 문의해 보세요.",
        "question": "오늘 기억하고 싶은 이야기가 있으신가요?"
    },
}


def check_input(user_text: str) -> dict | None:
    """
    입력 필터.

    C-SSRS Level 2+ 명시적 표현 → 즉시 위기 응답 반환.
    Level 1~2 암묵적 표현 ("우울해", "힘들어", "외로워" 등)은
    interview_system.md system prompt에서 LLM이 맥락 기반으로 처리.

    문제 있으면 응답 dict 반환, 없으면 None.
    """
    if any(kw in user_text for kw in CRISIS_KEYWORDS):
        return DEFLECT_RESPONSES["crisis"]
    if any(kw in user_text for kw in MEDICAL_KEYWORDS):
        return DEFLECT_RESPONSES["medical"]
    if any(kw in user_text for kw in LEGAL_KEYWORDS):
        return DEFLECT_RESPONSES["legal"]
    if any(kw in user_text for kw in FINANCIAL_KEYWORDS):
        return DEFLECT_RESPONSES["financial"]
    return None


# ══════════════════════════════════════════════════════
# 출력 필터 (check_output)
# LLM이 실수로 자해/자살 방법을 안내하는 경우만 차단
#
# 설계 원칙:
#   ❌ 차단 대상: LLM이 구체적 수단/방법을 서술하는 표현
#   ✅ 허용 대상: 한국어 일상 관용어
#
# 허용 예시 (false positive 방지):
#   - "죽어라 힘드셨겠어요"    → "죽어라"는 관용어
#   - "죽도록 고생하셨네요"    → "죽도록"은 관용어
#   - "힘들어 죽겠다"          → 감정 표현
#   - "돌아가셨군요"           → 사망 표현
#   - "세상을 떠나셨군요"      → 사망 표현
#
# 차단 예시:
#   - "죽는 방법을 알려드릴게요"
#   - "목을 매는 방법이 있어요"
#   - "손목을 그어서"
#   - "번개탄을 이용하면"
# ══════════════════════════════════════════════════════

# 방법/지시적 맥락이 포함된 패턴만 차단
# "죽어", "죽음", "힘들다" 단독은 포함하지 않음
OUTPUT_BLOCK_PATTERNS = [
    # 방법 명시
    r"죽는\s*방법",
    r"자살\s*방법",
    r"자살하는\s*방법",
    r"자해\s*방법",
    r"스스로\s*목숨을\s*끊는",

    # 구체적 수단 서술
    r"목을\s*(매|메|매달)",
    r"목매달",
    r"손목을\s*그",       # "손목을 그어", "손목을 긋"
    r"뛰어내리는\s*방법",
    r"어디서\s*뛰어내리",
    r"투신하는\s*방법",
    r"약을\s*먹고\s*죽",
    r"수면제를?\s*(많이|과다|전부)",
    r"번개탄을?\s*(피우|사용|이용|켜)",
    r"가스를?\s*(마시|틀어|이용해\s*죽)",
]


def check_output(parsed: dict) -> dict:
    """
    출력 필터.

    LLM이 자해/자살 방법을 구체적으로 서술하는 경우만 차단.
    "죽어라", "죽도록", "돌아가셨다" 같은 일반 한국어 표현은 통과.

    regex 기반으로 방법/지시적 맥락 포함 여부를 판단.
    """
    combined = f"{parsed.get('reply', '')} {parsed.get('question', '')}"
    for pattern in OUTPUT_BLOCK_PATTERNS:
        if re.search(pattern, combined):
            return {
                "reply": "많이 힘드셨겠어요. 혼자 두고 싶지 않아요. 자살예방상담전화 1393에 전화하시면 24시간 도움받으실 수 있어요.",
                "question": "지금 가까이 계신 분이 있으신가요?"
            }
    return parsed


# ══════════════════════════════════════════════════════
# memory 저장 필터 (check_memory)
# ══════════════════════════════════════════════════════

PII_PATTERNS = [
    r"\d{6}-\d{7}",        # 주민등록번호
    r"\d{3}-\d{4}-\d{4}", # 전화번호
    r"\d{10,16}",          # 계좌번호 / 카드번호
]


def check_memory(fact: str) -> bool:
    """
    memory 저장 필터. 저장해도 되면 True, PII 감지 시 False.
    """
    for pattern in PII_PATTERNS:
        if re.search(pattern, fact):
            return False
    return True