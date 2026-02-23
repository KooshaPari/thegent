"""
Top-level config package wrapper.

Historically the project stored the real implementations under
``config/python`` and downstream code imported modules like
``config.settings`` or ``from config import get_settings``. Because the
package itself lacked an ``__init__`` module those imports failed unless
extra PYTHONPATH tweaks were applied. This shim makes ``config`` a proper
package and re-exports the helpers from their existing locations so the
rest of the application can keep its current import paths.
"""

from __future__ import annotations

from .python.infrastructure import (
    get_auth_adapter,
    get_database_adapter,
    get_rate_limiter,
    get_realtime_adapter,
    get_storage_adapter,
)
from .python.session import get_session_manager
from .python.settings import AppSettings, Settings, get_settings, reset_settings_cache
from .python.vector import (
    get_embedding_service,
    get_enhanced_vector_search_service,
    get_progressive_embedding_service,
    get_vector_search_service,
)

__all__ = [
    # Settings
    "AppSettings",
    "Settings",
    "get_settings",
    "reset_settings_cache",
    # Infrastructure
    "get_auth_adapter",
    "get_database_adapter",
    "get_rate_limiter",
    "get_realtime_adapter",
    "get_storage_adapter",
    # Session
    "get_session_manager",
    # Vector / embeddings
    "get_embedding_service",
    "get_enhanced_vector_search_service",
    "get_progressive_embedding_service",
    "get_vector_search_service",
]
