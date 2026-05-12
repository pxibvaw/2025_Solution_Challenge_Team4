# ai.tests.test_prompt_builder.py
from ai.services.prompt_builder import build_prompt

prompt = build_prompt(
    user_text="나 우울해",
    memory="어릴 때 부산에서 살았다고 말한 적 있음",
    conversation="User: 요즘 옛날 생각이 자꾸 나네요"
)

print(prompt)