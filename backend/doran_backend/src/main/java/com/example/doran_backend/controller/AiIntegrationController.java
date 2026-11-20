package com.example.doran_backend.controller;

import com.example.doran_backend.dto.AiEpisodeCallbackRequest;
import com.example.doran_backend.dto.AiEpisodeCallbackResponse;
import com.example.doran_backend.dto.AiEpisodeResponse;
import com.example.doran_backend.service.AiEpisodeService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api")
@Tag(name = "AI Integration", description = "Spring Boot endpoints used by the FastAPI AI service")
public class AiIntegrationController {

    private final AiEpisodeService aiEpisodeService;

    @Operation(summary = "Get existing episodes for AI", description = "AI service calls this endpoint before segmentation/merge to avoid duplicate episodes.")
    @GetMapping("/episodes")
    public List<AiEpisodeResponse> getEpisodes(@RequestParam String userId) {
        return aiEpisodeService.getEpisodes(userId);
    }

    @Operation(summary = "Receive AI episode callback", description = "AI service posts created/merged episodes after end-session background processing.")
    @PostMapping("/ai/episodes")
    public AiEpisodeCallbackResponse receiveEpisodes(@RequestBody AiEpisodeCallbackRequest request) {
        return aiEpisodeService.receiveCallback(request);
    }
}
