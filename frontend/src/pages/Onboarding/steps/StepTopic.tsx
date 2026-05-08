import { useState, useEffect } from "react";
import "../../../styles/onboarding.css";

import iconFamily from "../../../assets/onboarding_family.png";
import iconLove from "../../../assets/onboarding_love.png";
import iconHealth from "../../../assets/onboarding_health.png";
import iconThink from "../../../assets/onboarding_think.png";
import iconEtc from "../../../assets/onboarding_etc.png";
import checkIcon from "../../../assets/icon_check.png";

interface Props {
    onNext: () => void;
    onPrev: () => void;
    onSave: (value: string) => void;
    }

    const topics = [
    { label: "가족", value: "FAMILY", icon: iconFamily },
    { label: "사랑", value: "LOVE", icon: iconLove },
    { label: "건강", value: "HEALTH", icon: iconHealth },
    { label: "가치관", value: "VALUES", icon: iconThink },
    { label: "직접 입력", value: "CUSTOM", icon: iconEtc },
    ];

    const StepTopic = ({ onNext, onPrev, onSave }: Props) => {
    const [selected, setSelected] = useState<string | null>(null);
    const [customText, setCustomText] = useState("");
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
        setError("하나 이상의 가치를 선택해주세요");
        return;
        }

        if (selected === "CUSTOM") {
        const trimmed = customText.trim();

        if (!trimmed) {
            setError("7자 이내로 입력해주세요");
            return;
        }

        if (trimmed.length > 7) {
            setError("7자 이내로 입력해주세요");
            return;
        }

        const specialCharRegex = /^[^가-힣a-zA-Z0-9]+$/;

        if (specialCharRegex.test(trimmed)) {
            setError("특수문자를 제외한 문자를 입력해주세요");
            return;
        }

        onSave(trimmed);
        } else {
        onSave(selected);
        }

        onNext();
    };

    return (
        <div className="onboarding-wrapper step-topic-wrapper">
        <div className="step-topic-content">
            <h2 className="step-title">
            어떤 이야기를 <br /> 나누고 싶으세요?
            </h2>

            <div
            className="topic-grid"
            style={{
                marginBottom:
                selected === "CUSTOM" ? "0px" : "85px",
            }}
            >
            {topics.map((item) => {
                const isActive = selected === item.value;

                return (
                <button
                    key={item.value}
                    className={`topic-card ${
                    isActive ? "active" : ""
                    }`}
                    onClick={() => {
                    setSelected(item.value);
                    setCustomText("");
                    }}
                >
                    {isActive && (
                    <img
                        src={checkIcon}
                        alt="체크"
                        className="topic-check"
                    />
                    )}

                    <img
                    src={item.icon}
                    alt={`${item.label} 아이콘`}
                    className="topic-icon"
                    />

                    <span>{item.label}</span>
                </button>
                );
            })}
            </div>

            {selected === "CUSTOM" && (
            <div className="topic-custom-input-wrapper">
                <input
                type="text"
                placeholder="이야기를 입력해주세요"
                value={customText}
                maxLength={7}
                onChange={(e) => {
                    if (e.target.value.length <= 7) {
                    setCustomText(e.target.value);
                    }
                }}
                className="topic-custom-input"
                />

                <span className="topic-length">
                {customText.length}/7
                </span>
            </div>
            )}
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

export default StepTopic;