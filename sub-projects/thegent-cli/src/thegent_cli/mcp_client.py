"""MCP client for CLI to agents communication."""

from __future__ import annotations

import asyncio
import subprocess
from contextlib import asynccontextmanager
from typing import AsyncIterator

import httpx
from pydantic import BaseModel


class AgentChunk(BaseModel):
    """Single chunk from agent streaming response."""

    type: str  # "chunk" | "done"
    data: str | None = None
    result: dict | None = None
    timing_ms: int | None = None


class CLIAgentClient:
    """Thin MCP wrapper for CLI -> agents communication."""

    def __init__(
        self,
        mcp_host: str = "127.0.0.1",
        mcp_port: int = 3847,
        auto_start: bool = True,
    ) -> None:
        self.mcp_host = mcp_host
        self.mcp_port = mcp_port
        self.auto_start = auto_start
        self._base_url = f"http://{mcp_host}:{mcp_port}"

    @asynccontextmanager
    async def connect(self) -> AsyncIterator[CLIAgentClient]:
        """Context manager for client lifecycle."""
        if self.auto_start:
            await self._ensure_agent_server()
        yield self

    async def _ensure_agent_server(self) -> None:
        """Start thegent-agents server if not already running."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self._base_url}/health",
                timeout=2.0,
            )
            resp.raise_for_status()

    async def run_agent(
        self,
        prompt: str,
        agent_id: str = "default",
        context: dict | None = None,
    ) -> AsyncIterator[str]:
        """Stream agent execution output."""
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self._base_url}/tools/run_agent",
                json={
                    "agent_id": agent_id,
                    "prompt": prompt,
                    "context": context or {},
                },
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    yield line

    async def list_agents(self) -> list[str]:
        """Get available agent personas."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self._base_url}/tools/list_agents")
            resp.raise_for_status()
            return resp.json()["agents"]
