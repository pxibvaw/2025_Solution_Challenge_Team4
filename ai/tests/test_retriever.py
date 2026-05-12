# ai/tests/test_memory_retriever.py
from ai.services.memory_service import save_memory
from ai.services.memory_retriever import retrieve

# 기억 저장
memories = [
    ("아버지가 어부였다.", 8.0),
    ("어릴 때 부산에서 살았다.", 7.5),
    ("손녀가 둘 있다.", 7.2),
    ("젊을 때 배를 탔다.", 7.6),
    ("오늘 날씨가 좋았다.", 1.0),
]

for text, importance in memories:
    save_memory(text, importance=importance)

# retrieval 테스트
query = "바다에 대한 기억이 있으신가요?"
results = retrieve(query, memory_count=5, top_k=3)

print("=== Retrieval Results ===")
for i, r in enumerate(results, 1):
    print(f"{i}. {r}")