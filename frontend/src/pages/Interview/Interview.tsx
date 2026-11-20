import { useEffect, useMemo, useRef, useState } from "react";
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

import {
  startRecording,
  stopRecording,
  transcribeAudio,
  type RecorderHandle,
} from "../../utils/stt";

import InterviewStage from "./components/InterviewStage";
import InterviewLogPanel from "./components/InterviewLogPanel";

const FIRST_QUESTION_FALLBACK = "오늘은 어떤 이야기를 나눠볼까요?";

function buildFirstQuestion(profileTitle?: string, happiestMoment?: string) {
  if (happiestMoment) {
    return `${
      profileTitle ? `${profileTitle}님, ` : ""
    }${happiestMoment} 이야기를 조금 더 들려주실 수 있을까요?`;
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

// TTS 자동 재생 헬퍼.
// audioRef로 직전 재생을 중단해서, 사용자가 빠르게 다음 답을 보낼 때
// 이전 도란 음성과 새 음성이 겹치지 않도록 한다.
function playTtsBase64(
  base64: string,
  audioRef: React.MutableRefObject<HTMLAudioElement | null>
) {
  if (audioRef.current) {
    try {
      audioRef.current.pause();
    } catch {
      // ignore
    }
    audioRef.current = null;
  }

  try {
    const audio = new Audio(`data:audio/mp3;base64,${base64}`);
    audioRef.current = audio;
    audio.play().catch((e) => {
      // 브라우저 자동재생 정책으로 첫 사용자 인터랙션 전엔 실패할 수 있음.
      // 인터뷰는 사용자가 마이크 버튼을 누른 직후에 응답이 오므로 보통 통과.
      console.warn("[Interview] TTS 자동 재생 실패:", e);
    });
  } catch (e) {
    console.warn("[Interview] TTS Audio 생성 실패:", e);
  }
}

export default function Interview() {
  const navigate = useNavigate();
  const profile = useMemo(() => loadProfile(), []);

  // 도란 TTS 재생을 위한 Audio 객체 ref (직전 재생 중단용)
  const audioRef = useRef<HTMLAudioElement | null>(null);

  // 사용자 음성 녹음을 위한 MediaRecorder 핸들 ref.
  // LISTENING 상태 진입 시 set, 정지 시 unset.
  const recordingRef = useRef<RecorderHandle | null>(null);

  // F3. 온보딩 없이 /interview 직접 진입한 경우 방어
  useEffect(() => {
    if (!profile) {
      navigate("/onboarding", { replace: true });
    }
  }, [navigate, profile]);

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
    // profile이 없으면 온보딩으로 이동하므로 인터뷰 시작 API 호출 방지
    if (!profile) return;
    if (session) return;

    let cancelled = false;

    async function start() {
      try {
        setIsStarting(true);

        const response = await startInterviewSession();

        if (cancelled) return;

        const q = buildFirstQuestion(
          profile?.userTitle,
          profile?.happiestMoment
        );

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
        if (!cancelled) {
          setIsStarting(false);
        }
      }
    }

    start();

    return () => {
      cancelled = true;
    };
  }, [navigate, profile, session]);

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

  const handleStartAnswer = async () => {
    if (!session || session.state === "ENDED" || session.state === "PAUSED") {
      return;
    }

    // 이미 녹음 중이면 중복 시작 방지
    if (recordingRef.current) return;

    try {
      const handle = await startRecording();
      recordingRef.current = handle;
      setState("LISTENING");
    } catch (e) {
      console.error("Recording start failed:", e);
      alert(
        e instanceof Error
          ? `마이크를 사용할 수 없어요: ${e.message}`
          : "마이크 권한이 필요해요."
      );
    }
  };

  const handleStopAnswer = async () => {
    if (!session || session.state !== "LISTENING") return;

    const handle = recordingRef.current;
    recordingRef.current = null;

    // 안전망 — 녹음 핸들이 어떤 이유로든 없으면 그냥 IDLE 복귀
    if (!handle) {
      setState("IDLE");
      return;
    }

    setState("PROCESSING");

    // 1) 녹음 중단 + STT
    let userText = "";
    try {
      const blob = await stopRecording(handle);
      userText = await transcribeAudio(blob);
    } catch (e) {
      console.error("STT failed:", e);
      alert(
        e instanceof Error
          ? `음성 인식에 실패했어요: ${e.message}`
          : "음성 인식에 실패했어요. 다시 시도해주세요."
      );
      setState("IDLE");
      return;
    }

    if (!userText) {
      alert("음성을 알아듣지 못했어요. 한 번 더 말씀해주세요.");
      setState("IDLE");
      return;
    }

    // 2) 인식된 텍스트를 사용자 메시지로 기록
    addMessage({
      id: `m_${Date.now()}_u`,
      speaker: "USER",
      text: userText,
      createdAt: Date.now(),
    });

    // 3) BE /interview/turn 호출 (기존 흐름 그대로)
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

      // TTS 자동 재생 (Voice-first UX).
      // BE/AI 응답에 audioContent가 있으면 즉시 재생 — 사용자가 화면 안 봐도 들림.
      // TTS가 비활성/실패면 audioContent가 null이라 조건 통과 안 함 → 텍스트 표시만.
      if (response.meta?.audioContent) {
        playTtsBase64(response.meta.audioContent, audioRef);
      }

      setState("IDLE");
    } catch (e) {
      console.error("Interview turn failed:", e);

      setSession((prev) =>
        prev
          ? {
              ...prev,
              state: "ERROR",
              lastError:
                e instanceof Error ? e.message : "답변 처리에 실패했습니다.",
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

    if (session.state === "LISTENING") {
      handleStopAnswer();
    } else {
      handleStartAnswer();
    }
  };

  const handlePauseToggle = () => {
    if (!session) return;

    if (session.state === "PAUSED") {
      setState("IDLE");
    } else if (session.state !== "ENDED") {
      setState("PAUSED");
    }
  };

  const handleEnd = async () => {
    if (!session) return;

    try {
      await endInterviewSession(session.sessionId);
    } catch (e) {
      console.error("Interview end failed:", e);

      alert(
        e instanceof Error ? e.message : "인터뷰 종료 요청에 실패했습니다."
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