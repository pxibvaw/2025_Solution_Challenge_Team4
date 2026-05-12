package com.example.doran_backend.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class AiEpisodeQualityResponse {

    @JsonProperty("faithfulness_score")
    private Double faithfulnessScore;

    @JsonProperty("coverage_score")
    private Double coverageScore;

    @JsonProperty("emotional_authenticity")
    private Double emotionalAuthenticity;

    @JsonProperty("sensory_vividness")
    private Double sensoryVividness;

    @JsonProperty("personal_voice")
    private Double personalVoice;

    @JsonProperty("narrative_flow")
    private Double narrativeFlow;

    @JsonProperty("narrative_richness")
    private Double narrativeRichness;

    @JsonProperty("quality_grade")
    private String qualityGrade;

    @JsonProperty("needs_regeneration")
    private Boolean needsRegeneration;
}
