package com.example.doran_backend.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;

import java.time.LocalDateTime;

@Getter
@AllArgsConstructor
public class ShareLinkResponse {
    private String shareId;
    private String essayId;
    private String token;
    private String url;
    private LocalDateTime expiresAt;
}
