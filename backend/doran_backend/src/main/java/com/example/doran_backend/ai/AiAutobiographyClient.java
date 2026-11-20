package com.example.doran_backend.ai;

import com.example.doran_backend.dto.AiEpisodeResponse;
import com.example.doran_backend.dto.AutobiographyResponse;
import com.example.doran_backend.dto.UserProfileContext;

import java.util.List;

public interface AiAutobiographyClient {

    AutobiographyResponse generate(String userId, List<String> selectedEpisodeIds, List<AiEpisodeResponse> episodes, UserProfileContext profileContext);
}
