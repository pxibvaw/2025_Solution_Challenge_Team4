# ai/services/autobiography_service.py
"""
자서전 생성 서비스.

처리 순서:
  1. 에피소드 정렬 + 시기별 그룹핑 (코드 처리)
  2. Planner LLM (1회) → 챕터 구조 + life_theme
  3. Chapter Writer LLM (N회 병렬) → 챕터별 서술
  4. Prologue / Epilogue LLM (각 1회)

논문 근거:
  StorySage (UIST 2025): Planner/Section Writer 분리 구조
  DOME (NAACL 2025): 계층적 outline → 챕터별 독립 생성 (Lost in the Middle 방지)
  McAdams (2008): 시기별 chapter + life_theme 구조
  Butler Life Review Theory (1963): quote 직접 포함 → "내 이야기" 체험
"""
import logging
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

from ai.app.schemas import (
    AutobiographyRequest,
    AutobiographyChapter,
    AutobiographyResponse,
)
from ai.clients.llm_gemini import generate_reply
from ai.prompts.autobiography_planner_prompt import PLANNER_PROMPT
from ai.prompts.autobiography_chapter_prompt import CHAPTER_PROMPT
from ai.prompts.autobiography_frame_prompt import PROLOGUE_PROMPT, EPILOGUE_PROMPT
from ai.utils.episode_formatters import (
    format_exemplars,
    parse_llm_json,
    calc_faithfulness,
)

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────
# 상수
# ──────────────────────────────────────────────────────────────

_MAX_CHAPTERS = 6
_MAX_EP_PER_CHAPTER = 4
_FAITHFULNESS_THRESHOLD = 0.70   # 챕터 재생성 기준
_CHAPTER_MAX_WORKERS = 6


# ──────────────────────────────────────────────────────────────
# Step 1 헬퍼: 시간순 정렬 / 그룹핑 / 포맷
#
# 설계 근거:
#   McAdams Life Story Model (2008): 생애단계별 chapter 구조.
#   DOME (NAACL 2025): Temporal Knowledge Graph로 시간 순서 보장.
#   Butler Life Review Theory (1963): 유년기→현재 순서의
#     시간순 회고가 치료 효과에 핵심.
#   Multi-tier 정렬: 연대 → 나이대 → 생애단계 → 미상.
# ──────────────────────────────────────────────────────────────

# McAdams 생애단계 정렬 프레임
_LIFE_STAGE_ORDER: dict[str, int] = {
    "유년기": 0, "어린 시절": 0, "유아기": 0,
    "청소년기": 1, "학창 시절": 1, "학생 시절": 1,
    "청년기": 2, "청년 시절": 2, "젊은 시절": 2,
    "중년기": 3, "중년": 3,
    "장년기": 4, "장년": 4,
    "노년기": 5, "노년": 5, "현재": 5,
}

# 연대 파싱: "1970년대" → 1975
_RE_DECADE = re.compile(r"(\d{4})년대")
# 나이대 파싱: "30대" → 30
_RE_AGE_RANGE = re.compile(r"(\d{1,3})대")


def _parse_period_sort_key(
    period_label: str,
    birth_year: int | None = None,
) -> tuple[int, float]:
    """
    period_label을 정렬 가능한 (tier, value) 튜플로 변환.

    Multi-tier 정렬:
      Tier 1: 연대 ("1970년대") → midpoint(1975)
      Tier 2: 나이대 ("30대") + birth_year → 절대 연도
      Tier 3: 생애단계 ("어린 시절") → _LIFE_STAGE_ORDER
      Tier 4: 미상 → inf (원래 순서 유지)

    Args:
        period_label: 에피소드의 시기 라벨
        birth_year:   사용자 출생연도 (나이대 → 절대연도 변환용)

    Returns:
        (tier, sortable_value) — 낮을수록 먼저
    """
    if not period_label:
        return (4, float("inf"))

    label = period_label.strip()

    # Tier 1: 연대 ("1970년대" → 1975)
    m = _RE_DECADE.search(label)
    if m:
        return (1, float(int(m.group(1)) + 5))

    # Tier 2: 나이대 ("30대" → birth_year + 35)
    m = _RE_AGE_RANGE.search(label)
    if m and "년대" not in label:
        age = int(m.group(1))
        if birth_year:
            return (2, float(birth_year + age + 5))
        # birth_year 없으면 나이 자체로 정렬 (상대값)
        return (2, float(age))

    # Tier 3: 생애단계 키워드 매칭
    for keyword, order in _LIFE_STAGE_ORDER.items():
        if keyword in label:
            return (3, float(order))

    # Tier 4: 파싱 불가
    return (4, float("inf"))


def _group_episodes_by_period(episodes: list[dict]) -> dict[str, list[dict]]:
    """
    period_label → time_hint → estimated_year_range → "기타" 순으로 그룹핑.
    그룹 내부는 importance_score 내림차순.
    """
    groups: dict[str, list[dict]] = {}
    for ep in episodes:
        key = (
            ep.get("period_label")
            or ep.get("time_hint")
            or ep.get("estimated_year_range")
            or "기타"
        )
        groups.setdefault(key, []).append(ep)
    for key in groups:
        groups[key].sort(key=lambda e: e.get("importance_score", 0), reverse=True)
    return groups


def _sort_groups_chronologically(
    groups: dict[str, list[dict]],
    birth_year: int | None = None,
) -> dict[str, list[dict]]:
    """
    그룹 키(period_label)를 시간순으로 정렬.
    Python 3.7+ dict는 삽입 순서 보장 → 정렬된 순서로 재구성.
    Planner에 시간순으로 전달되어 챕터 순서 보장.
    """
    sorted_keys = sorted(
        groups.keys(),
        key=lambda k: _parse_period_sort_key(k, birth_year),
    )
    return {k: groups[k] for k in sorted_keys}


def _prepare_episodes(
    episodes: list[dict],
    birth_year: int | None = None,
) -> tuple[dict[str, list[dict]], list[dict]]:
    """
    에피소드 시간순 정렬 + 그룹핑 + 챕터/에피소드 수 제한.

    Returns:
        groups: {period: [episode, ...]} — 시간순, 챕터당 max 4개
        sorted_eps: importance_score 내림차순 전체 목록
    """
    if not episodes:
        raise ValueError("에피소드가 없습니다.")

    sorted_eps = sorted(
        episodes,
        key=lambda e: e.get("importance_score", 0),
        reverse=True,
    )
    groups = _group_episodes_by_period(sorted_eps)

    # 시간순 정렬 (McAdams 생애단계 프레임)
    groups = _sort_groups_chronologically(groups, birth_year)

    # 챕터당 max 4개
    groups = {k: v[:_MAX_EP_PER_CHAPTER] for k, v in groups.items()}

    # max 6챕터 — 초과 시 importance 상위 챕터만 유지
    if len(groups) > _MAX_CHAPTERS:
        top_keys = sorted(
            groups,
            key=lambda k: max(e.get("importance_score", 0) for e in groups[k]),
            reverse=True,
        )[:_MAX_CHAPTERS]
        # 선별 후 다시 시간순 정렬
        groups = _sort_groups_chronologically(
            {k: groups[k] for k in top_keys}, birth_year,
        )

    return groups, sorted_eps


def _format_episode_summary(ep: dict) -> str:
    return (
        f"[{ep.get('id')}] {ep.get('title')} | "
        f"theme: {ep.get('theme')} | tone: {ep.get('emotion_tone')} | "
        f"period: {ep.get('period_label') or '미상'} | "
        f"life_value: {ep.get('life_value') or '없음'} | "
        f"importance: {ep.get('importance_score', 5.0)}\n"
        f"  quote: {ep.get('quote') or '없음'}"
    )


def _format_chapter_narratives(eps: list[dict]) -> str:
    parts = [
        f"[{ep.get('id')}] {ep.get('title')}\n{ep.get('narrative', '')}"
        for ep in eps
        if ep.get("narrative")
    ]
    return "\n\n".join(parts) if parts else "없음"


def _format_chapter_quotes(eps: list[dict]) -> str:
    quotes = [ep["quote"] for ep in eps if ep.get("quote")]
    return "\n".join(quotes) if quotes else "없음"


def _extract_chapter_exemplars(eps: list[dict]) -> dict:
    exemplars = []
    for ep in eps:
        exemplars.extend(ep.get("style_exemplars", {}).get("exemplars", []))
    return {"exemplars": list(dict.fromkeys(exemplars))[:5]}


def _select_top_quote(eps: list[dict]) -> str:
    sorted_eps = sorted(eps, key=lambda e: e.get("importance_score", 0), reverse=True)
    for ep in sorted_eps:
        if ep.get("quote"):
            return ep["quote"]
    return ""


def _format_chapter_titles(chapters: list[dict]) -> str:
    return "\n".join(f"{i+1}. {ch.get('title', '챕터')}" for i, ch in enumerate(chapters))


# ──────────────────────────────────────────────────────────────
# Step 2: Planner
# ──────────────────────────────────────────────────────────────

def _run_planner(
    groups: dict[str, list[dict]],
    all_episodes: list[dict],
    profile,
) -> dict:
    """
    에피소드 요약(title+quote)만 입력 → outline + life_theme 반환.
    새 사실 생성 불가 구조로 할루시네이션 원천 차단.
    """
    summaries = []
    for period, eps in groups.items():
        summaries.append(f"\n[{period}]")
        for ep in eps:
            summaries.append(_format_episode_summary(ep))

    prompt = PLANNER_PROMPT.format(
        user_title=profile.userTitle if profile else "사용자",
        birth_year=str(getattr(profile, "birthYear", None) or "미입력"),
        memorable_age=getattr(profile, "memorableAge", None) or "미입력",
        episode_count=len(all_episodes),
        episode_summaries="\n".join(summaries),
        max_chapters=_MAX_CHAPTERS,
    )

    raw = generate_reply(prompt)
    result = parse_llm_json(raw, "planner")

    if not result or "chapters" not in result:
        logger.warning("[autobiography] Planner 실패 → fallback 구조 사용")
        return _make_fallback_planner(groups)

    return result


def _make_fallback_planner(groups: dict[str, list[dict]]) -> dict:
    """Planner 실패 시 period_label 기반 기본 구조."""
    chapters = [
        {
            "title": period,
            "period_label": period,
            "episode_ids": [ep["id"] for ep in eps],
            "core_theme": "삶",
            "emotional_arc": "기억 → 회상",
            "transition_hint": "그렇게 시간이 흘렀다.",
        }
        for period, eps in groups.items()
    ]
    return {"life_theme": "소중한 삶의 기억들", "chapters": chapters}


# ──────────────────────────────────────────────────────────────
# Step 3: Chapter Writer (병렬)
# ──────────────────────────────────────────────────────────────

def _write_chapter(
    chapter_plan: dict,
    chapter_eps: list[dict],
    life_theme: str,
    retry: bool = False,
) -> dict:
    """
    단일 챕터 생성.
    해당 챕터 에피소드만 입력 → Lost in the Middle 방지.
    atomic_facts 자기검증으로 hallucination 탐지.
    """
    ep_count = len(chapter_eps)
    length_guide = "500~800자" if ep_count == 1 else "800~1500자"

    chapter_exemplars = _extract_chapter_exemplars(chapter_eps)

    prompt = CHAPTER_PROMPT.format(
        life_theme=life_theme,
        chapter_title=chapter_plan.get("title", ""),
        core_theme=chapter_plan.get("core_theme", "삶"),
        emotional_arc=chapter_plan.get("emotional_arc", ""),
        transition_hint=chapter_plan.get("transition_hint", ""),
        style_exemplars=format_exemplars(chapter_exemplars),
        episode_narratives=_format_chapter_narratives(chapter_eps),
        episode_quotes=_format_chapter_quotes(chapter_eps),
        length_guide=length_guide,
    )

    raw = generate_reply(prompt)
    result = parse_llm_json(raw, f"chapter[{chapter_plan.get('title')}]")

    if not result or not result.get("narrative"):
        logger.warning(f"[autobiography] 챕터 생성 실패: {chapter_plan.get('title')}")
        return {
            "narrative": _make_fallback_chapter_narrative(chapter_eps),
            "faithfulness_score": 0.0,
        }

    atomic_facts = result.get("atomic_facts", [])
    computed_faith = calc_faithfulness(atomic_facts)
    llm_faith = float(result.get("faithfulness_score", 0.5))
    final_faith = min(computed_faith, llm_faith)

    return {
        "narrative": result["narrative"],
        "faithfulness_score": final_faith,
        "atomic_facts": atomic_facts,
    }


def _make_fallback_chapter_narrative(chapter_eps: list[dict]) -> str:
    """챕터 생성 실패 시 에피소드 narratives 직접 연결."""
    parts = [ep.get("narrative", "") for ep in chapter_eps if ep.get("narrative")]
    return "\n\n".join(parts) if parts else ""


def _run_chapters(
    outline: dict,
    ep_map: dict[str, dict],
    life_theme: str,
) -> list[dict]:
    """
    챕터별 병렬 생성.
    faithfulness 낮으면 1회 재생성.
    """
    chapter_plans = outline.get("chapters", [])
    results: list[dict | None] = [None] * len(chapter_plans)

    def process(chapter_plan: dict, idx: int) -> dict:
        ep_ids = chapter_plan.get("episode_ids", [])
        chapter_eps = [ep_map[eid] for eid in ep_ids if eid in ep_map]

        if not chapter_eps:
            logger.warning(f"[autobiography] 챕터 에피소드 없음: {chapter_plan.get('title')}")
            return {"narrative": "", "faithfulness_score": 0.0}

        result = _write_chapter(chapter_plan, chapter_eps, life_theme)

        # faithfulness 낮으면 1회 재생성
        if result["faithfulness_score"] < _FAITHFULNESS_THRESHOLD:
            logger.info(
                f"[autobiography] 챕터 재생성: {chapter_plan.get('title')} "
                f"(faithfulness={result['faithfulness_score']:.3f})"
            )
            retry_result = _write_chapter(chapter_plan, chapter_eps, life_theme, retry=True)
            if retry_result.get("narrative"):
                result = retry_result

        return result

    with ThreadPoolExecutor(max_workers=_CHAPTER_MAX_WORKERS) as executor:
        futures = {
            executor.submit(process, plan, i): i
            for i, plan in enumerate(chapter_plans)
        }
        for future in as_completed(futures):
            idx = futures[future]
            try:
                results[idx] = future.result()
            except Exception as e:
                logger.error(f"[autobiography] 챕터 예외 idx={idx}: {e}")
                ep_ids = chapter_plans[idx].get("episode_ids", [])
                chapter_eps = [ep_map[eid] for eid in ep_ids if eid in ep_map]
                results[idx] = {
                    "narrative": _make_fallback_chapter_narrative(chapter_eps),
                    "faithfulness_score": 0.0,
                }

    return [r for r in results if r is not None]


# ──────────────────────────────────────────────────────────────
# Step 4: Prologue / Epilogue
# ──────────────────────────────────────────────────────────────

def _run_prologue(
    life_theme: str,
    chapter_plans: list[dict],
    all_episodes: list[dict],
) -> str:
    all_exemplars = []
    for ep in all_episodes:
        all_exemplars.extend(ep.get("style_exemplars", {}).get("exemplars", []))

    prompt = PROLOGUE_PROMPT.format(
        life_theme=life_theme,
        chapter_titles=_format_chapter_titles(chapter_plans),
        top_quote=_select_top_quote(all_episodes),
        style_exemplars=format_exemplars({"exemplars": list(dict.fromkeys(all_exemplars))[:5]}),
    )

    raw = generate_reply(prompt)
    result = parse_llm_json(raw, "prologue")
    prologue = result.get("prologue", "")

    if not prologue:
        logger.warning("[autobiography] Prologue 생성 실패 → life_theme으로 대체")
        return life_theme
    return prologue


def _run_epilogue(
    life_theme: str,
    last_chapter_plan: dict,
    all_episodes: list[dict],
) -> str:
    all_exemplars = []
    for ep in all_episodes:
        all_exemplars.extend(ep.get("style_exemplars", {}).get("exemplars", []))

    prompt = EPILOGUE_PROMPT.format(
        life_theme=life_theme,
        last_chapter_emotional_arc=last_chapter_plan.get("emotional_arc", ""),
        top_quote=_select_top_quote(all_episodes),
        style_exemplars=format_exemplars({"exemplars": list(dict.fromkeys(all_exemplars))[:5]}),
    )

    raw = generate_reply(prompt)
    result = parse_llm_json(raw, "epilogue")
    epilogue = result.get("epilogue", "")

    if not epilogue:
        logger.warning("[autobiography] Epilogue 생성 실패 → life_theme으로 대체")
        return life_theme
    return epilogue


# ──────────────────────────────────────────────────────────────
# 메인 함수
# ──────────────────────────────────────────────────────────────

def generate_autobiography(
    request: AutobiographyRequest,
    profile=None,
) -> AutobiographyResponse:
    """
    자서전 생성 파이프라인 전체 실행.
    api.py에서 직접 호출 (동기).

    Args:
        request: AutobiographyRequest
                 (selectedEpisodeIds, episodes: list[Episode])
        profile: UserProfileContext (optional)

    Returns:
        AutobiographyResponse (prologue, chapters, epilogue, life_theme)
    """
    episodes = [ep.dict() if hasattr(ep, "dict") else ep for ep in request.episodes]

    if not episodes:
        raise ValueError("에피소드가 없습니다. 에피소드를 먼저 생성해주세요.")

    logger.info(f"[autobiography] 시작: {len(episodes)}개 에피소드")

    # ── Step 1: 시간순 정렬 + 그룹핑 ─────────────────────────
    birth_year = getattr(profile, "birthYear", None) if profile else None
    groups, sorted_eps = _prepare_episodes(episodes, birth_year=birth_year)
    ep_map: dict[str, dict] = {ep["id"]: ep for ep in episodes if ep.get("id")}
    logger.info(f"[autobiography] 그룹핑 완료: {list(groups.keys())}")

    # ── Step 2: Planner ──────────────────────────────────────
    outline = _run_planner(groups, sorted_eps, profile)
    life_theme = outline.get("life_theme", "소중한 삶의 기억들")
    chapter_plans = outline.get("chapters", [])
    logger.info(f"[autobiography] Planner 완료: {len(chapter_plans)}챕터, theme={life_theme}")

    # ── Step 3: Chapter Writer (병렬) ────────────────────────
    chapter_results = _run_chapters(outline, ep_map, life_theme)
    logger.info(f"[autobiography] 챕터 생성 완료: {len(chapter_results)}개")

    # schemas.AutobiographyChapter로 조립
    chapters = []
    for plan, result in zip(chapter_plans, chapter_results):
        chapters.append(AutobiographyChapter(
            title=plan.get("title", ""),
            period_label=plan.get("period_label"),
            narrative=result.get("narrative", ""),
            episode_ids=plan.get("episode_ids", []),
        ))

    # ── Step 4: Prologue / Epilogue ──────────────────────────
    prologue = _run_prologue(life_theme, chapter_plans, sorted_eps)
    epilogue = _run_epilogue(
        life_theme,
        chapter_plans[-1] if chapter_plans else {},
        sorted_eps,
    )
    logger.info("[autobiography] Prologue/Epilogue 완료")

    return AutobiographyResponse(
        prologue=prologue,
        chapters=chapters,
        epilogue=epilogue,
        life_theme=life_theme,
    )
