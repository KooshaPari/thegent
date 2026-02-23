"""Chat and message history - ChatHistory, MessageRegistry.

Extracted from execution.py for maintainability.
"""

from __future__ import annotations

# Re-export from execution.py for now
from thegent.execution import (
    ChatEntry,
    ChatHistory,
    MessageEntry,
    MessageRegistry,
)

__all__ = [
    "ChatEntry",
    "ChatHistory",
    "MessageEntry",
    "MessageRegistry",
]
