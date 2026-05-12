package com.example.doran_backend.ai;

import com.example.doran_backend.dto.AiEpisodeResponse;
import com.example.doran_backend.dto.AutobiographyResponse;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import java.util.List;

@Component
@ConditionalOnProperty(name = "ai.service.enabled", havingValue = "true")
public class HttpAiAutobiographyClient implements AiAutobiographyClient {

    private final RestClient restClient;

    public HttpAiAutobiographyClient(AiServiceProperties properties) {
        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
        factory.setConnectTimeout(properties.getAutobiographyTimeout());
        factory.setReadTimeout(properties.getAutobiographyTimeout());
        this.restClient = RestClient.builder()
                .baseUrl(properties.getBaseUrl())
                .requestFactory(factory)
                .build();
    }

    @Override
    public AutobiographyResponse generate(String userId, List<String> selectedEpisodeIds, List<AiEpisodeResponse> episodes) {
        return restClient.post()
                .uri("/autobiography")
                .body(new AiAutobiographyRequest(userId, selectedEpisodeIds, episodes))
                .retrieve()
                .body(AutobiographyResponse.class);
    }

    private record AiAutobiographyRequest(
            String userId,
            List<String> selectedEpisodeIds,
            List<AiEpisodeResponse> episodes
    ) {
    }
}
