import { useState, useEffect } from "react";
import "../../../styles/onboarding.css";
import icon10 from "../../../assets/onboarding_10s.png";
import icon20 from "../../../assets/onboarding_20s.png";
import icon30 from "../../../assets/onboarding_30s.png";
import icon40 from "../../../assets/onboarding_40s.png";
import icon50 from "../../../assets/onboarding_50s.png";
import icon60 from "../../../assets/onboarding_60s.png";
import checkIcon from "../../../assets/icon_check.png";
import type { AgeGroup } from "../../../store/profileStore";

interface Props {
  onNext: () => void;
  onPrev: () => void;
  onSave: (value: AgeGroup) => void;
}

const ageOptions: { label: string; value: AgeGroup; icon: string }[] = [
  { label: "10대", value: "TEENS", icon: icon10 },
  { label: "20대", value: "TWENTIES", icon: icon20 },
  { label: "30대", value: "THIRTIES", icon: icon30 },
  { label: "40대", value: "FORTIES", icon: icon40 },
  { label: "50대", value: "FIFTIES", icon: icon50 },
  { label: "60대", value: "SIXTIES", icon: icon60 },
];

const StepAge = ({ onNext, onPrev, onSave }: Props) => {
  const [selected, setSelected] = useState<AgeGroup | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!error) return;

    const timer = setTimeout(() => {
      setError("");
    }, 2000);

    return () => clearTimeout(timer);
  }, [error]);

  const handleNext = () => {
    if (!selected) {
      setError("연령대를 선택해주세요");
      return;
    }

    setError("");
    onSave(selected);
    onNext();
  };

  return (
    <div className="onboarding-wrapper step-age-wrapper">
      <div className="step-age-content">
        <h2 className="step-title">
          제일 기억에 남는 시절은 <br /> 언제인가요?
        </h2>

        <div className="age-grid">
          {ageOptions.map((item) => {
            const isActive = selected === item.value;

            return (
              <button
                key={item.value}
                className={`age-card ${isActive ? "active" : ""}`}
                onClick={() => setSelected(item.value)}
              >
                {isActive && (
                  <img
                    src={checkIcon}
                    alt="체크"
                    className="check-icon"
                  />
                )}

                <img
                  src={item.icon}
                  alt={item.label}
                  className="age-icon-img"
                />

                {item.label}
              </button>
            );
          })}
        </div>
      </div>

      {error && (
        <div className="step-toast-error">
          {error}
        </div>
      )}

      <div className="step-bottom-buttons">
        <button className="step-btn-secondary" onClick={onPrev}>
          이전
        </button>

        <button
          className="step-btn-primary"
          onClick={handleNext}
        >
          다음
        </button>
      </div>
    </div>
  );
};

export default StepAge;