package com.example.doran_backend.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.AllArgsConstructor;
import lombok.Getter;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@Getter
@AllArgsConstructor
public class AiEpisodeResponse {
    private String id;

    @JsonProperty("user_id")
    private String userId;

    @JsonProperty("session_id")
    private String sessionId;

    private String title;
    private String narrative;
    private String quote;

    @JsonProperty("time_hint")
    private String timeHint;

    @JsonProperty("period_label")
    private String periodLabel;

    @JsonProperty("estimated_year_range")
    private String estimatedYearRange;

    private String location;
    private List<Map<String, Object>> persons;
    private Map<String, Object> sensory;
    private String type;

    @JsonProperty("key_scene_type")
    private String keySceneType;

    private String theme;

    @JsonProperty("emotion_tone")
    private String emotionTone;

    @JsonProperty("emotion_nuance")
    private String emotionNuance;

    @JsonProperty("autobiography_hint")
    private String autobiographyHint;

    @JsonProperty("life_value")
    private String lifeValue;

    @JsonProperty("importance_score")
    private Double importanceScore;

    private AiEpisodeQualityResponse quality;

    @JsonProperty("source_session_id")
    private String sourceSessionId;

    @JsonProperty("source_turn_range")
    private List<Integer> sourceTurnRange;

    @JsonProperty("source_facts")
    private List<String> sourceFacts;

    @JsonProperty("is_merged")
    private Boolean merged;

    @JsonProperty("merged_from")
    private String mergedFrom;

    private Integer version;

    @JsonProperty("is_selected_for_autobiography")
    private Boolean selectedForAutobiography;

    @JsonProperty("user_edited_title")
    private String userEditedTitle;

    @JsonProperty("user_memo")
    private String userMemo;

    @JsonProperty("created_at")
    @JsonFormat(shape = JsonFormat.Shape.STRING)
    private LocalDateTime createdAt;

    @JsonProperty("updated_at")
    @JsonFormat(shape = JsonFormat.Shape.STRING)
    private LocalDateTime updatedAt;
}
