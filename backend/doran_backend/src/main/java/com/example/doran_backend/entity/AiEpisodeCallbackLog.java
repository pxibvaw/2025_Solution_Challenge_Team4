package com.example.doran_backend.entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "ai_episode_callback_log")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor(access = AccessLevel.PRIVATE)
@Builder
public class AiEpisodeCallbackLog {

    @Id
    @Column(name = "session_id", length = 50, nullable = false)
    private String sessionId;

    @Column(name = "user_id", length = 50, nullable = false)
    private String userId;

    @Column(name = "episodes_created", nullable = false)
    private Integer episodesCreated;

    @Column(name = "episodes_merged", nullable = false)
    private Integer episodesMerged;

    @Column(name = "weak_episodes", nullable = false)
    private Integer weakEpisodes;

    @Column(name = "warnings_json", columnDefinition = "TEXT")
    private String warningsJson;

    @Column(name = "received_at", nullable = false)
    private LocalDateTime receivedAt;
}
