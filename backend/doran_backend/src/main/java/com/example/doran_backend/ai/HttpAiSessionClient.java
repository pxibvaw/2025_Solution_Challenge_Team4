package com.example.doran_backend.ai;

import com.example.doran_backend.dto.UserProfileContext;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

@Component
@ConditionalOnProperty(name = "ai.service.enabled", havingValue = "true")
public class HttpAiSessionClient implements AiSessionClient {

    private final RestClient restClient;

    public HttpAiSessionClient(AiServiceProperties properties) {
        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
        factory.setConnectTimeout(properties.getEndSessionTimeout());
        factory.setReadTimeout(properties.getEndSessionTimeout());
        this.restClient = RestClient.builder()
                .baseUrl(properties.getBaseUrl())
                .requestFactory(factory)
                .defaultHeader("ngrok-skip-browser-warning", "true")
                .build();
    }

    @Override
    public void endSession(String sessionId, String userId, UserProfileContext profileContext) {
        restClient.post()
                .uri("/end-session")
                .body(new AiEndSessionRequest(sessionId, userId, AiProfile.from(profileContext)))
                .retrieve()
                .toBodilessEntity();
    }

    private record AiEndSessionRequest(String sessionId, String userId, AiProfile profile) {
    }

    private record AiProfile(
            String userTitle,
            String speechLevel,
            String memorableAge,
            String coreValue,
            Integer birthYear
    ) {
        private static AiProfile from(UserProfileContext profileContext) {
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
    }
}
