package com.example.doran_backend.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class UserProfileContext {

    private String userTitle;
    private String ageGroup;
    private Boolean hasChildren;
    private String happiestMoment;
    private String speechLevel;
    private Defaults defaults;

    @Getter
    @AllArgsConstructor
    public static class Defaults {
        private String tone;
        private String questionRule;
        private Boolean noFabrication;
    }
}
