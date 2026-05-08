DORAN 프론트엔드 ↔ 백엔드 ↔ AI 연동 가이드
AI 인터뷰 기반 라이프로그 서비스 DORAN의 프론트(React + Vite + TS) / 백엔드(Spring Boot) / AI 서버 간 협업용 통합 README입니다. 백엔드/AI 팀은 본 문서의 API 스펙과 DTO 예시를 기준으로 구현해 주세요.
1. 프로젝트 개요
항목	내용
서비스명	DORAN (도란)
한 줄 소개	AI가 사용자에게 질문하고 답변을 모아 자서전(책)을 만들어주는 라이프로그 서비스
프론트엔드	React 18 + Vite + TypeScript + React Router
백엔드	Spring Boot (REST API, JWT 인증)
AI 서버	LLM 기반 — 인터뷰 다음 질문 생성 / 에피소드 요약 / 자서전(책) 생성
인증	카카오 OAuth 2.0 (소셜 로그인)
핵심 도메인	User / Profile / InterviewSession / Message / Episode / Book / Page
전체 플로우
[Login] → [Onboarding(최초 1회)] → [Main] → [Interview] (AI 질문 ↔ 사용자 답변 반복) → [Episode 저장] → [Episode 선택 → Generate Loading → Generate Complete] → [Library / BookDetail / PageViewer]
2. 프론트엔드 라우팅 구조
Path	컴포넌트	역할	인증 필요
/	EntryRouter	온보딩 여부 / 로그인 여부에 따라 라우팅 분기	-
/login	Login	카카오 로그인 진입	❌
/onboarding	Onboarding	최초 사용자 프로필 설정 (호칭, 말투, 연령대, 주제)	✅
/main	Main	홈, 인터뷰 시작 / 서재 / 에피소드 진입	✅
/interview	Interview	AI 인터뷰 진행 (마이크/일시정지/종료)	✅
/episodes	EpisodeList	저장된 에피소드 목록	✅
/episode/:id	EpisodeDetail	에피소드 상세 본문 보기	✅
/library	Library	자서전(책) 서재	✅
/library/month	LibraryMonth	월별 보기	✅
/book/:id	BookDetail	책 상세 + 댓글	✅
/reader/:id	PageViewer	책 페이지 뷰어	✅
/generate/loading	GenerateLoading	자서전 생성 중 로딩	✅
/generate/complete	GenerateComplete	생성 완료 화면	✅
*	Navigate /	fallback	-
3. 페이지별 역할 & 필요 데이터
페이지	주요 기능	필요한 데이터 (← 어디서?)
Login	카카오 OAuth 로그인 트리거	카카오 인가 코드 → 백엔드
Onboarding	호칭/말투/연령대/관심주제 입력 후 저장	UserProfileContext (현재 localStorage, 추후 PATCH /users/me/profile)
Main	인터뷰 시작 버튼, 최근 에피소드/책 미리보기	GET /users/me, GET /episodes?limit=3, GET /books?limit=3
Interview	AI 질문 표시, STT 답변, 다음 질문 요청, 종료	POST /interviews/start, POST /interviews/{id}/messages, POST /interviews/{id}/next-question, POST /interviews/{id}/end
InterviewLogPanel	종료 후 대화 로그 표시 → 닫기 시 에피소드 저장	session.messages
EpisodeList	에피소드 목록 카드	GET /episodes
EpisodeDetail	에피소드 본문 + 삭제	GET /episodes/{id}, DELETE /episodes/{id}
Library / LibraryMonth	책 목록 (월별 그룹)	GET /books, GET /books?month=YYYY-MM
BookDetail	책 메타 + 페이지 미리보기 + 댓글	GET /books/{id}
PageViewer	책 페이지 단위 뷰어	GET /books/{id}/pages
GenerateLoading	자서전 생성 폴링/대기	POST /books (선택 episodeId 배열 전송)
GenerateComplete	생성된 책으로 이동	응답 bookId
4. 현재 localStorage 데이터 구조 (프론트 단독 보유)
Key	타입	설명
user_profile_context_v1_1	UserProfileContext	호칭/말투/연령대/주제/defaults
onboarded	"true"	온보딩 완료 플래그
onboarding_draft_v1	OnboardingDraft	온보딩 중간 저장
interview_session_v1	InterviewSession	진행 중 인터뷰 세션 (state, messages, currentQuestion)
mockEpisodes (메모리)	Episode[]	임시 에피소드 — 추후 API 교체
mockBooks (메모리)	Book[]	임시 책 데이터 — 추후 API 교체
인증/최종 데이터(에피소드, 책)는 백엔드 DB가 SoT(Single Source of Truth). localStorage는 세션 임시 저장 + 프로필 캐시 용도로만 유지.
5. 백엔드 (Spring Boot) 연동 API 목록
Method	Path	설명	호출 페이지
POST	/api/auth/kakao	카카오 인가코드 → JWT 발급	Login
GET	/api/users/me	내 정보 + 프로필 조회	Main, Onboarding
PATCH	/api/users/me/profile	프로필 수정	Onboarding
POST	/api/interviews/start	인터뷰 세션 생성 + 첫 질문 발급	Interview
POST	/api/interviews/{sessionId}/messages	사용자 답변 메시지 저장	Interview
POST	/api/interviews/{sessionId}/next-question	다음 질문 요청 (백 → AI 호출)	Interview
POST	/api/interviews/{sessionId}/end	인터뷰 종료 + 에피소드 자동 생성	Interview
GET	/api/episodes	에피소드 목록 (페이징)	EpisodeList, Main
GET	/api/episodes/{episodeId}	에피소드 상세	EpisodeDetail
DELETE	/api/episodes/{episodeId}	에피소드 삭제	EpisodeDetail
POST	/api/books	선택 에피소드 → 자서전 생성 (백 → AI 호출)	GenerateLoading
GET	/api/books	책 목록 (월별 필터 ?month=YYYY-MM)	Library
GET	/api/books/{bookId}	책 상세 (메타 + 댓글)	BookDetail
GET	/api/books/{bookId}/pages	책 페이지 목록	PageViewer
DELETE	/api/books/{bookId}	책 삭제	BookDetail
공통 규약
인증: Authorization: Bearer <accessToken>
응답 포맷: { "data": ..., "error": null } / 실패 시 { "data": null, "error": { "code", "message" } }
시간: epoch millis (number) 또는 ISO8601 (string) — 팀 합의 필요. 본 문서는 epoch millis 기준.
6. AI 서버 연동 API 목록 (백엔드가 호출)
Method	Path	설명
POST	/api/ai/interview/next-question	대화 맥락 + 프로필 → 다음 질문 1개 생성
POST	/api/ai/interview/summary	인터뷰 메시지 → 에피소드 (제목/preview/본문) 요약
POST	/api/ai/book/generate	선택 에피소드 N개 → 책(chapters/pages)으로 변환
프론트는 AI 서버를 직접 호출하지 않습니다. 백엔드가 프록시하여 호출하고 결과만 프론트에 반환합니다.
7. API별 Request / Response JSON 예시
7.1 POST /api/auth/kakao
// Request
{ "code": "kakao_auth_code_xxx", "redirectUri": "https://doran.app/login/callback" }

// Response
{
  "data": {
    "accessToken": "eyJhbGciOi...",
    "refreshToken": "eyJhbGciOi...",
    "isNewUser": true,
    "onboarded": false
  },
  "error": null
}
7.2 GET /api/users/me
{
  "data": {
    "userId": 12,
    "nickname": "도란이",
    "onboarded": true,
    "profile": {
      "userTitle": "할머니",
      "ageGroup": "SENIOR_70S",
      "speechLevel": "HONORIFIC",
      "topic": "FAMILY",
      "happiestMoment": "손주들과 바다 갔던 날",
      "defaults": { "tone": "warm", "questionRule": "one_open_ended_question", "noFabrication": true }
    }
  }
}
7.3 PATCH /api/users/me/profile
// Request
{
  "userTitle": "할머니",
  "ageGroup": "SENIOR_70S",
  "speechLevel": "HONORIFIC",
  "topic": "FAMILY",
  "happiestMoment": "손주들과 바다 갔던 날"
}
// Response: 7.2와 동일 형태
7.4 POST /api/interviews/start
// Request
{ "topicHint": "FAMILY" }

// Response
{
  "data": {
    "sessionId": "s_1730000000000",
    "startedAt": 1730000000000,
    "state": "IDLE",
    "currentQuestion": "할머니, 손주들과 바다 갔던 날 이야기를 조금 더 들려주실 수 있을까요?",
    "messages": [
      { "id": "m_1730000000000_q", "speaker": "DORAN", "text": "할머니, ...", "createdAt": 1730000000000 }
    ]
  }
}
7.5 POST /api/interviews/{sessionId}/messages
// Request (사용자 답변 1건)
{ "speaker": "USER", "text": "그때가 참 따뜻했어요.", "createdAt": 1730000010000 }

// Response
{
  "data": {
    "id": "m_1730000010000_u",
    "speaker": "USER",
    "text": "그때가 참 따뜻했어요.",
    "createdAt": 1730000010000
  }
}
7.6 POST /api/interviews/{sessionId}/next-question
// Request (없거나 최근 메시지 ID 힌트만)
{ "lastMessageId": "m_1730000010000_u" }

// Response
{
  "data": {
    "question": {
      "id": "m_1730000011000_q",
      "speaker": "DORAN",
      "text": "그때 기분이 어떠셨어요?",
      "createdAt": 1730000011000
    },
    "state": "IDLE"
  }
}
7.7 POST /api/interviews/{sessionId}/end
// Request
{}

// Response (자동 요약된 에피소드 1건 반환)
{
  "data": {
    "sessionId": "s_1730000000000",
    "endedAt": 1730000600000,
    "episode": {
      "id": 101,
      "title": "달콤했던 호떡의 추억",
      "preview": "그날 엄마가 사주신 호떡은 유난히 맛있었다...",
      "content": "그날은 유난히 따뜻한 겨울 오후였다 ...",
      "createdAt": "2026-05-08"
    }
  }
}
7.8 GET /api/episodes?page=0&size=20
{
  "data": {
    "items": [
      { "id": 101, "title": "달콤했던 호떡의 추억", "preview": "그날 엄마가...", "createdAt": "2026-05-08" }
    ],
    "page": 0, "size": 20, "total": 1
  }
}
7.9 GET /api/episodes/{id}
{
  "data": {
    "id": 101,
    "title": "달콤했던 호떡의 추억",
    "preview": "그날 엄마가...",
    "content": "그날은 유난히 따뜻한 겨울 오후였다 ...",
    "createdAt": "2026-05-08"
  }
}
7.10 POST /api/books
// Request
{
  "title": "그 시절 추억",
  "episodeIds": [101, 102, 103],
  "coverColor": "#F5A623"
}

// Response (생성 비동기일 경우 jobId 반환 패턴 권장)
{
  "data": {
    "bookId": 1,
    "status": "GENERATING",   // or "COMPLETED"
    "jobId": "job_abc123"
  }
}
7.11 GET /api/books?month=2026-01
{
  "data": {
    "items": [
      { "id": 1, "title": "그 시절 추억", "createdAt": "2026-01-25", "coverColor": "#F5A623", "pageCount": 12 }
    ]
  }
}
7.12 GET /api/books/{id} & /pages
// /api/books/1
{
  "data": {
    "id": 1, "title": "그 시절 추억", "createdAt": "2026-01-25", "coverColor": "#F5A623",
    "comments": [
      { "id": 1, "author": "아들", "content": "정말 소중한 추억이에요 ❤️" }
    ]
  }
}

// /api/books/1/pages
{
  "data": {
    "items": [
      { "id": 1, "chapter": "제 5장", "content": "사랑이라는 단어를 떠올리면..." },
      { "id": 2, "chapter": "제 6장", "content": "어느덧 시간이 흘러..." }
    ]
  }
}
7.13 AI — POST /api/ai/interview/next-question
// Request (백엔드 → AI)
{
  "sessionId": "s_1730000000000",
  "profile": {
    "userTitle": "할머니",
    "ageGroup": "SENIOR_70S",
    "speechLevel": "HONORIFIC",
    "topic": "FAMILY"
  },
  "rules": { "tone": "warm", "questionRule": "one_open_ended_question", "noFabrication": true },
  "messages": [
    { "speaker": "DORAN", "text": "할머니, 손주들과 바다 갔던 날 이야기를 들려주세요." },
    { "speaker": "USER",  "text": "그때가 참 따뜻했어요." }
  ]
}

// Response
{
  "data": {
    "question": "그때 기분이 어떠셨어요?",
    "reasoning": "사용자 감정 심화를 위한 개방형 질문",
    "shouldEnd": false
  }
}
7.14 AI — POST /api/ai/interview/summary
// Request
{
  "sessionId": "s_1730000000000",
  "profile": { "userTitle": "할머니", "speechLevel": "HONORIFIC" },
  "messages": [
    { "speaker": "DORAN", "text": "..." },
    { "speaker": "USER",  "text": "..." }
  ]
}

// Response
{
  "data": {
    "title": "달콤했던 호떡의 추억",
    "preview": "그날 엄마가 사주신 호떡은 유난히 맛있었다...",
    "content": "그날은 유난히 따뜻한 겨울 오후였다 ...",
    "tags": ["가족", "겨울", "어린시절"]
  }
}
7.15 AI — POST /api/ai/book/generate
// Request
{
  "title": "그 시절 추억",
  "profile": { "userTitle": "할머니", "speechLevel": "HONORIFIC" },
  "episodes": [
    { "id": 101, "title": "...", "content": "..." },
    { "id": 102, "title": "...", "content": "..." }
  ]
}

// Response
{
  "data": {
    "title": "그 시절 추억",
    "coverColor": "#F5A623",
    "pages": [
      { "chapter": "제 1장", "content": "사랑이라는 단어를 떠올리면..." },
      { "chapter": "제 2장", "content": "어느덧 시간이 흘러..." }
    ]
  }
}
8. Spring Boot DTO 설계 참고용 타입 정의
// 공통
type ApiResponse<T> = { data: T | null; error: { code: string; message: string } | null };

// User / Profile
type SpeechLevel = "HONORIFIC" | "CASUAL";
type AgeGroup = "TEENS"|"TWENTIES"|"THIRTIES"|"FORTIES"|"FIFTIES"|"SIXTIES"|"SENIOR_70S";
type TopicValue = "FAMILY"|"LOVE"|"HEALTH"|"VALUES"|"CUSTOM";

interface UserProfileDto {
  userTitle?: string;
  ageGroup?: AgeGroup;
  speechLevel?: SpeechLevel;
  topic?: string;
  happiestMoment?: string;
  defaults?: { tone: "warm"|"neutral"; questionRule: "one_open_ended_question"; noFabrication: true };
}

interface UserMeDto { userId: number; nickname: string; onboarded: boolean; profile: UserProfileDto; }

// Interview
type InterviewState = "IDLE"|"LISTENING"|"PROCESSING"|"PAUSED"|"ENDED";
type Speaker = "DORAN"|"USER";

interface ChatMessageDto { id: string; speaker: Speaker; text: string; createdAt: number; }
interface InterviewSessionDto {
  sessionId: string; startedAt: number; endedAt?: number;
  state: InterviewState; currentQuestion: string; messages: ChatMessageDto[];
}

// Episode
interface EpisodeDto { id: number; title: string; preview: string; content?: string; createdAt: string; }

// Book
interface PageDto { id: number; chapter: string; content: string; }
interface CommentDto { id: number; author: string; content: string; }
interface BookDto {
  id: number; title: string; createdAt: string; coverColor?: string;
  pageCount?: number; pages?: PageDto[]; comments?: CommentDto[];
}
Spring Boot 매핑 가이드 (요약)
TS 타입	Java 매핑
string	String
number (epoch)	long / Instant
union string	enum
optional ?	@Nullable / Optional<>
배열	List<>
9. mock / localStorage → 실제 API 교체 포인트
위치	현재 처리	교체 후
Login.tsx	버튼 클릭 → navigate('/main')	POST /auth/kakao 호출 → JWT 저장 → /main
Onboarding.tsx	saveProfile() (localStorage)	PATCH /users/me/profile
EntryRouter	isOnboarded() localStorage 체크	GET /users/me의 onboarded 사용
Interview.tsx createNewSession()	프론트 단독 생성	POST /interviews/start
Interview.tsx handleStopAnswer mock 답변 "그때가 참 따뜻했어요."	하드코딩	STT 결과 → POST /interviews/{id}/messages
Interview.tsx setTimeout mock 다음 질문	1.2s 지연 후 하드코딩	POST /interviews/{id}/next-question 응답 사용
Interview.tsx handleEnd	state 변경만	POST /interviews/{id}/end → 에피소드 생성
EpisodeList, EpisodeDetail	mockEpisodes (data.ts)	GET /episodes, GET /episodes/{id}
Library, LibraryMonth	mockBooks (data.ts)	GET /books, GET /books?month=
BookDetail, PageViewer	mockBooks / mockComments	GET /books/{id}, GET /books/{id}/pages
GenerateLoading/Complete	프론트에서 episodes → pages 변환	POST /books (서버가 AI 호출)
sessionStore localStorage	세션 캐시	유지 (네트워크 끊김 대비) — 서버 응답이 SoT
10. 프론트엔드 환경변수 (.env)
# API
VITE_API_BASE_URL=https://api.doran.app
VITE_API_TIMEOUT_MS=15000

# 인증
VITE_KAKAO_CLIENT_ID=xxxxxxxxxxxxxxxx
VITE_KAKAO_REDIRECT_URI=https://doran.app/login/callback

# Feature Flags
VITE_USE_MOCK=false           # true이면 mock data.ts 사용
VITE_ENABLE_STT=true

# 기타
VITE_SENTRY_DSN=
VITE_APP_ENV=development      # development | staging | production
모든 키는 VITE_ 접두사 필수 (Vite 규칙). 비밀키는 절대 프론트에 두지 않습니다.


11. 백엔드 팀 TODO
 카카오 OAuth 연동 (/api/auth/kakao) + JWT 발급/리프레시
 User / Profile 엔티티 및 /users/me, PATCH /users/me/profile 구현
 Interview 도메인: Session, Message 엔티티 + 5개 인터뷰 API 구현
 next-question / end(요약) 에서 AI 서버 호출 프록시 구현 (WebClient/RestTemplate)
 Episode CRUD + 인터뷰 종료 시 자동 생성 로직
 Book 생성 API: 비동기 처리(Job 큐) 또는 동기 — 팀 합의 필요. 응답에 status 포함
 Book / Page / Comment 조회 API
 월별 필터 ?month=YYYY-MM 인덱스
 공통 응답 포맷 ApiResponse<T> + 에러 코드 정의
 CORS 설정 (VITE_API_BASE_URL 도메인 화이트리스트)
 Swagger / OpenAPI 3.0 문서 자동 배포
12. AI 팀 TODO
 /ai/interview/next-question — 프로필(호칭/말투/주제) + 직전 메시지 컨텍스트로 개방형 질문 1개 생성. shouldEnd 플래그로 종료 제안 가능
 톤 규칙: tone=warm, speechLevel=HONORIFIC이면 존댓말, noFabrication=true 강제 (없는 사실 생성 금지)
 /ai/interview/summary — 메시지 배열을 받아 {title, preview, content, tags} 반환. preview는 60자 내, title은 20자 내
 /ai/book/generate — 에피소드 배열을 받아 챕터 단위 pages[] 생성. 챕터 명칭은 "제 N장" 패턴
 프롬프트 버전 관리 + 응답 JSON 스키마 검증 (실패 시 재시도)
 PII / 민감정보 마스킹 가이드 정의
 응답 시간 SLA: next-question p95 < 2.5s, summary < 8s, book/generate < 30s