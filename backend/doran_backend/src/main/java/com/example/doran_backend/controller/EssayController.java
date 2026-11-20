package com.example.doran_backend.controller;

import com.example.doran_backend.dto.*;
import com.example.doran_backend.service.EssayService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequiredArgsConstructor
@RequestMapping
@Tag(name = "Essays & Library", description = "Essay generation, library archive, comments, and share links")
public class EssayController {

    private final EssayService essayService;

    @Operation(summary = "Generate essay from interview logs", description = "Creates or updates today's essay from the session turn logs. Current AI client is dummy until the AI team implementation is connected.")
    @PostMapping("/essays/generate")
    public EssayResponse generateEssay(@Valid @RequestBody EssayGenerateRequest request) {
        return essayService.generateEssay(request);
    }

    @Operation(summary = "Get essay detail", description = "Returns the essay body, metadata, and comments.")
    @GetMapping("/essays/{essayId}")
    public EssayResponse getEssay(@PathVariable String essayId) {
        return essayService.getEssay(essayId);
    }

    @Operation(summary = "Search library", description = "Returns saved essays for the library page. Supports optional year filter and keyword query.")
    @GetMapping("/library")
    public List<EssaySummaryResponse> getLibrary(
            @RequestParam Long userId,
            @RequestParam(required = false) Integer year,
            @RequestParam(required = false) String query
    ) {
        return essayService.getLibrary(userId, year, query);
    }

    @Operation(summary = "Add family comment", description = "Adds a comment to an essay. Family account permissions are not implemented in the current scope.")
    @PostMapping("/essays/{essayId}/comments")
    public CommentResponse addComment(
            @PathVariable String essayId,
            @Valid @RequestBody CommentCreateRequest request
    ) {
        return essayService.addComment(essayId, request);
    }

    @Operation(summary = "Get essay comments", description = "Returns comments for an essay in createdAt ascending order.")
    @GetMapping("/essays/{essayId}/comments")
    public List<CommentResponse> getComments(@PathVariable String essayId) {
        return essayService.getComments(essayId);
    }

    @Operation(summary = "Create share link", description = "Creates a 30-day share token. File storage and public share page are out of current scope.")
    @PostMapping("/essays/{essayId}/share")
    public ShareLinkResponse createShareLink(
            @PathVariable String essayId,
            @RequestParam Long userId
    ) {
        return essayService.createShareLink(essayId, userId);
    }
}
