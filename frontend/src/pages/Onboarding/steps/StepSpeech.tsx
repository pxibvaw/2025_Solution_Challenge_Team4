import { useState, useEffect } from "react";
import "../../../styles/onboarding.css";

interface Props {
    onNext: () => void;
    onPrev: () => void;
    onSave: (value: "HONORIFIC" | "CASUAL") => void;
    }

    const StepSpeech = ({ onNext, onPrev, onSave }: Props) => {
    const [selected, setSelected] = useState<
        "HONORIFIC" | "CASUAL" | null
    >(null);

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
        setError("말투를 선택해주세요");
        return;
        }

        setError("");
        onSave(selected);
        onNext();
    };

    return (
        <div className="onboarding-wrapper">
        <div className="step-speech-content">
            <div className="step-title">
            어떤 말투가 좋으세요?
            </div>

            <button
            className={`step-speech-option-button ${
                selected === "CASUAL" ? "active" : ""
            }`}
            onClick={() => setSelected("CASUAL")}
            >
            편안한 반말
            </button>

            <button
            className={`step-speech-option-button ${
                selected === "HONORIFIC" ? "active" : ""
            }`}
            onClick={() => setSelected("HONORIFIC")}
            >
            정중한 존댓말
            </button>
        </div>

        {error && (
            <div className="step-toast-error">
            {error}
            </div>
        )}

        <div className="step-bottom-buttons">
            <button
            className="step-btn-secondary"
            onClick={onPrev}
            >
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

export default StepSpeech;