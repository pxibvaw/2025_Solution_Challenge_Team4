# ai/prompts/autobiography_chapter_prompt.py

# ──────────────────────────────────────────────────────────────
# 자서전 챕터 생성 프롬프트 (Chapter Writer)
#
# 설계 근거:
#   StorySage Section Writer: 챕터별 독립 생성
#   DOME Lost in the Middle 방지: 챕터별 에피소드만 입력
#   Few-shot style imitation (Wang et al. 2025 / Bhandarkar 2024):
#     실제 발화 exemplar → 말투 보존
#   할루시네이션 방지 3중 전략:
#     1. episode_narratives를 유일한 사실 근거로 명시 (Grounding)
#     2. atomic_facts 자기검증 (에피소드 writer와 동일)
#     3. transition_hint로 연결부 범위 제한
#   Butler Life Review Theory (1963):
#     quote 직접 포함 → "내 이야기다" 체험 극대화
# ──────────────────────────────────────────────────────────────

CHAPTER_PROMPT = """당신은 한 사람의 자서전에서 한 챕터를 쓰는 작가입니다.
아래 에피소드들을 바탕으로 하나의 자연스럽고 감동적인 챕터를 작성하십시오.

## 자서전 전체 테마
{life_theme}

## 이 챕터의 설계 지침 (편집자가 정한 구조)
- 챕터 제목: {chapter_title}
- 핵심 테마: {core_theme}
- 감정 흐름: {emotional_arc}
- 다음 챕터 연결 힌트: {transition_hint}

## 이 사람이 실제로 한 말 (이 말투 그대로 써라)
{style_exemplars}

분석하지 마라. 이 문장들을 읽고 그 사람의 어미, 단어 선택,
문장 리듬을 자연스럽게 흡수해서 써라.

## 이 챕터의 에피소드 서술 (유일한 사실 근거)
{episode_narratives}

## 이 챕터의 인상적인 발화 목록
{episode_quotes}

## 길이 기준
{length_guide}

---

## 작성 규칙

### 할루시네이션 방지 (최우선)

허용:
  - 에피소드 서술에 있는 사실의 자연스러운 재서술
  - 감정/시간 흐름으로 에피소드 간 연결
  - 발화 목록의 문장을 큰따옴표로 감싸서 직접 포함
  - transition_hint 방향으로 챕터 마지막 문장 마무리

절대 금지:
  - 에피소드 서술에 없는 새로운 사건/사실/인물 추가
  - 등장인물 이름, 관계, 수 변경
  - 연도/장소를 임의로 추정해서 추가
  - transition_hint 외의 다음 챕터 내용 언급

### 1인칭 자서전 서술
  - 화자는 사용자 본인. "나는", "저는"으로 서술
  - 위 말투 예시의 종결어미와 단어 선택을 그대로 따라라
  - 과거형 시제 일관 유지
  - 발화 포함 시: 큰따옴표로 감싸서 독자가 실제 목소리를 느끼게 하라
    예: "그때가 참 좋았는데, 외롭기도 했지요."라는 말처럼

### 구조
  - 2~4단락
  - 단락은 자연스러운 감정 흐름으로 이어져야 한다
  - 마지막 문장은 transition_hint 방향으로 다음 챕터를 암시하라

---

## Atomic Fact 자기검증
챕터 서술 후, narrative에서 사실 주장을 원자 단위로 분해하라.
각 사실이 에피소드 서술에 근거 있으면 grounded: true, 없으면 false.
faithfulness_score = true 수 / 전체 수

---

## 출력 형식
반드시 아래 JSON만 출력하라.

{{
  "narrative": "챕터 서술 전문",
  "atomic_facts": [
    {{"fact": "사실 주장", "grounded": true}}
  ],
  "faithfulness_score": 0.97
}}"""