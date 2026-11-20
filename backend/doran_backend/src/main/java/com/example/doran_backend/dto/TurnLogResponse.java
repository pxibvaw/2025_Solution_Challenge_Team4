package com.example.doran_backend.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;

import java.time.LocalDateTime;

@Getter
@AllArgsConstructor
public class TurnLogResponse {
    private String sessionId;
    private String turnId;
    private Long userId;
    private String requestId;
    private LocalDateTime ts;
    private String inputMode;
    private String userText;
    private String reply;
    private String question;
    private String rawModelOutput;
    private String promptVersion;
    private String model;
    private Long latencyMs;
}
