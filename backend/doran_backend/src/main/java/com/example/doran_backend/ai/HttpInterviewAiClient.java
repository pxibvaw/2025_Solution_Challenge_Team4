package com.example.doran_backend.ai;

import com.example.doran_backend.dto.InterviewTurnRequest;
import com.example.doran_backend.dto.UserProfileContext;
import com.fasterxml.jackson.annotation.JsonProperty;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

@Component
@ConditionalOnProperty(name = "ai.service.enabled", havingValue = "true")
public class HttpInterviewAiClient implements InterviewAiClient {

    private final RestClient restClient;

    public HttpInterviewAiClient(AiServiceProperties properties) {
        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
        factory.setConnectTimeout(properties.getTurnTimeout());
        factory.setReadTimeout(properties.getTurnTimeout());
        this.restClient = RestClient.builder()
                .baseUrl(properties.getBaseUrl())
                .requestFactory(factory)
                .build();
    }

    @Override
    public InterviewAiResult generateTurn(InterviewTurnRequest request, UserProfileContext profileContext) {
        AiTurnResponse response = restClient.post()
                .uri("/turn")
                .body(new AiTurnRequest(
                        request.getSessionId(),
                        request.getRequestId(),
                        request.getInput().getUserText(),
                        toAiProfile(profileContext)
                ))
                .retrieve()
                .body(AiTurnResponse.class);

        if (response == null) {
            throw new IllegalArgumentException("AI turn 응답이 비어있습니다.");
        }

        return new InterviewAiResult(
                response.reply(),
                response.question(),
                null,
                response.audioContent(),
                "interview_v1",
                "ai-service",
                0L
        );
    }

    private AiProfile toAiProfile(UserProfileContext profileContext) {
        if (profileContext == null) {
            return null;
        }
        return new AiProfile(
                profileContext.getUserTitle(),
                profileContext.getSpeechLevel(),
                profileContext.getAgeGroup(),
                null,
                null
        );
    }

    private record AiTurnRequest(
            String sessionId,
            String requestId,
            String userText,
            AiProfile profile
    ) {
    }

    private record AiProfile(
            String userTitle,
            String speechLevel,
            String memorableAge,
            String coreValue,
            Integer birthYear
    ) {
    }

    private record AiTurnResponse(
            String requestId,
            String reply,
            String question,
            Integer turnIndex,
            @JsonProperty("audioContent") String audioContent
    ) {
    }
}
