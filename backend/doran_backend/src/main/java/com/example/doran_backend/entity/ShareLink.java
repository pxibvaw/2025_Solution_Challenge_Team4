package com.example.doran_backend.entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Table(
        name = "share_link",
        indexes = {
                @Index(name = "idx_share_link_token", columnList = "token")
        }
)
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor(access = AccessLevel.PRIVATE)
@Builder
public class ShareLink {

    @Id
    @Column(name = "share_id", length = 36, nullable = false)
    private String shareId;

    @Column(name = "essay_id", length = 36, nullable = false)
    private String essayId;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Column(name = "token", length = 64, nullable = false, unique = true)
    private String token;

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;

    @Column(name = "expires_at")
    private LocalDateTime expiresAt;
}
