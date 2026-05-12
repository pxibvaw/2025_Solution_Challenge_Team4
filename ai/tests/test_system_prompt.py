# ai/tests/test_system_prompt.py
from ai.prompts.interview_prompt import build_system_prompt

print("=== 존댓말 system prompt ===")
prompt_honorific = build_system_prompt("HONORIFIC")
print(prompt_honorific)

print("\n=== 반말 system prompt ===")
prompt_casual = build_system_prompt("CASUAL")
print(prompt_casual)

print("\n=== 검증 ===")

# 1. interview_system.md 내용이 포함됐는지
assert "위기 감지" in prompt_honorific, "❌ interview_system.md 로딩 실패"
print("✅ interview_system.md 로딩 확인")

# 2. speechLevel 명시 확인
assert "존댓말" in prompt_honorific, "❌ speech_label 주입 실패"
assert "반말" in prompt_casual, "❌ speech_label 주입 실패"
print("✅ speech_label 명시 확인")

# 3. 위기 감지 지침이 말투 규칙보다 앞에 있는지
crisis_pos = prompt_honorific.find("위기 감지")
speech_pos = prompt_honorific.find("말투 규칙")
assert crisis_pos < speech_pos, "❌ 프롬프트 순서 오류: 위기 감지가 말투 규칙보다 뒤에 있음"
print("✅ 프롬프트 순서 확인")

print("\n=== 모든 테스트 통과 ===")