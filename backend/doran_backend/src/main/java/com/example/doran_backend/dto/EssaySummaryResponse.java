package com.example.doran_backend.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;

import java.time.LocalDateTime;

@Getter
@AllArgsConstructor
public class EssaySummaryResponse {
    private String essayId;
    private String title;
    private String summary;
    private Integer representativeYear;
    private String category;
    private String thumbnailUrl;
    private LocalDateTime createdAt;
}
