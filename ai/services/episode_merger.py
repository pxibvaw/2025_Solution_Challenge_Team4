# ai/services/episode_merger.py
import concurrent.futures
from dataclasses import dataclass
from datetime import datetime, timezone
from ai.clients.llm_gemini import generate_reply
from ai.prompts.episode_merger_prompts import MERGER_PROMPT
from ai.services.episode_writer import (
    extract_style_exemplars,
    QUOTE_PRIORITY,
)
from ai.utils.episode_formatters import (
    format_conversation,
    format_source_facts,
    format_metadata,
    format_sensory,
    format_persons,
    format_length_guide,
    parse_llm_json,
    select_best_quote,
    extract_failed_facts,
    make_fallback_quality,
    merge_source_facts,
    calc_richness_from_quality,
    format_exemplars,    # ← 추가
    build_quality_data,  # ← 추가
    LENGTH_RANGES,       # ← 추가
)


# ──────────────────────────────────────────────────────────────
# 결과 타입
# ──────────────────────────────────────────────────────────────

@dataclass
class MergeResult:
    """
    에피소드 보강 결과.

    reason:
      "success"           보강 완료
      "quality_degraded"  보강 후 품질 저하 → 원본 유지
      "generation_failed" LLM 생성 실패
      "target_not_found"  existing_episodes에서 target 없음
      "no_target_id"      merge_target_id 미설정
    """
    was_merged: bool
    episode: dict
    reason: str


# ──────────────────────────────────────────────────────────────
# 통합 에피소드 생성
# ──────────────────────────────────────────────────────────────

def _run_merge(
    existing_episode: dict,
    new_segment: dict,
    merged_facts: list[str],
    style: dict,
) -> dict:
    """기존 에피소드 + 새 대화 구간 → LLM 통합 재생성."""
    episode_type = existing_episode.get("type", "GENERAL_EVENT")
    new_turns = new_segment.get("turns", [])

    existing_fact_set = set(existing_episode.get("source_facts", []))
    new_only_facts = [f for f in merged_facts if f not in existing_fact_set]

    prompt = MERGER_PROMPT.format(
        original_narrative=existing_episode.get("narrative", ""),
        original_facts=format_source_facts(existing_episode.get("source_facts", [])),
        new_conversation=format_conversation(new_turns),
        new_facts=format_source_facts(new_only_facts) if new_only_facts else "없음",
        metadata=format_metadata({
            **new_segment,
            "type":        existing_episode.get("type", new_segment.get("type", "GENERAL_EVENT")),
            "theme":       existing_episode.get("theme", new_segment.get("theme", "기타")),
            "emotion_tone": existing_episode.get("emotion_tone", new_segment.get("emotion_tone", "중립")),
        }),
        style_exemplars=format_exemplars(style),
        length_guide=format_length_guide(episode_type, LENGTH_RANGES),
        sensory_hints=format_sensory(new_segment.get("sensory")),
        person_hints=format_persons(new_segment.get("persons", [])),
    )

    raw = generate_reply(prompt)
    result = parse_llm_json(raw, f"merger[{existing_episode.get('id')}]")
    if not result:
        return {}

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
        "failed_facts":       extract_failed_facts(merged_facts, atomic_facts),
    }


def _build_merged_episode(
    original_episode: dict,
    write_result: dict,
    new_segment: dict,
    merged_facts: list[str],
) -> dict:
    """보강 완료된 에피소드 dict 조립."""
    now = datetime.now(timezone.utc).isoformat()

    existing_sensory = original_episode.get("sensory") or {}
    new_sensory = new_segment.get("sensory") or {}
    merged_sensory = {**existing_sensory, **{k: v for k, v in new_sensory.items() if v}}

    existing_names = {p.get("name") for p in original_episode.get("persons", [])}
    merged_persons = original_episode.get("persons", []) + [
        p for p in new_segment.get("persons", [])
        if p.get("name") not in existing_names
    ]

    return {
        **original_episode,
        "narrative":          write_result.get("narrative", original_episode.get("narrative", "")),
        "quote":              write_result.get("quote") or original_episode.get("quote"),
        "autobiography_hint": write_result.get("autobiography_hint") or original_episode.get("autobiography_hint"),
        "life_value":         write_result.get("life_value") or original_episode.get("life_value"),
        "emotion_nuance":     write_result.get("emotion_nuance") or original_episode.get("emotion_nuance"),
        "quality":            write_result.get("quality"),
        "source_facts":       merged_facts,
        "sensory":            merged_sensory if any(merged_sensory.values()) else original_episode.get("sensory"),
        "persons":            merged_persons,
        "is_merged":          True,
        "merged_from":        original_episode.get("id"),
        "version":            original_episode.get("version", 1) + 1,
        "updated_at":         now,
    }


# ──────────────────────────────────────────────────────────────
# 단일 에피소드 보강
# ──────────────────────────────────────────────────────────────

def merge_episode(
    existing_episode: dict,
    new_segment: dict,
    new_session_facts: list[str],
) -> MergeResult:
    """
    기존 에피소드 + 새 세션 구간 → MergeResult.

    품질 비교는 EpisodeQuality.narrative_richness 활용
    → settings 가중치 단일 소스 보장.
    """
    episode_id = existing_episode.get("id", "?")
    merged_facts = merge_source_facts(
        existing_episode.get("source_facts", []),
        new_session_facts,
    )
    style = extract_style_exemplars(new_segment.get("turns", []))
    write_result = _run_merge(existing_episode, new_segment, merged_facts, style)

    if not write_result or not write_result.get("narrative"):
        return MergeResult(False, existing_episode, "generation_failed")

    original_quality = existing_episode.get("quality") or make_fallback_quality()
    new_quality = write_result.get("quality", make_fallback_quality())

    orig_richness = calc_richness_from_quality(original_quality)
    new_richness = calc_richness_from_quality(new_quality)

    if new_richness < orig_richness:
        print(
            f"[episode_merger] 품질 저하 → 원본 유지: {episode_id} "
            f"({orig_richness:.3f} → {new_richness:.3f})"
        )
        return MergeResult(False, existing_episode, "quality_degraded")

    merged = _build_merged_episode(existing_episode, write_result, new_segment, merged_facts)
    print(
        f"[episode_merger] 보강 완료: {episode_id} v{merged['version']} "
        f"({orig_richness:.3f} → {new_richness:.3f})"
    )
    return MergeResult(True, merged, "success")


# ──────────────────────────────────────────────────────────────
# 병렬 배치 처리
# ──────────────────────────────────────────────────────────────

def process_merges(
    segments: list[dict],
    existing_episodes: list[dict],
    new_session_facts: list[str],
    max_workers: int = 5,
) -> tuple[list[dict], list[dict]]:
    """
    MERGE 대상 구간들을 병렬 처리.
    episode_service.py에서 호출.

    Returns:
        (new_segments, merged_episodes)
        new_segments: NEW 구간 + 보강 실패 구간 (merge_action=NEW로 변환)
        merged_episodes: 보강 성공 에피소드들
    """
    episode_map = {ep["id"]: ep for ep in existing_episodes if ep.get("id")}

    merge_jobs: list[tuple[dict, dict]] = []
    new_segments: list[dict] = []

    for seg in segments:
        if seg.get("merge_action") != "MERGE":
            new_segments.append(seg)
            continue
        target_id = seg.get("merge_target_id")
        if not target_id:
            new_segments.append({**seg, "merge_action": "NEW",
                                  "_merge_skip_reason": "no_target_id"})
            continue
        target_ep = episode_map.get(target_id)
        if not target_ep:
            new_segments.append({**seg, "merge_action": "NEW",
                                  "_merge_skip_reason": "target_not_found"})
            continue
        merge_jobs.append((seg, target_ep))

    merged_episodes: list[dict] = []

    if merge_jobs:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(merge_episode, ep, seg, new_session_facts): (seg, ep)
                for seg, ep in merge_jobs
            }
            for future in concurrent.futures.as_completed(futures):
                seg, ep = futures[future]
                try:
                    result: MergeResult = future.result()
                    if result.was_merged:
                        merged_episodes.append(result.episode)
                    else:
                        print(f"[episode_merger] 보강 실패 ({result.reason}): {ep.get('id')}")
                        new_segments.append({
                            **seg,
                            "merge_action": "NEW",
                            "_merge_skip_reason": result.reason,
                        })
                except Exception as e:
                    print(f"[episode_merger] 예외: {e}")
                    new_segments.append({
                        **seg,
                        "merge_action": "NEW",
                        "_merge_skip_reason": "exception",
                    })

    print(
        f"[episode_merger] 완료: NEW {len(new_segments)}개 / "
        f"MERGED {len(merged_episodes)}개"
    )
    return new_segments, merged_episodes
