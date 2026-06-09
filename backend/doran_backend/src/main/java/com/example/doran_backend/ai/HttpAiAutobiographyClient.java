package com.example.doran_backend.ai;

import com.example.doran_backend.dto.AiEpisodeResponse;
import com.example.doran_backend.dto.AutobiographyResponse;
import com.example.doran_backend.dto.UserProfileContext;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientResponseException;

import java.util.List;

@Component
@ConditionalOnProperty(name = "ai.service.enabled", havingValue = "true")
@Slf4j
public class HttpAiAutobiographyClient implements AiAutobiographyClient {

    private final RestClient restClient;

    public HttpAiAutobiographyClient(AiServiceProperties properties) {
        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
        factory.setConnectTimeout(properties.getAutobiographyTimeout());
        factory.setReadTimeout(properties.getAutobiographyTimeout());
        this.restClient = RestClient.builder()
                .baseUrl(properties.getBaseUrl())
                .requestFactory(factory)
                .defaultHeader("ngrok-skip-browser-warning", "true")
                .build();
    }

    @Override
    public AutobiographyResponse generate(String userId, List<String> selectedEpisodeIds, List<AiEpisodeResponse> episodes, UserProfileContext profileContext) {
        try {
            return restClient.post()
                    .uri("/autobiography")
                    .body(new AiAutobiographyRequest(userId, selectedEpisodeIds, episodes, AiProfile.from(profileContext)))
                    .retrieve()
                    .body(AutobiographyResponse.class);
        } catch (RestClientResponseException e) {
            log.error(
                    "AI 자서전 요청 실패: status={}, response={}",
                    e.getStatusCode(),
                    e.getResponseBodyAsString()
            );
            throw e;
        }
    }

    private record AiAutobiographyRequest(
            String userId,
            List<String> selectedEpisodeIds,
            List<AiEpisodeResponse> episodes,
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
