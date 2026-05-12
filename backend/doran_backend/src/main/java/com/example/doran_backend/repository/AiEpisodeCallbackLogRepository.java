package com.example.doran_backend.repository;

import com.example.doran_backend.entity.AiEpisodeCallbackLog;
import org.springframework.data.jpa.repository.JpaRepository;

public interface AiEpisodeCallbackLogRepository extends JpaRepository<AiEpisodeCallbackLog, String> {
}
