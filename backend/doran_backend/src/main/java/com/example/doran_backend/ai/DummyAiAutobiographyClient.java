package com.example.doran_backend.ai;

import com.example.doran_backend.dto.AiEpisodeResponse;
import com.example.doran_backend.dto.AutobiographyResponse;

import java.util.List;

public class DummyAiAutobiographyClient implements AiAutobiographyClient {

    @Override
    public AutobiographyResponse generate(String userId, List<String> selectedEpisodeIds, List<AiEpisodeResponse> episodes) {
        throw new IllegalArgumentException("AI service is disabled. Set AI_SERVICE_ENABLED=true to generate autobiography.");
    }
}
