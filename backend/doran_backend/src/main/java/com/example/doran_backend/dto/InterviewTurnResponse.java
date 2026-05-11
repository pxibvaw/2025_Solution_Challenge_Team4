package com.example.doran_backend.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class InterviewTurnResponse {

    private String sessionId;
    private String turnId;
    private Output output;
    private Meta meta;

    @Getter
    @AllArgsConstructor
    public static class Output {
        private String reply;
        private String question; // 반드시 ? 포함
    }

    @Getter
    @AllArgsConstructor
    public static class Meta {
        private String model;         // 예: "dummy"
        private String promptVersion; // 예: "interview_v1"
        private Long latencyMs;       // 예: 10L
    }
}