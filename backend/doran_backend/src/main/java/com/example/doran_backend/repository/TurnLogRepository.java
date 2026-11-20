package com.example.doran_backend.repository;

import com.example.doran_backend.entity.TurnLog;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface TurnLogRepository extends JpaRepository<TurnLog, String> {

    //멱등성 체크용 (이미 존재하는 turn인지 확인)
    Optional<TurnLog> findBySessionIdAndRequestId(String sessionId, String requestId);

    // 로그 페이지용 (특정 세션의 turn들을 시간순으로 조회)
    List<TurnLog> findBySessionIdOrderByTsAsc(String sessionId);

    long countByUserId(Long userId);
}
