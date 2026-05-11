package com.example.doran_backend.entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "interview_session")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor(access = AccessLevel.PRIVATE)
@Builder
public class InterviewSession {

    @Id
    @Column(name = "session_id", length = 36, nullable = false)
    private String sessionId; // UUID string

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Column(name = "started_at", nullable = false)
    private LocalDateTime startedAt;

    @Column(name = "ended_at")
    private LocalDateTime endedAt;

    @Column(name = "end_reason", length = 30)
    private String endReason; // 예: USER_EXIT

    @Column(name = "status", length = 10, nullable = false)
    private String status; // ACTIVE / ENDED -> enum 고려해보기 알아나 보기

    /** start 시점 생성용 */
    public static InterviewSession start(Long userId, LocalDateTime clientTs) {
        return InterviewSession.builder()
                .sessionId(UUID.randomUUID().toString())
                .userId(userId)
                .startedAt(clientTs != null ? clientTs : LocalDateTime.now())
                .status("ACTIVE")
                .build();
    }

    /** end 처리 */
    public void end(String endReason) {
        this.status = "ENDED";
        this.endReason = endReason;
        this.endedAt = LocalDateTime.now();
    }
}