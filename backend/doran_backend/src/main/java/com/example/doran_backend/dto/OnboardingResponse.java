package com.example.doran_backend.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;

import java.time.LocalDateTime;

@Getter
@AllArgsConstructor
public class OnboardingResponse {
    private Long userId;
    private Boolean onboardingCompleted;
    private LocalDateTime completedAt;
}