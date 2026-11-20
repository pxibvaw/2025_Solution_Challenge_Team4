package com.example.doran_backend.repository;

import com.example.doran_backend.entity.Episode;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface EpisodeRepository extends JpaRepository<Episode, String> {

    List<Episode> findByUserIdOrderByCreatedAtAsc(String userId);

    List<Episode> findByUserIdAndIdIn(String userId, List<String> ids);
}
