# Doran  
> Voice-first Autobiography & Memory Recording Service

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

- Speech-to-Text (STT)
- 대화 요약 및 에피소드 분리
- 자서전 생성 (서사 구조화)
- 사용자 맥락 기반 메모리 관리

---

## 🏗️ Repository Structure

```text
root/
├── frontend/      # Client
├── backend/       # Server API
├── ai/            # AI Pipeline
├── README.md
└── .gitignore

---

## 통합 브랜치 로컬 실행 가이드

이 섹션은 `feat/full-integration` 기준입니다. 프론트엔드, 백엔드, AI 코드가 한 레포에 합쳐진 상태에서 로컬로 화면과 API를 확인하는 방법입니다.

### 1. 브랜치 확인

```bash
git switch feat/full-integration
git pull origin feat/full-integration
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

현재 통합 브랜치에서 확인된 상태:

```text
backend ./gradlew test: 성공
frontend npm run build: 성공
```

### 6. 현재 동작 범위

현재 프론트 화면은 열어서 확인할 수 있습니다. 다만 프론트의 일부 화면은 아직 백엔드 API와 완전히 연결되지 않았고, `frontend/src/mock/data.ts`의 mock 데이터를 사용합니다.

예를 들어 에피소드/책 화면에 미리 보이는 데이터는 실제 DB에서 생성된 데이터가 아니라 프론트 화면 확인용 더미 데이터입니다.

백엔드 실제 에피소드 API는 다음 주소로 확인할 수 있습니다.

```text
GET http://localhost:8080/api/episodes?userId=1
```

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

### 8. 주의사항

- 카카오 로그인은 아직 실제 OAuth/JWT 연동 전입니다.
- 프론트의 mock 데이터 제거/디자인 수정은 FE 담당자가 처리합니다.
- 실제 AI 응답, 자서전 생성 품질, 이미지 생성, 음성/STT/TTS는 AI 담당 파트와 추가 연동이 필요합니다.
- `node_modules/`, `dist/`, 백엔드 build 산출물은 커밋하지 않습니다.
