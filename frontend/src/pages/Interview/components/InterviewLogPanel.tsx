// src/pages/Interview/components/InterviewLogPanel.tsx

import { useEffect } from "react";

import type { ChatMessage } from "../../../store/sessionStore";

import { formatKoreanTime } from "../../../store/sessionStore";

import "../../../styles/InterviewLogPanel.css";

interface Props {
  open: boolean;
  onClose: () => void;
  title: string;
  startedAt: number;
  messages: ChatMessage[];
}

export default function InterviewLogPanel({
  open,
  onClose,
  startedAt,
  messages,
}: Props) {

  useEffect(() => {
    window.scrollTo({
      top: 0,
      behavior: "instant",
    });
  }, []);

  if (!open) return null;

  /* =========================
    로그 → episode 저장
  ========================= */

  const saveAsEpisode = () => {
    const existing = JSON.parse(
      localStorage.getItem(
        "episodes"
      ) || "[]"
    );

    const newEpisode = {
      id: Date.now(),

      title:
        messages
          .find(
            (m) =>
              m.speaker === "USER"
          )
          ?.text.slice(0, 12) ||
        "새로운 이야기",

      preview: messages
        .map((m) => m.text)
        .join(" ")
        .slice(0, 50),

      content: messages
        .map((m) => m.text)
        .join("\n\n"),

      createdAt:
        new Date().toISOString(),
    };

    localStorage.setItem(
      "episodes",
      JSON.stringify([
        newEpisode,
        ...existing,
      ])
    );
  };

  return (
    <div className="log-page">
      {/* 헤더 */}

      <div className="log-container">
        <div className="log-title">
          오늘의 대화 기록
        </div>

        <div className="log-date">
          {new Date(startedAt)
            .toISOString()
            .slice(0, 10)}
        </div>

        {/* 로그 */}

        <div className="log-messages">
          {messages.map((m) => (
            <div
              key={m.id}
              className="log-message-group"
            >
              {/* 화자 */}

              {m.speaker !==
                "USER" && (
                <div className="log-speaker">
                  도란
                </div>
              )}

              {/* 말풍선 */}

              <div
                className={`log-bubble ${
                  m.speaker ===
                  "USER"
                    ? "log-bubble-user"
                    : "log-bubble-ai"
                }`}
              >
                <div className="log-bubble-text">
                  {m.text}
                </div>
              </div>

              {/* 시간 */}

              {m.speaker !==
                "USER" && (
                <div className="log-time">
                  {formatKoreanTime(
                    m.createdAt
                  )}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* 버튼 */}

        <div className="log-footer">
          <button
            className="log-close-btn"
            onClick={() => {
              saveAsEpisode();
              onClose();
            }}
          >
            닫기
          </button>
        </div>
      </div>
    </div>
  );
}