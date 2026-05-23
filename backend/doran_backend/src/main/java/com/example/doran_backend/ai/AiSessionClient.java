package com.example.doran_backend.ai;

import com.example.doran_backend.dto.UserProfileContext;

public interface AiSessionClient {

    void endSession(String sessionId, String userId, UserProfileContext profileContext);
}
