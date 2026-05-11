package com.example.doran_backend.ai;

import com.example.doran_backend.entity.TurnLog;

import java.util.List;

public class DummyEssayAiClient implements EssayAiClient {

    @Override
    public EssayAiResult generateEssay(List<TurnLog> logs, EssayAiRequest request) {
        return new EssayAiResult(
                valueOrDefault(request.getTitle(), "오늘의 기억"),
                buildEssayContent(logs),
                buildSummary(logs),
                "따뜻한 회상 분위기의 가족 기억 일러스트",
                "WARM",
                80
        );
    }

    private String buildEssayContent(List<TurnLog> logs) {
        StringBuilder builder = new StringBuilder();
        builder.append("오늘의 이야기는 이렇게 시작되었습니다.\n\n");
        for (TurnLog log : logs) {
            builder.append(log.getUserText()).append("\n\n");
        }
        builder.append("이 기억은 앞으로 나의 서재에 차곡차곡 쌓일 소중한 기록입니다.");
        return builder.toString();
    }

    private String buildSummary(List<TurnLog> logs) {
        String first = logs.get(0).getUserText();
        return first.length() > 80 ? first.substring(0, 80) + "..." : first;
    }

    private String valueOrDefault(String value, String defaultValue) {
        if (value == null || value.trim().isEmpty()) {
            return defaultValue;
        }
        return value.trim();
    }
}
