# DORAN AI Service

FastAPI 기반 도란 AI 서비스. Gemini LLM + ChromaDB 메모리 + 에피소드/자서전 파이프라인.

## 요구 사항

- Python 3.13 (다른 버전은 검증되지 않음)
- Gemini API Key (Google AI Studio)
- Google Cloud 프로젝트 (STT/TTS 사용 시)
- Spring Boot 백엔드가 별도로 떠 있어야 콜백/에피소드 조회 동작 (기본 `http://localhost:8080`)

## 빠른 시작

### 1) 가상환경 생성 및 활성화

레포 루트(`2025_-Solution_Challenge_Team4/`)에서:

```bash
python3 -m venv .venv
source .venv/bin/activate          # macOS / Linux
# .venv\Scripts\activate            # Windows PowerShell
```

### 2) 의존성 설치

```bash
pip install -r ai/requirements.txt
```

> `google-auth==2.49.0.dev0`은 pre-release. 설치가 실패하면
> `pip install --pre google-auth==2.49.0.dev0` 또는
> `requirements.txt`에서 `google-auth==2.49.0`(또는 그 이상의 stable)로 교체.

### 3) 환경변수 설정

레포 루트에 `.env` 생성 (또는 `.env.example` 복사):

```bash
cp .env.example .env
```

`.env`에 최소 다음 값들 채우기:

```
GEMINI_API_KEY=your_gemini_api_key
GOOGLE_CLOUD_PROJECT=your_gcp_project_id
GOOGLE_CLOUD_LOCATION=asia-northeast3
ENV=development
SPRING_BOOT_BASE_URL=http://localhost:8080
CHROMA_PERSIST_PATH=./data/chroma
```

전체 변수 목록은 `.env.example` 참고 (콜백 재시도, Circuit Breaker, 품질 가중치 등 튜닝용).

### 4) 서버 실행

레포 루트에서:

```bash
uvicorn ai.app.api:app --reload --port 8000
```

- 개발 모드: `http://localhost:8000/docs` → Swagger UI
- `http://localhost:8000/redoc` → ReDoc
- `http://localhost:8000/health` → liveness 체크

> 프로덕션(`ENV=production`)이면 `/docs`, `/redoc`, `/test/*` 모두 자동 비활성화.

## 디렉토리 구조

```
ai/
├── app/
│   ├── api.py             # FastAPI 라우터 (turn / end-session / autobiography)
│   ├── schemas.py         # 요청/응답 Pydantic 모델
│   ├── settings.py        # 환경 설정
│   └── orchestrator.py    # 인터뷰 턴 / 세션 종료 메모리 파이프라인
├── services/
│   ├── interview_service.py        # turn 단위 LLM 호출
│   ├── episode_service.py          # 세션 종료 후 에피소드 생성 + Spring Boot 콜백
│   ├── autobiography_service.py    # 챕터 기반 자서전 생성
│   ├── memory_service.py           # ChromaDB 메모리 저장/조회/삭제
│   └── ...
├── clients/
│   ├── llm_gemini.py     # Gemini 클라이언트 (Bulkhead, 응답 가드)
│   ├── stt_google.py
│   ├── tts_google.py
│   └── vectordb_chroma.py
├── prompts/               # 프롬프트 템플릿
├── memory/
│   └── chroma_store.py    # ChromaDB persistent client
├── utils/
│   ├── cache.py           # InMemoryCacheBackend (cachetools 래핑)
│   ├── callback_retry.py  # CircuitBreaker + CallbackOutbox
│   └── episode_formatters.py
└── tests/                 # pytest 테스트 (test_*.py)
```

## Spring Boot 연동

AI 서비스는 두 가지 방향으로 Spring Boot와 통신:

| 방향 | 엔드포인트 | 용도 |
|------|-----------|------|
| BE → AI | `POST /turn` | 인터뷰 턴 처리 (실시간) |
| BE → AI | `POST /end-session` | 세션 종료 (백그라운드 파이프라인 트리거) |
| BE → AI | `POST /autobiography` | 자서전 생성 |
| AI → BE | `GET /api/episodes?userId=` | 중복 회피용 기존 에피소드 조회 |
| AI → BE | `POST /api/ai/episodes` | 신규/병합 에피소드 콜백 |

- 콜백 실패 시 자동 재시도(지수 백오프 + 지터) + Outbox 파일 영속화
- 서버 startup 시 `lifespan` 훅이 Outbox의 미전송 파일을 자동 재전송

## 콜백 회복력

| 컴포넌트 | 동작 |
|---------|------|
| CircuitBreaker | 3회 연속 실패 → OPEN (30초 대기 후 HALF_OPEN) |
| CallbackOutbox | 실패 payload를 `data/chroma/../failed_callbacks/`에 JSON 영속화 |
| Startup Recovery | 서버 시작 시 PENDING/FAILED 파일을 자동 재전송 |

`GET /health`로 상태 확인 가능 (※ `episode_service.get_callback_health()` 활용 시).

## 테스트

```bash
pytest ai/tests/
```

특정 테스트만:

```bash
pytest ai/tests/test_interview.py -v
pytest ai/tests/test_pipeline.py -v
```

`/test/cleanup` 엔드포인트로 ChromaDB + 인메모리 캐시 정리 가능 (개발 모드에서만).

## 트러블슈팅

- **`/docs` 404**: `ENV=production` 인지 확인. 개발 시 `ENV=development`.
- **Gemini 응답이 비어있다는 안내문구가 자주 뜸**: safety filter 또는 할당량 의심. `ai/clients/llm_gemini.py`의 warning 로그 확인.
- **콜백이 BE에 안 들어옴**: Spring Boot가 `SPRING_BOOT_BASE_URL`로 띄워져 있는지 확인. `data/chroma/../failed_callbacks/` 디렉토리에 .json 파일 쌓이고 있으면 BE 다운 상태.
- **ChromaDB 권한 에러**: `CHROMA_PERSIST_PATH` 디렉토리 쓰기 권한 확인.
