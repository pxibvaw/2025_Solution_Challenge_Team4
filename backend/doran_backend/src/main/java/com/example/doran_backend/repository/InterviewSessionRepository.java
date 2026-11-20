package com.example.doran_backend.repository;

import com.example.doran_backend.entity.InterviewSession;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface InterviewSessionRepository extends JpaRepository<InterviewSession, String> {

    Optional<InterviewSession> findTopByUserIdAndStatusOrderByStartedAtDesc(Long userId, String status);
}
