package com.example.doran_backend.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;

import java.util.List;

@Getter
@AllArgsConstructor
public class HomeResponse {

    private ProfileResponse profile;
    private String activeSessionId;
    private TodayQuestion todayQuestion;
    private Stats stats;
    private List<EssaySummaryResponse> recentEssays;
    private List<FamilyMessageResponse> familyMessages;

    @Getter
    @AllArgsConstructor
    public static class TodayQuestion {
        private String title;
        private String question;
    }

    @Getter
    @AllArgsConstructor
    public static class Stats {
        private Long turnCount;
        private Long essayCount;
        private Long commentCount;
    }
}
