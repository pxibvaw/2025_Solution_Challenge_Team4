package com.example.doran_backend.repository;

import com.example.doran_backend.entity.Essay;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface EssayRepository extends JpaRepository<Essay, String> {

    Optional<Essay> findBySessionId(String sessionId);

    List<Essay> findTop5ByUserIdOrderByCreatedAtDesc(Long userId);

    List<Essay> findByUserIdOrderByCreatedAtDesc(Long userId);

    List<Essay> findByUserIdAndRepresentativeYearOrderByCreatedAtDesc(Long userId, Integer representativeYear);

    List<Essay> findByUserIdAndTitleContainingIgnoreCaseOrUserIdAndContentContainingIgnoreCaseOrderByCreatedAtDesc(
            Long titleUserId,
            String titleKeyword,
            Long contentUserId,
            String contentKeyword
    );

    long countByUserId(Long userId);
}
