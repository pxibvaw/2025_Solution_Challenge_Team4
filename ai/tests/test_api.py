# ai/tests/test_api.py
from fastapi.testclient import TestClient
from ai.app.api import app

client = TestClient(app)

PROFILE = {
    "userTitle": "할아버지",
    "speechLevel": "HONORIFIC",
    "memorableAge": "50대",
    "coreValue": "가족"
}

TURNS = [
    "젊을 때 부산에서 살았어요.",
    "아버지가 어부셨어요. 매일 새벽에 나가셨죠.",
    "어머니는 시장에서 생선 파셨어요.",
    "형제가 넷이었는데 제가 막내였어요.",
    "학교는 부산 영도에서 다녔어요.",
    "졸업하고 나서 서울로 올라왔어요.",
    "서울에서 처음엔 공장 일을 했어요.",
    "거기서 지금 아내를 만났어요.",
    "결혼은 30살에 했고, 딸이 둘 있어요.",
    "딸 둘 다 지금은 결혼해서 따로 살아요.",
    "손녀가 셋인데 제일 큰 애가 올해 중학교 들어갔어요.",
    "요즘은 아내랑 둘이 살아요. 조용하죠.",
]

print("=== /turn 테스트 (12턴) ===")
for i, text in enumerate(TURNS):
    req_id = f"req-{i+1:03d}"
    res = client.post("/turn", json={
        "sessionId": "session-001",
        "requestId": req_id,
        "userText": text,
        "profile": PROFILE
    })
    data = res.json()
    print(f"턴 {i+1}: reply={data.get('reply', '')[:30]}...")
    if i == 9:
        print("  → 10턴 도달: [mid-extraction] 로그 확인")

print("\n=== idempotency 테스트 ===")
res_a = client.post("/turn", json={
    "sessionId": "session-001",
    "requestId": "req-001",
    "userText": TURNS[0],
    "profile": PROFILE
})
res_b = client.post("/turn", json={
    "sessionId": "session-001",
    "requestId": "req-001",
    "userText": TURNS[0],
    "profile": PROFILE
})
assert res_a.json() == res_b.json(), "❌ idempotency 실패"
print("✅ idempotency 확인")

print("\n=== /end-session 테스트 ===")
res3 = client.post("/end-session", json={"sessionId": "session-001"})
print(res3.json())