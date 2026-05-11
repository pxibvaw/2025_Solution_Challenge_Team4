package com.example.doran_backend.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
public class EssayGenerateRequest {
    @NotBlank
    private String sessionId;

    @NotNull
    private Long userId;

    @Size(max = 80)
    private String title;

    private Integer representativeYear;

    @Size(max = 40)
    private String category;
}
