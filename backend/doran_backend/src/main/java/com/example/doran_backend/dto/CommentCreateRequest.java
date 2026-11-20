package com.example.doran_backend.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
public class CommentCreateRequest {
    private Long userId;

    @NotBlank
    @Size(max = 30)
    private String authorName;

    @NotBlank
    @Size(max = 1000)
    private String content;
}
