package com.example.doran_backend.service;

import com.example.doran_backend.dto.BookCreateRequest;
import com.example.doran_backend.dto.BookPageResponse;
import com.example.doran_backend.dto.BookResponse;
import com.example.doran_backend.entity.Book;
import com.example.doran_backend.entity.BookPage;
import com.example.doran_backend.repository.BookPageRepository;
import com.example.doran_backend.repository.BookRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.YearMonth;
import java.util.Comparator;
import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class BookService {

    private final BookRepository bookRepository;
    private final BookPageRepository bookPageRepository;

    @Transactional
    public BookResponse create(BookCreateRequest request) {
        requireNonNull(request, "요청 본문은 필수입니다.");
        String userId = requireText(request.getUserId(), "userId는 필수입니다.");
        String title = valueOrDefault(request.getTitle(), "나의 이야기");
        List<BookCreateRequest.BookPageRequest> pageRequests = requirePages(request.getPages());
        LocalDateTime now = LocalDateTime.now();
        String bookId = UUID.randomUUID().toString();

        Book book = Book.builder()
                .id(bookId)
                .userId(userId)
                .title(title)
                .coverGradient(request.getCoverGradient())
                .prologue(blankToNull(request.getPrologue()))
                .epilogue(blankToNull(request.getEpilogue()))
                .lifeTheme(blankToNull(request.getLifeTheme()))
                .generationError(blankToNull(request.getGenerationError()))
                .createdAt(now)
                .updatedAt(now)
                .build();
        bookRepository.save(book);

        List<BookCreateRequest.BookPageRequest> sortedPageRequests = pageRequests.stream()
                .sorted(Comparator.comparing(page -> page.getPageNumber() == null ? Integer.MAX_VALUE : page.getPageNumber()))
                .toList();
        List<BookPage> pages = new java.util.ArrayList<>();
        for (int i = 0; i < sortedPageRequests.size(); i++) {
            pages.add(toPage(bookId, sortedPageRequests.get(i), i + 1));
        }
        bookPageRepository.saveAll(pages);

        return toResponse(book, pages, true);
    }

    @Transactional(readOnly = true)
    public List<BookResponse> list(String userId, String month) {
        String normalizedUserId = requireText(userId, "userId는 필수입니다.");
        List<Book> books;

        if (month == null || month.trim().isEmpty()) {
            books = bookRepository.findByUserIdOrderByCreatedAtDesc(normalizedUserId);
        } else {
            YearMonth yearMonth = YearMonth.parse(month.trim());
            LocalDate startDate = yearMonth.atDay(1);
            LocalDateTime start = startDate.atStartOfDay();
            LocalDateTime end = yearMonth.plusMonths(1).atDay(1).atStartOfDay();
            books = bookRepository.findByUserIdAndCreatedAtGreaterThanEqualAndCreatedAtLessThanOrderByCreatedAtDesc(
                    normalizedUserId,
                    start,
                    end
            );
        }

        return books.stream()
                .map(book -> {
                    List<BookPage> pages = bookPageRepository.findByBookIdOrderByPageNumberAsc(book.getId());
                    return toResponse(book, pages, false);
                })
                .toList();
    }

    @Transactional(readOnly = true)
    public BookResponse get(String bookId, String userId) {
        String normalizedBookId = requireText(bookId, "bookId는 필수입니다.");
        String normalizedUserId = requireText(userId, "userId는 필수입니다.");
        Book book = bookRepository.findByIdAndUserId(normalizedBookId, normalizedUserId)
                .orElseThrow(() -> new IllegalArgumentException("책을 찾을 수 없습니다."));
        List<BookPage> pages = bookPageRepository.findByBookIdOrderByPageNumberAsc(book.getId());
        return toResponse(book, pages, true);
    }

    @Transactional(readOnly = true)
    public List<BookPageResponse> getPages(String bookId, String userId) {
        return get(bookId, userId).getPages();
    }

    @Transactional
    public void delete(String bookId, String userId) {
        String normalizedBookId = requireText(bookId, "bookId는 필수입니다.");
        String normalizedUserId = requireText(userId, "userId는 필수입니다.");
        Book book = bookRepository.findByIdAndUserId(normalizedBookId, normalizedUserId)
                .orElseThrow(() -> new IllegalArgumentException("책을 찾을 수 없습니다."));
        bookPageRepository.deleteByBookId(book.getId());
        bookRepository.delete(book);
    }

    private BookPage toPage(String bookId, BookCreateRequest.BookPageRequest request, int fallbackPageNumber) {
        String chapter = valueOrDefault(request.getChapter(), "제목 없는 장");
        String content = requireText(request.getContent(), "page content는 필수입니다.");
        Integer pageNumber = request.getPageNumber() == null || request.getPageNumber() < 1
                ? fallbackPageNumber
                : request.getPageNumber();

        return BookPage.builder()
                .id(UUID.randomUUID().toString())
                .bookId(bookId)
                .episodeId(blankToNull(request.getEpisodeId()))
                .chapter(chapter)
                .content(content)
                .pageNumber(pageNumber)
                .build();
    }

    private BookResponse toResponse(Book book, List<BookPage> pages, boolean includePages) {
        List<BookPageResponse> pageResponses = pages.stream()
                .sorted(Comparator.comparing(BookPage::getPageNumber))
                .map(this::toPageResponse)
                .toList();

        return new BookResponse(
                book.getId(),
                book.getUserId(),
                book.getTitle(),
                book.getCoverGradient(),
                book.getPrologue(),
                book.getEpilogue(),
                book.getLifeTheme(),
                book.getGenerationError(),
                book.getCreatedAt(),
                book.getUpdatedAt(),
                pageResponses.size(),
                includePages ? pageResponses : null
        );
    }

    private BookPageResponse toPageResponse(BookPage page) {
        return new BookPageResponse(
                page.getId(),
                page.getBookId(),
                page.getEpisodeId(),
                page.getChapter(),
                page.getContent(),
                page.getPageNumber()
        );
    }

    private List<BookCreateRequest.BookPageRequest> requirePages(List<BookCreateRequest.BookPageRequest> pages) {
        if (pages == null || pages.isEmpty()) {
            throw new IllegalArgumentException("pages는 최소 1개 이상 필요합니다.");
        }
        return pages;
    }

    private String valueOrDefault(String value, String defaultValue) {
        if (value == null || value.trim().isEmpty()) {
            return defaultValue;
        }
        return value.trim();
    }

    private String requireText(String value, String message) {
        if (value == null || value.trim().isEmpty()) {
            throw new IllegalArgumentException(message);
        }
        return value.trim();
    }

    private String blankToNull(String value) {
        if (value == null || value.trim().isEmpty()) {
            return null;
        }
        return value.trim();
    }

    private void requireNonNull(Object value, String message) {
        if (value == null) {
            throw new IllegalArgumentException(message);
        }
    }
}
