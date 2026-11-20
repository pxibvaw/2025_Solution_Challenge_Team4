# ai/utils/episode_formatters.py
"""
에피소드 생성 파이프라인 공통 포맷 유틸리티.

episode_segmentor, episode_writer, episode_merger에서 공유.
각 서비스의 private 함수 cross-import 대신 이 모듈에서 import.
"""
import json
import re


# ──────────────────────────────────────────────────────────────
# 대화 / 사실 / 에피소드 포맷
# ──────────────────────────────────────────────────────────────

def format_conversation(
    turns: list[dict],
    start: int = 0,
    end: int = None,
) -> str:
    """session_log를 번호 붙인 텍스트로 변환. start/end로 구간 지정 가능."""
    if end is None:
        end = len(turns) - 1
    lines = []
    for i, turn in enumerate(turns[start: end + 1], start=start):
        lines.append(f"[{i}] 사용자: {turn['user']}")
        lines.append(f"[{i}] AI: {turn['ai']}")
    return "\n".join(lines)


def format_source_facts(facts: list[str]) -> str:
    return "\n".join(f"- {f}" for f in facts) if facts else "없음"


def format_metadata(segment: dict) -> str:
    return (
        f"- type: {segment.get('type', 'GENERAL_EVENT')}\n"
        f"- key_scene_type: {segment.get('key_scene_type') or '없음'}\n"
        f"- theme: {segment.get('theme', '기타')}\n"
        f"- emotion_tone: {segment.get('emotion_tone', '중립')}\n"
        f"- time_hint: {segment.get('time_hint') or '없음'}\n"
        f"- period_label: {segment.get('period_label') or '없음'}\n"
        f"- location: {segment.get('location') or '없음'}"
    )


def format_sensory(sensory: dict | None) -> str:
    if not sensory:
        return "없음"
    parts = [f"{k}: {v}" for k, v in sensory.items() if v]
    return "\n".join(parts) if parts else "없음"


def format_persons(persons: list[dict]) -> str:
    if not persons:
        return "없음"
    return "\n".join(
        f"- {p.get('name', '?')} ({p.get('relation', '?')}): {p.get('role_in_episode', '')}"
        for p in persons
    )


def format_bridge_hints(segment: dict) -> str:
    return (
        f"- 서술 방향: {segment.get('narrative_direction') or '없음'}\n"
        f"- 지배 감정: {segment.get('dominant_emotion') or '없음'}\n"
        f"- 삶의 가치 후보: {segment.get('life_value_hint') or '없음'}"
    )


def format_length_guide(episode_type: str, length_ranges: dict) -> str:
    lo, hi = length_ranges.get(episode_type, (400, 700))
    return f"{lo}~{hi}자 (공백 포함)"


def format_existing_episodes(episodes: list[dict]) -> str:
    if not episodes:
        return "없음"
    return "\n".join(
        f"- id: {ep.get('id')} | 제목: {ep.get('title')} "
        f"| 주제: {ep.get('theme')} | 시기: {ep.get('period_label') or '미상'}"
        for ep in episodes
    )


# ──────────────────────────────────────────────────────────────
# JSON 파싱
# ──────────────────────────────────────────────────────────────

def parse_llm_json(raw: str, label: str = "") -> dict:
    """
    LLM 출력에서 JSON 파싱.
    마크다운 코드블록(```json ... ```) 자동 처리.
    파싱 실패 시 빈 dict 반환 — caller가 fallback 처리.
    """
    try:
        clean = raw.strip()
        if "```" in clean:
            for part in clean.split("```"):
                part = part.strip()
                if part.startswith("json"):
                    part = part[4:].strip()
                try:
                    return json.loads(part)
                except json.JSONDecodeError:
                    continue
        return json.loads(clean)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"[episode_formatters] {label} JSON 파싱 실패: {e}\nraw: {raw[:300]}")
        return {}


# ──────────────────────────────────────────────────────────────
# 품질 / facts 유틸리티
# ──────────────────────────────────────────────────────────────

def select_best_quote(
    raw_quote,
    priority: list[str],
) -> str | None:
    """
    quote: 문자열 / 배열(type+text 객체) / None 모두 처리.
    배열이면 우선순위 순으로 선택.
    """
    if raw_quote is None:
        return None
    if isinstance(raw_quote, str):
        return raw_quote
    if isinstance(raw_quote, list):
        for p in priority:
            for c in raw_quote:
                if c.get("type") == p:
                    return c.get("text")
        return raw_quote[0].get("text") if raw_quote else None
    return None


def calc_faithfulness(atomic_facts: list[dict]) -> float:
    """atomic_facts의 grounded 비율로 faithfulness_score 산출."""
    if not atomic_facts:
        return 1.0
    grounded = sum(1 for af in atomic_facts if af.get("grounded", False))
    return round(grounded / len(atomic_facts), 3)


def extract_failed_facts(
    source_facts: list[str],
    atomic_facts: list[dict],
) -> list[str]:
    """재생성 시 반영되지 않은 source_facts 추출."""
    if not atomic_facts:
        return source_facts
    grounded_texts = " ".join(
        af["fact"] for af in atomic_facts if af.get("grounded", False)
    )
    return [
        sf for sf in source_facts
        if not (
            set(re.findall(r'[가-힣]{2,}', sf))
            & set(re.findall(r'[가-힣]{2,}', grounded_texts))
        )
    ]


def make_fallback_quality() -> dict:
    return {
        "faithfulness_score": 0.5,
        "coverage_score": 0.5,
        "emotional_authenticity": 3.0,
        "sensory_vividness": 3.0,
        "personal_voice": 3.0,
        "narrative_flow": 3.0,
    }


def make_fallback_result(segment: dict) -> dict:
    return {
        "narrative": "",
        "quote": None,
        "atomic_facts": [],
        "autobiography_hint": None,
        "life_value": None,
        "emotion_nuance": None,
        "quality": make_fallback_quality(),
        "failed_facts": [],
    }


def merge_source_facts(
    existing: list[str],
    new: list[str],
) -> list[str]:
    """중복 제거 후 순서 보존 합치기."""
    return list(dict.fromkeys(existing + new))


def calc_richness_from_quality(quality: dict) -> float:
    """
    EpisodeQuality.narrative_richness를 dict에서 계산.
    가중치는 schemas.EpisodeQuality와 동일 소스(settings)를 사용해야 하므로
    EpisodeQuality 인스턴스를 생성해서 computed_field를 활용.

    ImportError 방어: schemas import 실패 시 fallback 계산.
    """
    try:
        from ai.app.schemas import EpisodeQuality
        return EpisodeQuality(**quality).narrative_richness
    except Exception:
        # fallback: settings 없이 기본 가중치로 계산 (비교용으로만 사용)
        W = {
            "faithfulness": 0.30, "emotional_authenticity": 0.25,
            "coverage": 0.20, "sensory_vividness": 0.15,
            "personal_voice": 0.07, "narrative_flow": 0.03,
        }
        return round(
            quality.get("faithfulness_score", 0.5)           * W["faithfulness"] +
            (quality.get("emotional_authenticity", 3.0) / 5) * W["emotional_authenticity"] +
            quality.get("coverage_score", 0.5)               * W["coverage"] +
            (quality.get("sensory_vividness", 3.0) / 5)      * W["sensory_vividness"] +
            (quality.get("personal_voice", 3.0) / 5)         * W["personal_voice"] +
            (quality.get("narrative_flow", 3.0) / 5)         * W["narrative_flow"],
            3
        )
        
# ──────────────────────────────────────────────────────────────
# 에피소드 서술 공통 (writer + merger 공유)
# ──────────────────────────────────────────────────────────────

LENGTH_RANGES: dict[str, tuple[int, int]] = {
    "KEY_SCENE":       (250, 600),
    "GENERAL_EVENT":   (400, 700),
    "LIFETIME_PERIOD": (600, 1000),
}

# KEY_SCENE 하위 타입별 범위 차등 (segmentor key_scene_type 활용)
KEY_SCENE_SUBTYPE_RANGES: dict[str, tuple[int, int]] = {
    "TURNING_POINT": (300, 600),
    "CRISIS":        (250, 500),
    "REVELATION":    (200, 450),
}


def format_exemplars(style: dict) -> str:
    """Few-shot 스타일 예시 포맷. writer/merger 공통 사용."""
    exemplars = style.get("exemplars", [])
    if not exemplars:
        return "예시 없음"
    return "\n".join(f"예시 {i+1}: \"{e}\"" for i, e in enumerate(exemplars))


def build_quality_data(quality_raw: dict, atomic_facts: list[dict]) -> dict:
    """
    LLM 출력 quality dict + atomic_facts → 최종 quality dict.
    faithfulness: computed vs LLM 중 낮은 것 사용 (보수적).
    writer/merger 동일 로직 → 단일 소스 보장.
    """
    computed_faith = calc_faithfulness(atomic_facts)
    llm_faith = float(quality_raw.get("faithfulness_score", 0.5))
    return {
        "faithfulness_score":     min(computed_faith, llm_faith),
        "coverage_score":         float(quality_raw.get("coverage_score", 0.5)),
        "emotional_authenticity": float(quality_raw.get("emotional_authenticity", 3.0)),
        "sensory_vividness":      float(quality_raw.get("sensory_vividness", 3.0)),
        "personal_voice":         float(quality_raw.get("personal_voice", 3.0)),
        "narrative_flow":         float(quality_raw.get("narrative_flow", 3.0)),
    }