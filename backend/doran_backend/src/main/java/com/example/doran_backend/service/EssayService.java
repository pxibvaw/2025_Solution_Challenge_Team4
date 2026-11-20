package com.example.doran_backend.service;

import com.example.doran_backend.dto.*;
import com.example.doran_backend.ai.EssayAiClient;
import com.example.doran_backend.ai.EssayAiRequest;
import com.example.doran_backend.ai.EssayAiResult;
import com.example.doran_backend.entity.Essay;
import com.example.doran_backend.entity.EssayComment;
import com.example.doran_backend.entity.ShareLink;
import com.example.doran_backend.entity.TurnLog;
import com.example.doran_backend.repository.EssayCommentRepository;
import com.example.doran_backend.repository.EssayRepository;
import com.example.doran_backend.repository.ShareLinkRepository;
import com.example.doran_backend.repository.TurnLogRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class EssayService {

    private final EssayRepository essayRepository;
    private final EssayCommentRepository essayCommentRepository;
    private final ShareLinkRepository shareLinkRepository;
    private final TurnLogRepository turnLogRepository;
    private final EssayAiClient essayAiClient;

    @Transactional
    public EssayResponse generateEssay(EssayGenerateRequest request) {
        requireNonNull(request, "요청 본문은 필수입니다.");
        requireNonNull(request.getUserId(), "userId는 필수입니다.");
        validateUuid(request.getSessionId(), "sessionId");

        List<TurnLog> logs = turnLogRepository.findBySessionIdOrderByTsAsc(request.getSessionId());
        if (logs.isEmpty()) {
            throw new IllegalArgumentException("수필을 생성할 인터뷰 로그가 없습니다.");
        }
        if (!logs.get(0).getUserId().equals(request.getUserId())) {
            throw new IllegalArgumentException("수필 생성 권한이 없습니다.");
        }

        Essay existing = essayRepository.findBySessionId(request.getSessionId()).orElse(null);
        EssayAiResult aiResult = essayAiClient.generateEssay(
                logs,
                new EssayAiRequest(request.getTitle(), request.getRepresentativeYear(), request.getCategory())
        );
        String title = valueOrDefault(aiResult.getTitle(), "오늘의 기억");
        String content = requireText(aiResult.getContent(), "수필 본문 생성 결과가 비어있습니다.");
        String summary = valueOrDefault(aiResult.getSummary(), content.length() > 80 ? content.substring(0, 80) + "..." : content);
        Integer year = request.getRepresentativeYear();
        String category = valueOrDefault(request.getCategory(), "기억");

        if (existing != null) {
            existing.updateContent(title, content, summary, year, category);
            return toResponse(essayRepository.save(existing));
        }

        LocalDateTime now = LocalDateTime.now();
        Essay essay = Essay.builder()
                .essayId(UUID.randomUUID().toString())
                .userId(request.getUserId())
                .sessionId(request.getSessionId())
                .title(title)
                .content(content)
                .summary(summary)
                .representativeYear(year)
                .category(category)
                .imagePrompt(aiResult.getImagePrompt())
                .emotionLabel(aiResult.getEmotionLabel())
                .emotionScore(aiResult.getEmotionScore())
                .createdAt(now)
                .updatedAt(now)
                .build();

        return toResponse(essayRepository.save(essay));
    }

    @Transactional(readOnly = true)
    public EssayResponse getEssay(String essayId) {
        return toResponse(findEssay(essayId));
    }

    @Transactional(readOnly = true)
    public List<EssaySummaryResponse> getLibrary(Long userId, Integer year, String query) {
        requireNonNull(userId, "userId는 필수입니다.");

        String keyword = trim(query);
        if (keyword != null) {
            return essayRepository
                    .findByUserIdAndTitleContainingIgnoreCaseOrUserIdAndContentContainingIgnoreCaseOrderByCreatedAtDesc(
                            userId, keyword, userId, keyword
                    )
                    .stream()
                    .map(this::toSummary)
                    .toList();
        }

        if (year != null) {
            return essayRepository.findByUserIdAndRepresentativeYearOrderByCreatedAtDesc(userId, year)
                    .stream()
                    .map(this::toSummary)
                    .toList();
        }

        return essayRepository.findByUserIdOrderByCreatedAtDesc(userId)
                .stream()
                .map(this::toSummary)
                .toList();
    }

    @Transactional
    public CommentResponse addComment(String essayId, CommentCreateRequest request) {
        Essay essay = findEssay(essayId);
        requireNonNull(request, "요청 본문은 필수입니다.");
        String authorName = trim(request.getAuthorName());
        String content = trim(request.getContent());
        if (authorName == null) {
            throw new IllegalArgumentException("authorName은 필수입니다.");
        }
        if (content == null) {
            throw new IllegalArgumentException("content는 필수입니다.");
        }

        EssayComment comment = EssayComment.builder()
                .commentId(UUID.randomUUID().toString())
                .essayId(essay.getEssayId())
                .userId(essay.getUserId())
                .authorName(authorName)
                .content(content)
                .createdAt(LocalDateTime.now())
                .build();

        return toCommentResponse(essayCommentRepository.save(comment));
    }

    @Transactional(readOnly = true)
    public List<CommentResponse> getComments(String essayId) {
        findEssay(essayId);
        return essayCommentRepository.findByEssayIdOrderByCreatedAtAsc(essayId)
                .stream()
                .map(this::toCommentResponse)
                .toList();
    }

    @Transactional
    public ShareLinkResponse createShareLink(String essayId, Long userId) {
        Essay essay = findEssay(essayId);
        if (!essay.getUserId().equals(userId)) {
            throw new IllegalArgumentException("공유 링크 생성 권한이 없습니다.");
        }

        String token = UUID.randomUUID().toString().replace("-", "");
        ShareLink link = ShareLink.builder()
                .shareId(UUID.randomUUID().toString())
                .essayId(essayId)
                .userId(userId)
                .token(token)
                .createdAt(LocalDateTime.now())
                .expiresAt(LocalDateTime.now().plusDays(30))
                .build();

        ShareLink saved = shareLinkRepository.save(link);
        return new ShareLinkResponse(
                saved.getShareId(),
                saved.getEssayId(),
                saved.getToken(),
                "/share/" + saved.getToken(),
                saved.getExpiresAt()
        );
    }

    private Essay findEssay(String essayId) {
        validateUuid(essayId, "essayId");
        return essayRepository.findById(essayId)
                .orElseThrow(() -> new IllegalArgumentException("수필을 찾을 수 없습니다. essayId=" + essayId));
    }

    private EssayResponse toResponse(Essay essay) {
        return new EssayResponse(
                essay.getEssayId(),
                essay.getUserId(),
                essay.getSessionId(),
                essay.getTitle(),
                essay.getContent(),
                essay.getSummary(),
                essay.getRepresentativeYear(),
                essay.getCategory(),
                essay.getThumbnailUrl(),
                essay.getImagePrompt(),
                essay.getPdfUrl(),
                essay.getEmotionLabel(),
                essay.getEmotionScore(),
                essay.getCreatedAt(),
                essay.getUpdatedAt(),
                getCommentsWithoutEssayCheck(essay.getEssayId())
        );
    }

    private EssaySummaryResponse toSummary(Essay essay) {
        return new EssaySummaryResponse(
                essay.getEssayId(),
                essay.getTitle(),
                essay.getSummary(),
                essay.getRepresentativeYear(),
                essay.getCategory(),
                essay.getThumbnailUrl(),
                essay.getCreatedAt()
        );
    }

    private List<CommentResponse> getCommentsWithoutEssayCheck(String essayId) {
        return essayCommentRepository.findByEssayIdOrderByCreatedAtAsc(essayId)
                .stream()
                .map(this::toCommentResponse)
                .toList();
    }

    private CommentResponse toCommentResponse(EssayComment comment) {
        return new CommentResponse(
                comment.getCommentId(),
                comment.getEssayId(),
                comment.getUserId(),
                comment.getAuthorName(),
                comment.getContent(),
                comment.getCreatedAt()
        );
    }

    private String valueOrDefault(String value, String defaultValue) {
        String trimmed = trim(value);
        return trimmed == null ? defaultValue : trimmed;
    }

    private String requireText(String value, String message) {
        String trimmed = trim(value);
        if (trimmed == null) {
            throw new IllegalArgumentException(message);
        }
        return trimmed;
    }

    private String trim(String value) {
        if (value == null) return null;
        String trimmed = value.trim();
        return trimmed.isEmpty() ? null : trimmed;
    }

    private void validateUuid(String value, String fieldName) {
        String trimmed = trim(value);
        if (trimmed == null) {
            throw new IllegalArgumentException(fieldName + "는 필수입니다.");
        }
        try {
            UUID.fromString(trimmed);
        } catch (IllegalArgumentException e) {
            throw new IllegalArgumentException(fieldName + "는 UUID 형식이어야 합니다.");
        }
    }

    private void requireNonNull(Object value, String message) {
        if (value == null) {
            throw new IllegalArgumentException(message);
        }
    }
}
