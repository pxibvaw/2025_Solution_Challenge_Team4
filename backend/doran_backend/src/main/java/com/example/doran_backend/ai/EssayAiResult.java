package com.example.doran_backend.ai;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class EssayAiResult {
    private String title;
    private String content;
    private String summary;
    private String imagePrompt;
    private String emotionLabel;
    private Integer emotionScore;
}
