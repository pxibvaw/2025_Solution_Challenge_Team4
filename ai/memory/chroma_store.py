# ai/memory/chroma_store.py
import logging
import chromadb
from chromadb.config import Settings as ChromaSettings
from ai.app.settings import settings

logger = logging.getLogger(__name__)

# ── Lazy initialization ───────────────────────────────────────────────────────
# module import 시점에 PersistentClient를 생성하지 않음.
# chromadb가 init 시 telemetry 서버로 HTTP 요청을 보내는데,
# 네트워크 환경에 따라 이 요청이 hang을 유발함.
# → 첫 실제 호출 시점까지 초기화를 미룬다.

_client = None
_collection = None


def _get_client() -> chromadb.PersistentClient:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_PATH,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        logger.info("[chroma_store] PersistentClient 초기화 완료: %s", settings.CHROMA_PERSIST_PATH)
    return _client


def get_collection():
    global _collection
    if _collection is None:
        _collection = _get_client().get_or_create_collection(
            name="memory",
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def add_memory(text: str, embedding: list, memory_id: str, metadata: dict = None):
    collection = get_collection()
    collection.add(
        documents=[text],
        embeddings=[embedding],
        ids=[memory_id],
        metadatas=[metadata or {}]
    )


def search_memory(query_embedding: list, k: int = 5):
    collection = get_collection()
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
    return get_collection().count()


def get_all_memory_ids() -> list[str]:
    """현재 저장된 모든 memory ID 반환. 테스트 후 더미 데이터 정리용."""
    collection = get_collection()
    if collection.count() == 0:
        return []
    result = collection.get(include=[])
    return result["ids"]


def delete_memories(ids: list[str]):
    """지정한 ID 목록 삭제. 테스트 후 더미 데이터 정리용."""
    if not ids:
        return
    get_collection().delete(ids=ids)