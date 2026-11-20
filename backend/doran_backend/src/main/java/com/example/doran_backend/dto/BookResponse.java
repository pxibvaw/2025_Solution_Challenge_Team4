package com.example.doran_backend.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.AllArgsConstructor;
import lombok.Getter;

import java.time.LocalDateTime;
import java.util.List;

@Getter
@AllArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)
public class BookResponse {
    private String id;
    private String userId;
    private String title;
    private String coverGradient;
    private String prologue;
    private String epilogue;
    private String lifeTheme;
    private String generationError;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    private Integer pageCount;
    private List<BookPageResponse> pages;
}
