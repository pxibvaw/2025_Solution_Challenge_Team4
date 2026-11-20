# ai/utils/cache.py
"""
캐시 백엔드 추상화 레이어.

현재: InMemoryCacheBackend (cachetools.TTLCache 래핑)
추후: RedisCacheBackend 추가 시 import만 교체하면 됨

설계 근거:
  - Strategy Pattern: 백엔드 교체 시 인터페이스 불변
  - cachetools.TTLCache: PyPI 1억+ 다운로드 검증 라이브러리
  - threading.Lock: cachetools는 thread-safe하지 않음 (이슈 #294)
    FastAPI의 run_in_executor 환경에서 동시 접근 보호 필수
"""
import threading
from typing import Any, Optional, Protocol, runtime_checkable

from cachetools import TTLCache


@runtime_checkable
class CacheBackend(Protocol):
    """
    캐시 백엔드 인터페이스.

    Redis 교체 시 이 Protocol만 구현하면 됨.
    runtime_checkable 덕분에 isinstance() 체크 가능.
    """

    def get(self, key: str) -> Optional[Any]: ...
    def set(self, key: str, value: Any) -> None: ...
    def delete(self, key: str) -> None: ...
    def clear_by_prefix(self, prefix: str) -> int: ...


class InMemoryCacheBackend:
    """
    cachetools.TTLCache 기반 in-memory 캐시.

    단일 프로세스 배포(uvicorn 1 worker)용.
    멀티 프로세스 전환 시 RedisCacheBackend로 교체.

    Thread Safety:
      cachetools.TTLCache는 thread-safe하지 않음.
      모든 접근을 threading.Lock으로 보호.
      Lock은 인스턴스 내부에 캡슐화 — 사용부에서 신경 쓸 필요 없음.
    """

    def __init__(self, maxsize: int, ttl: float):
        """
        Args:
            maxsize: 최대 항목 수 (초과 시 LRU 방식 제거)
            ttl:     항목 유효 시간 (초)
        """
        self._cache = TTLCache(maxsize=maxsize, ttl=ttl)
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            return self._cache.get(key)

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            self._cache[key] = value

    def delete(self, key: str) -> None:
        with self._lock:
            self._cache.pop(key, None)

    def clear_by_prefix(self, prefix: str) -> int:
        """prefix로 시작하는 모든 키 제거. /test/cleanup에서 사용."""
        with self._lock:
            keys = [k for k in self._cache if k.startswith(prefix)]
            for k in keys:
                self._cache.pop(k, None)
            return len(keys)

    def __contains__(self, key: str) -> bool:
        """'key in cache' 문법 지원."""
        with self._lock:
            return key in self._cache

    def __len__(self) -> int:
        with self._lock:
            return len(self._cache)
