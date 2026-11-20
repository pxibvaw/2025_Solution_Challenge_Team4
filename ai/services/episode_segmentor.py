# ai/services/episode_segmentor.py
import concurrent.futures
from ai.clients.llm_gemini import generate_reply
from ai.app.schemas import UserProfileContext
from ai.prompts.episode_segmentor_prompts import (
    PASS1_BOUNDARY_PROMPT,
    PASS2_ENRICH_PROMPT,
    METADATA_PROMPT,
)
from ai.utils.episode_formatters import (
    format_conversation,
    format_existing_episodes,
    parse_llm_json,
)


# ──────────────────────────────────────────────────────────────
# segmentor 고유 fallback (formatters에 없는 segmentor 전용)
# ──────────────────────────────────────────────────────────────

def _make_fallback_segment(session_log: list[dict]) -> list[dict]:
    """전체 대화를 하나의 구간으로 묶는 fallback."""
    return [{
        "turn_start": 0,
        "turn_end": len(session_log) - 1,
        "narrative_direction": None,
        "dominant_emotion": None,
        "life_value_hint": None,
        "merge_action": "NEW",
        "merge_target_id": None,
        "merge_reason": None,
    }]


def _make_fallback_metadata(start: int, end: int) -> dict:
    """메타데이터 추출 실패 시 기본값."""
    return {
        "title": f"#{start}~{end}번 대화",
        "type": "GENERAL_EVENT",
        "key_scene_type": None,
        "theme": "기타",
        "emotion_tone": "중립",
        "emotion_nuance": None,
        "time_hint": None,
        "period_label": None,
        "estimated_year_range": None,
        "location": None,
        "persons": [],
        "sensory": None,
    }


# ──────────────────────────────────────────────────────────────
# Pass 1: 이벤트 경계 감지
# ──────────────────────────────────────────────────────────────

def _pass1_detect_boundaries(session_log: list[dict]) -> list[int]:
    """
    1패스: 주제 전환 경계만 빠르게 감지.

    Event Segmentation Theory (Zacks & Swallow, 2007) 기반.
    의미 있는 전환점만 탐지해 oversegmentation 방지.

    Returns:
        새 에피소드가 시작되는 턴 인덱스 배열.
        (0은 항상 첫 에피소드 시작이므로 제외)
    """
    conversation_text = format_conversation(session_log)
    prompt = PASS1_BOUNDARY_PROMPT.format(conversation=conversation_text)
    raw = generate_reply(prompt)
    result = parse_llm_json(raw, "pass1")

    boundaries = result.get("boundaries", [])
    max_turn = len(session_log) - 1

    valid = sorted(set(
        b for b in boundaries
        if isinstance(b, int) and 1 <= b <= max_turn
    ))
    return valid


# ──────────────────────────────────────────────────────────────
# Pass 2: 경계 병합 + 비선형 처리 + 브릿지 힌트 추출
# ──────────────────────────────────────────────────────────────

def _pass2_merge_and_enrich(
    session_log: list[dict],
    boundaries: list[int],
    profile: UserProfileContext,
    existing_episodes: list[dict],
) -> list[dict]:
    """
    2패스: 1패스 경계를 재검토해 비선형 노인 대화 처리 + 브릿지 힌트 추출.

    브릿지 힌트는 episode_writer에게 전달되어 서술 품질을 높이는 레퍼런스로 활용됨.
      narrative_direction: 서술 방향 힌트
      dominant_emotion: 지배적 감정 뉘앙스
      life_value_hint: 드러나는 삶의 가치 후보

    Returns:
        segments: [{turn_start, turn_end, 브릿지 힌트 3개, merge 정보}]
    """
    conversation_text = format_conversation(session_log)
    existing_text = format_existing_episodes(existing_episodes)

    # profile=None 방어: BE가 profile 안 보내고 _session_profiles 캐시도 비었을 때
    # (AI 서버 재시작 / 1시간 TTL 만료 등) AttributeError 방지를 위해 fallback 값 사용.
    prompt = PASS2_ENRICH_PROMPT.format(
        conversation=conversation_text,
        boundaries=str(boundaries) if boundaries else "[]",
        existing_episodes=existing_text,
        user_title=profile.userTitle if profile else "사용자",
        memorable_age=(profile.memorableAge if profile else None) or "미입력",
        birth_year=(profile.birthYear if profile else None) or "미입력",
    )
    raw = generate_reply(prompt)
    result = parse_llm_json(raw, "pass2")
    segments = result.get("segments", [])

    if not segments:
        print("[episode_segmentor] pass2 응답 없음 → fallback 사용")
        return _make_fallback_segment(session_log)

    max_turn = len(session_log) - 1
    valid_segments = []
    for seg in segments:
        start = max(0, int(seg.get("turn_start", 0)))
        end = min(max_turn, int(seg.get("turn_end", max_turn)))
        if start > end:
            continue
        valid_segments.append({
            "turn_start": start,
            "turn_end": end,
            "narrative_direction": seg.get("narrative_direction"),
            "dominant_emotion": seg.get("dominant_emotion"),
            "life_value_hint": seg.get("life_value_hint"),
            "merge_action": seg.get("merge_action", "NEW"),
            "merge_target_id": seg.get("merge_target_id"),
            "merge_reason": seg.get("merge_reason"),
        })

    if not valid_segments:
        print("[episode_segmentor] pass2 유효 구간 없음 → fallback 사용")
        return _make_fallback_segment(session_log)

    return valid_segments


# ──────────────────────────────────────────────────────────────
# Pass 3: 메타데이터 추출 (구간별 병렬)
# ──────────────────────────────────────────────────────────────

def _extract_metadata(
    segment: dict,
    session_log: list[dict],
    profile: UserProfileContext,
) -> dict:
    """
    단일 구간의 메타데이터 추출.
    2패스의 브릿지 힌트를 레퍼런스로 활용해 추출 정확도 향상.
    """
    start = segment["turn_start"]
    end = segment["turn_end"]
    segment_conv = format_conversation(session_log, start, end)

    # profile=None 방어 (_pass2_merge_and_enrich과 동일 정책)
    prompt = METADATA_PROMPT.format(
        segment_conversation=segment_conv,
        narrative_direction=segment.get("narrative_direction") or "없음",
        dominant_emotion=segment.get("dominant_emotion") or "없음",
        life_value_hint=segment.get("life_value_hint") or "없음",
        user_title=profile.userTitle if profile else "사용자",
        memorable_age=(profile.memorableAge if profile else None) or "미입력",
        birth_year=(profile.birthYear if profile else None) or "미입력",
    )
    raw = generate_reply(prompt)
    meta = parse_llm_json(raw, f"metadata[{start}~{end}]")

    if not meta:
        return _make_fallback_metadata(start, end)
    return meta


def _extract_metadata_parallel(
    segments: list[dict],
    session_log: list[dict],
    profile: UserProfileContext,
    max_workers: int = 5,
) -> list[dict]:
    """
    모든 구간의 메타데이터를 병렬로 추출.
    개별 실패 시 fallback 사용, 전체 중단 없음.
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(_extract_metadata, seg, session_log, profile): i
            for i, seg in enumerate(segments)
        }
        results = [None] * len(segments)
        for future in concurrent.futures.as_completed(futures):
            idx = futures[future]
            try:
                results[idx] = future.result()
            except Exception as e:
                print(f"[episode_segmentor] 메타데이터 추출 실패 idx={idx}: {e}")
                seg = segments[idx]
                results[idx] = _make_fallback_metadata(
                    seg["turn_start"], seg["turn_end"]
                )
    return results


# ──────────────────────────────────────────────────────────────
# 메인 함수
# ──────────────────────────────────────────────────────────────

def segment_conversation(
    session_log: list[dict],
    profile: UserProfileContext,
    existing_episodes: list[dict] = [],
) -> list[dict]:
    """
    대화 로그를 에피소드 후보 구간으로 분리.

    B-1 방식 3단계 파이프라인:
      Pass 1 — 이벤트 경계 감지 (EST 기반, 1회 호출)
      Pass 2 — 경계 병합 + 비선형 처리 + 브릿지 힌트 추출 (1회 호출)
      Pass 3 — 구간별 메타데이터 추출 (병렬, N회 호출)

    Args:
        session_log: interview_service._sessions[session_id] 전체
        profile: 사용자 프로필 (UserProfileContext)
        existing_episodes: Spring Boot에서 받은 기존 에피소드 목록

    Returns:
        list[dict]: 에피소드 후보 구간 목록
        각 항목 포함 필드:
          turn_start, turn_end           구간 인덱스
          turns                          원본 대화 (G-Eval reference용)
          title, type, key_scene_type    McAdams 분류
          theme, emotion_tone, emotion_nuance
          time_hint, period_label, estimated_year_range
          location, persons, sensory     Conway SMS 4축
          narrative_direction            writer 서술 방향 힌트
          dominant_emotion               writer 감정 힌트
          life_value_hint                writer 삶의 가치 힌트
          merge_action, merge_target_id  StorySage 보강 판단
          merge_reason
    """
    if not session_log:
        print("[episode_segmentor] session_log 비어있음")
        return []

    print(f"[episode_segmentor] 시작: {len(session_log)}턴")

    boundaries = _pass1_detect_boundaries(session_log)
    print(f"[episode_segmentor] pass1 완료 | 경계: {boundaries}")

    segments = _pass2_merge_and_enrich(
        session_log, boundaries, profile, existing_episodes
    )
    print(f"[episode_segmentor] pass2 완료 | 구간: {len(segments)}개")

    metadata_list = _extract_metadata_parallel(segments, session_log, profile)
    print(f"[episode_segmentor] pass3 완료 | 메타데이터: {len(metadata_list)}개")

    final_segments = []
    for seg, meta in zip(segments, metadata_list):
        start = seg["turn_start"]
        end = seg["turn_end"]
        final_segments.append({
            "turn_start": start,
            "turn_end": end,
            "turns": session_log[start: end + 1],

            "title":          meta.get("title", f"에피소드 {start}~{end}"),
            "type":           meta.get("type", "GENERAL_EVENT"),
            "key_scene_type": meta.get("key_scene_type"),
            "theme":          meta.get("theme", "기타"),
            "emotion_tone":   meta.get("emotion_tone", "중립"),
            "emotion_nuance": meta.get("emotion_nuance"),

            "time_hint":            meta.get("time_hint"),
            "period_label":         meta.get("period_label"),
            "estimated_year_range": meta.get("estimated_year_range"),

            "location": meta.get("location"),
            "persons":  meta.get("persons", []),
            "sensory":  meta.get("sensory"),

            "narrative_direction": seg.get("narrative_direction"),
            "dominant_emotion":    seg.get("dominant_emotion"),
            "life_value_hint":     seg.get("life_value_hint"),

            "merge_action":    seg.get("merge_action", "NEW"),
            "merge_target_id": seg.get("merge_target_id"),
            "merge_reason":    seg.get("merge_reason"),
        })

    print(f"[episode_segmentor] 완료: {len(final_segments)}개 에피소드 후보")
    return final_segments