package com.example.doran_backend.service;

import com.example.doran_backend.dto.*;
import com.example.doran_backend.entity.EssayComment;
import com.example.doran_backend.repository.*;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class HomeService {

    private final OnboardingService onboardingService;
    private final InterviewSessionRepository interviewSessionRepository;
    private final TurnLogRepository turnLogRepository;
    private final EssayRepository essayRepository;
    private final EssayCommentRepository essayCommentRepository;

    @Transactional(readOnly = true)
    public HomeResponse getHome(Long userId) {
        if (userId == null) {
            throw new IllegalArgumentException("userId는 필수입니다.");
        }

        ProfileResponse profile = onboardingService.getProfile(userId);
        String activeSessionId = interviewSessionRepository
                .findTopByUserIdAndStatusOrderByStartedAtDesc(userId, "ACTIVE")
                .map(session -> session.getSessionId())
                .orElse(null);

        List<EssaySummaryResponse> recentEssays = essayRepository.findTop5ByUserIdOrderByCreatedAtDesc(userId)
                .stream()
                .map(essay -> new EssaySummaryResponse(
                        essay.getEssayId(),
                        essay.getTitle(),
                        essay.getSummary(),
                        essay.getRepresentativeYear(),
                        essay.getCategory(),
                        essay.getThumbnailUrl(),
                        essay.getCreatedAt()
                ))
                .toList();

        List<FamilyMessageResponse> familyMessages = essayCommentRepository.findTop5ByUserIdOrderByCreatedAtDesc(userId)
                .stream()
                .map(this::toFamilyMessage)
                .toList();

        return new HomeResponse(
                profile,
                activeSessionId,
                new HomeResponse.TodayQuestion("오늘의 질문", "요즘 가장 자주 떠오르는 기억은 무엇인가요?"),
                new HomeResponse.Stats(
                        turnLogRepository.countByUserId(userId),
                        essayRepository.countByUserId(userId),
                        essayCommentRepository.countByUserId(userId)
                ),
                recentEssays,
                familyMessages
        );
    }

    private FamilyMessageResponse toFamilyMessage(EssayComment comment) {
        String essayTitle = essayRepository.findById(comment.getEssayId())
                .map(essay -> essay.getTitle())
                .orElse("기억 기록");
        return new FamilyMessageResponse(
                comment.getEssayId(),
                essayTitle,
                comment.getAuthorName(),
                comment.getContent(),
                comment.getCreatedAt()
        );
    }
}
