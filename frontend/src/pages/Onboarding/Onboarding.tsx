import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import StepName from "./steps/StepName";
import StepSpeech from "./steps/StepSpeech";
import StepAge from "./steps/StepAge";
import StepTopic from "./steps/StepTopic";

import type { UserProfileContext } from "../../store/profileStore";

import {
  loadOnboardingDraft,
  saveOnboardingDraft,
  clearOnboardingDraft,
  saveProfile,
  setOnboardedTrue,
} from "../../store/profileStore";

const TOTAL_STEPS = 4;

export default function Onboarding() {
  const navigate = useNavigate();

  const draft = useMemo(
    () => loadOnboardingDraft(),
    []
  );

  const [step, setStep] = useState(
    draft?.step ?? 0
  );

  const [profile, setProfile] =
    useState<UserProfileContext>(
      draft?.profile ?? {}
    );

  useEffect(() => {
    saveOnboardingDraft({
      step,
      profile,
      updatedAt: Date.now(),
    });
  }, [step, profile]);

  const next = () => {
    if (step >= TOTAL_STEPS - 1) return;

    setStep((p) => p + 1);
  };

  const prev = () => {
    if (step <= 0) return;

    setStep((p) => p - 1);
  };

  const complete = () => {
    try {
      saveProfile(profile);

      setOnboardedTrue();

      clearOnboardingDraft();

      navigate("/main", {
        replace: true,
      });
    } catch (e) {
      console.error(
        "Onboarding save failed:",
        e
      );

      alert(
        "온보딩 데이터 저장에 실패했어요. 다시 시도해주세요."
      );
    }
  };

  return (
    <div className="onboarding-wrapper">
      <div
        className="progress-bar"
        style={{
          width:
            step === 0
              ? "25%"
              : step === 1
              ? "50%"
              : step === 2
              ? "75%"
              : "100%",
        }}
      />

      {step === 0 && (
        <StepName
          onNext={next}
          onSave={(value) =>
            setProfile(
              (prevProfile) => ({
                ...prevProfile,
                userTitle: value,
              })
            )
          }
        />
      )}

      {step === 1 && (
        <StepSpeech
          onPrev={prev}
          onNext={next}
          onSave={(value) =>
            setProfile(
              (prevProfile) => ({
                ...prevProfile,
                speechLevel: value,
              })
            )
          }
        />
      )}

      {step === 2 && (
        <StepAge
          onPrev={prev}
          onNext={next}
          onSave={(value) =>
            setProfile(
              (prevProfile) => ({
                ...prevProfile,
                ageGroup: value,
              })
            )
          }
        />
      )}

      {step === 3 && (
        <StepTopic
          onPrev={prev}
          onNext={complete}
          onSave={(value) =>
            setProfile(
              (prevProfile) => ({
                ...prevProfile,
                topic: value,
              })
            )
          }
        />
      )}
    </div>
  );
}