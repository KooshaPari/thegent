"""Multi-level caching subsystem for thegent.

Provides:
- MultiLevelCache: memory (L1) → disk (L2) cache with read-through and write-through
- cached_multi: decorator for easy function-level caching
- FrecencyCache: frecency-ranked cache (frequency × recency scoring)
- FrecencyEntry: snapshot of frecency data for a single key
- FrecencyModelSelector: model selection helper using frecency scoring
- CachePreWarmer: predictive pre-warmer for proactive cache loading
- WarmingStrategy: configuration dataclass for pre-warming strategies
- model_list_strategy: built-in strategy for model-list cache keys
- session_list_strategy: built-in strategy for session-list cache keys
"""

from thegent.cache.frecency import FrecencyCache, FrecencyEntry, FrecencyModelSelector
from thegent.cache.multi_level import MultiLevelCache, cached_multi
from thegent.cache.pre_warmer import (
    CachePreWarmer,
    WarmingStrategy,
    model_list_strategy,
    session_list_strategy,
)

__all__ = [
    "CachePreWarmer",
    "FrecencyCache",
    "FrecencyEntry",
    "FrecencyModelSelector",
    "MultiLevelCache",
    "WarmingStrategy",
    "cached_multi",
    "model_list_strategy",
    "session_list_strategy",
]
