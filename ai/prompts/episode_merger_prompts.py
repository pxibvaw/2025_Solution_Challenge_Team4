# ai/prompts/episode_merger_prompts.py

MERGER_PROMPT = """
당신은 노인의 삶의 이야기를 자서전으로 옮기는 전문 작가입니다.
같은 시기·인물·주제의 두 이야기를 하나의 더 풍부한 에피소드로 통합합니다.

## 기존 에피소드 서술 (보강 대상)
{original_narrative}

## 기존 검증된 사실 목록
{original_facts}

## 새로 추가된 대화 (이번 세션에서 나온 내용)
{new_conversation}

## 새로 검증된 사실 목록
{new_facts}

## 에피소드 분류 정보
{metadata}

## 이 사람이 실제로 한 말 (이 스타일 그대로 써라)
{style_exemplars}

## 길이 기준
{length_guide}

## 감각 표현 힌트
{sensory_hints}

## 등장인물
{person_hints}

---

## 통합 작성 규칙

### 핵심 원칙
- 기존 서술의 좋은 부분을 보존하면서 새 내용을 자연스럽게 녹여라
- 두 서술을 단순히 이어붙이지 마라. 하나의 흐름으로 재구성하라
- 기존 facts와 새 facts 모두를 반영하되, 중복은 한 번만 서술하라

### 할루시네이션 방지
- 기존 facts + 새 facts 목록에 있는 내용만 서술하라
- 두 목록 모두에 없는 내용을 추가하지 마라

### 1인칭 자서전 서술
- 화자는 사용자 본인
- 위 예시 문장의 종결어미와 단어 선택을 그대로 사용하라
- 과거형 시제 일관 유지
- 1~2단락, 길이 기준 준수

---

## Atomic Fact Decomposition (자기 검증)
narrative의 사실 주장을 원자 단위로 분해.
기존 facts 또는 새 facts에 근거 있으면 grounded: true.

---

## 품질 평가 (원본 대화 + 기존 서술 기준)

emotional_authenticity (1~5): 감정 뉘앙스 보존도
sensory_vividness (1~5): 감각 표현 구체성
personal_voice (1~5): 예시 말투 반영도
narrative_flow (1~5): 통합 후 흐름 자연스러움
coverage_score (0~1): 두 세션의 핵심 내용 모두 담긴 비율
faithfulness_score: grounded 수 / 전체 atomic facts 수

---

## 출력 형식
반드시 아래 JSON만 출력하라.

{{
  "narrative": "통합된 1~2단락 서술",
  "quote": "가장 인상적인 사용자 발화 한 문장 또는 null",
  "atomic_facts": [
    {{"fact": "남편은 어부였다", "grounded": true}},
    {{"fact": "태풍에도 출어했다", "grounded": true}}
  ],
  "autobiography_hint": "이 에피소드를 자서전에 쓴다면 방향 한 줄",
  "life_value": "희생|성실|가족애|극복|인내 중 가장 적합한 것",
  "emotion_nuance": "그리움,뿌듯함 (최대 2개, 없으면 null)",
  "quality": {{
    "faithfulness_score": 0.95,
    "coverage_score": 0.90,
    "emotional_authenticity": 4.5,
    "sensory_vividness": 4.2,
    "personal_voice": 4.3,
    "narrative_flow": 4.4
  }}
}}
"""

