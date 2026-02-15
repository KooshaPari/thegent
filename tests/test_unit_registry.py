"""Unit tests for agent and droid registry."""

from pathlib import Path

from thegent.agents import get_runner, list_agent_names, list_droid_names
from thegent.agents.codex_proxy import CodexProxyRunner
from thegent.agents.cursor_api_runner import CursorApiRunner
from thegent.agents.direct_agents import DirectAgentRunner


class TestListAgentNames:
    """Tests for list_agent_names."""

    def test_returns_all_agents(self) -> None:
        """Returns expected agent names."""
        names = list_agent_names()
        expected = {
            "gemini",
            "codex",
            "copilot",
            "cursor-agent",
            "cursor-api",
            "claude",
            "antigravity",
            "minimax",
            "glm",
            "cliproxy",
            "roo",
            "kilo",
        }
        assert set(names) == expected
        assert len(names) == len(expected)


class TestListDroidNames:
    """Tests for list_droid_names."""

    def test_empty_dir_returns_empty(self, tmp_path: Path) -> None:
        """Empty dir returns empty list."""
        assert list_droid_names(tmp_path) == []

    def test_returns_md_stems(self, tmp_path: Path) -> None:
        """Returns stem of each .md file."""
        (tmp_path / "plan-orchestrator.md").touch()
        (tmp_path / "code-reviewer.md").touch()
        (tmp_path / "readme.md").touch()
        names = list_droid_names(tmp_path)
        assert "plan-orchestrator" in names
        assert "code-reviewer" in names
        assert "readme" in names
        assert len(names) == 3

    def test_ignores_non_md(self, tmp_path: Path) -> None:
        """Ignores non-.md files."""
        (tmp_path / "foo.md").touch()
        (tmp_path / "bar.txt").touch()
        names = list_droid_names(tmp_path)
        assert names == ["foo"]

    def test_nonexistent_dir_returns_empty(self) -> None:
        """Nonexistent dir returns empty list."""
        assert list_droid_names(Path("/nonexistent/path/xyz")) == []


class TestGetRunner:
    """Tests for get_runner."""

    def test_returns_direct_runner_for_gemini(self) -> None:
        """Returns DirectAgentRunner for gemini (native CLI)."""
        runner = get_runner("gemini")
        assert runner is not None
        assert isinstance(runner, DirectAgentRunner)
        assert runner.agent_name == "gemini"

    def test_cursor_label_resolves_to_cursor_agent(self) -> None:
        """Label 'cursor' resolves to cursor-agent runner."""
        runner = get_runner("cursor")
        assert runner is not None
        assert isinstance(runner, DirectAgentRunner)
        assert runner.agent_name == "cursor-agent"

    def test_returns_none_for_unknown(self) -> None:
        """Returns None for unknown agent name."""
        assert get_runner("unknown-agent") is None

    def test_returns_proxy_runner_for_minimax_glm(self) -> None:
        """Returns CodexProxyRunner for minimax/glm (same backend as antigravity)."""
        for agent in ("minimax", "glm"):
            runner = get_runner(agent)
            assert runner is not None
            assert isinstance(runner, CodexProxyRunner)
            assert runner.agent_name == agent

    def test_all_agents_have_runners(self) -> None:
        """Every list_agent_names entry has a runner."""
        proxy_agents = {"antigravity", "minimax", "glm", "cliproxy", "roo", "kilo"}
        cursor_api_agents = {"cursor-api"}
        for name in list_agent_names():
            runner = get_runner(name)
            assert runner is not None, f"Missing runner for {name}"
            if name in proxy_agents:
                assert isinstance(runner, CodexProxyRunner)
            elif name in cursor_api_agents:
                assert isinstance(runner, CursorApiRunner)
            else:
                assert isinstance(runner, DirectAgentRunner)

    def test_returns_cursor_api_runner_for_cursor_api(self) -> None:
        """Returns CursorApiRunner for cursor-api."""
        runner = get_runner("cursor-api")
        assert runner is not None
        assert isinstance(runner, CursorApiRunner)
