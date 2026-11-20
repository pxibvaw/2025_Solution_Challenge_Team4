# ai/services/episode_writer.py
import concurrent.futures
from ai.clients.llm_gemini import generate_reply
from ai.app.schemas import UserProfileContext
from ai.prompts.episode_writer_prompts import (
    WRITER_PROMPT,
    WRITER_REGEN_PROMPT,
    WRITER_LENGTH_RETRY_PROMPT,
)
from ai.utils.episode_formatters import (
    format_conversation,
    format_source_facts,
    format_metadata,
    format_sensory,
    format_persons,
    format_bridge_hints,
    format_length_guide,
    parse_llm_json,
    select_best_quote,
    calc_faithfulness,
    extract_failed_facts,
    make_fallback_quality,
    make_fallback_result,
    format_exemplars,
    build_quality_data,
    LENGTH_RANGES,
    KEY_SCENE_SUBTYPE_RANGES,
)


# ──────────────────────────────────────────────────────────────
# 상수
# ──────────────────────────────────────────────────────────────

QUOTE_PRIORITY = ["감정_농축", "가치관", "감각_표현", "전환점", "관계_핵심"]


# ──────────────────────────────────────────────────────────────
# Few-shot 스타일 예시 추출
# ──────────────────────────────────────────────────────────────

def extract_style_exemplars(turns: list[dict]) -> dict:
    """
    대화 로그에서 사용자 고유 스타일 예시 추출.

    regex 분석 대신 실제 발화를 직접 LLM에 제공.
    (Wang et al. 2025 / Bhandarkar et al. 2024 few-shot style imitation)

    Returns:
        exemplars: 대표 발화 최대 5개 (초반/중반/후반 균등 분산)
        total_turns: 전체 사용자 발화 수
    """
    user_texts = [t["user"] for t in turns if t.get("user")]
    if not user_texts:
        return {"exemplars": [], "total_turns": 0}

    meaningful = [t for t in user_texts if len(t) >= 10]
    if not meaningful:
        return {"exemplars": user_texts[:3], "total_turns": len(user_texts)}

    n = len(meaningful)
    indices = {0}
    if n > 1: indices.add(n - 1)
    if n > 2: indices.add(n // 2)
    if n > 4: indices.add(n // 4)
    if n > 4: indices.add(3 * n // 4)

    exemplars = list(dict.fromkeys(
        meaningful[i] for i in sorted(indices) if i < len(meaningful)
    ))[:5]

    return {"exemplars": exemplars, "total_turns": len(user_texts)}


# ──────────────────────────────────────────────────────────────
# 내부 유틸
# ──────────────────────────────────────────────────────────────

def _get_length_range(segment: dict) -> tuple[int, int]:
    """
    에피소드 타입별 길이 범위. KEY_SCENE은 하위 타입 차등 적용.
    """
    episode_type = segment.get("type", "GENERAL_EVENT")
    if episode_type == "KEY_SCENE":
        subtype = segment.get("key_scene_type")
        if subtype and subtype in KEY_SCENE_SUBTYPE_RANGES:
            return KEY_SCENE_SUBTYPE_RANGES[subtype]
    return LENGTH_RANGES.get(episode_type, (300, 700))


def _needs_length_retry(narrative: str, segment: dict) -> bool:
    lo, hi = _get_length_range(segment)
    return not (lo <= len(narrative) <= hi)


def _should_accept_by_emotion_density(
    narrative: str,
    segment: dict,
    quality: dict,
) -> bool:
    """
    감정 밀도 기반 수용 판정 (McAdams Life Story Model).

    노인 인터뷰에서 짧지만 감정이 농축된 에피소드는
    길이 미달이어도 서사적 가치가 높을 수 있음.
    emotional_authenticity + personal_voice 모두 4.0 이상이고
    길이가 하한의 70% 이상이면 수용.
    """
    lo, _hi = _get_length_range(segment)
    if len(narrative) < lo * 0.7:
        return False

    emotion_auth = float(quality.get("emotional_authenticity", 0))
    personal_voice = float(quality.get("personal_voice", 0))
    return emotion_auth >= 4.0 and personal_voice >= 4.0


# ──────────────────────────────────────────────────────────────
# 단일 에피소드 서술 생성
# ──────────────────────────────────────────────────────────────

def _write_single(
    segment: dict,
    source_facts: list[str],
    style: dict,
    is_regeneration: bool = False,
    original_narrative: str = "",
    failed_facts: list[str] | None = None,
) -> dict:
    """
    단일 구간 에피소드 서술 생성.

    할루시네이션 방지 3중 전략:
      1. 명시적 Grounding Constraint (프롬프트)
      2. Atomic Fact Decomposition + self-verification (동시 출력)
      3. self-correction (재생성 시 실패 원인 명시)
    """
    episode_type = segment.get("type", "GENERAL_EVENT")
    turns = segment.get("turns", [])
    exemplars_text = format_exemplars(style)

    if is_regeneration and failed_facts:
        prompt = WRITER_REGEN_PROMPT.format(
            conversation=format_conversation(turns),
            source_facts=format_source_facts(source_facts),
            original_narrative=original_narrative,
            failed_facts="\n".join(f"- {f}" for f in failed_facts),
            metadata=format_metadata(segment),
            style_exemplars=exemplars_text,
            length_guide=format_length_guide(episode_type, LENGTH_RANGES),
        )
    else:
        prompt = WRITER_PROMPT.format(
            conversation=format_conversation(turns),
            source_facts=format_source_facts(source_facts),
            metadata=format_metadata(segment),
            style_exemplars=exemplars_text,
            length_guide=format_length_guide(episode_type, LENGTH_RANGES),
            sensory_hints=format_sensory(segment.get("sensory")),
            person_hints=format_persons(segment.get("persons", [])),
            bridge_hints=format_bridge_hints(segment),
        )

    raw = generate_reply(prompt)
    result = parse_llm_json(
        raw,
        f"writer[{segment.get('turn_start')}~{segment.get('turn_end')}]"
    )
    if not result:
        return make_fallback_result(segment)

    atomic_facts = result.get("atomic_facts", [])
    quality_data = build_quality_data(result.get("quality") or make_fallback_quality(), atomic_facts)
    quote = select_best_quote(result.get("quote"), QUOTE_PRIORITY)

    return {
        "narrative":          result.get("narrative", ""),
        "quote":              quote,
        "atomic_facts":       atomic_facts,
        "autobiography_hint": result.get("autobiography_hint"),
        "life_value":         result.get("life_value"),
        "emotion_nuance":     result.get("emotion_nuance"),
        "quality":            quality_data,
        "failed_facts":       extract_failed_facts(source_facts, atomic_facts),
    }


def _retry_if_length_invalid(
    result: dict,
    segment: dict,
    source_facts: list[str],
    style: dict,
) -> dict:
    """
    Self-Refine 패턴 길이 재시도 (Madaan et al. 2023).

    기존: 동일 프롬프트로 맹목적 재시도 → 같은 결과 반복.
    개선: 3단계 Progressive Retry.
      1차 시도: 이미 완료 (result).
      2차 시도: 이전 출력 + 구체적 피드백 (Self-Refine).
      3차 시도: 프레임 전환 재작성.
    3차까지 실패 → 감정 밀도 판정 → 완화 범위 수용.
    """
    narrative = result.get("narrative", "")
    quality = result.get("quality", {})

    # 1차: 길이 통과 시 즉시 반환
    if not _needs_length_retry(narrative, segment):
        return result

    # 감정 밀도 기반 수용 (짧지만 감정 농축된 에피소드 허용)
    if _should_accept_by_emotion_density(narrative, segment, quality):
        print(f"[episode_writer] 감정 밀도 높아 수용 ({len(narrative)}자)")
        return result

    lo, hi = _get_length_range(segment)
    print(f"[episode_writer] Self-Refine 재시도 (현재 {len(narrative)}자, 기준 {lo}~{hi}자)")

    # ── 2차: Self-Refine (구체적 피드백 포함) ─────────────────
    episode_type = segment.get("type", "GENERAL_EVENT")
    turns = segment.get("turns", [])
    exemplars_text = format_exemplars(style)
    sensory = segment.get("sensory")
    persons = segment.get("persons", [])

    sensory_hint = ""
    if sensory:
        sensory_items = [f"{k}: {v}" for k, v in sensory.items() if v]
        if sensory_items:
            sensory_hint = ", ".join(sensory_items)

    persons_hint = ""
    if persons:
        persons_hint = ", ".join(p.get("name", "?") for p in persons)

    retry_prompt = WRITER_LENGTH_RETRY_PROMPT.format(
        conversation=format_conversation(turns),
        source_facts=format_source_facts(source_facts),
        previous_narrative=narrative,
        current_length=len(narrative),
        target_lo=lo,
        target_hi=hi,
        sensory_hint=sensory_hint or "없음",
        persons_hint=persons_hint or "없음",
        metadata=format_metadata(segment),
        style_exemplars=exemplars_text,
        length_guide=format_length_guide(episode_type, LENGTH_RANGES),
    )

    raw = generate_reply(retry_prompt)
    retry_result = parse_llm_json(
        raw,
        f"writer_retry[{segment.get('turn_start')}~{segment.get('turn_end')}]",
    )

    if retry_result and retry_result.get("narrative"):
        atomic_facts = retry_result.get("atomic_facts", [])
        retry_quality = build_quality_data(
            retry_result.get("quality") or make_fallback_quality(), atomic_facts,
        )
        retry_narrative = retry_result["narrative"]

        if not _needs_length_retry(retry_narrative, segment):
            print(f"[episode_writer] Self-Refine 성공 ({len(retry_narrative)}자)")
            return {
                "narrative":          retry_narrative,
                "quote":              select_best_quote(retry_result.get("quote"), QUOTE_PRIORITY),
                "atomic_facts":       atomic_facts,
                "autobiography_hint": retry_result.get("autobiography_hint"),
                "life_value":         retry_result.get("life_value"),
                "emotion_nuance":     retry_result.get("emotion_nuance"),
                "quality":            retry_quality,
                "failed_facts":       extract_failed_facts(source_facts, atomic_facts),
            }

        # Self-Refine도 감정 밀도 수용 체크
        if _should_accept_by_emotion_density(retry_narrative, segment, retry_quality):
            print(f"[episode_writer] Self-Refine 감정 밀도 수용 ({len(retry_narrative)}자)")
            return {
                "narrative":          retry_narrative,
                "quote":              select_best_quote(retry_result.get("quote"), QUOTE_PRIORITY),
                "atomic_facts":       atomic_facts,
                "autobiography_hint": retry_result.get("autobiography_hint"),
                "life_value":         retry_result.get("life_value"),
                "emotion_nuance":     retry_result.get("emotion_nuance"),
                "quality":            retry_quality,
                "failed_facts":       extract_failed_facts(source_facts, atomic_facts),
            }

    # ── 3차: 프레임 전환 (완전 새 시도) ──────────────────────
    print("[episode_writer] 3차 시도: 프레임 전환 재작성")
    retry3 = _write_single(segment, source_facts, style)
    retry3_narrative = retry3.get("narrative", "")
    retry3_quality = retry3.get("quality", {})

    if not _needs_length_retry(retry3_narrative, segment):
        print(f"[episode_writer] 3차 성공 ({len(retry3_narrative)}자)")
        return retry3

    if _should_accept_by_emotion_density(retry3_narrative, segment, retry3_quality):
        print(f"[episode_writer] 3차 감정 밀도 수용 ({len(retry3_narrative)}자)")
        return retry3

    # ── 완화 범위 최종 수용 ──────────────────────────────────
    soft_lo = int(lo * 0.7)
    soft_hi = int(hi * 1.3)
    # 3개 중 가장 나은 것 선택 (길이가 완화 범위 안이면서 가장 길이 기준에 가까운 것)
    candidates = [
        (result, narrative),
        (retry3, retry3_narrative),
    ]
    for cand_result, cand_narrative in candidates:
        if soft_lo <= len(cand_narrative) <= soft_hi:
            print(f"[episode_writer] 완화 범위 수용 ({len(cand_narrative)}자, 완화 {soft_lo}~{soft_hi})")
            return cand_result

    print(f"[episode_writer] 3회 모두 실패, 원본 반환 ({len(narrative)}자)")
    return result


# ──────────────────────────────────────────────────────────────
# 메인 함수
# ──────────────────────────────────────────────────────────────

def write_episodes(
    segments: list[dict],
    source_facts: list[str],
    profile: UserProfileContext,
    max_workers: int = 5,
) -> list[dict]:
    """
    세그멘터 결과를 에피소드 서술로 변환 (병렬).

    Args:
        segments: episode_segmentor.segment_conversation() 반환값
        source_facts: 해당 세션 ChromaDB facts
        profile: UserProfileContext
        max_workers: 병렬 스레드 수
    """
    if not segments:
        return []

    print(f"[episode_writer] 시작: {len(segments)}개 구간 병렬 처리")

    def process_segment(seg: dict, idx: int) -> dict:
        turns = seg.get("turns", [])
        style = extract_style_exemplars(turns)
        result = _write_single(seg, source_facts, style)
        result = _retry_if_length_invalid(result, seg, source_facts, style)
        result["style_exemplars"] = style
        return result

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(process_segment, seg, i): i
            for i, seg in enumerate(segments)
        }
        results = [None] * len(segments)
        for future in concurrent.futures.as_completed(futures):
            idx = futures[future]
            try:
                results[idx] = future.result()
            except Exception as e:
                print(f"[episode_writer] 서술 생성 실패 idx={idx}: {e}")
                results[idx] = make_fallback_result(segments[idx])

    success = sum(1 for r in results if r.get("narrative"))
    print(f"[episode_writer] 완료: {success}/{len(segments)} 성공")
    return results


def regenerate_episode(
    segment: dict,
    source_facts: list[str],
    original_narrative: str,
    failed_facts: list[str],
) -> dict:
    """needs_regeneration=True 에피소드 재생성. episode_service에서 호출."""
    turns = segment.get("turns", [])
    style = extract_style_exemplars(turns)
    result = _write_single(
        segment=segment,
        source_facts=source_facts,
        style=style,
        is_regeneration=True,
        original_narrative=original_narrative,
        failed_facts=failed_facts,
    )
    result["style_exemplars"] = style
    return result