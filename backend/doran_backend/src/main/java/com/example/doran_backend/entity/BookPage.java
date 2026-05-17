package com.example.doran_backend.entity;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(
        name = "book_pages",
        indexes = {
                @Index(name = "idx_book_pages_book_id", columnList = "book_id")
        }
)
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor(access = AccessLevel.PRIVATE)
@Builder
public class BookPage {

    @Id
    @Column(name = "id", length = 36, nullable = false)
    private String id;

    @Column(name = "book_id", length = 36, nullable = false)
    private String bookId;

    @Column(name = "page_number", nullable = false)
    private Integer pageNumber;

    @Column(name = "chapter", length = 150, nullable = false)
    private String chapter;

    @Column(name = "content", columnDefinition = "TEXT", nullable = false)
    private String content;

    @Column(name = "episode_id", length = 100)
    private String episodeId;
}
