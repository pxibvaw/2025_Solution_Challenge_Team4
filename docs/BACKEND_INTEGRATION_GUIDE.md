# Doran AI ↔ Spring Boot 백엔드 연동 가이드

> **작성일**: 2025-05-05  
> **대상**: 백엔드 개발자 (Spring Boot)  
> **AI 서비스 주소**: `http://localhost:8000` (FastAPI + Uvicorn)

---

## 1. 아키텍처 개요

```
┌──────────┐     ┌───────────────────┐     ┌──────────────────┐
│ Frontend │────▶│  Spring Boot BE   │────▶│  AI Service      │
│ (React)  │◀────│  :8080            │◀────│  (FastAPI) :8000 │
└──────────┘     └───────────────────┘     └──────────────────┘
                         ▲                          │
                         │    POST /api/ai/episodes │
                         └──────────────────────────┘
                              (Callback: AI → BE)
```

**핵심 흐름:**
1. FE → BE → AI: 인터뷰 턴 요청 (`POST /turn`)
2. FE → BE → AI: 세션 종료 (`POST /end-session`)
3. AI → BE: 에피소드 생성 완료 후 콜백 (`POST /api/ai/episodes`)
4. FE → BE → AI: 자서전 생성 (`POST /autobiography`)

---

## 2. 백엔드가 구현해야 할 엔드포인트 (2개)

### 2.1 `GET /api/episodes`

AI가 에피소드 중복 방지를 위해 기존 에피소드를 조회할 때 호출합니다.

| 항목 | 값 |
|------|-----|
| Method | GET |
| Query Param | `userId` (String, 필수) |
| Response | `200 OK` + JSON Array of Episode objects |
| 실패 시 | AI는 빈 배열로 처리 (중복 발생 가능 → warning 포함) |

**Response 예시:**
```json
[
  {
    "id": "ep_001",
    "user_id": "user_123",
    "session_id": "sess_abc",
    "title": "첫 출근날의 설렘",
    "narrative": "1985년 봄, 나는 처음으로...",
    "type": "KEY_SCENE",
    "theme": "직장",
    "emotion_tone": "설렘",
    "time_hint": "1985년 봄",
    "turn_start": 3,
    "turn_end": 8
  }
]
```

> AI는 이 데이터에서 `title`, `turn_start`, `turn_end`, `type`을 기반으로 MERGE 여부를 판단합니다. 최소한 이 필드들은 반환해주세요.

---

### 2.2 `POST /api/ai/episodes`

AI가 에피소드 생성 완료 후 결과를 전송하는 콜백 엔드포인트입니다.

| 항목 | 값 |
|------|-----|
| Method | POST |
| Content-Type | application/json |
| Response | `200 OK` (body 무관, status code만 확인) |

**Request Body:**
```json
{
  "sessionId": "sess_abc123",
  "userId": "user_123",
  "newEpisodes": [ /* 신규 생성된 에피소드 배열 */ ],
  "mergedEpisodes": [ /* 기존 에피소드와 병합된 에피소드 배열 */ ],
  "episodesCreated": 3,
  "episodesMerged": 1,
  "weakEpisodes": 0,
  "warnings": ["existing_episodes_fetch_failed: ..."]
}
```

---

## 3. Episode 스키마 (상세)

`newEpisodes`, `mergedEpisodes` 배열의 각 항목:

```json
{
  "turn_start": 3,
  "turn_end": 8,
  "title": "첫 출근날의 설렘",
  "type": "KEY_SCENE",
  "key_scene_type": "achievement",
  "theme": "직장",
  "emotion_tone": "설렘",
  "time_hint": "1985년 봄",
  "period_label": "청년기",
  "estimated_year_range": "1985-1986",
  "location": "서울 종로구",
  "persons": [
    {
      "name": "김부장",
      "relation": "직장 상사",
      "role_in_episode": "첫 업무를 배정해준 사람"
    }
  ],
  "sensory": {
    "smell": "새 건물 페인트 냄새",
    "sound": "타자기 소리",
    "visual": "형광등 아래 빽빽한 책상들",
    "texture": null,
    "weather": "맑은 봄날"
  },
  "narrative": "1985년 봄, 처음으로 출근한 날...(500~1500자 서술)",
  "quote": "그때 부장님이 '걱정 마, 다 처음이야'라고 하셨어요",
  "autobiography_hint": "직장생활의 시작과 사회인으로의 첫 발걸음",
  "life_value": "성실함",
  "emotion_nuance": "설렘 속에 긴장감이 섞인",
  "quality": {
    "faithfulness_score": 0.92,
    "coverage_score": 0.85,
    "emotional_authenticity": 4.2,
    "sensory_vividness": 3.8,
    "personal_voice": 4.0,
    "narrative_flow": 4.5,
    "narrative_richness": 0.82,
    "quality_grade": "GOOD",
    "needs_regeneration": false
  },
  "source_session_id": "sess_abc123",
  "source_turn_range": [3, 8],
  "source_facts": ["1985년에 첫 직장에 입사했다", "종로구 빌딩에서 근무했다"],
  "importance_score": 5.0
}
```

### 필드 타입 정리

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| turn_start | int | O | 대화 시작 턴 인덱스 |
| turn_end | int | O | 대화 끝 턴 인덱스 |
| title | String | O | 에피소드 제목 |
| type | String | O | `GENERAL_EVENT` \| `KEY_SCENE` \| `TURNING_POINT` \| `LIFETIME_PERIOD` |
| key_scene_type | String | X | type이 KEY_SCENE일 때만 |
| theme | String | O | 주제 분류 |
| emotion_tone | String | O | 감정 톤 |
| time_hint | String | X | 시간 힌트 ("1985년 봄", "30대 초반" 등) |
| period_label | String | X | 생애주기 ("유년기", "청년기" 등) |
| estimated_year_range | String | X | "1985-1986" 형태 |
| location | String | X | 장소 |
| persons | Array | O (빈배열 가능) | 등장인물 |
| sensory | Object | X | 감각 묘사 (5가지) |
| narrative | String | O | 서술 본문 (500~1500자) |
| quote | String | X | 사용자 직접 인용 |
| autobiography_hint | String | X | 자서전 작성 시 힌트 |
| life_value | String | X | 삶의 가치 |
| emotion_nuance | String | X | 감정 뉘앙스 상세 |
| quality | Object | O | 품질 점수 (아래 참조) |
| source_session_id | String | O | 원본 세션 ID |
| source_turn_range | [int, int] | X | 원본 턴 범위 |
| source_facts | Array[String] | O (빈배열 가능) | 근거 메모리 |
| importance_score | float | O | 중요도 (기본 5.0) |

### Quality 필드

| 필드 | 타입 | 범위 | 설명 |
|------|------|------|------|
| faithfulness_score | float | 0.0~1.0 | 사실 충실도 |
| coverage_score | float | 0.0~1.0 | 대화 내용 커버리지 |
| emotional_authenticity | float | 1.0~5.0 | 감정 진정성 |
| sensory_vividness | float | 1.0~5.0 | 감각 묘사 생생함 |
| personal_voice | float | 1.0~5.0 | 개인적 어조 |
| narrative_flow | float | 1.0~5.0 | 서술 흐름 |
| narrative_richness | float | 0.0~1.0 | **종합 점수** (가중 합산, computed) |
| quality_grade | String | RICH/GOOD/NORMAL/WEAK | **등급** (computed) |
| needs_regeneration | bool | - | 재생성 필요 여부 (computed) |

---

## 4. 백엔드가 AI에 요청하는 엔드포인트 (3개)

### 4.1 `POST /turn` — 인터뷰 대화 턴

```json
// Request
{
  "sessionId": "sess_abc123",
  "requestId": "req_uuid_001",
  "userText": "저는 1985년에 첫 직장에 다녔어요",
  "profile": {
    "userTitle": "할머니",
    "speechLevel": "HONORIFIC",
    "memorableAge": "20대",
    "coreValue": "가족",
    "birthYear": 1963
  }
}

// Response
{
  "requestId": "req_uuid_001",
  "reply": "1985년이면 22살 때시네요! 정말 설레셨겠어요.",
  "question": "첫 출근하셨을 때 기분이 어떠셨어요?",
  "turnIndex": 5,
  "audioContent": "base64_encoded_mp3..."
}
```

| 필드 | 설명 |
|------|------|
| sessionId | 세션 식별자 (BE에서 생성, UUID 권장) |
| requestId | 요청 식별자 (멱등성 보장용, 60초 TTL 캐시) |
| userText | 사용자 발화 텍스트 (STT 결과 또는 직접 입력) |
| profile | 사용자 프로필 (온보딩에서 수집) |
| audioContent | AI 응답 TTS 음성 (base64 인코딩 MP3) |

> **멱등성**: 같은 `requestId`로 60초 내 재요청 시 캐시된 응답 반환. 네트워크 재시도 안전.

---

### 4.2 `POST /end-session` — 세션 종료

```json
// Request
{
  "sessionId": "sess_abc123",
  "userId": "user_123"
}

// Response (즉시 반환 — 에피소드 생성은 백그라운드)
{
  "sessionId": "sess_abc123",
  "saved": 0,
  "skipped": 0
}
```

> **중요**: 이 응답은 즉시 반환됩니다. 에피소드 생성은 백그라운드에서 처리되며, 완료 시 `POST /api/ai/episodes`로 콜백합니다.

---

### 4.3 `POST /autobiography` — 자서전 생성

```json
// Request
{
  "userId": "user_123",
  "selectedEpisodeIds": ["ep_001", "ep_003", "ep_005"],
  "episodes": [ /* Episode 객체 배열 (위 스키마 참조) */ ]
}

// Response
{
  "prologue": "나는 1963년 부산에서 태어났다...",
  "chapters": [
    {
      "title": "봄날의 시작",
      "period_label": "유년기",
      "narrative": "어린 시절, 우리 집 앞 골목길은...",
      "episode_ids": ["ep_001", "ep_003"]
    }
  ],
  "epilogue": "돌아보면 내 삶은...",
  "life_theme": "사랑과 성실함으로 일군 평범한 행복"
}
```

> **주의**: 동기 처리. 챕터 수에 따라 20~60초 소요. BE에서 적절한 timeout 설정 필요 (최소 120초 권장).

---

## 5. 백엔드 구현 시 주의사항

### 5.1 멱등성 (Idempotency)

AI의 콜백(`POST /api/ai/episodes`)은 재시도될 수 있습니다.

- Circuit Breaker 복구 후 재전송
- Outbox에서 재전송
- 서버 재시작 시 Startup Recovery

**권장**: `sessionId` + `episodesCreated` + `episodesMerged` 조합으로 중복 감지하거나, 첫 번째 성공 콜백만 처리.

### 5.2 Partial Success

`warnings` 배열이 비어있지 않을 수 있습니다:
- `existing_episodes_fetch_failed`: 기존 에피소드 조회 실패 → 중복 가능
- `segmentor_failed`: 세분화 실패 → episodes 비어있을 수 있음
- `regen_failed`: 재생성 실패 → 원본(약한 품질) 그대로 전달

**에피소드가 0개여도 200 반환해주세요.** AI 쪽에서 정상 처리로 인식합니다.

### 5.3 응답 코드

| AI가 기대하는 응답 | 의미 |
|-------------------|------|
| `2xx` | 성공 (Circuit Breaker에 success 기록) |
| `4xx` / `5xx` | 실패 (재시도 대상, Circuit Breaker에 failure 기록) |
| 타임아웃 (10초) | 실패 처리 |

### 5.4 AI 서비스 Health Check

```
GET http://localhost:8000/health
→ {"status": "ok"}
```

---

## 6. 환경 변수 (AI 서비스)

백엔드 개발자가 알아야 할 AI 서비스 설정값:

```bash
# AI가 백엔드에 연결할 주소 (기본값)
SPRING_BOOT_BASE_URL=http://localhost:8080

# 기존 에피소드 조회 설정
FETCH_EPISODES_RETRIES=2          # GET 재시도 횟수
FETCH_EPISODES_TIMEOUT=5          # GET 타임아웃 (초)

# 에피소드 콜백 설정
CALLBACK_MAX_RETRIES=3            # POST 초기 재시도
CALLBACK_BASE_DELAY=1.0           # 백오프 기본 대기 (초)
CALLBACK_MAX_DELAY=10.0           # 백오프 최대 대기 (초)
CALLBACK_TIMEOUT=10               # POST 타임아웃 (초)

# Circuit Breaker
CB_FAIL_MAX=3                     # 연속 실패 N회 → 회로 열림
CB_RESET_TIMEOUT=30.0             # 회로 열림 → 반열림 대기 (초)

# Outbox (파일 기반 Fallback)
OUTBOX_MAX_RETRIES=5              # 파일 재전송 최대 횟수
OUTBOX_BASE_DELAY=2.0             # 파일 재전송 기본 대기 (초)
OUTBOX_MAX_DELAY=300.0            # 파일 재전송 최대 대기 (초)
```

---

## 7. 시퀀스 다이어그램

### 인터뷰 세션 흐름

```
FE          BE(:8080)       AI(:8000)        ChromaDB
│            │                │                 │
│──turn───▶│──POST /turn──▶│                 │
│            │                │──memory check─▶│
│            │                │◀─facts─────────│
│            │                │──Gemini LLM───▶│
│            │◀──response────│                 │
│◀──reply───│                │                 │
│            │                │                 │
│  (10턴마다 백그라운드 메모리 추출)             │
│            │                │──extract─────▶│
│            │                │                 │
│──종료───▶│──POST /end────▶│                 │
│            │◀──202 즉시────│                 │
│◀──완료───│                │                 │
│            │                │  [백그라운드]    │
│            │                │──segment───────│
│            │                │──write episodes─│
│            │  ◀─────────────│                 │
│            │  POST /api/ai/episodes (콜백)    │
│            │──200 OK──────▶│                 │
```

### 에피소드 콜백 재시도 흐름

```
AI Service                    BE(:8080)
│                               │
│──POST /api/ai/episodes──────▶│
│  (실패: timeout/5xx)          │
│                               │
│──[1초 대기]───────────────────│
│──POST (retry 2/3)───────────▶│
│  (실패)                       │
│                               │
│──[3초 대기]───────────────────│
│──POST (retry 3/3)───────────▶│
│  (실패)                       │
│                               │
│──[Circuit Breaker failure]────│
│──[Outbox 파일 저장]───────────│
│                               │
│  ... 30초 후 (HALF_OPEN) ...  │
│                               │
│──[Outbox retry]─────────────▶│
│◀──200 OK────────────────────│
│──[Circuit Breaker success]────│
```

---

## 8. 데이터베이스 설계 권장사항

### episodes 테이블

```sql
CREATE TABLE episodes (
    id              VARCHAR(50) PRIMARY KEY,  -- UUID 생성 (BE에서)
    user_id         VARCHAR(50) NOT NULL,
    session_id      VARCHAR(50) NOT NULL,
    
    -- 기본 정보
    title           VARCHAR(200) NOT NULL,
    narrative       TEXT NOT NULL,
    quote           TEXT,
    
    -- 시간/장소
    time_hint       VARCHAR(100),
    period_label    VARCHAR(50),
    estimated_year_range VARCHAR(20),
    location        VARCHAR(200),
    
    -- 분류
    type            VARCHAR(30) NOT NULL,     -- GENERAL_EVENT|KEY_SCENE|TURNING_POINT|LIFETIME_PERIOD
    key_scene_type  VARCHAR(50),
    theme           VARCHAR(100) NOT NULL,
    emotion_tone    VARCHAR(100) NOT NULL,
    emotion_nuance  VARCHAR(200),
    
    -- 자서전 관련
    autobiography_hint TEXT,
    life_value      VARCHAR(100),
    importance_score FLOAT DEFAULT 5.0,
    
    -- 품질
    faithfulness_score      FLOAT,
    coverage_score          FLOAT,
    emotional_authenticity  FLOAT,
    sensory_vividness       FLOAT,
    personal_voice          FLOAT,
    narrative_flow          FLOAT,
    narrative_richness      FLOAT,    -- computed
    quality_grade           VARCHAR(10), -- RICH|GOOD|NORMAL|WEAK
    
    -- 출처
    source_session_id VARCHAR(50),
    source_turn_start INT,
    source_turn_end   INT,
    
    -- 병합
    is_merged       BOOLEAN DEFAULT FALSE,
    merged_from     VARCHAR(50),
    version         INT DEFAULT 1,
    
    -- 사용자 편집
    is_selected_for_autobiography BOOLEAN DEFAULT FALSE,
    user_edited_title VARCHAR(200),
    user_memo       TEXT,
    
    -- 타임스탬프
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_episodes_user_id ON episodes(user_id);
CREATE INDEX idx_episodes_session_id ON episodes(session_id);
```

### episode_persons 테이블

```sql
CREATE TABLE episode_persons (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    episode_id      VARCHAR(50) NOT NULL,
    name            VARCHAR(100),
    relation        VARCHAR(100),
    role_in_episode VARCHAR(200),
    FOREIGN KEY (episode_id) REFERENCES episodes(id)
);
```

### episode_sensory 테이블

```sql
CREATE TABLE episode_sensory (
    episode_id  VARCHAR(50) PRIMARY KEY,
    smell       VARCHAR(200),
    sound       VARCHAR(200),
    visual      VARCHAR(200),
    texture     VARCHAR(200),
    weather     VARCHAR(200),
    FOREIGN KEY (episode_id) REFERENCES episodes(id)
);
```

### source_facts 테이블

```sql
CREATE TABLE episode_source_facts (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    episode_id  VARCHAR(50) NOT NULL,
    fact_text   TEXT NOT NULL,
    FOREIGN KEY (episode_id) REFERENCES episodes(id)
);
```

---

## 9. 백엔드 → AI 연결 설정

### application.yml (Spring Boot)

```yaml
ai:
  service:
    base-url: http://localhost:8000
    timeout:
      turn: 30s           # /turn (TTS 포함)
      end-session: 5s     # /end-session (즉시 반환)
      autobiography: 120s # /autobiography (LLM 다회 호출)
```

### CORS 설정

AI 서비스에서 CORS는 설정하지 않았습니다. BE → AI 호출은 서버 간 통신이므로 CORS 불필요.

---

## 10. 체크리스트

백엔드 개발자가 완료해야 할 항목:

- [ ] `GET /api/episodes?userId={userId}` 구현
- [ ] `POST /api/ai/episodes` 구현 (콜백 수신)
- [ ] 콜백 멱등성 처리 (중복 방지)
- [ ] episodes DB 테이블 생성
- [ ] AI `/turn` 프록시 (FE → BE → AI)
- [ ] AI `/end-session` 프록시
- [ ] AI `/autobiography` 프록시 (timeout 120초 설정)
- [ ] 사용자 인증/인가 레이어
- [ ] `SPRING_BOOT_BASE_URL` 환경변수로 AI 서비스 주소 설정 확인
- [ ] Health check 연동 (`GET /health`)

---

## 11. FAQ

**Q: AI 서비스를 먼저 띄워야 하나요?**  
A: 아니요. BE를 먼저 띄워도 됩니다. AI 서비스의 Circuit Breaker가 BE 불가 시 자동으로 Outbox에 저장하고, BE 복구 후 재전송합니다.

**Q: 에피소드 ID는 누가 생성하나요?**  
A: AI는 ID를 생성하지 않습니다. BE에서 콜백 수신 시 UUID를 생성해서 저장하세요.

**Q: `warnings` 배열에 값이 있으면 에피소드를 저장하면 안 되나요?**  
A: 저장하셔도 됩니다. warnings는 "참고 사항"이지 에피소드 무효화 사유가 아닙니다.

**Q: audioContent는 어떤 포맷인가요?**  
A: Google Cloud TTS MP3를 base64로 인코딩한 문자열입니다. FE에서 `atob()` → `Blob` → `URL.createObjectURL()`로 재생.

**Q: 자서전 생성이 너무 오래 걸리면?**  
A: 챕터 수에 비례합니다 (챕터당 약 5~10초). 6챕터 기준 최대 60초. BE에서 비동기 처리 후 FE에 폴링/웹소켓으로 알리는 것도 방법입니다.

**Q: AI 서비스 .env에 뭘 넣어야 하나요?**  
A: 최소 3개: `GEMINI_API_KEY`, `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`. 나머지는 기본값으로 동작합니다.
