"""
Compatibility wrapper for :mod:`config.python.infrastructure`.

Re-exports keep ``from config.infrastructure import ...`` working without
moving the underlying implementation.
"""

from __future__ import annotations

from .python.infrastructure import *  # noqa: F401,F403
