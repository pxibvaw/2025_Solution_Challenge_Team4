package com.example.doran_backend.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class GuideCompleteResponse {
    private Long userId;
    private Boolean guideCompleted;
}
