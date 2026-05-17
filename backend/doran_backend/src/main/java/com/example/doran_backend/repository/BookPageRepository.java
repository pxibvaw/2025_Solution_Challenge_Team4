package com.example.doran_backend.repository;

import com.example.doran_backend.entity.BookPage;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface BookPageRepository extends JpaRepository<BookPage, String> {
    List<BookPage> findByBookIdOrderByPageNumberAsc(String bookId);

    void deleteByBookId(String bookId);
}
