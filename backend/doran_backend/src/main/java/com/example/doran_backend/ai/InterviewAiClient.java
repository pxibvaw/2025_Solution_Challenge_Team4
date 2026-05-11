package com.example.doran_backend.ai;

import com.example.doran_backend.dto.InterviewTurnRequest;
import com.example.doran_backend.dto.UserProfileContext;

public interface InterviewAiClient {

    InterviewAiResult generateTurn(InterviewTurnRequest request, UserProfileContext profileContext);
}
