package com.example.doran_backend.ai;

public class DummyAiSessionClient implements AiSessionClient {

    @Override
    public void endSession(String sessionId, String userId) {
        // AI service is disabled in local/default mode.
    }
}
