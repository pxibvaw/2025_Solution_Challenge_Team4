# ai/app/settings.py
from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    # ── 환경 설정 ─────────────────────────────────────────────
    # "development" | "production"
    # 프로덕션 배포 시 ENV=production 설정 필수
    ENV = os.getenv("ENV", "development")

    GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    CHROMA_PERSIST_PATH = os.path.abspath(
        os.getenv("CHROMA_PERSIST_PATH", "./data/chroma")
    )

    @property
    def is_production(self) -> bool:
        return self.ENV.lower() == "production"

settings = Settings()


# ── 에피소드 품질 가중치 ───────────────────────────────────────
# 실데이터 기반 재조정 시 여기만 수정
EPISODE_QUALITY_WEIGHTS = {
    "faithfulness":           float(os.getenv("EQ_W_FAITHFULNESS",   "0.30")),
    "emotional_authenticity": float(os.getenv("EQ_W_EMOTIONAL",      "0.25")),
    "coverage":               float(os.getenv("EQ_W_COVERAGE",       "0.20")),
    "sensory_vividness":      float(os.getenv("EQ_W_SENSORY",        "0.15")),
    "personal_voice":         float(os.getenv("EQ_W_VOICE",          "0.07")),
    "narrative_flow":         float(os.getenv("EQ_W_FLOW",           "0.03")),
}

# ── 에피소드 품질 임계값 ──────────────────────────────────────
EPISODE_QUALITY_THRESHOLDS = {
    "RICH":              float(os.getenv("EQ_T_RICH",         "0.85")),
    "GOOD":              float(os.getenv("EQ_T_GOOD",         "0.70")),
    "NORMAL":            float(os.getenv("EQ_T_NORMAL",       "0.50")),
    "faithfulness_min":  float(os.getenv("EQ_T_FAITH_MIN",   "0.70")),
    "richness_min":      float(os.getenv("EQ_T_RICH_MIN",    "0.50")),
}