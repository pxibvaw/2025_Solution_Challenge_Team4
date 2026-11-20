// src/pages/Interview/components/InterviewStage.tsx

import type { InterviewState } from "../../../store/sessionStore";

import micIcon from "../../../assets/icon_mic.png";

interface Props {
  statusText: string;
  questionText: string;
  state: InterviewState;
  onPause: () => void;
  onMic: () => void;
  onEnd: () => void;
}

export default function InterviewStage({
  statusText,
  questionText,
  state,
  onPause,
  onMic,
  onEnd,
}: Props) {
  const pauseLabel =
    state === "PAUSED"
      ? "재개"
      : "잠시 멈춤";

  const micDisabled =
    state === "PROCESSING" ||
    state === "PAUSED" ||
    state === "ENDED";

  const isListening =
    state === "LISTENING";

  return (
    <div className="stage-container">
      {/* 상단 상태 */}

      <div className="stage-top">
        <div className="stage-status">
          {statusText}
        </div>
      </div>

      {/* 질문 */}

      <div className="stage-question-wrapper">
        {state ===
        "PROCESSING" ? (
          <div className="thinking-dots">
            <span />
            <span />
            <span />
          </div>
        ) : (
          <div className="stage-question">
            {questionText}
          </div>
        )}
      </div>

      {/* 캐릭터 */}

      <div
        className={`character-glow ${
          isListening
            ? "active"
            : ""
        }`}
      >
        <div className="character-ring"></div>

        <div
          className={`character-circle ${state.toLowerCase()}`}
        >
          <div className="character-face">
            <span className="face-eye left"></span>

            <span className="face-eye right"></span>

            <span className="face-mouth"></span>
          </div>
        </div>
      </div>

      {/* 마이크 */}

      <button
        className={`mic-btn ${
          isListening
            ? "active"
            : ""
        }`}
        onClick={onMic}
        disabled={micDisabled}
      >
        <img
          src={micIcon}
          alt="mic"
        />
      </button>

      {/* 하단 버튼 */}

      <div className="stage-bottom">
        <button
          className="btn-pause"
          onClick={onPause}
        >
          {pauseLabel}
        </button>

        <button
          className="btn-end"
          onClick={onEnd}
        >
          대화 끝내기
        </button>
      </div>
    </div>
  );
}