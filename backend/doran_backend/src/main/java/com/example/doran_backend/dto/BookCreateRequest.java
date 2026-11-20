package com.example.doran_backend.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.util.List;

@Getter
@NoArgsConstructor
@AllArgsConstructor
public class BookCreateRequest {
    private String userId;
    private String title;
    private String coverGradient;
    private String prologue;
    private String epilogue;
    private String lifeTheme;
    private String generationError;
    private List<BookPageRequest> pages;

    @Getter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class BookPageRequest {
        private String episodeId;
        private String chapter;
        private String content;
        private Integer pageNumber;
    }
}
