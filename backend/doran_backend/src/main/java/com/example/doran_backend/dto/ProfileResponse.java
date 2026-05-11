package com.example.doran_backend.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;

import java.util.List;

@Getter
@AllArgsConstructor
public class ProfileResponse {
    private Long userId;
    private String userTitle;
    private String ageGroup;
    private String speechLevel;
    private Boolean hasChildren;
    private String happiestMoment;
    private List<String> coreValues;
    private String extraValue;
    private Boolean onboardingCompleted;
    private Boolean guideCompleted;
}
