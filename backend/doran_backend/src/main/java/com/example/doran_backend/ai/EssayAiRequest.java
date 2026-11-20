package com.example.doran_backend.ai;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class EssayAiRequest {
    private String title;
    private Integer representativeYear;
    private String category;
}
