package com.example.doran_backend.controller;

import com.example.doran_backend.dto.InterviewEndRequest;
import com.example.doran_backend.dto.InterviewEndResponse;
import com.example.doran_backend.dto.InterviewStartRequest;
import com.example.doran_backend.dto.InterviewStartResponse;
import com.example.doran_backend.dto.InterviewTurnRequest;
import com.example.doran_backend.dto.InterviewTurnResponse;
import com.example.doran_backend.service.InterviewService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequiredArgsConstructor
@RequestMapping("/interview")
@Tag(name = "Interview", description = "Text interview session lifecycle and turn APIs")
public class InterviewController {

    private final InterviewService interviewService;

    // POST /interview/start
    @Operation(summary = "Start interview session", description = "Creates an ACTIVE interview session and returns a UUID sessionId.")
    @PostMapping("/start")
    public InterviewStartResponse start(@Valid @RequestBody InterviewStartRequest request) {
        return interviewService.startInterview(request);
    }

    // POST /interview/end
    @Operation(summary = "End interview session", description = "Ends an ACTIVE session. Calling this again on an ENDED session is idempotent.")
    @PostMapping("/end")
    public InterviewEndResponse end(@Valid @RequestBody InterviewEndRequest request) {
        return interviewService.endInterview(request);
    }

    // POST /interview/turn
    @Operation(summary = "Submit text interview turn", description = "Stores one user text input and one AI response. sessionId + requestId is idempotent.")
    @PostMapping("/turn")
    public InterviewTurnResponse turn(@Valid @RequestBody InterviewTurnRequest request) {
        return interviewService.turn(request);
    }
}
