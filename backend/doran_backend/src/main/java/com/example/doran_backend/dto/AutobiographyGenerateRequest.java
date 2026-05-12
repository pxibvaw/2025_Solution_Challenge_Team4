package com.example.doran_backend.dto;

import lombok.Getter;
import lombok.NoArgsConstructor;

import java.util.List;

@Getter
@NoArgsConstructor
public class AutobiographyGenerateRequest {
    private String userId;
    private List<String> selectedEpisodeIds;
}
