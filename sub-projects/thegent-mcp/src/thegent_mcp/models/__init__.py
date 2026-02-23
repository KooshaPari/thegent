"""Shared models for thegent-mcp."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ToolCall(BaseModel):
    """Contract for agents calling MCP tools."""

    tool_name: str
    args: dict[str, Any]
    timeout_sec: int = 30


class ToolResult(BaseModel):
    """Tool execution result."""

    tool_name: str
    success: bool
    output: Any = None
    error: str | None = None
    duration_ms: int = 0
