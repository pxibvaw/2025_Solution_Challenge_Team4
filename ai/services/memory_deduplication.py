# ai/services/memory_deduplication.py

from ai.embedding.embedder import embed_text
from ai.memory.chroma_store import search_memory

DEDUP_THRESHOLD = 0.85
DEDUP_TOP_K = 3


def is_duplicate(fact: str) -> bool:
    """
    새로운 fact가 기존 메모리와 중복인지 확인.
    top-3 유사 메모리 중 하나라도 cosine similarity > 0.85면 중복으로 판단.
    """
    embedding = embed_text(fact)
    results = search_memory(embedding, k=DEDUP_TOP_K)

    # results가 비어있으면 중복 없음
    if not results:
        return False

    for result in results:
        distance = result.get("distance", 1.0)
        similarity = 1 - distance
        if similarity > DEDUP_THRESHOLD:
            return True

    return False