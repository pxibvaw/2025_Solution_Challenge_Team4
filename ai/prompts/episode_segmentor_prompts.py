# ai/prompts/episode_segmentor_prompts.py

# ──────────────────────────────────────────────────────────────
# Pass 1 — 이벤트 경계 감지
#
# 목적: 전체 대화에서 주제 전환 경계만 빠르게 탐지.
# 근거: Event Segmentation Theory (Zacks & Swallow, 2007)
#       인간은 경험을 연속 스트림이 아닌 의미 단위로 분절해 인식.
#       경계는 과도한 분절(oversegmentation) 없이 주요 전환만 잡아야 함.
# ──────────────────────────────────────────────────────────────

PASS1_BOUNDARY_PROMPT = """
당신은 노인 자서전 인터뷰 전문가입니다.

## 작업
아래 대화 로그에서 주제가 전환되는 경계 턴을 찾아라.
경계란: 이전 턴과 이 턴 사이에서 이야기의 핵심 주제가 바뀌는 시점.

## 대화 로그
{conversation}

## 판단 기준
- 완전히 다른 삶의 영역으로 넘어갈 때만 경계 (가족→직업, 신혼→노년 등)
- 같은 주제를 다른 각도로 이야기하는 건 경계 아님
- 인물이 바뀌어도 같은 시기 연결된 이야기면 경계 아님
  예: 남편→시어머니가 같은 신혼 시절 이야기면 연속
- 노인 대화 특성: 시간대가 섞이거나 회상이 중첩돼도
  핵심 사건이 같으면 경계 아님
- 너무 잘게 자르지 마라. 에피소드는 보통 5~15턴 분량

## 출력 형식
반드시 아래 JSON만 출력하라. 다른 텍스트 없이.
경계가 없으면 empty list.

{{ "boundaries": [3, 8, 15] }}

boundaries는 새 에피소드가 시작되는 턴 인덱스 배열.
(예: [3]이면 0~2턴이 첫 에피소드, 3턴~끝이 두 번째 에피소드)
"""


# ──────────────────────────────────────────────────────────────
# Pass 2 — 경계 병합 + 비선형 노인 대화 처리 + 브릿지 힌트 추출
#
# 목적: 1패스 경계를 재검토하고, 노인 대화 특성에 맞게 구간 확정.
#       브릿지 힌트(narrative_direction, dominant_emotion, life_value_hint)를
#       추출해 episode_writer에게 전달 → 서술 품질 향상.
# 근거: GTLC (Li & Li, ICIC 2025) — 전역 주제 전환 + 로컬 개체 일관성
#       두 레벨을 함께 보는 계층적 접근이 단일 granularity보다 우수.
# ──────────────────────────────────────────────────────────────

PASS2_ENRICH_PROMPT = """
당신은 노인 자서전 인터뷰 전문가입니다.

## 작업
아래 대화 로그와 예비 경계를 보고,
최종 에피소드 구간을 확정하고 각 구간의 방향을 분석하라.

## 대화 로그
{conversation}

## 예비 경계 (1차 감지)
{boundaries}
(위 인덱스에서 새 에피소드가 시작됨)

## 기존 에피소드 목록
{existing_episodes}

## 사용자 프로필
- 호칭: {user_title}
- 기억에 남는 나이대: {memorable_age}
- 출생연도: {birth_year}

## 처리 규칙

### 비선형 노인 대화 처리
1. 한 구간 안에서 시간대가 섞일 수 있음
   → "30대 때 이야기인데 40대에도 그랬어요" → 하나의 구간 유지
   → time_hint에 복수 시기 표기 가능
2. 인물 연쇄 처리
   → 남편→시어머니→아들이 같은 시기 이야기면 하나의 구간
   → 완전히 다른 삶의 영역으로 넘어갈 때만 분리
3. 중첩 회상 처리
   → "그때 생각하니까 더 옛날 기억도 나는데" → 별도 구간으로 분리

### 구간 병합/분리 판단
- 예비 경계 중 의미적으로 연결되면 병합 가능
- 한 구간이 20턴 이상이면 중간 추가 분리 가능
- 최소 2턴, 권장 5~15턴

### 기존 에피소드 보강 판단 (StorySage 방식)
- 같은 시기 + 같은 인물 + 같은 주제면 MERGE
- 새로운 내용이면 NEW

## 출력 형식
반드시 아래 JSON만 출력하라.

{{
  "segments": [
    {{
      "turn_start": 0,
      "turn_end": 7,
      "narrative_direction": "가족을 위해 묵묵히 살아온 헌신의 상징으로 쓸 수 있음",
      "dominant_emotion": "그리움",
      "life_value_hint": "희생",
      "merge_action": "NEW",
      "merge_target_id": null,
      "merge_reason": null
    }}
  ]
}}
"""


# ──────────────────────────────────────────────────────────────
# Pass 3 — 구간별 메타데이터 추출
#
# 목적: 각 구간에서 Conway SMS 4축 + McAdams 분류 + 감각/인물 추출.
#       Pass 2의 브릿지 힌트를 레퍼런스로 활용해 추출 정확도 향상.
# 근거: Conway Self Memory System (2000) — 시간/장소/인물/감각 4축
#       McAdams Life Story Interview (2008) — 에피소드 유형 분류
#       Herz & Cupchik (1992) — 감각 기억의 자서전적 중요성
# ──────────────────────────────────────────────────────────────

METADATA_PROMPT = """
당신은 노인 자서전 인터뷰 전문가입니다.

## 작업
아래 대화 구간을 분석해 에피소드 메타데이터를 추출하라.

## 대화 구간
{segment_conversation}

## 분석 힌트 (1차 분석 결과 — 참고만, 대화 내용이 우선)
- 서술 방향: {narrative_direction}
- 지배 감정: {dominant_emotion}
- 삶의 가치 후보: {life_value_hint}

## 사용자 프로필
- 호칭: {user_title}
- 기억에 남는 나이대: {memorable_age}
- 출생연도: {birth_year}

## 추출 항목

**제목** (20자 이내, 사용자 삶의 언어로)
예: "새벽 바다를 지키던 시절", "어머니의 손맛", "첫 월급날"

**분류 (McAdams 기반)**
- type:
  - LIFETIME_PERIOD: 특정 시기 전체 ("30대 부산 시절")
  - GENERAL_EVENT: 반복/대표 경험 ("남편 배웅하던 새벽들")
  - KEY_SCENE: 특정 하나의 순간 ("태풍 오던 날 새벽")
- key_scene_type: type이 KEY_SCENE일 때만
  - HIGH_POINT | LOW_POINT | TURNING_POINT | null

**주제/감정**
- theme: 가족|직업|고향|사랑|고생|성취|신앙|상실|기타
- emotion_tone: 긍정|부정|복합|중립
- emotion_nuance: 아래 중 대화에 가장 부합하는 것
  그리움|뿌듯함|안타까움|외로움|보람|설렘|슬픔|기쁨
  복합 감정이면 쉼표로 최대 2개: "그리움,뿌듯함"
  해당 없으면 null

**시간 정보 (대화에서만 추론, 추측 금지)**
- time_hint: "30대 초반 추정", "결혼 직후", "6.25 이후" 등
  → 대화에서 명확한 근거 없으면 null
- period_label: "신혼 시절", "부산 시절", "아이들 어릴 때" 등
  → 없으면 null
- estimated_year_range: 출생연도 + time_hint 조합으로 추정
  → 예: "1975~1985년" / 추론 불가면 null

**장소**
- location: 대화에서 언급된 장소만. 없으면 null

**인물 (실명 저장 금지, 관계 호칭만)**
- persons: 배열 (등장인물 없으면 [])
  - name: "남편", "어머니", "큰아들"
  - relation: 배우자|부모|자녀|형제|친구|동료|기타
  - role_in_episode: 이 에피소드에서의 역할 한 줄

**감각 (사용자가 실제 언급한 것만)**
- sensory:
  - smell / sound / visual / texture / weather 각각 또는 null
  → 감각 표현이 전혀 없으면 sensory 자체를 null로

## 주의
- 사용자가 말하지 않은 내용 추론 금지
- 시간/장소는 대화에 명확한 근거 있을 때만 채워라
- 감각 표현은 사용자가 실제로 언급한 것만 추출

## 출력 형식
반드시 아래 JSON만 출력하라.

{{
  "title": "새벽 바다를 지키던 시절",
  "type": "GENERAL_EVENT",
  "key_scene_type": null,
  "theme": "가족",
  "emotion_tone": "복합",
  "emotion_nuance": "그리움,뿌듯함",
  "time_hint": "30대 초반 추정",
  "period_label": "신혼 시절",
  "estimated_year_range": "1975~1985년",
  "location": "부산 영도",
  "persons": [
    {{
      "name": "남편",
      "relation": "배우자",
      "role_in_episode": "매일 새벽 출어하는 어부"
    }}
  ],
  "sensory": {{
    "smell": "짭짤한 바다 냄새",
    "sound": null,
    "visual": "안개 낀 항구",
    "texture": null,
    "weather": null
  }}
}}
"""