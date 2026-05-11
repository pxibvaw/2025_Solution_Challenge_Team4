package com.example.doran_backend.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;

import java.time.LocalDateTime;

@Getter
@AllArgsConstructor
public class CommentResponse {
    private String commentId;
    private String essayId;
    private Long userId;
    private String authorName;
    private String content;
    private LocalDateTime createdAt;
}
