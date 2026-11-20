package com.example.doran_backend.entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "user_profile")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor
@Builder
public class UserProfile {

    @Id
    @Column(name = "user_id")
    private Long userId;

    @Column(name = "user_title", nullable = false, length = 10)
    private String userTitle;

    @Column(name = "age_group", nullable = false, length = 30)
    private String ageGroup; // MVP: String으로 저장 (나중에 Enum으로 바꿔도 됨)

    @Column(name = "speech_level", nullable = false, length = 20)
    private String speechLevel; // HONORIFIC / CASUAL

    @Column(name = "has_children", nullable = false)
    private Boolean hasChildren;

    @Column(name = "happiest_moment", length = 200)
    private String happiestMoment;

    @Column(name = "onboarding_completed", nullable = false)
    private Boolean onboardingCompleted;

    @Column(name = "completed_at")
    private LocalDateTime completedAt;

    @Column(name = "core_values", length = 200)
    private String coreValues;

    @Column(name = "extra_value", length = 7)
    private String extraValue;

    @Column(name = "guide_completed", nullable = false)
    @Builder.Default
    private Boolean guideCompleted = false;

    // 필요하면 나중에 setter 대신 update 메서드로 변경
    public void completeOnboarding() {
        this.onboardingCompleted = true;
        this.completedAt = LocalDateTime.now();
    }

    public void completeGuide() {
        this.guideCompleted = true;
    }
}
