// src/store/sessionStore.ts

export type InterviewState =
  | "IDLE"
  | "LISTENING"
  | "PROCESSING"
  | "PAUSED"
  | "ERROR"
  | "ENDED";

export type Speaker = "DORAN" | "USER";

export interface ChatMessage {
  id: string;
  speaker: Speaker;
  text: string;
  createdAt: number;
}

export interface InterviewSession {
  sessionId: string;
  startedAt: number;
  endedAt?: number;
  state: InterviewState;
  currentQuestion: string;
  messages: ChatMessage[];
  lastError?: string;
}

const LS_SESSION_KEY = "interview_session_v1";

export function loadSession(): InterviewSession | null {
  try {
    const raw = localStorage.getItem(LS_SESSION_KEY);
    if (!raw) return null;
    return JSON.parse(raw) as InterviewSession;
  } catch {
    return null;
  }
}

export function saveSession(session: InterviewSession) {
  localStorage.setItem(LS_SESSION_KEY, JSON.stringify(session));
}

export function clearSession() {
  localStorage.removeItem(LS_SESSION_KEY);
}

export function createNewSession(
  initialQuestion: string,
  sessionId?: string
): InterviewSession {
  const now = Date.now();
  return {
    sessionId: sessionId ?? `s_${now}`,
    startedAt: now,
    state: "IDLE",
    currentQuestion: initialQuestion,
    messages: [
      {
        id: `m_${now}_q`,
        speaker: "DORAN",
        text: initialQuestion,
        createdAt: now,
      },
    ],
  };
}

export function formatKoreanTime(ms: number) {
  const d = new Date(ms);
  const hh = d.getHours();
  const mm = d.getMinutes().toString().padStart(2, "0");
  const isPM = hh >= 12;
  const h12 = hh % 12 === 0 ? 12 : hh % 12;
  return `${isPM ? "오후" : "오전"} ${h12}:${mm}`;
}