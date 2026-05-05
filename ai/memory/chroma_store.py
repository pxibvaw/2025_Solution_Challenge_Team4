# ai/memory/chroma_store.py
import chromadb
from ai.app.settings import settings

client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_PATH)

collection = client.get_or_create_collection(
    name="memory",
    metadata={"hnsw:space": "cosine"}
)


def add_memory(text: str, embedding: list, memory_id: str, metadata: dict = None):
    collection.add(
        documents=[text],
        embeddings=[embedding],
        ids=[memory_id],
        metadatas=[metadata or {}]
    )


def search_memory(query_embedding: list, k: int = 5):
    total = collection.count()
    if total == 0:
        return []

    n = min(k, total)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n,
        include=["documents", "distances", "metadatas"]
    )

    documents = results["documents"][0]
    distances = results["distances"][0]
    metadatas = results["metadatas"][0]

    return [
        {"text": doc, "distance": dist, "metadata": meta}
        for doc, dist, meta in zip(documents, distances, metadatas)
    ]


def count_memories() -> int:
    return collection.count()


def get_all_memory_ids() -> list[str]:
    """현재 저장된 모든 memory ID 반환. 테스트 후 더미 데이터 정리용."""
    if collection.count() == 0:
        return []
    result = collection.get(include=[])
    return result["ids"]


def delete_memories(ids: list[str]):
    """지정한 ID 목록 삭제. 테스트 후 더미 데이터 정리용."""
    if not ids:
        return
    collection.delete(ids=ids)