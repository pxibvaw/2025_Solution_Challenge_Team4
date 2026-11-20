package com.example.doran_backend.dto;

import lombok.Getter;
import lombok.NoArgsConstructor;

import java.util.List;

@Getter
@NoArgsConstructor
public class AiEpisodeCallbackRequest {
    private String sessionId;
    private String userId;
    private List<AiEpisodePayload> newEpisodes;
    private List<AiEpisodePayload> mergedEpisodes;
    private Integer episodesCreated;
    private Integer episodesMerged;
    private Integer weakEpisodes;
    private List<String> warnings;
}
