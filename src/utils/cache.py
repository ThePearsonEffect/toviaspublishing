from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Optional
from diskcache import Cache

from src.config import ensure_output_dir


_cache: Optional[Cache] = None


def get_cache() -> Cache:
    global _cache
    if _cache is None:
        base = Path(ensure_output_dir()) / ".cache"
        base.mkdir(parents=True, exist_ok=True)
        _cache = Cache(str(base))
    return _cache


def memoize(key: str, creator: Callable[[], Any], expire: int = 24 * 3600) -> Any:
    c = get_cache()
    if key in c:
        return c[key]
    value = creator()
    c.set(key, value, expire=expire)
    return value
