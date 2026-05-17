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
  clearSession,
} from "../../store/sessionStore";

import {
  endInterviewSession,
  sendInterviewTurn,
  startInterviewSession,
} from "../../api/doran";

import InterviewStage from "./components/InterviewStage";
import InterviewLogPanel from "./components/InterviewLogPanel";

const FIRST_QUESTION_FALLBACK = "오늘은 어떤 이야기를 나눠볼까요?";

function buildFirstQuestion(profileTitle?: string, happiestMoment?: string) {
  if (happiestMoment) {
    return `${profileTitle ? `${profileTitle}님, ` : ""}${happiestMoment} 이야기를 조금 더 들려주실 수 있을까요?`;
  }
  return `${profileTitle ? `${profileTitle}님, ` : ""}${FIRST_QUESTION_FALLBACK}`;
}

function isUuid(value?: string) {
  return Boolean(
    value &&
      /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(
        value
      )
  );
}

export default function Interview() {
  const navigate = useNavigate();
  const profile = useMemo(() => loadProfile(), []);

  const [session, setSession] = useState<InterviewSession | null>(() => {
    const existing = loadSession();
    if (existing && existing.state !== "ENDED" && isUuid(existing.sessionId)) {
      return existing;
    }
    return null;
  });

  const [isStarting, setIsStarting] = useState(!session);

  useEffect(() => {
    if (session) {
      saveSession(session);
    }
  }, [session]);

  useEffect(() => {
    if (session) return;

    let cancelled = false;

    async function start() {
      try {
        setIsStarting(true);
        const response = await startInterviewSession();
        if (cancelled) return;

        const q = buildFirstQuestion(profile?.userTitle, profile?.happiestMoment);
        const created = createNewSession(q, response.sessionId);
        saveSession(created);
        setSession(created);
      } catch (e) {
        console.error("Interview start failed:", e);
        alert(
          e instanceof Error
            ? e.message
            : "인터뷰를 시작하지 못했어요. 백엔드 서버를 확인해주세요."
        );
        navigate("/main", { replace: true });
      } finally {
        if (!cancelled) setIsStarting(false);
      }
    }

    start();

    return () => {
      cancelled = true;
    };
  }, [navigate, profile?.happiestMoment, profile?.userTitle, session]);

  const setState = (state: InterviewSession["state"]) => {
    setSession((prev) => (prev ? { ...prev, state } : prev));
  };

  const addMessage = (msg: ChatMessage) => {
    setSession((prev) =>
      prev
        ? {
            ...prev,
            messages: [...prev.messages, msg],
          }
        : prev
    );
  };

  const addDoranMessage = (text: string) => {
    addMessage({
      id: `m_${Date.now()}_q`,
      speaker: "DORAN",
      text,
      createdAt: Date.now(),
    });
  };

  const setQuestion = (text: string) => {
    setSession((prev) =>
      prev
        ? {
            ...prev,
            currentQuestion: text,
          }
        : prev
    );

    addDoranMessage(text);
  };

  const handleStartAnswer = () => {
    if (!session || session.state === "ENDED" || session.state === "PAUSED") return;
    setState("LISTENING");
  };

  const handleStopAnswer = async () => {
    if (!session || session.state !== "LISTENING") return;

    const userText =
      window.prompt("백엔드로 보낼 답변을 입력해주세요.", "그때가 참 따뜻했어요.")?.trim() ?? "";

    if (!userText) {
      setState("IDLE");
      return;
    }

    addMessage({
      id: `m_${Date.now()}_u`,
      speaker: "USER",
      text: userText,
      createdAt: Date.now(),
    });

    setState("PROCESSING");

    try {
      const response = await sendInterviewTurn({
        sessionId: session.sessionId,
        requestId: crypto.randomUUID(),
        userText,
        profile,
      });

      if (response.output.reply) {
        addDoranMessage(response.output.reply);
      }

      setQuestion(response.output.question);
      setState("IDLE");
    } catch (e) {
      console.error("Interview turn failed:", e);
      setSession((prev) =>
        prev
          ? {
              ...prev,
              state: "ERROR",
              lastError:
                e instanceof Error
                  ? e.message
                  : "답변 처리에 실패했습니다.",
            }
          : prev
      );
      alert(
        e instanceof Error
          ? e.message
          : "답변 처리에 실패했습니다. 다시 시도해주세요."
      );
      setState("IDLE");
    }
  };

  const handleMicToggle = () => {
    if (!session) return;
    if (session.state === "LISTENING") handleStopAnswer();
    else handleStartAnswer();
  };

  const handlePauseToggle = () => {
    if (!session) return;
    if (session.state === "PAUSED") setState("IDLE");
    else if (session.state !== "ENDED") setState("PAUSED");
  };

  const handleEnd = async () => {
    if (!session) return;

    try {
      await endInterviewSession(session.sessionId);
    } catch (e) {
      console.error("Interview end failed:", e);
      alert(
        e instanceof Error
          ? e.message
          : "인터뷰 종료 요청에 실패했습니다."
      );
    }

    const endedSession = {
      ...session,
      state: "ENDED" as const,
      endedAt: Date.now(),
    };

    saveSession(endedSession);
    setSession(endedSession);
  };

  if (isStarting || !session) {
    return (
      <div className="interview-single">
        <div className="interview-loading">인터뷰를 시작하는 중입니다...</div>
      </div>
    );
  }

  if (session.state === "ENDED") {
    return (
      <div className="interview-single">
        <InterviewLogPanel
          open={true}
          onClose={() => {
            clearSession();
            navigate("/main");
          }}
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
