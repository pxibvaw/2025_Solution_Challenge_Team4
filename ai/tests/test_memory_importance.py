# ai/tests/test_memory_importance.py
from ai.services.memory_importance import score_importance, is_important

facts = [
    "어릴 때 부산에서 살았다.",
    "아버지가 어부였다.",
    "젊을 때 배를 탔다.",
    "손녀가 둘 있다.",
    "오늘 날씨가 좋았다.",  # 중요하지 않은 것
]

print("=== Importance Scoring ===")
for fact in facts:
    important, score = is_important(fact, memory_count=0)
    print(f"[{'✅' if important else '❌'}] score={score} | {fact}")