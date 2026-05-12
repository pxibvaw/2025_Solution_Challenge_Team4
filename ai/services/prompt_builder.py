# ai/services/prompt_builder.py
import json
from ai.prompts.interview_prompt import build_system_prompt, INTERVIEW_PROMPT
from ai.app.schemas import UserProfileContext


def build_prompt(user_text: str, memory=None, conversation=None, profile: UserProfileContext = None) -> str:

    # 1. SYSTEM — speechLevel에 따라 말투 규칙 분기
    if profile:
        system_block = build_system_prompt(profile.speechLevel)
    else:
        system_block = INTERVIEW_PROMPT

    # 2. DEVELOPER — UserProfileContext JSON 주입
    developer_block = ""
    if profile:
        profile_dict = profile.model_dump(exclude_none=True)
        developer_block = f"사용자 프로필:\n{json.dumps(profile_dict, ensure_ascii=False, indent=2)}"

    # 3. MEMORY
    # memory 있을 때만 섹션 자체를 포함
    # 사용 지침: 사용자가 관련 주제를 먼저 꺼낼 때만 자연스럽게 연결
    # 억지로 꺼내거나 "지난번에"로 시작하지 않음
    memory_section = ""
    if memory:
        memory_lines = (
            "\n".join(f"- {m}" for m in memory)
            if isinstance(memory, list)
            else memory
        )
        memory_block = (
            "[이전 세션에서 기억된 내용입니다. "
            "사용자가 관련 주제를 먼저 꺼낼 때만 자연스럽게 연결하세요. "
            "억지로 꺼내거나 '지난번에'로 시작하지 마세요.]\n"
            f"{memory_lines}"
        )
        memory_section = f"\nMEMORY\n{memory_block}"

    # 4. CONVERSATION
    conversation_block = conversation if conversation else ""

    # 5. USER
    prompt = f"""SYSTEM
{system_block}

DEVELOPER
{developer_block}{memory_section}

CONVERSATION
{conversation_block}

USER
{user_text}"""

    return prompt