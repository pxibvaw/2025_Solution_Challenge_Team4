package com.example.doran_backend.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.util.List;

@Getter
@NoArgsConstructor
public class AutobiographyResponse {
    private String prologue;
    private List<Chapter> chapters;
    private String epilogue;

    @JsonProperty("life_theme")
    private String lifeTheme;

    @Getter
    @NoArgsConstructor
    public static class Chapter {
        private String title;

        @JsonProperty("period_label")
        private String periodLabel;

        private String narrative;

        @JsonProperty("episode_ids")
        private List<String> episodeIds;
    }
}
