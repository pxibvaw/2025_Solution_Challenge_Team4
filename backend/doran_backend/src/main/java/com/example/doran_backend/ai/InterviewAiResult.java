package com.example.doran_backend.ai;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class InterviewAiResult {
    private String reply;
    private String question;
    private String rawModelOutput;
    private String audioContent;
    private String promptVersion;
    private String model;
    private Long latencyMs;
}
