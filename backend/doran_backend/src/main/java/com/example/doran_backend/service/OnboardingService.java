package com.example.doran_backend.service;

import com.example.doran_backend.dto.OnboardingRequest;
import com.example.doran_backend.dto.OnboardingResponse;
import com.example.doran_backend.dto.ProfileResponse;
import com.example.doran_backend.dto.UserProfileContext;
import com.example.doran_backend.entity.UserProfile;
import com.example.doran_backend.repository.UserProfileRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class OnboardingService {

    private final UserProfileRepository userProfileRepository;

    @Transactional
    public OnboardingResponse saveOnboarding(Long userId, OnboardingRequest request) {
        // 1) 검증 (최소룰)
        validate(request);

        // 2) 기존 유저 프로필 있으면 업데이트, 없으면 생성
        UserProfile profile = userProfileRepository.findById(userId)
                .orElseGet(() -> UserProfile.builder().userId(userId).build());
        LocalDateTime completedAt = LocalDateTime.now();

        // 3) 값 세팅 (엔티티에 setter 없으면 "엔티티에 update 메서드"로 바꾸는게 정석)
        // 지금은 빠르게 가려고 reflection/Setter 없이 "새 객체로 다시 build" 방식 사용
        UserProfile newProfile = UserProfile.builder()
                .userId(userId)
                .userTitle(trim(request.getUserTitle()))
                .ageGroup(request.getAgeGroup())
                .speechLevel(request.getSpeechLevel() == null ? "HONORIFIC" : request.getSpeechLevel())
                .hasChildren(request.getHasChildren())
                .happiestMoment(request.getHappiestMoment())
                .coreValues(joinCoreValues(request.getCoreValues()))
                .extraValue(trim(request.getExtraValue()))
                .onboardingCompleted(true)
                .completedAt(completedAt)
                .guideCompleted(Boolean.TRUE.equals(profile.getGuideCompleted()))
                .build();

        userProfileRepository.save(newProfile);
        return new OnboardingResponse(userId, true, completedAt);
    }

    @Transactional(readOnly = true)
    public ProfileResponse getProfile(Long userId) {
        UserProfile p = userProfileRepository.findById(userId)
                .orElseThrow(() -> new IllegalArgumentException("사용자 프로필을 찾을 수 없습니다. userId=" + userId));
        return new ProfileResponse(
                p.getUserId(),
                p.getUserTitle(),
                p.getAgeGroup(),
                p.getSpeechLevel(),
                p.getHasChildren(),
                p.getHappiestMoment(),
                splitCoreValues(p.getCoreValues()),
                p.getExtraValue(),
                p.getOnboardingCompleted(),
                p.getGuideCompleted()
        );
    }

    @Transactional(readOnly = true)
    public UserProfileContext getUserProfileContext(Long userId) {
        UserProfile p = userProfileRepository.findById(userId)
                .orElseThrow(() -> new IllegalArgumentException("사용자 프로필을 찾을 수 없습니다. userId=" + userId));
        return toContext(p);
    }

    @Transactional
    public Boolean completeGuide(Long userId) {
        UserProfile p = userProfileRepository.findById(userId)
                .orElseThrow(() -> new IllegalArgumentException("사용자 프로필을 찾을 수 없습니다. userId=" + userId));

        UserProfile updated = UserProfile.builder()
                .userId(p.getUserId())
                .userTitle(p.getUserTitle())
                .ageGroup(p.getAgeGroup())
                .speechLevel(p.getSpeechLevel())
                .hasChildren(p.getHasChildren())
                .happiestMoment(p.getHappiestMoment())
                .coreValues(p.getCoreValues())
                .extraValue(p.getExtraValue())
                .onboardingCompleted(p.getOnboardingCompleted())
                .completedAt(p.getCompletedAt())
                .guideCompleted(true)
                .build();

        userProfileRepository.save(updated);
        return true;
    }

    // ----------------- validation -----------------

    private void validate(OnboardingRequest r) {
        String title = trim(r.getUserTitle());
        if (title == null || title.isEmpty() || title.length() > 10) {
            throw new IllegalArgumentException("호칭(userTitle)은 1~10자로 입력해주세요.");
        }

        if (r.getAgeGroup() == null || trim(r.getAgeGroup()).isEmpty()) {
            throw new IllegalArgumentException("연령대(ageGroup)를 선택해주세요.");
        }

        if (r.getHasChildren() == null) {
            throw new IllegalArgumentException("자녀 여부(hasChildren)를 선택해주세요.");
        }

        boolean hasCoreValues = r.getCoreValues() != null && !r.getCoreValues().isEmpty();
        boolean hasExtraValue = trim(r.getExtraValue()) != null && !trim(r.getExtraValue()).isEmpty();
        if (!hasCoreValues && !hasExtraValue) {
            throw new IllegalArgumentException("핵심가치(coreValues) 또는 기타 가치(extraValue) 중 하나는 반드시 입력해야 합니다.");
        }

        String extra = trim(r.getExtraValue());
        if (extra != null && extra.length() > 7) {
            throw new IllegalArgumentException("기타 가치(extraValue)는 최대 7자까지 입력할 수 있어요.");
        }
    }

    private String trim(String s) {
        if (s == null) return null;
        String t = s.trim();
        return t.isEmpty() ? null : t;
    }

    // DB에는 1:1 컬럼 원칙이라 coreValues를 문자열로 저장한다고 가정 (예: "가족,건강")
    private String joinCoreValues(List<String> coreValues) {
        if (coreValues == null || coreValues.isEmpty()) return null;
        return coreValues.stream()
                .map(this::trim)
                .filter(v -> v != null && !v.isEmpty())
                .collect(Collectors.joining(","));
    }

    private List<String> splitCoreValues(String coreValues) {
        if (coreValues == null || coreValues.trim().isEmpty()) return List.of();
        return Arrays.stream(coreValues.split(","))
                .map(String::trim)
                .filter(s -> !s.isEmpty())
                .collect(Collectors.toList());
    }

    private UserProfileContext toContext(UserProfile p) {
        return new UserProfileContext(
                valueOrDefault(p.getUserTitle(), "사용자"),
                valueOrDefault(p.getAgeGroup(), "UNKNOWN"),
                p.getHasChildren(),
                p.getHappiestMoment(),
                valueOrDefault(p.getSpeechLevel(), "HONORIFIC"),
                new UserProfileContext.Defaults("warm", "one_open_ended_question", true)
        );
    }

    private String valueOrDefault(String value, String defaultValue) {
        String trimmed = trim(value);
        return trimmed == null ? defaultValue : trimmed;
    }
}
