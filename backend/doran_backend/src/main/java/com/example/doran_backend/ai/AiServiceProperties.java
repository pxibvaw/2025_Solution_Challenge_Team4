package com.example.doran_backend.ai;

import lombok.Getter;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.time.Duration;

@Getter
@Component
public class AiServiceProperties {

    private final boolean enabled;
    private final String baseUrl;
    private final Duration turnTimeout;
    private final Duration endSessionTimeout;
    private final Duration autobiographyTimeout;

    public AiServiceProperties(
            @Value("${ai.service.enabled:false}") boolean enabled,
            @Value("${ai.service.base-url:http://localhost:8000}") String baseUrl,
            @Value("${ai.service.timeout.turn:30s}") Duration turnTimeout,
            @Value("${ai.service.timeout.end-session:5s}") Duration endSessionTimeout,
            @Value("${ai.service.timeout.autobiography:120s}") Duration autobiographyTimeout
    ) {
        this.enabled = enabled;
        this.baseUrl = baseUrl;
        this.turnTimeout = turnTimeout;
        this.endSessionTimeout = endSessionTimeout;
        this.autobiographyTimeout = autobiographyTimeout;
    }
}
