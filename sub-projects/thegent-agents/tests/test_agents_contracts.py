"""Contract tests for thegent-agents sub-project.

# @trace FR-T4-002 — Agents MCP server interface contracts
"""

from __future__ import annotations

import json

import pytest

from thegent_agents.server import (
    AddMemoryRequest,
    AgentIdRequest,
    QueryMemoryRequest,
    RunAgentRequest,
    add_memory,
    get_agent_state,
    list_agents,
    query_memory,
    run_agent,
    stop_agent,
)


class TestAgentModels:
    """Verify Pydantic models conform to interface spec."""

    def test_run_agent_request_defaults(self) -> None:
        req = RunAgentRequest(prompt="test")
        assert req.agent_id == "default"
        assert req.prompt == "test"
        assert req.context == {}
        assert req.model is None
        assert req.temperature == 1.0

    def test_run_agent_request_custom(self) -> None:
        req = RunAgentRequest(
            agent_id="research",
            prompt="find info",
            context={"key": "val"},
            model="claude-opus-4.6",
            temperature=0.5,
        )
        assert req.agent_id == "research"
        assert req.model == "claude-opus-4.6"

    def test_agent_id_request(self) -> None:
        req = AgentIdRequest(agent_id="code")
        assert req.agent_id == "code"

    def test_query_memory_request(self) -> None:
        req = QueryMemoryRequest(agent_id="default", query="recent files")
        assert req.limit == 10

    def test_add_memory_request(self) -> None:
        req = AddMemoryRequest(
            agent_id="default",
            item={"type": "decision", "content": "use pydantic"},
        )
        assert req.item["type"] == "decision"


@pytest.mark.asyncio
class TestAgentTools:
    """Verify MCP tools return correct response format."""

    async def test_run_agent_returns_json(self) -> None:
        result = await run_agent(prompt="test")
        data = json.loads(result)
        assert data["type"] == "done"
        assert "result" in data

    async def test_list_agents_returns_agents(self) -> None:
        result = await list_agents()
        data = json.loads(result)
        assert "agents" in data
        assert isinstance(data["agents"], list)
        assert len(data["agents"]) > 0

    async def test_get_agent_state_returns_status(self) -> None:
        result = await get_agent_state(agent_id="default")
        data = json.loads(result)
        assert data["agent_id"] == "default"
        assert "status" in data

    async def test_stop_agent_returns_success(self) -> None:
        result = await stop_agent(agent_id="default")
        data = json.loads(result)
        assert data["success"] is True

    async def test_query_memory_returns_results(self) -> None:
        result = await query_memory(agent_id="default", query="test")
        data = json.loads(result)
        assert "results" in data

    async def test_add_memory_returns_success(self) -> None:
        result = await add_memory(agent_id="default", item={"key": "val"})
        data = json.loads(result)
        assert data["success"] is True
