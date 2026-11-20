# Doran Memory Mate Backend

Spring Boot backend for the Memory Mate web service. The current backend supports onboarding, text interview sessions, turn logs, home dashboard data, essay generation stubs, library search, comments, sharing tokens, PostgreSQL schema migration, and Swagger/OpenAPI docs.

## Tech Stack

- Java 17
- Spring Boot 3.5
- Spring Web
- Spring Data JPA
- PostgreSQL
- Flyway
- H2 for tests
- springdoc-openapi Swagger UI

## Current Scope

Implemented:

- Onboarding and profile APIs
- LLM-safe `UserProfileContext v1.1`
- Text interview start, turn, end APIs
- TurnLog persistence and `sessionId + requestId` idempotency
- Chat log lookup sorted by timestamp ascending
- Main home dashboard API
- Essay generation API with dummy AI client
- Library list, year filter, and keyword search
- Essay comments
- Share token creation
- CORS for local frontend origins
- Global error response format
- PostgreSQL Flyway migration
- Swagger/OpenAPI docs

Not implemented in this scope:

- Google login/JWT. Requires Google OAuth Client ID.
- Family account, family invite, and permission management.
- File storage such as S3, GCS, or Firebase Storage.
- Actual AI model calls, image generation, and emotion analysis.
- PDF generation/download.
- Voice, STT, TTS, and WebSocket audio streaming.
- pgvector semantic search.

## Run Locally

Start PostgreSQL:

```bash
cd backend/doran_backend
docker compose up -d postgres
```

Run the backend:

```bash
./gradlew bootRun
```

Local URLs:

- API server: `http://localhost:8080`
- Swagger UI: `http://localhost:8080/swagger-ui.html`
- OpenAPI JSON: `http://localhost:8080/v3/api-docs`
- PostgreSQL: `127.0.0.1:15432`

Database credentials:

```text
database: doran
username: doran
password: doran
```

The PostgreSQL host port is `15432` to avoid conflicts with another local PostgreSQL on `5432`.

## Test

```bash
cd backend/doran_backend
./gradlew test
```

The test profile uses H2, not PostgreSQL. The full-flow test covers onboarding, interview start, turn idempotency, log lookup, essay generation, library lookup, comment creation, home lookup, interview end, and blocked turn after end.

## Manual API Flow

Use `backend/doran_backend/api-test.http` in IntelliJ HTTP Client.

Recommended order:

1. `POST /users/onboarding?userId=1`
2. `GET /users/profile?userId=1`
3. `GET /users/profile/context?userId=1`
4. `POST /users/guide/complete?userId=1`
5. `POST /interview/start`
6. Copy `sessionId` into `api-test.http`
7. `POST /interview/turn`
8. Call the same turn again to check idempotency
9. `GET /chat/sessions/{sessionId}/turns`
10. `POST /essays/generate`
11. Copy `essayId` into `api-test.http`
12. `GET /essays/{essayId}`
13. `GET /library?userId=1`
14. `POST /essays/{essayId}/comments`
15. `POST /essays/{essayId}/share?userId=1`
16. `POST /interview/end`

## Error Response

```json
{
  "code": "VALIDATION_ERROR",
  "message": "요청 값이 올바르지 않습니다.",
  "fieldErrors": [
    {
      "field": "userText",
      "message": "must not be blank"
    }
  ]
}
```

Common codes:

- `INVALID_REQUEST`
- `VALIDATION_ERROR`
- `MISSING_PARAMETER`

## AI Integration Points

The backend does not call a real AI model yet. AI team integration should implement these interfaces:

- `InterviewAiClient`
- `EssayAiClient`

Current dummy implementations:

- `DummyInterviewAiClient`
- `DummyEssayAiClient`

When a real Spring bean implementing the interface is added, the dummy bean is automatically replaced.
