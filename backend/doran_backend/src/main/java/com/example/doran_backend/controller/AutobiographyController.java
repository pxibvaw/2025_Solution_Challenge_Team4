package com.example.doran_backend.controller;

import com.example.doran_backend.dto.AutobiographyGenerateRequest;
import com.example.doran_backend.dto.AutobiographyResponse;
import com.example.doran_backend.service.AutobiographyService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequiredArgsConstructor
@RequestMapping("/autobiography")
@Tag(name = "Autobiography", description = "Autobiography generation proxy API")
public class AutobiographyController {

    private final AutobiographyService autobiographyService;

    @Operation(summary = "Generate autobiography", description = "Loads selected episodes from Spring Boot and proxies the generation request to the AI service.")
    @PostMapping
    public AutobiographyResponse generate(@RequestBody AutobiographyGenerateRequest request) {
        return autobiographyService.generate(request);
    }
}
