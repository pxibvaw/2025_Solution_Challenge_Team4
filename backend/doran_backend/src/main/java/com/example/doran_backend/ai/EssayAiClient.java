package com.example.doran_backend.ai;

import com.example.doran_backend.entity.TurnLog;

import java.util.List;

public interface EssayAiClient {

    EssayAiResult generateEssay(List<TurnLog> logs, EssayAiRequest request);
}
