package com.example.doran_backend.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class AiEpisodeCallbackResponse {
    private String sessionId;
    private Integer episodesCreated;
    private Integer episodesMerged;
    private Integer weakEpisodes;
    private Boolean duplicate;
}
