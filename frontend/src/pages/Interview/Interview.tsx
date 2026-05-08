// src/pages/Interview/Interview.tsx

import { useEffect, useMemo, useState } from "react";
import "../../styles/interviewRoom.css";
import { useNavigate } from "react-router-dom";

import { loadProfile } from "../../store/profileStore";
import type { InterviewSession, ChatMessage } from "../../store/sessionStore";

import {
  loadSession,
  createNewSession,
  saveSession,
} from "../../store/sessionStore";

import InterviewStage from "./components/InterviewStage";
import InterviewLogPanel from "./components/InterviewLogPanel";

const FIRST_QUESTION_FALLBACK = "오늘은 어떤 이야기를 나눠볼까요?";

function buildFirstQuestion(profileTitle?: string, happiestMoment?: string) {
  if (happiestMoment) {
    return `${profileTitle ? `${profileTitle}님, ` : ""}${happiestMoment} 이야기를 조금 더 들려주실 수 있을까요?`;
  }
  return `${profileTitle ? `${profileTitle}님, ` : ""}${FIRST_QUESTION_FALLBACK}`;
}

export default function Interview() {
  const navigate = useNavigate(); // ⭐ 추가
  const profile = useMemo(() => loadProfile(), []);

  const [session, setSession] = useState<InterviewSession>(() => {
    const existing = loadSession();
    if (existing && existing.state !== "ENDED") return existing;

    const q = buildFirstQuestion(profile?.userTitle, profile?.happiestMoment);
    const created = createNewSession(q);
    saveSession(created);
    return created;
  });

  useEffect(() => {
    saveSession(session);
  }, [session]);

  const setState = (state: InterviewSession["state"]) => {
    setSession((prev) => ({ ...prev, state }));
  };

  const addMessage = (msg: ChatMessage) => {
    setSession((prev) => ({
      ...prev,
      messages: [...prev.messages, msg],
    }));
  };

  const setQuestion = (text: string) => {
    setSession((prev) => ({
      ...prev,
      currentQuestion: text,
    }));

    addMessage({
      id: `m_${Date.now()}_q`,
      speaker: "DORAN",
      text,
      createdAt: Date.now(),
    });
  };

  const handleStartAnswer = () => {
    if (session.state === "ENDED" || session.state === "PAUSED") return;
    setState("LISTENING");
  };

  const handleStopAnswer = () => {
    if (session.state !== "LISTENING") return;

    addMessage({
      id: `m_${Date.now()}_u`,
      speaker: "USER",
      text: "그때가 참 따뜻했어요.",
      createdAt: Date.now(),
    });

    setState("PROCESSING");

    setTimeout(() => {
      const nextQ = `${
        profile?.userTitle ? `${profile.userTitle}님, ` : ""
      }그때 기분이 어떠셨어요?`;

      setQuestion(nextQ);
      setState("IDLE");
    }, 1200);
  };

  const handleMicToggle = () => {
    if (session.state === "LISTENING") handleStopAnswer();
    else handleStartAnswer();
  };

  const handlePauseToggle = () => {
    if (session.state === "PAUSED") setState("IDLE");
    else if (session.state !== "ENDED") setState("PAUSED");
  };

  const handleEnd = () => {
  const endedSession = {
    ...session,
    state: "ENDED" as const,
    endedAt: Date.now(),
  };

  saveSession(endedSession);

  setSession(endedSession);
};

  if (session.state === "ENDED") {
    return (
      <div className="interview-single">
        <InterviewLogPanel
          open={true}
          onClose={() => navigate("/main")}
          title="오늘의 대화기록"
          startedAt={session.startedAt}
          messages={session.messages}
        />
      </div>
    );
  }

  const stageStatusText =
    session.state === "LISTENING"
      ? "이야기 듣는중"
      : session.state === "PROCESSING"
      ? "생각중..."
      : session.state === "PAUSED"
      ? "잠시 멈춤"
      : "이야기 듣는중";

  return (
    <div className="interview-single">
      <InterviewStage
        statusText={stageStatusText}
        questionText={session.currentQuestion}
        state={session.state}
        onPause={handlePauseToggle}
        onMic={handleMicToggle}
        onEnd={handleEnd}
      />
    </div>
  );
}