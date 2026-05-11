package com.example.doran_backend.service;

import com.example.doran_backend.dto.TurnLogResponse;
import com.example.doran_backend.entity.TurnLog;
import com.example.doran_backend.repository.TurnLogRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class ChatLogService {

    private final TurnLogRepository turnLogRepository;

    @Transactional(readOnly = true)
    public List<TurnLogResponse> getTurnsBySessionId(String sessionId) {

        List<TurnLog> logs = turnLogRepository.findBySessionIdOrderByTsAsc(sessionId);

        // 로그가 없으면 빈 배열로 반환(프론트에서 "아직 없어요" 처리 가능)
        return logs.stream()
                .map(l -> new TurnLogResponse(
                        l.getSessionId(),
                        l.getTurnId(),
                        l.getUserId(),
                        l.getRequestId(),
                        l.getTs(),
                        l.getInputMode(),
                        l.getUserText(),
                        l.getReply(),
                        l.getQuestion(),
                        l.getRawModelOutput(),
                        l.getPromptVersion(),
                        l.getModel(),
                        l.getLatencyMs()
                ))
                .toList();
    }
}
