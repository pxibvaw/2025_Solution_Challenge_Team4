package com.example.doran_backend.controller;

import com.example.doran_backend.dto.OnboardingRequest;
import com.example.doran_backend.dto.OnboardingResponse;
import com.example.doran_backend.dto.ProfileResponse;
import com.example.doran_backend.dto.GuideCompleteResponse;
import com.example.doran_backend.dto.UserProfileContext;
import com.example.doran_backend.service.OnboardingService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequiredArgsConstructor
@RequestMapping("/users")
@Tag(name = "Users", description = "Onboarding, profile, and first-guide completion APIs")
public class OnboardingController {

    private final OnboardingService onboardingService;

    // POST /users/onboarding?userId=1
    @Operation(summary = "Save onboarding profile", description = "Stores the user's title, age group, speech level, family context, and values.")
    @PostMapping("/onboarding")
    public ResponseEntity<OnboardingResponse> saveOnboarding(
            @RequestParam Long userId,
            @Valid @RequestBody OnboardingRequest request
    ) {
        return ResponseEntity.ok(onboardingService.saveOnboarding(userId, request));
    }

    // GET /users/profile?userId=1
    @Operation(summary = "Get user profile", description = "Returns the saved onboarding profile used by the web app.")
    @GetMapping("/profile")
    public ResponseEntity<ProfileResponse> getProfile(@RequestParam Long userId) {
        ProfileResponse response = onboardingService.getProfile(userId);
        return ResponseEntity.ok(response);
    }

    @Operation(summary = "Get LLM-safe profile context", description = "Returns UserProfileContext v1.1. This structure is intended for AI prompts and hides raw onboarding details from direct output.")
    @GetMapping("/profile/context")
    public ResponseEntity<UserProfileContext> getProfileContext(@RequestParam Long userId) {
        return ResponseEntity.ok(onboardingService.getUserProfileContext(userId));
    }

    @Operation(summary = "Mark guide as completed", description = "Marks the first-use guide as completed for the main flow.")
    @PostMapping("/guide/complete")
    public ResponseEntity<GuideCompleteResponse> completeGuide(@RequestParam Long userId) {
        return ResponseEntity.ok(new GuideCompleteResponse(userId, onboardingService.completeGuide(userId)));
    }
}
