package com.example.doran_backend.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;

import java.time.LocalDateTime;

@Getter
@AllArgsConstructor
public class FamilyMessageResponse {
    private String essayId;
    private String essayTitle;
    private String authorName;
    private String content;
    private LocalDateTime createdAt;
}
