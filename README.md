# Doran  
> Voice-first Autobiography & Memory Recording Service  
> 2026 Google Solution Challenge · GDG on Campus Sookmyung

---

## 📌 Project Overview

**Doran**은 음성 기반 대화를 통해 사용자의 기억을 기록하고,  
이를 에피소드 단위로 정리하여 **하나의 자서전으로 완성하는 AI 서비스**입니다.

텍스트 중심 디지털 환경에 익숙하지 않은 사용자도  
자연스러운 대화를 통해 자신의 삶을 남길 수 있도록 설계되었습니다.

---

## 🎯 Problem Statement

- 많은 사람들이 하루를 대화 없이 보내며 정서적 고립을 경험함
- 기존 AI는 대화를 기억하지 못해 관계 형성이 어려움
- 텍스트 중심 UI는 고령층 및 비숙련 사용자에게 높은 진입장벽이 됨

---

## 💡 Solution

Doran은 단순한 Q&A AI가 아닌, **말벗이자 기록 파트너**를 지향합니다.

- **Long-term Memory**  
  이전 대화를 기억하여 오늘의 대화가 내일로 이어지는 경험 제공

- **Proactive Interviewer**  
  사용자가 먼저 묻지 않아도 AI가 회상 기반 질문을 제시

- **Voice-first UX**  
  버튼 한 번으로 시작하는 100% 음성 중심 인터랙션

---

## 🔁 User Flow

1. 온보딩 (호칭, 말투, 기본 정보 설정)
2. 인터뷰룸에서 음성 대화 진행
3. 대화 로그 기반 에피소드 생성
4. 에피소드 선택
5. 자서전 생성
6. 서재에서 자서전 열람 및 관리

---

## 🖥️ Screen Walkthrough

<p align="center">
  <img src="docs/images/doran_screens.png" alt="Doran 주요 화면: 메인 홈, 인터뷰룸, 에피소드 선택, 자서전 리더" width="100%" />
</p>
<p align="center"><sub>메인 홈 · 인터뷰룸(이야기 듣는 중) · 에피소드 선택 · 자서전 리더 — 디자인 시안(Figma)</sub></p>

### 1. Onboarding
- 최초 1회 진행
- 사용자 맞춤 대화를 위한 기본 정보 설정

### 2. Main Page
- 오늘의 질문 제시
- 인터뷰룸 바로 진입
- 최근 에피소드 및 자서전 요약 확인

### 3. Interview Room
- AI 주도 질문 + 음성 응답
- 대화 상태 시각적 피드백 제공
- 대화 종료 시 자동 기록

### 4. Make Episodes
- 대화 로그를 에피소드 단위로 정리
- 자서전에 포함할 에피소드 선택

### 5. Library & Autobiography
- 자서전 형태로 기록 축적
- 열람 / 수정 / 공유 가능

---

## 🧠 Tech Highlights

- **음성 대화 파이프라인**: 브라우저 녹음(MediaRecorder) → ffmpeg 16kHz mono 변환 → Google Speech-to-Text → 대화 응답 생성 → Google Text-to-Speech 음성 재생
- **대화 오케스트레이션**: 공감 → 회상 유도 → 확장 질문 흐름과 상황별 지침(질문만 반복하지 않기, 감정 발화에는 공감)을 시스템 프롬프트로 설계
- **장기 기억**: ChromaDB 기반 조건부 기억 조회로 이전 대화 맥락을 반영한 질문 생성
- **에피소드 → 자서전**: 대화 로그에서 에피소드를 추출·병합하고, 선택한 에피소드로 자서전(chapters/pages) 생성. 10턴마다 백그라운드 중간 추출
- **장애 복원력**: AI → BE 콜백에 Circuit Breaker + Outbox 재시도 패턴 적용, 요청 ID 기반 중복 응답 캐시

---

## 🛠️ Tech Stack

| 구분 | 기술 |
|---|---|
| AI | Python, FastAPI, Gemini API, ChromaDB, Google STT / TTS, ffmpeg |
| Backend | Spring Boot (Gradle), PostgreSQL (Docker) |
| Frontend | React, Vite, TypeScript |

---

## 👥 Team

| 파트 | 담당 |
|---|---|
| AI · 최종 통합 | pxibvaw 대화 엔진·에피소드/자서전 파이프라인, STT/TTS·ChromaDB 연동, FE–BE-AI 연동 |
| Backend | gunu |
| Frontend | dy0401kwon |
| Design | UI/UX 디자인 |

---

## 🏗️ Repository Structure

```text
root/
├── frontend/          # Client (React + Vite)
├── backend/           # Server API (Spring Boot)
├── ai/                # AI Pipeline (FastAPI)
├── data/              # 로컬 데이터 (ChromaDB 등, git 제외)
├── docs/              # FE·BE·AI 연동 가이드
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 로컬 실행 가이드

프론트엔드, 백엔드, AI 코드가 한 레포에 합쳐진 `main` 기준입니다.

### 1. 브랜치 확인

```bash
git switch main
git pull origin main
```

### 2. PostgreSQL 실행

백엔드는 PostgreSQL을 사용합니다. Docker가 켜져 있어야 합니다.

```bash
cd backend/doran_backend
docker compose up -d postgres
```

기본 DB 설정은 다음과 같습니다.

```text
host: 127.0.0.1
port: 15432
database: doran
username: doran
password: doran
```

### 3. 백엔드 실행

```bash
cd backend/doran_backend
./gradlew bootRun
```

백엔드 실행 확인 URL:

```text
API Server: http://localhost:8080
Swagger UI: http://localhost:8080/swagger-ui.html
OpenAPI JSON: http://localhost:8080/v3/api-docs
```

### 4. 프론트엔드 실행

처음 한 번만 의존성을 설치합니다.

```bash
cd frontend
npm ci
```

개발 서버 실행:

```bash
npm run dev
```

프론트 실행 확인 URL:

```text
http://localhost:5173
```

환경에 따라 Vite가 아래 주소로 열릴 수도 있습니다.

```text
http://127.0.0.1:5173
```

### 5. 빌드/테스트 확인

백엔드 테스트:

```bash
cd backend/doran_backend
./gradlew test
```

프론트 빌드:

```bash
cd frontend
npm run build
```

통합 후 확인된 상태:

```text
backend ./gradlew test: 성공
frontend npm run build: 성공
```

### 6. 현재 동작 범위

로그인을 제외한 주요 사용자 흐름은 백엔드 API 기준으로 연결되어 있습니다. `frontend/src/mock/data.ts`는 FE 참고용 파일로 남아 있지만, 현재 앱 실행 흐름에서는 에피소드/책/서재 화면이 실제 API를 조회합니다.

주요 확인 API:

```text
GET    http://localhost:8080/api/episodes?userId=1
POST   http://localhost:8080/api/books
GET    http://localhost:8080/api/books?userId=1
GET    http://localhost:8080/api/books/{bookId}?userId=1
GET    http://localhost:8080/api/books/{bookId}/pages?userId=1
DELETE http://localhost:8080/api/books/{bookId}?userId=1
```

`/api/books`는 AI 자서전 생성 결과를 프론트가 저장한 뒤, 서재/책 상세/리더에서 다시 조회하는 용도입니다.

### 7. AI 서버 연동

기본 설정에서는 백엔드가 dummy AI client를 사용합니다.

실제 AI FastAPI 서버와 붙여서 확인하려면 AI 서버를 `http://localhost:8000`에 띄운 뒤 백엔드를 아래 환경변수와 함께 실행합니다.

```bash
AI_SERVICE_ENABLED=true AI_SERVICE_BASE_URL=http://localhost:8000 ./gradlew bootRun
```

AI 서버 실행 방법과 상세 계약은 아래 문서를 참고합니다.

```text
docs/BACKEND_INTEGRATION_GUIDE.md
docs/DORAN_INTEGRATION_GUIDE.md
```

### 8. 현재 상태

- 음성 대화(STT → 대화 → TTS), 에피소드 생성, 자서전 생성·조회 흐름이 FE–BE–AI 코드로 연결되어 있습니다.
- 실제 AI·음성 기능을 쓰려면 백엔드를 `AI_SERVICE_ENABLED=true`로 실행하고, AI 서버에 Google Cloud 서비스 계정 키와 ffmpeg가 필요합니다. 키 파일은 저장소에 포함하지 않습니다.
- 카카오 로그인은 아직 실제 OAuth/JWT 연동 전입니다.
- `node_modules/`, `dist/`, 백엔드 build 산출물은 커밋하지 않습니다.
