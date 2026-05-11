package com.example.doran_backend.ai;

import com.example.doran_backend.dto.InterviewTurnRequest;
import com.example.doran_backend.dto.UserProfileContext;

public class DummyInterviewAiClient implements InterviewAiClient {

    @Override
    public InterviewAiResult generateTurn(InterviewTurnRequest request, UserProfileContext profileContext) {
        return new InterviewAiResult(
                "말씀해주셔서 감사합니다.",
                "그때 어떤 기분이셨나요?",
                null,
                "interview_v1",
                "dummy",
                0L
        );
    }
}
