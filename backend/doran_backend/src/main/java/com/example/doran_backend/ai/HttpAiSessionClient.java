package com.example.doran_backend.ai;

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
                .build();
    }

    @Override
    public void endSession(String sessionId, String userId) {
        restClient.post()
                .uri("/end-session")
                .body(new AiEndSessionRequest(sessionId, userId))
                .retrieve()
                .toBodilessEntity();
    }

    private record AiEndSessionRequest(String sessionId, String userId) {
    }
}
