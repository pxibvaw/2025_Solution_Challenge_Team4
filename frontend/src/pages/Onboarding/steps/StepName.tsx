import { useState, useRef, useEffect } from "react";
import "../../../styles/onboarding.css";
import character from "../../../assets/character.png";
import mic from "../../../assets/icon_mic.png";

interface Props {
    onNext: () => void;
    onSave: (value: string) => void;
    }

    const StepName = ({ onNext, onSave }: Props) => {
    const [name, setName] = useState("");
    const [mode, setMode] = useState<"idle" | "voice" | "manual">("idle");
    const [error, setError] = useState("");
    const inputRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
        if (mode === "manual" && inputRef.current) {
        inputRef.current.focus();
        }
    }, [mode]);

    useEffect(() => {
        if (!error) return;

        const timer = setTimeout(() => {
        setError("");
        }, 2000);

        return () => clearTimeout(timer);
    }, [error]);

    const handleVoiceStart = () => {
        setMode("voice");
        setName("할아버지");
    };

    const handleManualStart = () => {
        setMode("manual");
    };

    const isInputting = mode !== "idle" || name.length > 0;

    const handleNext = () => {
        const trimmed = name.trim();

        if (!trimmed) {
        setError("호칭을 입력해주세요");
        return;
        }

        if (mode === "manual") {
        const specialCharRegex = /[^가-힣a-zA-Z0-9]/;

        if (specialCharRegex.test(trimmed)) {
            setError("특수문자를 제외한 문자를 입력해주세요");
            return;
        }
        }

        setError("");
        onSave(trimmed);
        onNext();
    };

    return (
        <div className="onboarding-wrapper">
        <div className="step-name-wrapper">
            <div className="step-name-content">
            <div className="title-area">
                {!isInputting ? (
                <>
                    <div className="step-name-greeting-title">
                    반가워요! <br />
                    어떻게 불러드릴까요?
                    </div>

                    <div className="step-subtitle">
                    본명도 좋고, 편한 호칭도 좋아요.
                    </div>
                </>
                ) : (
                <div className="step-title active-title">
                    {mode === "manual" ? (
                    <input
                        ref={inputRef}
                        type="text"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        className="hidden-input"
                        placeholder="호칭을 입력해주세요"
                        maxLength={7}
                    />
                    ) : (
                    <>
                        {name}
                        <span className="blinking-cursor">|</span>
                    </>
                    )}
                </div>
                )}
            </div>

            <div className="character-image">
                <img src={character} alt="캐릭터" />
            </div>

            <button
                className="manual-input-btn"
                onClick={handleManualStart}
            >
                손으로 입력하기
            </button>
            </div>

            {error && (
            <div className="step-toast-error">
                {error}
            </div>
            )}

            <div className="step-bottom">
            {mode === "voice" ? (
                <button
                className="step-btn step-btn-voice-active"
                onClick={() => setMode("idle")}
                >
                <img src={mic} alt="마이크" className="mic-icon" />
                </button>
            ) : (
                <button
                className="step-btn step-btn-voice"
                onClick={handleVoiceStart}
                >
                대답하기
                </button>
            )}

            <button
                className="step-name-btn-primary"
                onClick={handleNext}
            >
                다음
            </button>
            </div>
        </div>
        </div>
    );
};

export default StepName;