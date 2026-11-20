# ai/services/memory_importance.py
import json
import re
from ai.clients.llm_gemini import generate_reply

IMPORTANCE_PROMPT = """
아래 문장이 한 사람의 인생을 이해하는 데 얼마나 중요한지 1~10으로 평가하세요.

1 = 전혀 중요하지 않음 (날씨, 오늘 기분 등 일시적인 것)
10 = 매우 중요함 (가족, 고향, 직업, 인생의 전환점 등)

규칙:
1. 숫자만 출력하세요
2. 다른 텍스트는 절대 포함하지 마세요

문장: {fact}
"""

# heuristic 키워드
# 근거: Butler(1963) Life Review, Haight Life Story Book methodology,
#       PMC2682386 (출생지/부모/형제/관계/직업/상실),
#       한국 노인 세대(1930~60년대생) 특성 반영
HEURISTIC_RULES = [
    # 카테고리 1 — 핵심 가족 관계 (+3)
    # 배우자/자녀/부모는 Life Review 연구에서 일관되게 가장 중요한 카테고리
    (["남편", "아내", "부인", "아들", "딸", "아버지", "어머니",
      "아버님", "어머님", "아빠", "엄마", "부모"], 3),

    # 카테고리 2 — 삶의 전환점 (+3)
    # 결혼, 출산, 사별, 전쟁, 피난은 한국 노인 서사의 핵심 변곡점
    # 근거: Life Story Book research — relationships and loss, turning points
    (["결혼", "혼인", "장가", "시집", "낳았", "출산", "태어났",
      "죽었", "돌아가셨", "떠나셨", "여의었", "사별",
      "전쟁", "6.25", "피난", "군대", "입대", "제대",
      "졸업", "입학", "취직", "이사", "고향 떠났"], 3),

    # 카테고리 3 — 확대 가족 관계 (+2)
    # 한국 노인 세대는 대가족 구조 — 며느리, 사위, 손자녀가 삶의 의미의 핵심
    (["며느리", "사위", "손자", "손녀", "외손자", "외손녀",
      "시어머니", "시아버지", "장인", "장모",
      "할머니", "할아버지", "외할머니", "외할아버지",
      "형", "오빠", "언니", "누나", "동생", "남동생", "여동생",
      "조카", "친척"], 2),

    # 카테고리 4 — 직업 / 사회적 역할 (+2)
    # 근거: Life Story Book — occupation, social roles
    (["어부", "농부", "농사", "장사", "상인", "공장", "직장", "회사",
      "선생", "교사", "교수", "의사", "간호사",
      "군인", "경찰", "공무원", "사업",
      "주부", "살림", "일했", "일하셨", "기술자"], 2),

    # 카테고리 5 — 고향 / 출생지 / 성장 장소 (+2)
    # 근거: PMC2682386 — "places of birth" 핵심 기억으로 일관되게 등장
    # 특정 도시명 대신 장소의 의미를 담은 단어로 설계
    (["고향", "태어난", "자란", "살던", "살았던",
      "마을", "동네", "시골", "농촌", "산골",
      "바닷가", "섬", "항구", "산", "강가"], 2),

    # 카테고리 6 — 역경 / 고생 (+2)
    # 한국 1930~60년대생 노인의 서사에서 가난과 전후 고생은
    # 자아 정체성과 자녀 교육에 대한 의미와 직결됨
    (["가난", "고생", "어려웠", "힘들었", "못 먹었",
      "굶었", "보릿고개", "없었", "빈곤", "전쟁통", "피난길"], 2),

    # 카테고리 7 — 감정 기억 (+1)
    # 근거: Sensory/emotional memories — Life Review에서 보조적 역할
    (["기뻤", "슬펐", "행복했", "외로웠", "그립",
      "무서웠", "설레었", "즐거웠", "보고 싶", "잊을 수 없",
      "사랑", "그리움"], 1),

    # 카테고리 8 — 신앙 / 가치관 (+1)
    # 한국 노인 세대에서 종교적 정체성은 삶의 의미와 연결됨
    (["교회", "성당", "절", "신앙", "기도", "믿음",
      "하느님", "하나님", "부처", "스님"], 1),

    # 카테고리 9 — 시간 표현 (+1)
    # 맥락적 지표 — 단독으로는 낮은 점수, 다른 카테고리와 결합 시 의미 강화
    (["어릴 때", "젊었을 때", "그 시절", "당시", "옛날",
      "학창시절", "신혼", "결혼 전", "결혼 후"], 1),
]


def heuristic_score(fact: str) -> float:
    """
    rule-based heuristic 점수 계산 (1~10 정규화)
    기본값 1점, 카테고리 hit마다 가산, 최대 10점 cap
    """
    score = 1  # 기본값
    for keywords, point in HEURISTIC_RULES:
        if any(kw in fact for kw in keywords):
            score += point
    return min(score, 10)


def llm_score(fact: str) -> float:
    """
    LLM importance 점수 계산 (1~10)
    """
    prompt = IMPORTANCE_PROMPT.format(fact=fact)
    raw = generate_reply(prompt).strip()

    try:
        score = float(re.search(r"\d+(\.\d+)?", raw).group())
        return min(max(score, 1), 10)
    except:
        return 5.0


def score_importance(fact: str) -> float:
    """
    최종 importance score
    importance_final = 0.7 * llm_score + 0.3 * heuristic_score
    """
    l_score = llm_score(fact)
    h_score = heuristic_score(fact)
    return round(0.7 * l_score + 0.3 * h_score, 2)


def is_important(fact: str, memory_count: int) -> tuple[bool, float]:
    """
    threshold 기준으로 저장 여부 판단
    memory < 50: >= 5
    memory >= 50: >= 6
    """
    threshold = 5 if memory_count < 50 else 6
    score = score_importance(fact)
    return score >= threshold, score