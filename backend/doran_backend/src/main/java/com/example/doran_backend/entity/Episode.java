package com.example.doran_backend.entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Table(
        name = "episodes",
        indexes = {
                @Index(name = "idx_episodes_user_id", columnList = "user_id"),
                @Index(name = "idx_episodes_session_id", columnList = "session_id")
        }
)
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor(access = AccessLevel.PRIVATE)
@Builder
public class Episode {

    @Id
    @Column(name = "id", length = 50, nullable = false)
    private String id;

    @Column(name = "user_id", length = 50, nullable = false)
    private String userId;

    @Column(name = "session_id", length = 50, nullable = false)
    private String sessionId;

    @Column(name = "title", length = 200, nullable = false)
    private String title;

    @Column(name = "narrative", columnDefinition = "TEXT", nullable = false)
    private String narrative;

    @Column(name = "quote", columnDefinition = "TEXT")
    private String quote;

    @Column(name = "time_hint", length = 100)
    private String timeHint;

    @Column(name = "period_label", length = 50)
    private String periodLabel;

    @Column(name = "estimated_year_range", length = 20)
    private String estimatedYearRange;

    @Column(name = "location", length = 200)
    private String location;

    @Column(name = "persons_json", columnDefinition = "TEXT")
    private String personsJson;

    @Column(name = "sensory_json", columnDefinition = "TEXT")
    private String sensoryJson;

    @Column(name = "type", length = 30, nullable = false)
    private String type;

    @Column(name = "key_scene_type", length = 50)
    private String keySceneType;

    @Column(name = "theme", length = 100, nullable = false)
    private String theme;

    @Column(name = "emotion_tone", length = 100, nullable = false)
    private String emotionTone;

    @Column(name = "emotion_nuance", length = 200)
    private String emotionNuance;

    @Column(name = "autobiography_hint", columnDefinition = "TEXT")
    private String autobiographyHint;

    @Column(name = "life_value", length = 100)
    private String lifeValue;

    @Column(name = "importance_score")
    private Double importanceScore;

    @Column(name = "faithfulness_score")
    private Double faithfulnessScore;

    @Column(name = "coverage_score")
    private Double coverageScore;

    @Column(name = "emotional_authenticity")
    private Double emotionalAuthenticity;

    @Column(name = "sensory_vividness")
    private Double sensoryVividness;

    @Column(name = "personal_voice")
    private Double personalVoice;

    @Column(name = "narrative_flow")
    private Double narrativeFlow;

    @Column(name = "narrative_richness")
    private Double narrativeRichness;

    @Column(name = "quality_grade", length = 10)
    private String qualityGrade;

    @Column(name = "needs_regeneration")
    private Boolean needsRegeneration;

    @Column(name = "source_session_id", length = 50)
    private String sourceSessionId;

    @Column(name = "source_turn_start")
    private Integer sourceTurnStart;

    @Column(name = "source_turn_end")
    private Integer sourceTurnEnd;

    @Column(name = "source_facts_json", columnDefinition = "TEXT")
    private String sourceFactsJson;

    @Column(name = "is_merged", nullable = false)
    @Builder.Default
    private Boolean merged = false;

    @Column(name = "merged_from", length = 50)
    private String mergedFrom;

    @Column(name = "version", nullable = false)
    @Builder.Default
    private Integer version = 1;

    @Column(name = "is_selected_for_autobiography", nullable = false)
    @Builder.Default
    private Boolean selectedForAutobiography = false;

    @Column(name = "user_edited_title", length = 200)
    private String userEditedTitle;

    @Column(name = "user_memo", columnDefinition = "TEXT")
    private String userMemo;

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;

    public void updateFrom(Episode source) {
        this.title = source.title;
        this.narrative = source.narrative;
        this.quote = source.quote;
        this.timeHint = source.timeHint;
        this.periodLabel = source.periodLabel;
        this.estimatedYearRange = source.estimatedYearRange;
        this.location = source.location;
        this.personsJson = source.personsJson;
        this.sensoryJson = source.sensoryJson;
        this.type = source.type;
        this.keySceneType = source.keySceneType;
        this.theme = source.theme;
        this.emotionTone = source.emotionTone;
        this.emotionNuance = source.emotionNuance;
        this.autobiographyHint = source.autobiographyHint;
        this.lifeValue = source.lifeValue;
        this.importanceScore = source.importanceScore;
        this.faithfulnessScore = source.faithfulnessScore;
        this.coverageScore = source.coverageScore;
        this.emotionalAuthenticity = source.emotionalAuthenticity;
        this.sensoryVividness = source.sensoryVividness;
        this.personalVoice = source.personalVoice;
        this.narrativeFlow = source.narrativeFlow;
        this.narrativeRichness = source.narrativeRichness;
        this.qualityGrade = source.qualityGrade;
        this.needsRegeneration = source.needsRegeneration;
        this.sourceSessionId = source.sourceSessionId;
        this.sourceTurnStart = source.sourceTurnStart;
        this.sourceTurnEnd = source.sourceTurnEnd;
        this.sourceFactsJson = source.sourceFactsJson;
        this.merged = source.merged;
        this.mergedFrom = source.mergedFrom;
        this.version = source.version == null ? this.version + 1 : source.version;
        this.updatedAt = LocalDateTime.now();
    }
}
