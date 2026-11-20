package com.example.doran_backend.controller;

import com.example.doran_backend.dto.HomeResponse;
import com.example.doran_backend.service.HomeService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequiredArgsConstructor
@RequestMapping("/home")
@Tag(name = "Home", description = "Main dashboard API")
public class HomeController {

    private final HomeService homeService;

    @Operation(summary = "Get main home dashboard", description = "Returns profile, active session, today's question, stats, recent essays, and family message feed.")
    @GetMapping
    public HomeResponse getHome(@RequestParam Long userId) {
        return homeService.getHome(userId);
    }
}
