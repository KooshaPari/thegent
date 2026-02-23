"""Contract tests for thegent-cli sub-project.

# @trace FR-T4-001 — CLI sub-project interface contracts
"""

from __future__ import annotations

import pytest

from thegent_cli.mcp_client import AgentChunk, CLIAgentClient
from thegent_cli.output import CLIOutput, format_output


class TestCLIAgentClient:
    """Verify CLIAgentClient conforms to interface spec."""

    def test_client_has_required_attributes(self) -> None:
        client = CLIAgentClient(auto_start=False)
        assert client.mcp_host == "127.0.0.1"
        assert client.mcp_port == 3847
        assert client.auto_start is False

    def test_client_custom_host_port(self) -> None:
        client = CLIAgentClient(mcp_host="192.168.1.1", mcp_port=9999, auto_start=False)
        assert client._base_url == "http://192.168.1.1:9999"

    def test_agent_chunk_model(self) -> None:
        chunk = AgentChunk(type="chunk", data="hello")
        assert chunk.type == "chunk"
        assert chunk.data == "hello"
        assert chunk.result is None

    def test_agent_chunk_done(self) -> None:
        chunk = AgentChunk(type="done", result={"success": True}, timing_ms=100)
        assert chunk.type == "done"
        assert chunk.result == {"success": True}
        assert chunk.timing_ms == 100


class TestCLIOutput:
    """Verify CLIOutput contract."""

    def test_format_output_success(self) -> None:
        output = format_output(status="success", result="done", agent_id="default")
        assert output.status == "success"
        assert output.result == "done"
        assert output.agent_id == "default"

    def test_format_output_error(self) -> None:
        output = format_output(status="error", result="failed")
        assert output.to_pretty_print() == "Error: failed"

    def test_format_output_json(self) -> None:
        output = format_output(status="success", result="ok")
        json_str = output.to_json()
        assert '"status": "success"' in json_str

    def test_cli_output_all_statuses(self) -> None:
        for status in ("pending", "running", "success", "error", "partial"):
            output = format_output(status=status, result="test")
            assert output.status == status
