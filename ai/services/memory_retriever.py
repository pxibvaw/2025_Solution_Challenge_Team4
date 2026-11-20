# ai/services/memory_retriever.py
import math
from datetime import datetime
from ai.embedding.embedder import embed_text
from ai.memory.chroma_store import search_memory

RECENCY_DECAY = 0.01  # 반감기 약 70일


def _get_weights(memory_count: int) -> dict:
    if memory_count < 50:
        return {"relevance": 0.5, "importance": 0.4, "recency": 0.1}
    elif memory_count < 300:
        return {"relevance": 0.5, "importance": 0.3, "recency": 0.2}
    else:
        return {"relevance": 0.4, "importance": 0.3, "recency": 0.3}


def _recency_score(created_at: str) -> float:
    """
    저장된 지 오래될수록 점수 낮아짐
    score = e^(-0.01 * age_in_days)
    """
    try:
        created = datetime.fromisoformat(created_at)
        age_days = (datetime.utcnow() - created).days
        return math.exp(-RECENCY_DECAY * age_days)
    except:
        return 0.5  # 파싱 실패 시 중간값


def retrieve(query_text: str, memory_count: int, top_k: int = 5) -> list[str]:
    """
    vector search → reranking → top_k 반환
    """
    query_embedding = embed_text(query_text)
    # 넉넉하게 꺼내서 reranking 후 top_k로 자름
    candidates = search_memory(query_embedding, k=top_k * 2)

    if not candidates:
        return []

    weights = _get_weights(memory_count)
    scored = []

    for candidate in candidates:
        relevance = 1 - candidate["distance"]
        importance = candidate["metadata"].get("importance", 5.0) / 10.0  # 0~1 정규화
        recency = _recency_score(candidate["metadata"].get("created_at", ""))

        final_score = (
            weights["relevance"] * relevance +
            weights["importance"] * importance +
            weights["recency"] * recency
        )

        scored.append({"text": candidate["text"], "score": final_score})

    scored.sort(key=lambda x: x["score"], reverse=True)
    return [item["text"] for item in scored[:top_k]]