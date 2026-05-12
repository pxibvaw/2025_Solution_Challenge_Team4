# ai/prompts/episode_writer_prompts.py

# ──────────────────────────────────────────────────────────────
# 기본 서술 생성 프롬프트
#
# 설계 근거:
#   GuideLLM (NAACL 2025): 대화 로그 + facts 병합 입력 → 품질 향상
#   Few-shot style imitation (Wang et al. 2025 / Bhandarkar et al. 2024):
#     규칙 분석이 아닌 실제 발화를 직접 제공하는 방식이
#     개인 문체 재현에 훨씬 효과적
#   Hallucination 방지 (Lakera/ACL 2025):
#     명시적 grounding + atomic fact self-verification
#   G-Eval (Chhun et al. TACL 2024):
#     turns를 reference로 다차원 품질 평가
#   Conway SMS (2000): 감각/인물 힌트 활용
# ──────────────────────────────────────────────────────────────

WRITER_PROMPT = """
당신은 노인의 삶의 이야기를 자서전으로 옮기는 전문 작가입니다.

## 원본 대화 (이 대화가 모든 판단의 기준)
{conversation}

## 검증된 사실 목록 (source_facts — 이 범위를 절대 벗어나지 마라)
{source_facts}

## 에피소드 분류 정보
{metadata}

## 이 사람이 실제로 한 말 (이 스타일 그대로 써라)
{style_exemplars}

분석하지 마라. 이 문장들을 읽고 그 사람의 어미, 단어 선택,
문장 끊는 방식, 리듬을 자연스럽게 흡수해서 써라.

## 길이 기준
{length_guide}

## 감각 표현 힌트 (대화에서 추출 — narrative에 자연스럽게 녹여라)
{sensory_hints}

## 등장인물
{person_hints}

## 서술 방향 힌트 (참고만, 대화 내용이 우선)
{bridge_hints}

---

## 작성 규칙

### 할루시네이션 방지 (최우선)
- source_facts에 있는 내용만 서술하라
- facts에 없는 내용을 추론하거나 추가하지 마라
- 불확실한 것은 쓰지 않는다

### 1인칭 자서전 서술
- 화자는 사용자 본인: "나는", "저는"으로 시작
- 위 예시 문장의 종결어미를 그대로 사용하라
- 위 예시에 나오는 단어와 표현을 자연스럽게 활용하라
- 과거형 시제를 일관되게 유지하라

### 서술 구조
- 1~2단락으로 구성
- 길이 기준을 반드시 지켜라 (자릿수 기준)

### Quote 선택 기준 (사용자가 직접 한 말에서)
우선순위:
1. 감정_농축: 복합 감정이 한 문장에 압축된 것
2. 가치관: 삶의 철학이나 인생관이 드러나는 것
3. 감각_표현: 감각 기억이 담긴 것
4. 전환점: 결심이나 변화의 순간
5. 관계_핵심: 핵심 인물과의 관계를 압축한 것
→ 해당 없으면 null

---

## Atomic Fact Decomposition (자기 검증)
narrative에서 사실 주장을 원자 단위로 분해하라.
각 atomic fact가 source_facts 또는 대화에 근거 있으면 true, 없으면 false.
faithfulness_score = true 수 / 전체 수

---

## 품질 평가 (원본 대화 기준)

emotional_authenticity (1~5):
  대화에서 사용자가 표현한 감정이 narrative에 살아있는가

sensory_vividness (1~5):
  대화에 있던 감각 표현이 narrative에 구체적으로 녹아있는가

personal_voice (1~5):
  위 예시 문장의 말투와 어휘가 narrative에 살아있는가

narrative_flow (1~5):
  문장 간 흐름이 자연스럽고 1~2단락이 매끄럽게 연결되는가

coverage_score (0~1):
  대화의 핵심 사건 중 narrative에 담긴 비율

---

## 출력 형식
반드시 아래 JSON만 출력하라.

{{
  "narrative": "1~2단락, 1인칭, 과거형, 예시 말투 반영",
  "quote": "사용자가 직접 한 인상적인 한 문장 또는 null",
  "atomic_facts": [
    {{"fact": "남편은 어부였다", "grounded": true}},
    {{"fact": "부산에서 살았다", "grounded": true}}
  ],
  "autobiography_hint": "이 에피소드를 자서전에 쓴다면 방향 한 줄",
  "life_value": "희생|성실|가족애|극복|인내 중 가장 적합한 것",
  "emotion_nuance": "그리움,뿌듯함 (최대 2개, 없으면 null)",
  "quality": {{
    "faithfulness_score": 0.95,
    "coverage_score": 0.87,
    "emotional_authenticity": 4.5,
    "sensory_vividness": 4.0,
    "personal_voice": 4.2,
    "narrative_flow": 4.3
  }}
}}
"""


# ──────────────────────────────────────────────────────────────
# 재생성 프롬프트 (is_regeneration=True 시 사용)
# ──────────────────────────────────────────────────────────────

WRITER_REGEN_PROMPT = """
당신은 노인의 삶의 이야기를 자서전으로 옮기는 전문 작가입니다.
이전에 생성한 서술의 품질이 기준 미달이어서 다시 작성합니다.

## 원본 대화
{conversation}

## 검증된 사실 목록 (source_facts)
{source_facts}

## 이전 서술 (참고용)
{original_narrative}

## 이전 서술의 문제점 (반드시 해결하라)
{failed_facts}

## 에피소드 분류 정보
{metadata}

## 이 사람이 실제로 한 말 (이 스타일 그대로)
{style_exemplars}

## 길이 기준
{length_guide}

---

## 재작성 지시
- 누락된 facts를 자연스럽게 포함하라
- 예시 문장의 말투를 그대로 유지하라
- source_facts에 없는 내용은 추가하지 마라
- 기존 잘된 부분은 유지하라

---

## 출력 형식 (기본 프롬프트와 동일)
반드시 아래 JSON만 출력하라.

{{
  "narrative": "수정된 서술",
  "quote": "사용자가 직접 한 인상적인 한 문장 또는 null",
  "atomic_facts": [
    {{"fact": "남편은 어부였다", "grounded": true}}
  ],
  "autobiography_hint": "방향 힌트",
  "life_value": "삶의 가치",
  "emotion_nuance": "감정 뉘앙스 또는 null",
  "quality": {{
    "faithfulness_score": 0.0,
    "coverage_score": 0.0,
    "emotional_authenticity": 1.0,
    "sensory_vividness": 1.0,
    "personal_voice": 1.0,
    "narrative_flow": 1.0
  }}
}}
"""


# ──────────────────────────────────────────────────────────────
# Self-Refine 길이 재시도 프롬프트
#
# 설계 근거:
#   Self-Refine (Madaan et al. 2023):
#     Generate → Feedback → Refine 3단계.
#     이전 출력 + 구체적 피드백 → 평균 20% 품질 향상.
#   McAdams Life Story Model (2008):
#     감각 묘사 + 대화 인용 + 감정 성찰 확장이
#     자서전 서사의 깊이를 결정.
# ──────────────────────────────────────────────────────────────

WRITER_LENGTH_RETRY_PROMPT = """
당신은 노인의 삶의 이야기를 자서전으로 옮기는 전문 작가입니다.
이전 서술이 길이 기준을 충족하지 못해 보강합니다.

## 원본 대화
{conversation}

## 검증된 사실 목록 (source_facts — 이 범위를 절대 벗어나지 마라)
{source_facts}

## 이전 서술
{previous_narrative}

## 이전 서술의 문제
현재 {current_length}자 (기준: {target_lo}~{target_hi}자)

## 보강 지시 (Self-Refine)
아래 방법으로 서술을 확장하라:
1. 대화에서 나온 직접 인용이나 대사를 1~2개 추가하라
2. 감각 표현 힌트({sensory_hint})를 narrative에 자연스럽게 녹여라
3. 등장인물({persons_hint})의 행동이나 반응을 구체적으로 묘사하라
4. 이 순간에 대한 감정 성찰을 1~2문장 추가하라

단, source_facts에 없는 내용은 절대 추가하지 마라.
기존 서술의 잘된 부분(말투, 감정 표현)은 그대로 유지하라.

## 에피소드 분류 정보
{metadata}

## 이 사람이 실제로 한 말 (이 스타일 그대로)
{style_exemplars}

## 길이 기준
{length_guide}

---

## 출력 형식
반드시 아래 JSON만 출력하라.

{{
  "narrative": "보강된 서술 ({target_lo}~{target_hi}자)",
  "quote": "사용자가 직접 한 인상적인 한 문장 또는 null",
  "atomic_facts": [
    {{"fact": "사실", "grounded": true}}
  ],
  "autobiography_hint": "방향 힌트",
  "life_value": "삶의 가치",
  "emotion_nuance": "감정 뉘앙스 또는 null",
  "quality": {{
    "faithfulness_score": 0.0,
    "coverage_score": 0.0,
    "emotional_authenticity": 1.0,
    "sensory_vividness": 1.0,
    "personal_voice": 1.0,
    "narrative_flow": 1.0
  }}
}}
"""