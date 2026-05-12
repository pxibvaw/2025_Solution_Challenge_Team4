# ai/tests/test_memory_consolidation.py
from ai.services.memory_service import save_memory
from ai.services.memory_consolidation import run_consolidation

# 의도적으로 유사한 기억 여러 개 저장
memories = [
    ("아버지가 어부였다.", 8.0),
    ("아버지는 어업을 하셨다.", 7.5),       # 위와 유사 → 합쳐져야 함
    ("아버지가 바다에서 일했다.", 7.0),      # 위와 유사 → 합쳐져야 함
    ("손녀가 둘 있다.", 7.2),               # 독립적 → 유지
    ("어릴 때 부산에서 살았다.", 7.5),       # 독립적 → 유지
]

for text, importance in memories:
    save_memory(text, importance=importance)

print("=== Before Consolidation ===")
from ai.memory.chroma_store import collection
before = collection.get()
for doc in before["documents"]:
    print(f" - {doc}")

result = run_consolidation()
print(f"\n=== Consolidation Result ===")
print(f"merged groups: {result['merged']}")

print(f"\n=== After Consolidation ===")
after = collection.get()
for doc in after["documents"]:
    print(f" - {doc}")