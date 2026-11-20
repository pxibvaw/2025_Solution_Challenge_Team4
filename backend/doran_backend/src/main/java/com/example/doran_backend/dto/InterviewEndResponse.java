package com.example.doran_backend.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class InterviewEndResponse {

    private String sessionId;
    private String status;
}