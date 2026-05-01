"""ACP Session Endpoints.

Session management for ACP server.
"""

from __future__ import annotations

from typing import Any

# SessionEndpoints is defined in acp_server.py
from thegent.adapters.acp_server import SessionEndpoints, resolve_session_backend

__all__ = ["SessionEndpoints", "resolve_session_backend"]
