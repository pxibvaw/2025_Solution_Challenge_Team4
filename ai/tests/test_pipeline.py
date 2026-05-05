# ai/tests/test_pipeline.py
"""
인터뷰룸 전체 파이프라인 테스트
STT → /turn (LLM + memory + guardrails) → TTS(base64)

실행:
  python -m ai.tests.test_pipeline

오디오 파일 없으면 텍스트로 fallback.
테스트 완료 후 ai/audio/samples/pipeline_output_N.mp3 저장됨.
"""

import base64
import os
import time
from fastapi.testclient import TestClient
from ai.app.api import app
from ai.memory.chroma_store import get_all_memory_ids, delete_memories

client = TestClient(app)

PROFILE = {
    "userTitle": "할머니",
    "speechLevel": "HONORIFIC",
    "memorableAge": "30대",
    "coreValue": "가족"
}

# 테스트 발화 시나리오
SCENARIO = [
    "안녕하세요. 오늘 날씨가 참 좋네요.",
    "젊을 때 부산에서 살았어요. 바다가 참 좋았죠.",
    "남편이 어부였어요. 매일 새벽에 나가셨어요.",
    "아이가 셋인데 다들 서울에 있어요.",
    "손자가 둘 있는데 볼 때마다 너무 반가워요.",
]

OUTPUT_DIR = "ai/audio/samples"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def try_stt(audio_path: str) -> str | None:
    """오디오 파일 있으면 STT, 없으면 None 반환"""
    if not os.path.exists(audio_path):
        return None
    try:
        from ai.clients.stt_google import speech_to_text
        text = speech_to_text(audio_path)
        return text if text.strip() else None
    except Exception as e:
        print(f"  [STT 실패] {e}")
        return None


def save_audio(b64: str, path: str):
    """base64 → MP3 저장"""
    audio_bytes = base64.b64decode(b64)
    with open(path, "wb") as f:
        f.write(audio_bytes)


def run_turn(session_id: str, req_id: str, text: str, turn_num: int):
    print(f"\n--- 턴 {turn_num} ---")
    print(f"  [입력] {text}")

    t = time.time()
    res = client.post("/turn", json={
        "sessionId": session_id,
        "requestId": req_id,
        "userText": text,
        "profile": PROFILE
    })
    elapsed = time.time() - t

    assert res.status_code == 200, f"❌ /turn 실패: {res.status_code}"
    data = res.json()

    reply = data.get("reply", "")
    question = data.get("question", "")
    audio_b64 = data.get("audioContent", "")
    turn_index = data.get("turnIndex", -1)

    print(f"  [reply]    {reply}")
    print(f"  [question] {question}")
    print(f"  [turnIndex] {turn_index}")
    print(f"  [응답시간] {elapsed:.2f}s")

    # TTS 검증
    assert audio_b64, "❌ audioContent 없음"
    assert len(audio_b64) > 100, "❌ audioContent 너무 짧음"

    # MP3 저장
    out_path = f"{OUTPUT_DIR}/pipeline_output_{turn_num}.mp3"
    save_audio(audio_b64, out_path)
    print(f"  [TTS 저장] {out_path} ({len(audio_b64)} chars base64)")

    return data


def main():
    session_id = "pipeline-test-001"
    print("=" * 55)
    print("인터뷰룸 전체 파이프라인 테스트 시작")
    print("STT → /turn (LLM + memory + guardrails) → TTS")
    print("=" * 55)

    # 테스트 전 스냅샷
    ids_before = set(get_all_memory_ids())

    # STT 테스트 (샘플 파일 있을 때만)
    print("\n[1] STT 테스트")
    stt_audio = "ai/audio/samples/test_stt.wav"
    stt_result = try_stt(stt_audio)
    if stt_result:
        print(f"  ✅ STT 성공: '{stt_result}'")
    else:
        print(f"  ⚠️  {stt_audio} 없음 → 텍스트 시나리오로 진행")

    # 인터뷰 시나리오 실행
    print("\n[2] 인터뷰 시나리오 (5턴)")
    results = []
    for i, text in enumerate(SCENARIO):
        # STT 결과 있으면 첫 턴에 사용
        input_text = stt_result if (i == 0 and stt_result) else text
        data = run_turn(session_id, f"req-{i+1:03d}", input_text, i + 1)
        results.append(data)

    # 세션 종료
    print("\n[3] 세션 종료 (/end-session)")
    res = client.post("/end-session", json={"sessionId": session_id})
    assert res.status_code == 200
    print(f"  {res.json()}")

    # 결과 요약
    print("\n" + "=" * 55)
    print("✅ 파이프라인 테스트 완료")
    print(f"  총 {len(results)}턴 처리")
    print(f"  MP3 저장 위치: {OUTPUT_DIR}/pipeline_output_1~{len(results)}.mp3")
    print("  확인 포인트:")
    print("  - 각 턴 reply/question이 자연스러운지")
    print("  - MP3 파일 재생이 되는지")
    print("=" * 55)

    # 더미 데이터 정리
    ids_after = set(get_all_memory_ids())
    test_ids = list(ids_after - ids_before)
    if test_ids:
        delete_memories(test_ids)
        print(f"\n[더미 정리] {len(test_ids)}개 삭제 완료")


if __name__ == "__main__":
    main()