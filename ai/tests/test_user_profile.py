# ai/tests/test_user_profile.py
from ai.app.schemas import UserProfileContext
from ai.services.prompt_builder import build_prompt

# 1. 존댓말 프로필
profile_honorific = UserProfileContext(
    userTitle="할아버지",
    speechLevel="HONORIFIC",
    memorableAge="50대",
    coreValue="가족"
)

# 2. 반말 프로필
profile_casual = UserProfileContext(
    userTitle="영수씨",
    speechLevel="CASUAL",
    memorableAge="30대",
    coreValue="자기발전"
)

# 3. 최소 프로필 (optional 필드 없음)
profile_minimal = UserProfileContext(
    userTitle="어머니"
)

# --- 스키마 검증 ---
print("=== 스키마 검증 ===")
print(f"존댓말: {profile_honorific.model_dump()}")
print(f"반말: {profile_casual.model_dump()}")
print(f"최소: {profile_minimal.model_dump(exclude_none=True)}")

# --- 프롬프트 빌드 검증 ---
print("\n=== 존댓말 프롬프트 ===")
prompt1 = build_prompt(
    user_text="요즘 옛날 생각이 나네요",
    memory=["어릴 때 부산에서 살았다고 말한 적 있음"],
    conversation="User: 안녕하세요\nAI: 할아버지, 반갑습니다.",
    profile=profile_honorific
)
print(prompt1)
assert "존댓말" in prompt1
assert "할아버지" in prompt1
assert "HONORIFIC" in prompt1

print("\n=== 반말 프롬프트 ===")
prompt2 = build_prompt(
    user_text="요즘 옛날 생각이 나",
    profile=profile_casual
)
print(prompt2)
assert "반말" in prompt2
assert "영수씨" in prompt2
assert "CASUAL" in prompt2

print("\n=== profile 없이 (하위 호환) ===")
prompt3 = build_prompt(
    user_text="요즘 옛날 생각이 나네요"
)
print(prompt3)
assert "존댓말" in prompt3  # 기본값 HONORIFIC

# --- 금지 규칙이 system prompt에 없는지 확인 ---
print("\n=== 금지 규칙 분리 확인 ===")
assert "의료" not in prompt1, "금지 규칙은 guardrails.py에서 처리해야 함"
assert "개인정보" not in prompt1, "금지 규칙은 guardrails.py에서 처리해야 함"
print("금지 규칙이 system prompt에서 정상적으로 분리됨")

print("\n=== 모든 테스트 통과 ===")
