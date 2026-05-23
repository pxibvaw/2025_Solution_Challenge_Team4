package com.example.doran_backend.service;

import com.example.doran_backend.dto.*;
import com.example.doran_backend.ai.InterviewAiClient;
import com.example.doran_backend.ai.InterviewAiResult;
import com.example.doran_backend.ai.AiSessionClient;
import com.example.doran_backend.entity.InterviewSession;
import com.example.doran_backend.entity.TurnLog;
import com.example.doran_backend.entity.UserProfile;
import com.example.doran_backend.repository.InterviewSessionRepository;
import com.example.doran_backend.repository.TurnLogRepository;
import com.example.doran_backend.repository.UserProfileRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class InterviewService {

    private final InterviewSessionRepository interviewSessionRepository;
    private final TurnLogRepository turnLogRepository; // turn() 저장/멱등성용
    private final UserProfileRepository userProfileRepository;
    private final OnboardingService onboardingService;
    private final InterviewAiClient interviewAiClient;
    private final AiSessionClient aiSessionClient;

    // -------------------------
    // 1) 인터뷰 시작
    // -------------------------
    @Transactional
    public InterviewStartResponse startInterview(InterviewStartRequest request) {
        requireNonNull(request, "요청 본문은 필수입니다.");
        requireNonNull(request.getUserId(), "userId는 필수입니다.");

        String sessionId = UUID.randomUUID().toString();

        InterviewSession session = InterviewSession.builder()
                .sessionId(sessionId)
                .userId(request.getUserId())
                .startedAt(LocalDateTime.now())
                .status("ACTIVE")
                .build();

        interviewSessionRepository.save(session);

        return new InterviewStartResponse(sessionId);
    }

    // -------------------------
    // 2) 인터뷰 종료
    // -------------------------
    @Transactional
    public InterviewEndResponse endInterview(InterviewEndRequest request) {
        requireNonNull(request, "요청 본문은 필수입니다.");
        validateUuid(request.getSessionId(), "sessionId");
        requireNonNull(request.getUserId(), "userId는 필수입니다.");

        InterviewSession session = interviewSessionRepository.findById(request.getSessionId())
                .orElseThrow(() -> new IllegalArgumentException("세션을 찾을 수 없습니다. sessionId=" + request.getSessionId()));

        if (!session.getUserId().equals(request.getUserId())) {
            throw new IllegalArgumentException("세션 접근 권한이 없습니다. userId=" + request.getUserId());
        }

        // 멱등성: 이미 ENDED면 그대로 반환
        if ("ENDED".equals(session.getStatus())) {
            return new InterviewEndResponse(session.getSessionId(), session.getStatus());
        }

        session.end(request.getEndReason());
        interviewSessionRepository.save(session);
        notifyAiEndSession(session);

        return new InterviewEndResponse(session.getSessionId(), session.getStatus());
    }

    // -------------------------
    // 3) 인터뷰 턴 (HARD CONTRACT 핵심)
    // -------------------------
    @Transactional
    public InterviewTurnResponse turn(InterviewTurnRequest request) {
        requireNonNull(request, "요청 본문은 필수입니다.");
        validateUuid(request.getSessionId(), "sessionId");
        validateUuid(request.getRequestId(), "requestId");
        requireNonNull(request.getUserId(), "userId는 필수입니다.");
        requireNonNull(request.getInput(), "input은 필수입니다.");

        // (1) 세션 존재/ACTIVE 확인
        InterviewSession session = interviewSessionRepository.findById(request.getSessionId())
                .orElseThrow(() -> new IllegalArgumentException("세션을 찾을 수 없습니다. sessionId=" + request.getSessionId()));

        if (!session.getUserId().equals(request.getUserId())) {
            throw new IllegalArgumentException("세션 접근 권한이 없습니다. userId=" + request.getUserId());
        }

        if (!"ACTIVE".equals(session.getStatus())) {
            throw new IllegalArgumentException("종료된 세션입니다. sessionId=" + request.getSessionId());
        }

        validateSpeechLevel(request);

        // (2) userText 공백 체크 (HARD CONTRACT)
        String userText = trim(request.getInput().getUserText());
        if (userText == null) {
            throw new IllegalArgumentException("userText는 비어있을 수 없습니다.");
        }

        String inputMode = trim(request.getInput().getMode());
        if (inputMode == null) {
            inputMode = "TEXT";
        }
        if (!"TEXT".equals(inputMode)) {
            throw new IllegalArgumentException("v1은 TEXT 입력만 지원합니다.");
        }

        // (3) 멱등성: sessionId + requestId로 기존 TurnLog 있으면 그대로 반환
        TurnLog existing = turnLogRepository
                .findBySessionIdAndRequestId(request.getSessionId(), request.getRequestId())
                .orElse(null);

        if (existing != null) {
            InterviewTurnResponse.Output output =
                    new InterviewTurnResponse.Output(existing.getReply(), existing.getQuestion());

            InterviewTurnResponse.Meta meta =
                    new InterviewTurnResponse.Meta(existing.getModel(), existing.getPromptVersion(), existing.getLatencyMs());

            return new InterviewTurnResponse(existing.getSessionId(), existing.getTurnId(), output, meta);
        }

        // (4) AI 호출 접점. 현재 구현체는 dummy, 추후 Gemini 구현체로 교체한다.
        UserProfileContext profileContext = onboardingService.getUserProfileContext(request.getUserId());
        InterviewAiResult aiResult = interviewAiClient.generateTurn(request, profileContext);
        String reply = aiResult.getReply();
        String question = aiResult.getQuestion();
        validateOutput(reply, question);

        // (5) TurnLog 저장
        String turnId = UUID.randomUUID().toString();
        long latencyMs = 0L;

        TurnLog log = TurnLog.builder()
                .sessionId(request.getSessionId())
                .turnId(turnId)
                .userId(request.getUserId())
                .requestId(request.getRequestId())
                .ts(LocalDateTime.now()) // ✅ clientTs 파싱 안하고 "현재시간"으로 박아서 에러 제거
                .inputMode(inputMode)
                .userText(userText)
                .reply(reply)
                .question(question)
                .rawModelOutput(aiResult.getRawModelOutput())
                .promptVersion(valueOrDefault(aiResult.getPromptVersion(), "interview_v1"))
                .model(valueOrDefault(aiResult.getModel(), "dummy"))
                .latencyMs(aiResult.getLatencyMs() == null ? latencyMs : aiResult.getLatencyMs())
                .build();

        turnLogRepository.save(log);

        // (6) 응답 반환
        InterviewTurnResponse.Output output = new InterviewTurnResponse.Output(reply, question);
        InterviewTurnResponse.Meta meta = new InterviewTurnResponse.Meta(
                log.getModel(),
                log.getPromptVersion(),
                log.getLatencyMs()
        );

        return new InterviewTurnResponse(request.getSessionId(), turnId, output, meta);
    }

    // -------------------------
    // helper
    // -------------------------
    private String trim(String s) {
        if (s == null) return null;
        String t = s.trim();
        return t.isEmpty() ? null : t;
    }

    private String valueOrDefault(String value, String defaultValue) {
        String trimmed = trim(value);
        return trimmed == null ? defaultValue : trimmed;
    }

    private void validateUuid(String value, String fieldName) {
        String trimmed = trim(value);
        if (trimmed == null) {
            throw new IllegalArgumentException(fieldName + "는 필수입니다.");
        }
        try {
            UUID.fromString(trimmed);
        } catch (IllegalArgumentException e) {
            throw new IllegalArgumentException(fieldName + "는 UUID 형식이어야 합니다.");
        }
    }

    private void validateOutput(String reply, String question) {
        String trimmedReply = trim(reply);
        String trimmedQuestion = trim(question);
        if (trimmedReply == null) {
            throw new IllegalArgumentException("reply는 비어있을 수 없습니다.");
        }
        if (reply.contains("?")) {
            throw new IllegalArgumentException("reply에는 질문을 포함할 수 없습니다.");
        }
        if (trimmedQuestion == null) {
            throw new IllegalArgumentException("question은 비어있을 수 없습니다.");
        }
        if (!question.contains("?")) {
            throw new IllegalArgumentException("question에는 ?가 포함되어야 합니다.");
        }
    }

    private void validateSpeechLevel(InterviewTurnRequest request) {
        if (request.getContext() == null || trim(request.getContext().getSpeechLevel()) == null) {
            return;
        }

        UserProfile profile = userProfileRepository.findById(request.getUserId()).orElse(null);
        if (profile == null || trim(profile.getSpeechLevel()) == null) {
            return;
        }

        if (!profile.getSpeechLevel().equals(request.getContext().getSpeechLevel())) {
            throw new IllegalArgumentException("세션 중 말투는 변경할 수 없습니다.");
        }
    }

    private void requireNonNull(Object value, String message) {
        if (value == null) {
            throw new IllegalArgumentException(message);
        }
    }

    private void notifyAiEndSession(InterviewSession session) {
        try {
            UserProfileContext profileContext = onboardingService.getUserProfileContext(session.getUserId());
            aiSessionClient.endSession(session.getSessionId(), String.valueOf(session.getUserId()), profileContext);
        } catch (RuntimeException ignored) {
            // Session end must remain stable even if the optional AI service is unavailable.
        }
    }
}
