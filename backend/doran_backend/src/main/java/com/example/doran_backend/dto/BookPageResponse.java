package com.example.doran_backend.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class BookPageResponse {
    private String id;
    private String bookId;
    private String episodeId;
    private String chapter;
    private String content;
    private Integer pageNumber;
}
