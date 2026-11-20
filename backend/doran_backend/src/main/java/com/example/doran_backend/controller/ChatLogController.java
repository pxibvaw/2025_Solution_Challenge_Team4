package com.example.doran_backend.controller;

import com.example.doran_backend.dto.TurnLogResponse;
import com.example.doran_backend.service.ChatLogService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequiredArgsConstructor
@RequestMapping("/chat")
@Tag(name = "Chat Logs", description = "Interview turn log APIs")
public class ChatLogController {

    private final ChatLogService chatLogService;

    // GET /chat/sessions/{sessionId}/turns
    @Operation(summary = "Get session turn logs", description = "Returns TurnLog records for a session ordered by timestamp ascending.")
    @GetMapping("/sessions/{sessionId}/turns")
    public List<TurnLogResponse> getTurns(@PathVariable String sessionId) {
        return chatLogService.getTurnsBySessionId(sessionId);
    }
}
