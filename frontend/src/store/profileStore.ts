// src/store/profileStore.ts

export type SpeechLevel = "HONORIFIC" | "CASUAL";
export type AgeGroup =
  | "TEENS"
  | "TWENTIES"
  | "THIRTIES"
  | "FORTIES"
  | "FIFTIES"
  | "SIXTIES"
  | "SENIOR_70S"; // 필요하면 확장

export type TopicValue = "FAMILY" | "LOVE" | "HEALTH" | "VALUES" | "CUSTOM";

export type Tone = "warm" | "neutral";
export type QuestionRule = "one_open_ended_question";

export interface UserProfileContext {
  userTitle?: string; // 호칭 (필수로 쓰는 게 목표지만 optional 허용)
  ageGroup?: AgeGroup;
  hasChildren?: boolean; // MVP에서는 온보딩에 없으면 undefined로 둠
  happiestMoment?: string; // MVP에서는 온보딩에 없으면 undefined
  speechLevel?: SpeechLevel;
  defaults?: {
    tone: Tone;
    questionRule: QuestionRule;
    noFabrication: true;
  };
  topic?: string; // "FAMILY" 등 코드 또는 "CUSTOM" 직접입력 텍스트(7자 제한 반영)
}

// --- localStorage keys ---
export const LS_KEYS = {
  onboarded: "onboarded",
  profile: "user_profile_context_v1_1",
  onboardingDraft: "onboarding_draft_v1", // 온보딩 중 이탈 시
} as const;

// --- defaults (PDF 규칙) ---
export const DEFAULT_PROFILE: Required<Pick<UserProfileContext, "defaults">> = {
  defaults: {
    tone: "warm",
    questionRule: "one_open_ended_question",
    noFabrication: true,
  },
};

export function loadProfile(): UserProfileContext | null {
  try {
    const raw = localStorage.getItem(LS_KEYS.profile);
    if (!raw) return null;
    return JSON.parse(raw) as UserProfileContext;
  } catch {
    return null;
  }
}

export function saveProfile(profile: UserProfileContext) {
  const merged: UserProfileContext = {
    ...DEFAULT_PROFILE,
    ...profile,
    defaults: {
      ...DEFAULT_PROFILE.defaults,
      ...(profile.defaults ?? {}),
      noFabrication: true,
    },
  };

  localStorage.setItem(LS_KEYS.profile, JSON.stringify(merged));
}

export function clearProfile() {
  localStorage.removeItem(LS_KEYS.profile);
  localStorage.removeItem(LS_KEYS.onboardingDraft);
  localStorage.removeItem(LS_KEYS.onboarded);
}

// 온보딩 “중간 저장” (이탈/재진입)
export interface OnboardingDraft {
  step: number;
  profile: UserProfileContext;
  updatedAt: number;
}

export function loadOnboardingDraft(): OnboardingDraft | null {
  try {
    const raw = localStorage.getItem(LS_KEYS.onboardingDraft);
    if (!raw) return null;
    return JSON.parse(raw) as OnboardingDraft;
  } catch {
    return null;
  }
}

export function saveOnboardingDraft(draft: OnboardingDraft) {
  localStorage.setItem(LS_KEYS.onboardingDraft, JSON.stringify(draft));
}

export function clearOnboardingDraft() {
  localStorage.removeItem(LS_KEYS.onboardingDraft);
}

export function isOnboarded(): boolean {
  return localStorage.getItem(LS_KEYS.onboarded) === "true";
}

export function setOnboardedTrue() {
  localStorage.setItem(LS_KEYS.onboarded, "true");
}