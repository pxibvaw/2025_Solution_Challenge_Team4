package com.example.doran_backend.entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Table(
        name = "essay",
        uniqueConstraints = {
                @UniqueConstraint(name = "uq_essay_session", columnNames = "session_id")
        },
        indexes = {
                @Index(name = "idx_essay_user_created", columnList = "user_id, created_at"),
                @Index(name = "idx_essay_user_year", columnList = "user_id, representative_year")
        }
)
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor(access = AccessLevel.PRIVATE)
@Builder
public class Essay {

    @Id
    @Column(name = "essay_id", length = 36, nullable = false)
    private String essayId;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Column(name = "session_id", length = 36, nullable = false)
    private String sessionId;

    @Column(name = "title", length = 80, nullable = false)
    private String title;

    @Column(name = "content", columnDefinition = "TEXT", nullable = false)
    private String content;

    @Column(name = "summary", columnDefinition = "TEXT")
    private String summary;

    @Column(name = "representative_year")
    private Integer representativeYear;

    @Column(name = "category", length = 40)
    private String category;

    @Column(name = "thumbnail_url", length = 500)
    private String thumbnailUrl;

    @Column(name = "image_prompt", columnDefinition = "TEXT")
    private String imagePrompt;

    @Column(name = "pdf_url", length = 500)
    private String pdfUrl;

    @Column(name = "emotion_label", length = 40)
    private String emotionLabel;

    @Column(name = "emotion_score")
    private Integer emotionScore;

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;

    public void updateContent(String title, String content, String summary, Integer representativeYear, String category) {
        this.title = title;
        this.content = content;
        this.summary = summary;
        this.representativeYear = representativeYear;
        this.category = category;
        this.updatedAt = LocalDateTime.now();
    }
}
