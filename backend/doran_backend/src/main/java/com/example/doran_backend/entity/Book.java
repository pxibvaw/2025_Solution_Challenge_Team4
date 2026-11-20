package com.example.doran_backend.entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Table(
        name = "books",
        indexes = {
                @Index(name = "idx_books_user_created", columnList = "user_id, created_at")
        }
)
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor(access = AccessLevel.PRIVATE)
@Builder
public class Book {

    @Id
    @Column(name = "id", length = 36, nullable = false)
    private String id;

    @Column(name = "user_id", length = 50, nullable = false)
    private String userId;

    @Column(name = "title", length = 100, nullable = false)
    private String title;

    @Column(name = "cover_gradient", columnDefinition = "TEXT")
    private String coverGradient;

    @Column(name = "prologue", columnDefinition = "TEXT")
    private String prologue;

    @Column(name = "epilogue", columnDefinition = "TEXT")
    private String epilogue;

    @Column(name = "life_theme", length = 100)
    private String lifeTheme;

    @Column(name = "generation_error", columnDefinition = "TEXT")
    private String generationError;

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;
}
