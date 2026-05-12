// src/pages/Generate/GenerateLoading.tsx

import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  useNavigate,
  useLocation,
} from "react-router-dom";

import loadingImage from "../../assets/loading.png";
import loadingCompleteImage from "../../assets/loading_complete.png";

import "../../styles/GenerateLoading.css";

/* =========================
  컨페티 랜덤 데이터
========================= */

const confettiPieces = Array.from({
  length: 24,
}).map(() => ({
  left: `${Math.random() * 100}%`,

  duration: `${
    1.8 + Math.random() * 2
  }s`,

  rotate: `rotate(${
    Math.random() * 360
  }deg)`,
}));

export default function GenerateLoading() {
  const navigate = useNavigate();
  const location = useLocation();

  const [step, setStep] = useState(0);

  const selectedIds = useMemo(
    () => location.state?.selectedIds || [],
    [location.state]
  );

  useEffect(() => {
    const timers = [
      setTimeout(() => setStep(1), 1200),

      setTimeout(() => setStep(2), 2400),

      setTimeout(() => setStep(3), 3600),

      setTimeout(() => {
        navigate("/generate/complete", {
          state: { selectedIds },
        });
      }, 5200),
    ];

    return () => {
      timers.forEach(clearTimeout);
    };
  }, [navigate, selectedIds]);

  const loadingData = [
    {
      title: "조금만 기다려 주세요",
      subtitle:
        "당신의 이야기를 정리하는 중이에요",
      image: loadingImage,
    },

    {
      title: "소중한 말씀을 모으는 중",
      subtitle:
        "따뜻한 순간들을 담고 있어요",
      image: loadingImage,
    },

    {
      title: "어울리는 단어 고르는 중",
      subtitle:
        "당신만의 표현을 찾고 있어요",
      image: loadingImage,
    },

    {
      title: "자서전이 완성됐어요!",
      subtitle:
        "이제 이야기를 만나보세요",
      image: loadingCompleteImage,
    },
  ];

  return (
    <main className="generate-loading-page">
      <div className="generate-loading-card">
        <div className="generate-loading-status">
          {step === 3 ? "완성" : "생성중"}
        </div>

        <h2 className="generate-loading-title">
          {loadingData[step].title}
        </h2>

        <p className="generate-loading-subtitle">
          {loadingData[step].subtitle}
        </p>

        <div
          className={`generate-loading-visual ${
            step === 3
              ? "complete"
              : "loading"
          }`}
        >
          {step !== 3 && (
            <div className="loading-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
          )}

          {step === 3 && (
            <div className="confetti">
              {confettiPieces.map(
                (piece, i) => (
                  <span
                    key={i}
                    style={{
                      left: piece.left,

                      animationDuration:
                        piece.duration,

                      transform:
                        piece.rotate,
                    }}
                  >
                    ✦
                  </span>
                )
              )}
            </div>
          )}

          <img
            src={loadingData[step].image}
            alt="loading"
            className={`generate-loading-image ${
              step === 3
                ? "complete-character"
                : ""
            }`}
          />
        </div>
      </div>
    </main>
  );
}