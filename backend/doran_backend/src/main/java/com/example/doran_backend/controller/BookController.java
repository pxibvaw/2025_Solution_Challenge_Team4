package com.example.doran_backend.controller;

import com.example.doran_backend.dto.BookCreateRequest;
import com.example.doran_backend.dto.BookPageResponse;
import com.example.doran_backend.dto.BookResponse;
import com.example.doran_backend.service.BookService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/books")
@Tag(name = "Books", description = "Generated autobiography book library API")
public class BookController {

    private final BookService bookService;

    @Operation(summary = "Save generated book")
    @PostMapping
    public BookResponse create(@RequestBody BookCreateRequest request) {
        return bookService.create(request);
    }

    @Operation(summary = "List generated books")
    @GetMapping
    public List<BookResponse> list(
            @RequestParam String userId,
            @RequestParam(required = false) String month
    ) {
        return bookService.list(userId, month);
    }

    @Operation(summary = "Get generated book detail")
    @GetMapping("/{bookId}")
    public BookResponse get(@PathVariable String bookId, @RequestParam String userId) {
        return bookService.get(bookId, userId);
    }

    @Operation(summary = "Get generated book pages")
    @GetMapping("/{bookId}/pages")
    public List<BookPageResponse> pages(@PathVariable String bookId, @RequestParam String userId) {
        return bookService.getPages(bookId, userId);
    }

    @Operation(summary = "Delete generated book")
    @DeleteMapping("/{bookId}")
    public Map<String, Object> delete(@PathVariable String bookId, @RequestParam String userId) {
        bookService.delete(bookId, userId);
        return Map.of("deleted", true, "bookId", bookId);
    }
}
