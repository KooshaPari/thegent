"""FastMCP server for agent orchestration."""

from __future__ import annotations

import json
from typing import Any

from fastmcp import FastMCP
from pydantic import BaseModel

mcp = FastMCP("thegent-agents")


# ===== Tool Input Models =====


class RunAgentRequest(BaseModel):
    agent_id: str = "default"
    prompt: str
    context: dict[str, Any] = {}
    model: str | None = None
    temperature: float = 1.0


class AgentIdRequest(BaseModel):
    agent_id: str


class QueryMemoryRequest(BaseModel):
    agent_id: str
    query: str
    limit: int = 10


class AddMemoryRequest(BaseModel):
    agent_id: str
    item: dict[str, Any]


# ===== Tools =====


@mcp.tool()
async def run_agent(
    agent_id: str = "default",
    prompt: str = "",
    context: dict[str, Any] | None = None,
    model: str | None = None,
    temperature: float = 1.0,
) -> str:
    """Execute an agent task."""
    # Placeholder: will be wired to actual agent runner after extraction
    return json.dumps(
        {
            "type": "done",
            "result": {"success": True, "agent_id": agent_id},
            "timing_ms": 0,
        }
    )


@mcp.tool()
async def list_agents() -> str:
    """Get available agent personas."""
    return json.dumps(
        {
            "agents": ["default", "research", "code", "fix", "review", "explain"],
        }
    )


@mcp.tool()
async def get_agent_state(agent_id: str) -> str:
    """Get current agent state."""
    return json.dumps(
        {
            "agent_id": agent_id,
            "status": "idle",
            "current_task": None,
            "elapsed_ms": 0,
        }
    )


@mcp.tool()
async def stop_agent(agent_id: str) -> str:
    """Stop a running agent."""
    return json.dumps({"success": True, "agent_id": agent_id})


@mcp.tool()
async def query_memory(agent_id: str, query: str, limit: int = 10) -> str:
    """Query agent memory store."""
    return json.dumps({"results": []})


@mcp.tool()
async def add_memory(agent_id: str, item: dict[str, Any] | None = None) -> str:
    """Add item to agent memory."""
    return json.dumps({"success": True})
