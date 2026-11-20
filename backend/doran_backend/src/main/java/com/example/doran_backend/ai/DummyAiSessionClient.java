package com.example.doran_backend.ai;

import com.example.doran_backend.dto.UserProfileContext;

public class DummyAiSessionClient implements AiSessionClient {

    @Override
    public void endSession(String sessionId, String userId, UserProfileContext profileContext) {
        // AI service is disabled in local/default mode.
    }
}
