# tests/test_a_api.py
"""
테스트 A: 실제 API 호출 기반 end-to-end 테스트

노인 대화 패턴 반영 근거:
  - 발화 길이: 젊은 성인보다 길고 반복 많음 (PMC6497023)
  - False starts: "그... 그 뭐냐", "아, 그게 아니라" (PMC7525396)
  - 주제 이탈 후 복귀: 비선형 회상 패턴
  - 감정 표현: 복합 감정 ("좋았는데, 외롭기도 했지요")
  - 현재-과거 교차: 회상 중 현재 상황 언급

실행:
  uvicorn ai.app.api:app --reload --port 8000
  python tests/test_a_api.py
"""
import requests
import time

BASE_URL   = "http://localhost:8000"
SPRING_URL = "http://localhost:8080"

PROFILE = {
    "userTitle":    "김복순 할머니",
    "speechLevel":  "HONORIFIC",
    "memorableAge": "30대",
    "coreValue":    "가족",
    "birthYear":    1945,
}

SESSION_ID = "test-a-session-001"
USER_ID    = "test-a-user-001"

# ── 실제 노인 대화 패턴 기반 발화 ────────────────────────────
# 특징:
#   - 단어를 찾다가 멈추는 패턴 ("그... 그게 뭐냐")
#   - 이야기 중간에 "어머, 내가 무슨 말 하다가" 식 자각
#   - 현재로 돌아왔다가 다시 과거로
#   - 같은 감정이나 사실을 다른 방식으로 반복
#   - 추임새 ("아이고", "글쎄요", "참", "어머")
#   - 손자/자식 언급하다가 남편으로 복귀하는 비선형성

TURNS = [
    # [0] 짧게 시작 — 노인 특유의 짧은 첫 발화
    "남편이 참... 부지런한 사람이었어요.",

    # [1] 구체적 기억으로 확장 — 느리게 풀어나감
    "새벽 네 시면 어김없이 일어나서 바다로 나갔지요. "
    "아직 어두컴컴한데, 저는 반쯤 잠에 취해서 일어나서 밥을 해줬어요. "
    "그 사람은 밥도 빨리 먹고, 국물만 홀짝이고는 금방 나갔지요. "
    "'다녀올게' 이 한마디 하고. 그 목소리가 아직도 귀에 남아요.",

    # [2] 감각 기억 — 냄새, 소리 묘사 길게
    "부산 영도에서 살았는데... 거기가 참 좋았어요. "
    "창문 열면 바다가 보이고, 새벽에는 갈매기 소리가 들리고. "
    "아, 그리고 그 짭짤한 냄새요. 비린내라고 하면 나쁜 것 같은데, "
    "저한테는 그게 집 냄새였어요. 남편 냄새였고요. "
    "서울 와서 제일 아쉬운 게 그거예요. 그 냄새.",

    # [3] 주제 이탈 — 현재로 넘어갔다가
    "지금 노원구에 사는데, 여기는... 아파트잖아요. "
    "냄새가 없어요. 그냥 아무 냄새도 없어. "
    "어머, 내가 무슨 얘기 하다가 이랬지.",

    # [4] 원래 주제로 복귀 + 생활고
    "그래요, 남편이 바다 나가면 저 혼자서 다 했지요. "
    "애들이 셋이었는데... 딸 둘에 막내가 아들. "
    "막내가 많이 어려서, 기저귀도 갈고 밥도 먹이고, "
    "그러고 나서 위에 애들 학교 챙겨 보내고, "
    "그다음에 시장에 나가야 하고. "
    "아이고, 그때는 몸이 여러 개였으면 싶었어요.",

    # [5] 시장 이야기 — 직업, 공동체
    "저는 시장에서 생선을 팔았어요. "
    "남편이 잡아오는 걸 받아다가 영도 시장에서 팔았지요. "
    "새벽 다섯 시에 나가서, 다 팔면 들어오는데 보통 저녁 여섯 시, 일곱 시. "
    "힘들었는데 그래도 사람들이 좋았어요. "
    "옆 자리 아주머니가 제 단골이었고, 저도 그 집 단골이고. "
    "뭐 하나라도 더 얹어주고, 그런 게 있었지요. 정이라는 게.",

    # [6] 짧은 대조 — 현재와 비교
    "지금은 그런 게 없잖아요. 마트 가면 그냥 계산하고 나오고.",

    # [7] 위기 에피소드 — 핵심 장면, 감정 풍부
    "막내가 일곱 살 때 크게 아팠어요. "
    "열이... 그게 얼마나 높았냐면, 손으로 만지면 뜨거울 정도로. "
    "밤새 찬 수건 갈아주고 안고 있었는데 안 내리는 거예요. "
    "남편은 바다에 나가 있고, 전화도 없던 시절이고. "
    "새벽에 옆집 아주머니 문 두드려서 같이 아이 들쳐업고 병원을 갔지요. "
    "택시도 없어서 걸어서. "
    "그때 의사 선생님이 '조금만 늦었으면 위험할 뻔했다' 하는 거예요. "
    "그 말 들었을 때... 그 자리에서 주저앉을 뻔했어요. "
    "다리가 후들후들하고.",

    # [8] 반전 — 현재의 결과
    "근데 그 아이가 지금 소아과 의사예요. "
    "자기가 왜 소아과 갔냐면, 그때 그 선생님 때문이래요. "
    "아, 이 얘기 하면 항상 눈물이 나려고 해요.",

    # [9] 짧게 — 감정 정리
    "잘 됐지요. 참 잘 됐어.",

    # [10] 남편으로 복귀 — 비선형, 회상
    "남편이 태풍 때도 나갔어요. "
    "제가 얼마나 말렸는지 몰라요. '오늘은 쉬어요, 위험해요' 했더니 "
    "'내가 어부인데 비 좀 온다고 못 나가면 어디다 써' 하는 거예요. "
    "그렇게 나가고. 저는 그날 하루 종일 창문만 봤어요. "
    "비 오고 바람 불고, 파도 소리가 어찌나 크던지. "
    "그 날 남편이 들어왔을 때... '왜 이렇게 늦었어요' 하면서 툴툴댔지요. "
    "속으로는 얼마나 반가웠는지. 그런데 그걸 표현을 못 했어요. 그때는.",

    # [11] 핵심 감정 문장
    "그때가 참 좋았는데... 외롭기도 했지요.",

    # [12] 사별 — 천천히, 구체적으로
    "남편이 십 년 전에 갑자기 갔어요. "
    "심장이었어요. "
    "아침에 밥 같이 먹었는데, 텔레비전 보다가... 그렇게 됐지요. "
    "제가 옆에 있었는데도 어떻게 할 수가 없었어요. "
    "119 불렀는데 오는 동안에... 이미 그때는. "
    "그 날이 아직도 생생해요. "
    "그 사람 아침에 먹은 게 된장찌개였는데, "
    "그 이후로 된장찌개를 못 끓였어요. 한참을.",

    # [13] 짧게 — 회상 마무리
    "꿈에는 아직 나와요. 새벽에 바다 나가는 꿈.",

    # [14] 현재 생활 — 길게
    "이사 온 게 오 년 됐나. 노원구요. "
    "막내가 '엄마 가까이 있어야 한다'고 해서. "
    "처음엔 낯설었는데, 이제는 좀 익숙해졌어요. "
    "손자 둘이 자주 와요. 큰 손자가 중학생이고, 작은 게 초등학생이고. "
    "그 애들 보는 재미가 있어요. "
    "작은 손자가 저 껴안으면서 '할머니 냄새 좋아' 하는데, "
    "그때 울 뻔했어요. 진짜로.",

    # [15] 건강 — 담담하게
    "몸이... 무릎이 안 좋아요. "
    "오래 걸으면 아프고, 계단도 좀 힘들고. "
    "의사는 수술하자는데 겁도 나고, 나이가 있으니까. "
    "막내한테는 그냥 괜찮다고 했어요. 걱정할까봐.",

    # [16] 짧게 — 체념과 수용
    "이 나이에 뭘 바라겠어요.",

    # [17] 삶의 의미 — 가장 길고 핵심적
    "근데 생각해보면... 살아있는 것만으로도 감사하지요. "
    "남편은 못 보는 것들을 내가 보고 있잖아요. "
    "막내가 의사 된 것도, 손자들이 크는 것도. "
    "그 사람이 살아있었으면 얼마나 좋아했을까 싶은데. "
    "뭐... 내가 대신 보는 거지요. "
    "힘들었는데, 돌아보면 잘 살았어요. "
    "후회는 없어요. 남편한테도, 애들한테도, 내 자신한테도.",

    # [18] 짧고 담담한 마무리
    "그렇게 살았어요, 나는.",

    # [19] 마지막 — 한 문장 정리
    "잘 살았다고 생각해요. 힘들었지만, 잘 살았어요.",
]


def _p(msg: str, indent: int = 0):
    print("  " * indent + msg)


def test_health():
    r = requests.get(f"{BASE_URL}/health")
    assert r.status_code == 200, f"/health 실패: {r.text}"
    _p("✓ /health OK")


def test_turns() -> list[str]:
    _p(f"\n/turn 호출 시작 ({len(TURNS)}회)...")
    request_ids = []

    for i, user_text in enumerate(TURNS):
        req_id = f"req-{SESSION_ID}-{i:03d}"
        request_ids.append(req_id)

        r = requests.post(f"{BASE_URL}/turn", json={
            "sessionId": SESSION_ID,
            "requestId": req_id,
            "userText":  user_text,
            "profile":   PROFILE,
        })
        assert r.status_code == 200, f"turn {i} 실패: {r.text}"
        resp = r.json()
        assert "reply" in resp and "question" in resp

        _p(f"[{i+1:02d}] 사용자: {user_text[:45].replace(chr(10), ' ')}...", indent=1)
        _p(f"     AI: {resp['reply'][:50]}...", indent=1)
        time.sleep(0.3)

    _p(f"✓ /turn {len(TURNS)}회 완료")
    return request_ids


def test_end_session(wait_sec: int = 45) -> list[dict]:
    _p("\n/end-session 호출...")
    r = requests.post(
        f"{BASE_URL}/end-session",
        json={"sessionId": SESSION_ID, "userId": USER_ID},
    )
    assert r.status_code == 200, f"/end-session 실패: {r.text}"
    _p("✓ /end-session 완료 (백그라운드 처리 중)")
    _p(f"  파이프라인 완료까지 {wait_sec}초 대기...")

    for elapsed in range(0, wait_sec, 5):
        time.sleep(5)
        _p(f"  {elapsed+5}/{wait_sec}초 경과...", indent=1)

    try:
        ep_resp = requests.get(
            f"{SPRING_URL}/api/episodes",
            params={"userId": USER_ID},
            timeout=5,
        )
        if ep_resp.status_code == 200:
            episodes = ep_resp.json()
            _p(f"✓ 에피소드 {len(episodes)}개 생성 확인")
            for ep in episodes:
                quality = ep.get("quality", {})
                _p(
                    f"  [{ep.get('type')}] {ep.get('title')} | "
                    f"importance={ep.get('importance_score', '?')} | "
                    f"richness={quality.get('narrative_richness', '?')}",
                    indent=1,
                )
            return episodes
        else:
            _p(f"⚠ 에피소드 조회 실패: {ep_resp.status_code}")
            return []
    except Exception as e:
        _p(f"⚠ Spring Boot 연결 실패: {e}")
        return []


def test_autobiography(episodes: list[dict]):
    if not episodes:
        _p("\n⚠ 에피소드 없음 — autobiography 테스트 스킵")
        return

    _p(f"\n/autobiography 호출 ({len(episodes)}개 에피소드)...")
    r = requests.post(
        f"{BASE_URL}/autobiography",
        json={
            "userId":             USER_ID,
            "selectedEpisodeIds": [ep["id"] for ep in episodes],
            "episodes":           episodes,
        },
        timeout=120,
    )
    assert r.status_code == 200, f"/autobiography 실패: {r.text}"
    resp = r.json()

    _p(f"✓ /autobiography OK")
    _p(f"\n  life_theme: {resp['life_theme']}")
    _p(f"\n{'='*60}")
    _p("서문")
    _p(f"{'='*60}")
    _p(resp["prologue"])
    for i, ch in enumerate(resp["chapters"]):
        _p(f"\n{'='*60}")
        _p(f"챕터 {i+1}: {ch['title']}")
        _p(f"{'='*60}")
        _p(ch["narrative"])
    _p(f"\n{'='*60}")
    _p("마무리")
    _p(f"{'='*60}")
    _p(resp["epilogue"])


def cleanup(episodes: list[dict]):
    _p("\n=== 데이터 정리 시작 ===")

    # 1. AI 서버 인메모리 + ChromaDB 정리
    try:
        r = requests.delete(
            f"{BASE_URL}/test/cleanup",
            json={"sessionId": SESSION_ID, "userId": USER_ID},
            timeout=5,
        )
        if r.status_code == 200:
            result = r.json()
            _p(f"  AI 서버 정리: {result.get('cleaned')}")
        else:
            _p(f"  ⚠ AI 서버 정리 실패: {r.status_code}")
    except Exception as e:
        _p(f"  ⚠ AI 서버 정리 오류: {e}")

    # 2. Spring Boot 에피소드 삭제
    deleted = 0
    for ep in episodes:
        try:
            r = requests.delete(
                f"{SPRING_URL}/api/episodes/{ep['id']}",
                timeout=5,
            )
            if r.status_code in (200, 204):
                deleted += 1
            else:
                _p(f"  ⚠ 에피소드 삭제 실패: {ep['id']} ({r.status_code})")
        except Exception as e:
            _p(f"  ⚠ 에피소드 삭제 오류: {ep['id']} — {e}")
    _p(f"  에피소드 삭제: {deleted}/{len(episodes)}개")

    # 3. Spring Boot 유저 테스트 데이터 삭제
    try:
        r = requests.delete(
            f"{SPRING_URL}/api/users/{USER_ID}/test-data",
            timeout=5,
        )
        if r.status_code in (200, 204):
            _p("  사용자 테스트 데이터 삭제: OK")
        else:
            _p(f"  ⚠ 사용자 데이터 삭제: {r.status_code} — 수동 정리 필요")
    except Exception:
        _p(f"  ⚠ Spring Boot 사용자 정리 — 수동 정리 필요")
        _p(f"    userId={USER_ID}")

    _p("=== 정리 완료 ===")


if __name__ == "__main__":
    episodes = []
    try:
        _p("=== 테스트 A 시작 ===\n")
        test_health()
        test_turns()
        episodes = test_end_session(wait_sec=45)
        test_autobiography(episodes)
        _p("\n=== 테스트 A 완료 ===")
    finally:
        cleanup(episodes)