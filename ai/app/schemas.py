# ai/app/schemas.py
from pydantic import BaseModel, Field, computed_field
from typing import Optional
from datetime import datetime
from ai.app.settings import EPISODE_QUALITY_WEIGHTS as _W, EPISODE_QUALITY_THRESHOLDS as _T


# ────────────────────────────────────────────
# 인터뷰룸 기존 스키마 (변경 없음)
# ────────────────────────────────────────────

class UserProfileContext(BaseModel):
    userTitle: str
    speechLevel: str = "HONORIFIC"
    memorableAge: Optional[str] = None
    coreValue: Optional[str] = None
    birthYear: Optional[int] = None


class TurnRequest(BaseModel):
    sessionId: str
    requestId: str
    userText: str
    profile: UserProfileContext


class TurnResponse(BaseModel):
    requestId: str
    reply: str
    question: str
    turnIndex: int = 0
    audioContent: Optional[str] = None


class EndSessionRequest(BaseModel):
    sessionId: str
    userId: str


class EndSessionResponse(BaseModel):
    sessionId: str
    saved: int
    skipped: int


# ────────────────────────────────────────────
# 에피소드 품질 스키마
# ────────────────────────────────────────────

class EpisodeQuality(BaseModel):
    """
    에피소드 서술 품질 점수.
    episode_writer.py의 LLM 출력에 포함되어 별도 호출 없이 산출됨.

    가중치/임계값은 settings.py에서 관리.
    실데이터 기반 재조정 시 settings.py 또는 .env만 수정하면 됨.
    """

    # ── 방법 2: 객관적 검증 ────────────────────
    faithfulness_score: float = Field(ge=0.0, le=1.0)
    coverage_score: float = Field(ge=0.0, le=1.0)

    # ── 방법 1: G-Eval 다차원 품질 ────────────
    emotional_authenticity: float = Field(ge=1.0, le=5.0)
    sensory_vividness: float = Field(ge=1.0, le=5.0)
    personal_voice: float = Field(ge=1.0, le=5.0)
    narrative_flow: float = Field(ge=1.0, le=5.0)

    @computed_field
    @property
    def narrative_richness(self) -> float:
        """
        최종 종합 품질 점수 (0~1).
        가중치는 settings.EPISODE_QUALITY_WEIGHTS에서 읽음.
        """
        return round(
            self.faithfulness_score          * _W["faithfulness"] +
            (self.emotional_authenticity / 5) * _W["emotional_authenticity"] +
            self.coverage_score              * _W["coverage"] +
            (self.sensory_vividness / 5)     * _W["sensory_vividness"] +
            (self.personal_voice / 5)        * _W["personal_voice"] +
            (self.narrative_flow / 5)        * _W["narrative_flow"],
            3
        )

    @computed_field
    @property
    def quality_grade(self) -> str:
        """
        에피소드 페이지 배지용 등급.
        임계값은 settings.EPISODE_QUALITY_THRESHOLDS에서 읽음.
        """
        r = self.narrative_richness
        if r >= _T["RICH"]:
            return "RICH"
        elif r >= _T["GOOD"]:
            return "GOOD"
        elif r >= _T["NORMAL"]:
            return "NORMAL"
        else:
            return "WEAK"

    @computed_field
    @property
    def needs_regeneration(self) -> bool:
        """
        재생성 권고 여부.
        임계값은 settings.EPISODE_QUALITY_THRESHOLDS에서 읽음.
        """
        return (
            self.faithfulness_score < _T["faithfulness_min"]
            or self.narrative_richness < _T["richness_min"]
        )


# ────────────────────────────────────────────
# 에피소드 보조 스키마
# ────────────────────────────────────────────

class EpisodePerson(BaseModel):
    name: Optional[str] = None
    relation: Optional[str] = None
    role_in_episode: Optional[str] = None


class EpisodeSensory(BaseModel):
    smell: Optional[str] = None
    sound: Optional[str] = None
    visual: Optional[str] = None
    texture: Optional[str] = None
    weather: Optional[str] = None


# ────────────────────────────────────────────
# 에피소드 메인 스키마
# ────────────────────────────────────────────

class Episode(BaseModel):
    id: str
    user_id: str
    session_id: str

    title: str
    narrative: str
    quote: Optional[str] = None

    time_hint: Optional[str] = None
    period_label: Optional[str] = None
    estimated_year_range: Optional[str] = None
    location: Optional[str] = None
    persons: list[EpisodePerson] = []
    sensory: Optional[EpisodeSensory] = None

    type: str
    key_scene_type: Optional[str] = None
    theme: str
    emotion_tone: str
    emotion_nuance: Optional[str] = None

    autobiography_hint: Optional[str] = None
    life_value: Optional[str] = None
    importance_score: float = 5.0

    quality: Optional[EpisodeQuality] = None

    source_session_id: str = ""
    source_turn_range: Optional[tuple[int, int]] = None
    source_facts: list[str] = []

    is_merged: bool = False
    merged_from: Optional[str] = None
    version: int = 1

    is_selected_for_autobiography: bool = False
    user_edited_title: Optional[str] = None
    user_memo: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ────────────────────────────────────────────
# 요청/응답 스키마
# ────────────────────────────────────────────

class EpisodeGenerateRequest(BaseModel):
    sessionId: str
    userId: str


class EpisodeGenerateResponse(BaseModel):
    sessionId: str
    episodes_created: int
    episodes_merged: int
    weak_episodes: int


class AutobiographyRequest(BaseModel):
    userId: str
    selectedEpisodeIds: list[str]
    episodes: list[Episode]


class AutobiographyChapter(BaseModel):
    title: str
    period_label: Optional[str] = None
    narrative: str
    episode_ids: list[str]


class AutobiographyResponse(BaseModel):
    prologue: str
    chapters: list[AutobiographyChapter]
    epilogue: str
    life_theme: str