package com.example.doran_backend.ai;

import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class AiClientConfig {

    @Bean
    @ConditionalOnMissingBean(InterviewAiClient.class)
    public InterviewAiClient interviewAiClient() {
        return new DummyInterviewAiClient();
    }

    @Bean
    @ConditionalOnMissingBean(EssayAiClient.class)
    public EssayAiClient essayAiClient() {
        return new DummyEssayAiClient();
    }
}
