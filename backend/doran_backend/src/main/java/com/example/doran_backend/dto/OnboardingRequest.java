package com.example.doran_backend.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.util.List;

@Getter
@NoArgsConstructor
public class OnboardingRequest {
    @NotBlank
    @Size(max = 10)
    private String userTitle;        // 1~10

    @NotBlank
    private String ageGroup;         // SENIOR_60S ...

    private String speechLevel;      // HONORIFIC / CASUAL

    @NotNull
    private Boolean hasChildren;     // true/false

    @Size(max = 200)
    private String happiestMoment;   // 0~200 (optional)

    private List<String> coreValues; // optional, max 5

    @Size(max = 7)
    private String extraValue;       // 1~7 (optional)
}
