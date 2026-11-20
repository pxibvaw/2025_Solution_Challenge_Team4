package com.example.doran_backend.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.util.List;

@Getter
@AllArgsConstructor
@NoArgsConstructor
public class InterviewTurnRequest {

    @NotBlank
    private String sessionId;

    @NotNull
    private Long userId;

    @NotBlank
    private String requestId;

    @Valid
    @NotNull
    private Input input;

    @Valid
    private Context context;

    private String clientTs; // ISO8601 (문자열로 받기)

    @Getter
    @AllArgsConstructor
    @NoArgsConstructor
    public static class Input {
        @Size(max = 20)
        private String mode;     // "TEXT"

        @NotBlank
        private String userText; // 사용자 발화
    }

    @Getter
    @AllArgsConstructor
    @NoArgsConstructor
    public static class Context {
        @Size(max = 20)
        private String speechLevel;     // "HONORIFIC" 등

        @Size(max = 30)
        private String ageGroup;        // "SENIOR_70S" 등

        private List<String> coreValues; // ["가족", ...]

        @Size(max = 7)
        private String extraValue;      // "정" 등
    }
}
