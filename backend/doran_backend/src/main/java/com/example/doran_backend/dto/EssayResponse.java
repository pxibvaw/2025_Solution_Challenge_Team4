package com.example.doran_backend.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;

import java.time.LocalDateTime;
import java.util.List;

@Getter
@AllArgsConstructor
public class EssayResponse {
    private String essayId;
    private Long userId;
    private String sessionId;
    private String title;
    private String content;
    private String summary;
    private Integer representativeYear;
    private String category;
    private String thumbnailUrl;
    private String imagePrompt;
    private String pdfUrl;
    private String emotionLabel;
    private Integer emotionScore;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    private List<CommentResponse> comments;
}
