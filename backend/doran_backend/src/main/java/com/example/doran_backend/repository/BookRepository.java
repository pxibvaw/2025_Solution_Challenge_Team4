package com.example.doran_backend.repository;

import com.example.doran_backend.entity.Book;
import org.springframework.data.jpa.repository.JpaRepository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

public interface BookRepository extends JpaRepository<Book, String> {
    List<Book> findByUserIdOrderByCreatedAtDesc(String userId);

    List<Book> findByUserIdAndCreatedAtGreaterThanEqualAndCreatedAtLessThanOrderByCreatedAtDesc(
            String userId,
            LocalDateTime start,
            LocalDateTime end
    );

    Optional<Book> findByIdAndUserId(String id, String userId);
}
