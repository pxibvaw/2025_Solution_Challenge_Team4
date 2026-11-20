package com.example.doran_backend.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.Map;

@Getter
@NoArgsConstructor
public class AiEpisodePayload {
    private String id;

    @JsonProperty("user_id")
    private String userId;

    @JsonProperty("session_id")
    private String sessionId;

    @JsonProperty("turn_start")
    private Integer turnStart;

    @JsonProperty("turn_end")
    private Integer turnEnd;

    private String title;
    private String type;

    @JsonProperty("key_scene_type")
    private String keySceneType;

    private String theme;

    @JsonProperty("emotion_tone")
    private String emotionTone;

    @JsonProperty("time_hint")
    private String timeHint;

    @JsonProperty("period_label")
    private String periodLabel;

    @JsonProperty("estimated_year_range")
    private String estimatedYearRange;

    private String location;
    private List<Map<String, Object>> persons;
    private Map<String, Object> sensory;
    private String narrative;
    private String quote;

    @JsonProperty("autobiography_hint")
    private String autobiographyHint;

    @JsonProperty("life_value")
    private String lifeValue;

    @JsonProperty("emotion_nuance")
    private String emotionNuance;

    private AiEpisodeQualityPayload quality;

    @JsonProperty("source_session_id")
    private String sourceSessionId;

    @JsonProperty("source_turn_range")
    private List<Integer> sourceTurnRange;

    @JsonProperty("source_facts")
    private List<String> sourceFacts;

    @JsonProperty("importance_score")
    private Double importanceScore;
}
