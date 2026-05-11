package com.example.doran_backend.dto;

import jakarta.validation.constraints.NotNull;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
public class InterviewStartRequest {

    @NotNull
    private Long userId;
    private String clientTs; // ISO8601 형식 문자열
}
