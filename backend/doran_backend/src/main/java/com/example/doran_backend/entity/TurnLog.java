package com.example.doran_backend.entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Table(
        name = "turn_log",
        uniqueConstraints = {
                @UniqueConstraint(name = "uq_turn_log_session_request", columnNames = {"session_id", "request_id"})
        },
        indexes = {
                @Index(name = "idx_turn_log_session_ts", columnList = "session_id, ts"),
                @Index(name = "idx_turn_log_user_id", columnList = "user_id")
        }
)
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor
@Builder
public class TurnLog {

    @Id
    @Column(name = "turn_id", length = 36, nullable = false)
    private String turnId; // uuid

    @Column(name = "session_id", length = 36, nullable = false)
    private String sessionId; // uuid

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Column(name = "request_id", length = 36, nullable = false)
    private String requestId; // uuid (idempotency 키)

    @Column(name = "ts", nullable = false)
    private LocalDateTime ts; // ISO8601 -> 서버에서는 LocalDateTime로 받는 형태

    @Column(name = "input_mode", length = 20, nullable = false)
    private String inputMode; // TEXT (v1 고정이지만 계약상 필드 유지)

    @Column(name = "user_text", columnDefinition = "TEXT", nullable = false)
    private String userText;

    @Column(name = "reply", columnDefinition = "TEXT", nullable = false)
    private String reply;

    @Column(name = "question", columnDefinition = "TEXT", nullable = false)
    private String question;

    @Column(name = "raw_model_output", columnDefinition = "TEXT")
    private String rawModelOutput;

    @Column(name = "prompt_version", length = 50, nullable = false)
    private String promptVersion; // "interview_v1"

    @Column(name = "model", length = 50, nullable = false)
    private String model; // "dummy" or "gemini"

    @Column(name = "latency_ms", nullable = false)
    private Long latencyMs;
}
