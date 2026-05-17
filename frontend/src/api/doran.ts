import type { UserProfileContext } from "../store/profileStore";

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8080";

export const DEFAULT_USER_ID = Number(
  import.meta.env.VITE_USER_ID ?? 1
);

export type ApiEpisode = {
  id: string;
  title: string;
  narrative?: string;
  quote?: string;
  theme?: string;
  emotion_tone?: string;
  life_value?: string;
  created_at?: string;
};

export type UiEpisode = {
  id: string;
  title: string;
  preview: string;
  content: string;
  createdAt: string;
};

export type AutobiographyResponse = {
  prologue?: string;
  chapters?: {
    title?: string;
    period_label?: string;
    narrative?: string;
    episode_ids?: string[];
  }[];
  epilogue?: string;
  life_theme?: string;
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    ...init,
  });

  if (!response.ok) {
    let message = `API 요청 실패 (${response.status})`;
    try {
      const body = await response.json();
      message = body.message ?? body.error?.message ?? body.code ?? message;
    } catch {
      // keep default message
    }
    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

function topicToCoreValues(topic?: string) {
  const topicMap: Record<string, string> = {
    FAMILY: "가족",
    LOVE: "사랑",
    HEALTH: "건강",
    VALUES: "가치관",
  };

  if (!topic) return ["가족"];
  return topicMap[topic] ? [topicMap[topic]] : [];
}

export function toUiEpisode(episode: ApiEpisode): UiEpisode {
  const content = episode.narrative?.trim() || episode.quote?.trim() || "";

  return {
    id: episode.id,
    title: episode.title || "제목 없는 에피소드",
    preview: content ? `${content.slice(0, 80)}${content.length > 80 ? "..." : ""}` : "아직 본문이 없습니다.",
    content: content || "아직 본문이 없습니다.",
    createdAt: episode.created_at ?? new Date().toISOString(),
  };
}

export async function saveOnboardingToBackend(profile: UserProfileContext) {
  const coreValues = topicToCoreValues(profile.topic);
  const isCustomTopic = Boolean(profile.topic && coreValues.length === 0);

  return request(`/users/onboarding?userId=${DEFAULT_USER_ID}`, {
    method: "POST",
    body: JSON.stringify({
      userTitle: profile.userTitle?.trim() || "사용자",
      ageGroup: profile.ageGroup || "SIXTIES",
      speechLevel: profile.speechLevel || "HONORIFIC",
      hasChildren: profile.hasChildren ?? false,
      happiestMoment: profile.happiestMoment ?? "",
      coreValues: isCustomTopic ? [] : coreValues,
      extraValue: isCustomTopic ? profile.topic : "",
    }),
  });
}

export async function startInterviewSession() {
  return request<{ sessionId: string }>("/interview/start", {
    method: "POST",
    body: JSON.stringify({
      userId: DEFAULT_USER_ID,
      clientTs: new Date().toISOString(),
    }),
  });
}

export async function sendInterviewTurn(params: {
  sessionId: string;
  requestId: string;
  userText: string;
  profile?: UserProfileContext | null;
}) {
  return request<{
    sessionId: string;
    turnId: string;
    output: { reply: string; question: string };
    meta: { model: string; promptVersion: string; latencyMs: number };
  }>("/interview/turn", {
    method: "POST",
    body: JSON.stringify({
      sessionId: params.sessionId,
      userId: DEFAULT_USER_ID,
      requestId: params.requestId,
      input: {
        mode: "TEXT",
        userText: params.userText,
      },
      context: {
        speechLevel: params.profile?.speechLevel || "HONORIFIC",
        ageGroup: params.profile?.ageGroup || "SIXTIES",
        coreValues: topicToCoreValues(params.profile?.topic),
        extraValue: params.profile?.topic && topicToCoreValues(params.profile.topic).length === 0 ? params.profile.topic : "",
      },
      clientTs: new Date().toISOString(),
    }),
  });
}

export async function endInterviewSession(sessionId: string) {
  return request<{ sessionId: string; status: string }>("/interview/end", {
    method: "POST",
    body: JSON.stringify({
      sessionId,
      userId: DEFAULT_USER_ID,
      endReason: "USER_EXIT",
    }),
  });
}

export async function fetchEpisodes() {
  const episodes = await request<ApiEpisode[]>(
    `/api/episodes?userId=${DEFAULT_USER_ID}`
  );
  return episodes.map(toUiEpisode);
}

export async function generateAutobiography(selectedEpisodeIds: string[]) {
  return request<AutobiographyResponse>("/autobiography", {
    method: "POST",
    body: JSON.stringify({
      userId: String(DEFAULT_USER_ID),
      selectedEpisodeIds,
    }),
  });
}
