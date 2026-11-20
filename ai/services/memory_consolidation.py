# ai/services/memory_consolidation.py
import json
import re
from ai.clients.llm_gemini import generate_reply
from ai.embedding.embedder import embed_text
from ai.memory.chroma_store import get_collection

CONSOLIDATION_THRESHOLD = 0.75  # dedup(0.85)보다 낮게 — 더 넓은 범위 압축
CONSOLIDATION_PROMPT = """
아래 문장들은 같은 사람에 대한 유사한 기억들입니다.
이 기억들을 하나의 정확한 문장으로 합쳐주세요.

규칙:
1. 가장 최신 정보나 더 구체적인 정보를 우선합니다
2. 정보가 충돌하면 더 구체적인 쪽을 선택합니다
3. 반드시 1문장으로만 출력하세요
4. 다른 텍스트는 절대 포함하지 마세요

기억들:
{memories}
"""


def _get_all_memories() -> list[dict]:
    """
    ChromaDB에서 전체 memory 조회
    반환: [{"id": ..., "text": ..., "metadata": ...}, ...]
    """
    result = get_collection().get(include=["documents", "metadatas"])
    if not result["ids"]:
        return []
    return [
        {"id": id_, "text": doc, "metadata": meta}
        for id_, doc, meta in zip(
            result["ids"], result["documents"], result["metadatas"]
        )
    ]


def _find_similar_groups(memories: list[dict]) -> list[list[dict]]:
    """
    유사도 > CONSOLIDATION_THRESHOLD인 memory 쌍을 그룹으로 묶음
    단순 O(n^2) 비교 — memory 수가 적을 때 적합
    """
    import numpy as np

    # 전체 embedding 계산
    embeddings = [embed_text(m["text"]) for m in memories]

    visited = set()
    groups = []

    for i in range(len(memories)):
        if i in visited:
            continue
        group = [memories[i]]
        visited.add(i)

        for j in range(i + 1, len(memories)):
            if j in visited:
                continue
            # cosine similarity 계산
            a = np.array(embeddings[i])
            b = np.array(embeddings[j])
            similarity = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

            if similarity > CONSOLIDATION_THRESHOLD:
                group.append(memories[j])
                visited.add(j)

        if len(group) > 1:
            groups.append(group)

    return groups


def _merge_group(group: list[dict]) -> str:
    """
    LLM으로 유사 기억 그룹을 1문장으로 합침
    """
    memory_texts = "\n".join(f"- {m['text']}" for m in group)
    prompt = CONSOLIDATION_PROMPT.format(memories=memory_texts)
    merged = generate_reply(prompt).strip()
    return merged


def _delete_memories(ids: list[str]):
    """
    ChromaDB에서 memory 삭제
    """
    get_collection().delete(ids=ids)


def run_consolidation():
    """
    전체 consolidation 실행
    1. 전체 memory 조회
    2. 유사 그룹 탐색
    3. 그룹별 LLM 합치기
    4. 기존 삭제 + 새 memory 저장
    """
    import uuid
    from datetime import datetime
    from ai.memory.chroma_store import add_memory

    memories = _get_all_memories()
    if len(memories) < 2:
        return {"merged": 0, "remaining": len(memories)}

    groups = _find_similar_groups(memories)
    merged_count = 0

    for group in groups:
        merged_text = _merge_group(group)
        if not merged_text:
            continue

        # 그룹 중 가장 높은 importance 유지
        max_importance = max(
            m["metadata"].get("importance", 5.0) for m in group
        )

        # 기존 memory 삭제
        _delete_memories([m["id"] for m in group])

        # 합쳐진 memory 저장
        embedding = embed_text(merged_text)
        add_memory(
            text=merged_text,
            embedding=embedding,
            memory_id=str(uuid.uuid4()),
            metadata={
                "importance": max_importance,
                "created_at": datetime.utcnow().isoformat(),
                "consolidated": True  # consolidation 여부 표시
            }
        )
        merged_count += 1

    remaining = len(memories) - sum(len(g) for g in groups) + merged_count
    return {"merged": merged_count, "remaining": remaining}