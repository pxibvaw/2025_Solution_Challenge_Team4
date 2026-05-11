package com.example.doran_backend.repository;

import com.example.doran_backend.entity.EssayComment;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface EssayCommentRepository extends JpaRepository<EssayComment, String> {

    List<EssayComment> findByEssayIdOrderByCreatedAtAsc(String essayId);

    List<EssayComment> findTop5ByUserIdOrderByCreatedAtDesc(Long userId);

    long countByUserId(Long userId);
}
