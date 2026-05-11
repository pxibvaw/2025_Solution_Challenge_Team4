package com.example.doran_backend.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.servers.Server;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.List;

@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI doranOpenApi() {
        return new OpenAPI()
                .info(new Info()
                        .title("Doran Memory Mate API")
                        .description("Spring Boot backend API for onboarding, interview, essays, library, comments, and sharing.")
                        .version("v1"))
                .servers(List.of(new Server()
                        .url("http://localhost:8080")
                        .description("Local development server")));
    }
}
