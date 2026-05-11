package com.example.doran_backend.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;

import java.util.List;

@Getter
@AllArgsConstructor
public class ErrorResponse {
    private String code;
    private String message;
    private List<FieldErrorResponse> fieldErrors;

    public static ErrorResponse of(String code, String message) {
        return new ErrorResponse(code, message, List.of());
    }

    public static ErrorResponse withFields(String code, String message, List<FieldErrorResponse> fieldErrors) {
        return new ErrorResponse(code, message, fieldErrors);
    }

    @Getter
    @AllArgsConstructor
    public static class FieldErrorResponse {
        private String field;
        private String message;
    }
}
