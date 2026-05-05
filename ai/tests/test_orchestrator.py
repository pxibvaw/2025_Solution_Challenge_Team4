# ai/tests/test_orchestrator.py
from ai.app.orchestrator import handle_turn, end_session
from ai.app.schemas import UserProfileContext

profile = UserProfileContext(
    userTitle="할아버지",
    speechLevel="HONORIFIC",
    memorableAge="50대",
    coreValue="가족"
)

print("=== 대화 진행 ===")
turns = [
    "젊을 때 부산에서 살았어요.",
    "아버지가 어부셨어요.",
    "손녀가 둘 있어요.",
]

for text in turns:
    result = handle_turn(text, profile=profile)
    print(f"User: {text}")
    print(f"AI: {result['reply']} {result['question']}\n")

print("=== 세션 종료 ===")
result = end_session()
print(f"저장됨: {result['saved']}개")
print(f"스킵됨: {result['skipped']}개")