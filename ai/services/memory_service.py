# ai/services/memory_service.py
"""
ChromaDB 메모리 저장/조회/삭제 서비스.

변경 이력:
  - session_id/user_id 기반 격리 추가 (이슈 1+5)
  - MemoryService 인스턴스 메서드로 통합
  - 기존 모듈 레벨 함수(save_memory, retrieve_memory)는
    하위 호환을 위해 deprecated wrapper로 유지

설계 근거:
  - ChromaDB Cookbook Multi-Tenancy: 단일 컬렉션 + metadata 필터
  - 컬렉션 객체는 싱글턴으로 공유, 격리는 where 절로 수행
  - delete_by_session: session_id 필터로 해당 세션만 삭제 (기존: 전체 삭제 버그)
"""
import logging
import uuid
from datetime import datetime

from ai.embedding.embedder import embed_text
from ai.memory.chroma_store import (
    add_memory,
    search_memory,
    count_memories,
    get_all_memory_ids,
    delete_memories,
    get_collection,
)
from ai.services.memory_retriever import retrieve

logger = logging.getLogger(__name__)


class MemoryService:
    """
    ChromaDB 메모리 서비스.

    collection 객체는 모듈 레벨 싱글턴을 공유.
    세션/유저 격리는 metadata의 session_id, user_id 필드 + where 절로 수행.
    """

    # ── 저장 ─────────────────────────────────────────────────

    def save(
        self,
        text: str,
        importance: float = 5.0,
        session_id: str = "",
        user_id: str = "",
    ) -> None:
        """
        메모리 저장 (session_id/user_id 포함).

        Args:
            text:        저장할 fact 텍스트
            importance:  중요도 점수
            session_id:  세션 ID (격리용)
            user_id:     사용자 ID (격리용)
        """
        embedding = embed_text(text)
        metadata = {
            "importance": importance,
            "session_id": session_id,
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
        }
        add_memory(
            text=text,
            embedding=embedding,
            memory_id=str(uuid.uuid4()),
            metadata=metadata,
        )

    # ── 조회 ─────────────────────────────────────────────────

    def retrieve(self, query_text: str, k: int = 5) -> list[str]:
        """
        기존 retrieve_memory와 동일한 기능.

        embed_text/ChromaDB 호출 실패 시 빈 리스트 반환 → /turn은 계속 동작.
        (Gemini embed API 일시 장애 / 할당량 초과 / 네트워크 블립 대비)
        """
        try:
            memory_count = count_memories()
            return retrieve(
                query_text=query_text,
                memory_count=memory_count,
                top_k=k,
            )
        except Exception as e:
            logger.warning(
                f"[memory_service] retrieve 실패 — 빈 메모리로 계속 진행: {e}",
                exc_info=True,
            )
            return []

    # ── 에피소드 파이프라인용 ──────────────────────────────────

    def flush(self, session_id: str) -> None:
        """
        미저장 facts 강제 저장.

        현재 구조에서는 orchestrator.end_session()이 먼저
        process_memory_pipeline()을 완료한 뒤 episode_service가 호출되므로
        별도 처리 불필요. 타이밍 의존 관계를 명시하기 위해 메서드 유지.
        """
        pass

    def get_facts_by_session(self, session_id: str) -> list[str]:
        """
        해당 세션의 메모리 텍스트만 반환.

        수정 전: session_id를 무시하고 전체 문서를 반환 (버그)
        수정 후: where={"session_id": session_id}로 격리
        """
        if not session_id:
            logger.warning("[memory_service] get_facts_by_session: session_id가 비어있음")
            return []
        try:
            result = get_collection().get(
                where={"session_id": session_id},
                include=["documents"],
            )
            return result["documents"] if result["documents"] else []
        except Exception as e:
            logger.error(f"[memory_service] get_facts_by_session 실패: {e}")
            return []

    def delete_by_session(self, session_id: str) -> int:
        """
        해당 세션의 메모리만 삭제.

        수정 전: 전체 메모리를 삭제 (버그)
        수정 후: where={"session_id": session_id}로 해당 세션만 삭제
        """
        if not session_id:
            logger.warning("[memory_service] delete_by_session: session_id가 비어있음")
            return 0
        try:
            result = get_collection().get(
                where={"session_id": session_id},
                include=[],
            )
            ids = result["ids"]
            if ids:
                delete_memories(ids)
            return len(ids)
        except Exception as e:
            logger.error(f"[memory_service] delete_by_session 실패: {e}")
            return 0


# ── 싱글턴 인스턴스 ──────────────────────────────────────────
memory_service = MemoryService()


# ── Deprecated 하위 호환 래퍼 ─────────────────────────────────
# orchestrator.py의 기존 `from ai.services.memory_service import save_memory`
# 호출을 깨뜨리지 않기 위해 유지.
# 신규 코드에서는 memory_service.save()를 직접 사용할 것.

def save_memory(
    text: str,
    importance: float = 5.0,
    session_id: str = "",
    user_id: str = "",
) -> None:
    """
    Deprecated: memory_service.save()를 직접 사용하세요.

    하위 호환을 위해 유지. session_id/user_id를 넘기지 않으면
    빈 문자열로 저장되어 세션 격리가 되지 않습니다.
    """
    memory_service.save(
        text=text,
        importance=importance,
        session_id=session_id,
        user_id=user_id,
    )


def retrieve_memory(query_text: str, k: int = 5) -> list[str]:
    """Deprecated: memory_service.retrieve()를 직접 사용하세요."""
    return memory_service.retrieve(query_text=query_text, k=k)
