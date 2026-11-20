# ai/tests/test_memory_extractor.py
"""
memory_extractor.py 품질 검증 테스트

3가지 케이스:
  Case 1 — 단순 대화: 기본 추출 가능한지 확인
  Case 2 — 감정 중심 대화: 감정만 있고 fact 없을 때 빈 배열 반환하는지 확인
  Case 3 — 긴 복잡한 대화: 두서없고 여러 인물/시제 섞인 실제 노인 대화 패턴

실행:
  python -m ai.tests.test_memory_extractor
"""

from ai.services.memory_extractor import extract_facts, _split_into_chunks


# ──────────────────────────────────────────
# Case 1: 단순 대화
# 기대: 인물/장소/직업 명확하게 추출
# ──────────────────────────────────────────
CASE1 = [
    {"user": "어릴 때 부산 영도에서 살았어요.", "ai": "부산에서 사셨군요."},
    {"user": "아버지가 어부셨어요.", "ai": "아버지께서 바다 일을 하셨군요."},
    {"user": "손녀가 둘 있어요.", "ai": "손녀가 두 분 계시는군요."},
]

# ──────────────────────────────────────────
# Case 2: 감정 중심 대화
# 기대: 구체적 fact 없으므로 빈 배열 또는 최소 추출
# ──────────────────────────────────────────
CASE2 = [
    {"user": "요즘 옛날 생각이 많이 나요.", "ai": "어떤 기억이 떠오르세요?"},
    {"user": "그냥 그때가 좋았던 것 같아요.", "ai": "그 시절이 그리우시군요."},
    {"user": "요즘은 뭔가 허전해요.", "ai": "많이 허전하시겠어요."},
]

# ──────────────────────────────────────────
# Case 3: 긴 복잡한 대화 (실제 노인 대화 패턴)
# - 두서없이 여러 시대 이야기
# - 여러 인물 등장
# - 같은 이야기 반복
# - 주제가 섞임
# 기대: 핵심 facts만 골라내고 중복 없이 추출
# ──────────────────────────────────────────
CASE3 = [
    {
        "user": "우리 아들이 서울 가서 회사 다니는데, 거기서 만난 며느리가 참 착해요. 근데 옛날엔 제가 대전에서 살았어요, 거기서 학교 다녔고.",
        "ai": "대전에서 학교를 다니셨군요."
    },
    {
        "user": "그때 선생님이 되고 싶었어요. 근데 결국엔 못 했죠. 남편이 부산 가자고 해서 따라갔어요.",
        "ai": "부산으로 이사하셨군요."
    },
    {
        "user": "부산에서 애들 셋 낳았어요. 큰딸은 지금 미국에 있고, 아들은 서울, 막내는 부산에 있어요.",
        "ai": "세 분의 자녀가 계시는군요."
    },
    {
        "user": "남편이 3년 전에 갔어요. 많이 힘들었죠. 그래도 큰딸이 자주 전화해줘요.",
        "ai": "많이 힘드셨겠어요."
    },
    {
        "user": "우리 아들이 서울에 있다고 했잖아요. 거기 회사가 크다고 하던데.",
        "ai": "아드님이 큰 회사에 다니시는군요."
    },
    {
        "user": "젊을 때 뜨개질 잘했어요. 동네에서 제일 잘한다고 했어요.",
        "ai": "뜨개질 솜씨가 좋으셨군요."
    },
    {
        "user": "대전 얘기 했죠? 거기서 중학교 나왔어요.",
        "ai": "대전에서 중학교를 나오셨군요."
    },
    {
        "user": "손녀가 둘인데 하나는 올해 대학 갔어요.",
        "ai": "손녀분이 올해 대학에 입학했군요."
    },
]


# ──────────────────────────────────────────
# Case 4: 한 턴에 긴 발화 (에피소드)
# 노인이 한 번에 긴 이야기를 풀어낼 때
# 문자 수 기준 청크 분리가 작동하는지 확인
# 기대: 청크가 2개 이상으로 분리되고 facts 누락 없이 추출
# ──────────────────────────────────────────
CASE4 = [
    {
        "user": "6.25 때 우리 식구가 부산으로 피난을 갔어요. 아버지가 짐을 싸는데 어머니는 울고 계셨고, 동생이 셋이 있었는데 제일 막내가 세 살이었어요. 걷다가 막내가 넘어져서 무릎에서 피가 났는데 아버지가 업고 걸으셨어요. 그때 제가 열두 살이었어요.",
        "ai": "정말 힘든 시절이었겠어요. 열두 살에 그런 경험을 하셨군요."
    },
    {
        "user": "부산에 도착해서 판자촌에서 살았어요. 방이 하나였는데 여섯 식구가 다 거기서 잤어요. 그래도 아버지가 일을 구해서 우리가 굶지는 않았어요. 아버지가 부두에서 짐 나르는 일을 하셨거든요.",
        "ai": "부두에서 일하시면서 가족을 먹여 살리셨군요."
    },
    {
        "user": "전쟁이 끝나고 서울로 다시 올라왔는데, 집이 없어서 친척 집에 얹혀살았어요. 그때 제가 학교를 제대로 못 다녔어요. 중학교도 늦게 들어갔고요.",
        "ai": "어려운 환경에서도 학업을 이어가셨군요."
    },
]


def run_test(name: str, history: list, expected_empty: bool = False):
    print(f"\n{'='*50}")
    print(f"[{name}]")
    print(f"{'='*50}")
    print(f"입력 턴 수: {len(history)}")

    # 청크 분리 확인
    chunks = _split_into_chunks(history)
    print(f"청크 분리: {len(chunks)}개")
    for idx, chunk in enumerate(chunks):
        chars = sum(len(t.get("user", "")) for t in chunk)
        print(f"  chunk {idx+1}: {len(chunk)}턴, {chars}자")

    facts = extract_facts(history)

    print(f"추출된 facts ({len(facts)}개):")
    if facts:
        for f in facts:
            print(f"  - {f}")
    else:
        print("  (없음)")

    # 품질 체크
    issues = []

    if expected_empty and facts:
        issues.append(f"⚠️  감정/의견만 있는 대화인데 {len(facts)}개 추출됨 — 과추출 가능성")

    if not expected_empty and not facts:
        issues.append("⚠️  추출 결과 없음 — 누락 가능성")

    # 중복 체크
    if len(facts) != len(set(facts)):
        issues.append("⚠️  중복 fact 존재")

    if issues:
        print("\n[품질 이슈]")
        for i in issues:
            print(f"  {i}")
    else:
        print("\n✅ 이슈 없음")


if __name__ == "__main__":
    print("memory_extractor 품질 검증 시작\n")

    run_test("Case 1 — 단순 대화", CASE1, expected_empty=False)
    run_test("Case 2 — 감정 중심 대화 (fact 없음)", CASE2, expected_empty=True)
    run_test("Case 3 — 긴 복잡한 대화 (실제 노인 패턴)", CASE3, expected_empty=False)
    run_test("Case 4 — 한 턴에 긴 발화 (에피소드)", CASE4, expected_empty=False)

    print(f"\n{'='*50}")
    print("테스트 완료")
    print("확인 포인트:")
    print("  Case 1 — 인물/장소/직업이 정확하게 추출됐는지")
    print("  Case 2 — 감정만 있을 때 빈 배열 또는 최소 추출인지")
    print("  Case 3 — 반복 언급(아들/대전)이 중복 없이 추출됐는지")
    print("           남편 사망 같은 민감 정보가 적절히 처리됐는지")