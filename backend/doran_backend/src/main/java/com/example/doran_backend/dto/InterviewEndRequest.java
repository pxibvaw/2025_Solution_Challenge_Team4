package com.example.doran_backend.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
public class InterviewEndRequest {

    @NotBlank
    private String sessionId;

    @NotNull
    private Long userId;

    @Size(max = 30)
    private String endReason; // USER_EXIT 등
}
