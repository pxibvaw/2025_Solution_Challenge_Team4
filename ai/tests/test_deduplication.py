# ai/tests/test_memory_deduplication.py
from ai.services.memory_service import save_memory
from ai.services.memory_deduplication import is_duplicate

# 먼저 하나 저장
save_memory("아버지가 어부였다.")

tests = [
    "아버지가 어부였다.",        # 완전 동일 → 중복
    "아버지는 어업을 했다.",      # 의미 유사 → 중복 가능
    "어머니는 선생님이었다.",     # 다른 내용 → 중복 아님
]

print("=== Deduplication Check ===")
for fact in tests:
    result = is_duplicate(fact)
    print(f"[{'중복' if result else '저장 OK'}] {fact}")