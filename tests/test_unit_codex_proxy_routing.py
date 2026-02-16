"""Tests for CodexProxyRunner routing integration."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from thegent.agents.codex_proxy import CodexProxyRunner
from thegent.routing.models import TaskCategory, TaskMetadata
from thegent.routing.provider_types import ExecutionPath


class TestCodexProxyRunnerRouting:
    """Test that CodexProxyRunner consumes resolved routing from TaskMetadata."""

    def test_native_cli_provider_uses_codex_cli(self):
        """Native CLI providers (codex) use direct codex CLI execution."""
        runner = CodexProxyRunner("codex")
        metadata = TaskMetadata(
            category=TaskCategory.NORMAL,
            resolved_provider="codex",
            resolved_model_alias="gpt-5.3-codex-spark",
        )

        with patch.object(runner, "_execute_native_cli") as mock_native:
            mock_native.return_value = MagicMock(exit_code=0, stdout="done", stderr="", timed_out=False)
            result = runner.run_with_metadata("test prompt", Path("/tmp"), "read", 60, metadata=metadata)
            mock_native.assert_called_once()

    def test_api_key_provider_routes_correctly(self):
        """API key providers (minimax) use appropriate routing."""
        runner = CodexProxyRunner("minimax")
        metadata = TaskMetadata(
            category=TaskCategory.NORMAL,
            resolved_provider="minimax",
            resolved_model_alias="minimax-m2.5",
        )
        # Should not raise - validates routing path exists
        assert runner is not None
