package com.example.doran_backend.entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Table(
        name = "essay_comment",
        indexes = {
                @Index(name = "idx_essay_comment_essay_created", columnList = "essay_id, created_at"),
                @Index(name = "idx_essay_comment_user_created", columnList = "user_id, created_at")
        }
)
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor(access = AccessLevel.PRIVATE)
@Builder
public class EssayComment {

    @Id
    @Column(name = "comment_id", length = 36, nullable = false)
    private String commentId;

    @Column(name = "essay_id", length = 36, nullable = false)
    private String essayId;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Column(name = "author_name", length = 30, nullable = false)
    private String authorName;

    @Column(name = "content", columnDefinition = "TEXT", nullable = false)
    private String content;

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;
}
