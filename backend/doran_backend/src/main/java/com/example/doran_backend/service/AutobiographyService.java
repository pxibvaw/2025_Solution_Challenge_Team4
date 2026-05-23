package com.example.doran_backend.service;

import com.example.doran_backend.ai.AiAutobiographyClient;
import com.example.doran_backend.dto.AiEpisodeResponse;
import com.example.doran_backend.dto.AutobiographyGenerateRequest;
import com.example.doran_backend.dto.AutobiographyResponse;
import com.example.doran_backend.dto.UserProfileContext;
import com.example.doran_backend.entity.Episode;
import com.example.doran_backend.repository.EpisodeRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class AutobiographyService {

    private final EpisodeRepository episodeRepository;
    private final AiEpisodeService aiEpisodeService;
    private final AiAutobiographyClient aiAutobiographyClient;
    private final OnboardingService onboardingService;

    @Transactional(readOnly = true)
    public AutobiographyResponse generate(AutobiographyGenerateRequest request) {
        if (request == null) {
            throw new IllegalArgumentException("요청 본문은 필수입니다.");
        }
        String userId = requireText(request.getUserId(), "userId는 필수입니다.");
        List<String> selectedEpisodeIds = request.getSelectedEpisodeIds();
        if (selectedEpisodeIds == null || selectedEpisodeIds.isEmpty()) {
            throw new IllegalArgumentException("selectedEpisodeIds는 필수입니다.");
        }

        List<Episode> episodes = episodeRepository.findByUserIdAndIdIn(userId, selectedEpisodeIds);
        if (episodes.isEmpty()) {
            throw new IllegalArgumentException("자서전 생성에 사용할 에피소드가 없습니다.");
        }

        List<AiEpisodeResponse> aiEpisodes = episodes.stream()
                .map(aiEpisodeService::toResponse)
                .toList();

        UserProfileContext profileContext = onboardingService.getUserProfileContext(parseUserId(userId));

        return aiAutobiographyClient.generate(userId, selectedEpisodeIds, aiEpisodes, profileContext);
    }

    private Long parseUserId(String userId) {
        try {
            return Long.parseLong(userId);
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException("userId는 숫자 형식이어야 합니다.");
        }
    }

    private String requireText(String value, String message) {
        if (value == null || value.trim().isEmpty()) {
            throw new IllegalArgumentException(message);
        }
        return value.trim();
    }
}
