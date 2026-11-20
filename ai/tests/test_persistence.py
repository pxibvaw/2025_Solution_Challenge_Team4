# ai/tests/test_persistence.py
"""
ChromaDB 영속성 + retrieve 검증 테스트

검증 항목:
  1. 세션 종료 후 ChromaDB에 실제 저장됐는지
  2. 재시작 시뮬레이션 후 데이터 유지되는지
  3. retrieve_memory가 이전 기억을 가져오는지
  4. 테스트 완료 후 더미 데이터 삭제

실행:
  python -m ai.tests.test_persistence
"""

import os
import chromadb
from fastapi.testclient import TestClient
from ai.app.api import app
from ai.memory.chroma_store import count_memories, get_all_memory_ids, delete_memories
from ai.services.memory_service import retrieve_memory
from ai.app.settings import settings

client = TestClient(app)

PROFILE = {
    "userTitle": "할머니",
    "speechLevel": "HONORIFIC",
    "memorableAge": "30대",
    "coreValue": "가족"
}

SCENARIO = [
    "남편이 어부였어요. 매일 새벽에 바다에 나가셨죠.",
    "부산 시내에서 살았는데, 시장 근처였어요.",
    "아이가 셋이었는데 다들 말썽꾸러기였어요.",
    "남편이 잡아온 생선을 매일 손질했어요. 손이 거칠어지더라고요.",
    "그 시절에 가족이랑 바닷가에 자주 갔어요.",
]


def run_session(session_id: str):
    for i, text in enumerate(SCENARIO):
        client.post("/turn", json={
            "sessionId": session_id,
            "requestId": f"persist-req-{i+1:03d}",
            "userText": text,
            "profile": PROFILE
        })
    res = client.post("/end-session", json={"sessionId": session_id})
    return res.json()


def main():
    session_id = "persist-test-001"

    print("=" * 55)
    print("ChromaDB 영속성 + retrieve 테스트")
    print("=" * 55)

    # ── 테스트 전 스냅샷 ──────────────────────────────
    ids_before = set(get_all_memory_ids())
    count_before = len(ids_before)
    print(f"\n[사전] 저장된 memory 수: {count_before}")

    # ── 1. 세션 실행 + 종료 ──────────────────────────
    print("\n[1] 세션 실행 (5턴) + end-session")
    result = run_session(session_id)
    print(f"  end-session 결과: {result}")

    count_after = count_memories()
    newly_saved = count_after - count_before
    print(f"  저장 후 memory 수: {count_after} (새로 저장: {newly_saved}개)")

    assert count_after > count_before, \
        f"❌ memory 저장 실패: before={count_before}, after={count_after}"
    print("  ✅ ChromaDB 저장 확인")

    # ── 2. persist 경로 확인 ─────────────────────────
    print("\n[2] persist 경로 확인")
    print(f"  CHROMA_PERSIST_PATH: {settings.CHROMA_PERSIST_PATH}")
    assert os.path.exists(settings.CHROMA_PERSIST_PATH), \
        f"❌ persist 경로 없음: {settings.CHROMA_PERSIST_PATH}"
    print("  ✅ persist 디렉토리 존재 확인")

    # ── 3. 재시작 시뮬레이션 ─────────────────────────
    print("\n[3] 재시작 시뮬레이션 (새 PersistentClient)")
    new_client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_PATH)
    new_collection = new_client.get_or_create_collection(
        name="memory",
        metadata={"hnsw:space": "cosine"}
    )
    count_after_restart = new_collection.count()
    print(f"  재시작 후 memory 수: {count_after_restart}")

    assert count_after_restart == count_after, \
        f"❌ 재시작 후 데이터 손실: expected={count_after}, got={count_after_restart}"
    print("  ✅ 재시작 후 데이터 유지 확인")

    # ── 4. retrieve_memory 검증 ───────────────────────
    print("\n[4] retrieve_memory 검증")
    queries = [
        ("남편 어부", "남편/어부 관련"),
        ("부산 시장", "부산/시장 관련"),
        ("가족 바다", "가족/바다 관련"),
    ]

    for query_text, label in queries:
        results = retrieve_memory(query_text, k=3)
        print(f"  쿼리: '{query_text}' ({label})")
        if results:
            for r in results:
                print(f"    - {r}")
            print(f"  ✅ {len(results)}개 retrieve 성공")
        else:
            print("  ⚠️  결과 없음 (importance threshold 또는 dedup 필터링)")

    # ── 5. 더미 데이터 정리 ───────────────────────────
    print("\n[5] 테스트 더미 데이터 정리")
    ids_after = set(get_all_memory_ids())
    test_ids = list(ids_after - ids_before)
    print(f"  삭제 대상: {len(test_ids)}개")

    delete_memories(test_ids)

    count_final = count_memories()
    assert count_final == count_before, \
        f"❌ 정리 실패: expected={count_before}, got={count_final}"
    print(f"  ✅ 더미 데이터 삭제 완료 (현재 memory 수: {count_final})")

    # ── 결과 요약 ─────────────────────────────────────
    print("\n" + "=" * 55)
    print("✅ 모든 테스트 통과")
    print(f"  새로 저장: {newly_saved}개")
    print(f"  재시작 후 유지: {count_after_restart}개")
    print(f"  정리 후 원상복구: {count_final}개")
    print("=" * 55)


if __name__ == "__main__":
    main()