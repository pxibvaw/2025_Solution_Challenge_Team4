# ai/prompts/autobiography_planner_prompt.py

# ──────────────────────────────────────────────────────────────
# 자서전 구조 설계 프롬프트 (Planner)
#
# 설계 근거:
#   StorySage (UIST 2025): Planner/Section Writer 분리 구조
#     — Planner는 구조만, Writer는 서술만 담당
#   DOME (NAACL 2025): 계층적 outline 생성 후 서술
#     — 구조 확정 후 챕터별 독립 생성으로 Lost in the Middle 방지
#   McAdams (2008): 삶의 이야기는 시기별 chapter + 전체 life_theme 구조
#   할루시네이션 방지: Planner는 narrative 쓰지 않음
#     — 에피소드 요약(title+quote)만 보고 구조 결정
#     — 새 사실 생성 가능성 자체를 차단
# ──────────────────────────────────────────────────────────────

PLANNER_PROMPT = """당신은 한 사람의 삶을 자서전으로 구성하는 편집자입니다.
아래 에피소드 목록을 분석해서 자서전의 전체 구조를 설계하십시오.

## 사용자 정보
- 이름/호칭: {user_title}
- 출생연도: {birth_year}
- 기억에 남는 나이: {memorable_age}

## 에피소드 목록 (전체 {episode_count}개)
{episode_summaries}

---

## 설계 규칙

### 챕터 구성
- 최대 {max_chapters}개 챕터로 구성하라
- 시기(period_label)가 비슷한 에피소드를 같은 챕터로 묶어라
- 챕터는 시간 순서대로 배열하라
- 챕터당 최대 4개 에피소드 (importance_score 높은 것 우선)

### life_theme 도출
- 전체 에피소드의 life_value, emotion_nuance, quote를 종합해
  이 사람의 삶을 관통하는 핵심 테마를 한 문장으로 도출하라
- 추상적 표현 금지. 구체적이고 이 사람만의 테마여야 한다
  나쁜 예: "열심히 살아온 삶"
  좋은 예: "묵묵한 헌신으로 가족을 지킨 새벽의 사람"

### transition_hint
- 각 챕터의 transition_hint는 다음 챕터로 자연스럽게 이어지는
  감정적/시간적 흐름 한 문장이다
- 에피소드에 있는 내용에서만 도출하라. 새 사실을 만들지 마라
- 마지막 챕터의 transition_hint는 epilogue로 연결되는 마무리 방향

---

## 출력 형식
반드시 아래 JSON만 출력하라. 다른 텍스트 없이.

{{
  "life_theme": "이 사람의 삶을 관통하는 핵심 테마 한 문장",
  "chapters": [
    {{
      "title": "챕터 제목",
      "period_label": "유년기 / 신혼 / 육아기 등",
      "episode_ids": ["ep-001", "ep-002"],
      "core_theme": "핵심 테마 한 단어",
      "emotional_arc": "설렘 → 외로움 → 적응",
      "transition_hint": "다음 챕터로 이어지는 감정/시간 흐름 한 문장"
    }}
  ]
}}"""