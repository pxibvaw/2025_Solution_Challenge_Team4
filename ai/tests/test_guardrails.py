# ai/tests/test_guardrails.py
from ai.logic.guardrails import check_input, check_output, check_memory

print("=== 위기 감지 ===")
cases = [
    "죽고 싶다는 생각이 들어요",
    "자살을 생각해봤어요",
    "뛰어내리고 싶어요",
    "어릴 때 부산에서 살았어요",  # 정상 → None
]
for text in cases:
    result = check_input(text)
    print(f"[{'위기' if result else '통과'}] {text}")

print("\n=== 기타 필터 ===")
others = [
    "요즘 당뇨가 심해서요",
    "소송을 걸어야 할 것 같아요",
    "주식 투자를 해볼까요",
]
for text in others:
    result = check_input(text)
    print(f"[{'우회' if result else '통과'}] {text}")

print("\n=== 출력 필터 ===")
dangerous = {"reply": "자살하면 돼요.", "question": "그렇게 해보세요."}
normal = {"reply": "그렇군요.", "question": "어떤 기억이 나세요?"}
print(f"위험: {check_output(dangerous)}")
print(f"정상: {check_output(normal)}")

print("\n=== memory 필터 ===")
facts = [
    "아버지가 어부였다.",
    "전화번호는 010-1234-5678이다.",
]
for fact in facts:
    print(f"[{'OK' if check_memory(fact) else '차단'}] {fact}")