"""Tool borrowing mechanism for thegent MCP server.

Allows external agents to discover and borrow thegent tools.
"""

from __future__ import annotations

import orjson as json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from phenotype_thegent_sync.integrations.base import SerializableMixin

_DEFAULT_MCP_HOST = "127.0.0.1"
_DEFAULT_MCP_PORT = 3847

# Category display names for CLAUDE.md snippets
_CATEGORY_DISPLAY: dict[str, str] = {
    "session": "Session Management",
    "research": "Web Research",
    "general": "General",
}

# Core tool catalog
TOOL_CATALOG: list[dict[str, Any]] = [
    {
        "name": "phenotype_thegent_run",
        "description": "Run an agent task",
        "module": "thegent.mcp.server",
        "function": "phenotype_thegent_run",
        "requires": ["thegent"],
        "category": "session",
        "read_only": False,
    },
    {
        "name": "phenotype_thegent_ps",
        "description": "List sessions",
        "module": "thegent.mcp.server",
        "function": "phenotype_thegent_ps",
        "requires": ["thegent"],
        "category": "session",
        "read_only": True,
    },
    {
        "name": "phenotype_thegent_free",
        "description": "Free agent task",
        "module": "thegent.mcp.server",
        "function": "phenotype_thegent_free",
        "requires": ["thegent"],
        "category": "session",
        "read_only": False,
    },
    {
        "name": "phenotype_thegent_history",
        "description": "Session history",
        "module": "thegent.mcp.server",
        "function": "phenotype_thegent_history",
        "requires": ["thegent"],
        "category": "session",
        "read_only": True,
    },
    {
        "name": "phenotype_thegent_ddg_search",
        "description": "DuckDuckGo search",
        "module": "thegent.mcp.server",
        "function": "phenotype_thegent_ddg_search",
        "requires": ["thegent"],
        "category": "research",
        "read_only": True,
    },
]


@dataclass
class ToolManifest(SerializableMixin):
    """Describes a borrowable tool."""

    name: str
    description: str
    module: str
    function: str
    requires: list[str]
    category: str = "general"
    read_only: bool = True


@dataclass
class BorrowConfig:
    """Configuration for borrowing tools from a thegent MCP server."""

    host: str = _DEFAULT_MCP_HOST
    port: int = _DEFAULT_MCP_PORT

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}/mcp"


class ToolBorrower:
    """Discovers and borrows tools from a thegent MCP server."""

    def __init__(self, config: BorrowConfig | None = None) -> None:
        self._config = config or BorrowConfig()
        self._catalog = [ToolManifest(**entry) for entry in TOOL_CATALOG]

    def list_available_tools(self) -> list[ToolManifest]:
        """Return all available tools sorted by category then name."""
        return sorted(self._catalog, key=lambda t: (t.category, t.name))

    def list_available_tools_by_category(self) -> dict[str, list[ToolManifest]]:
        """Return tools grouped by category."""
        result: dict[str, list[ToolManifest]] = {}
        for tool in self.list_available_tools():
            result.setdefault(tool.category, []).append(tool)
        return result

    def get_tool(self, name: str) -> ToolManifest | None:
        """Look up a tool by name."""
        for tool in self._catalog:
            if tool.name == name:
                return tool
        return None

    def export_tool_config(self, tool_names: list[str]) -> dict[str, Any]:
        """Export MCP server config for the given tool names.

        Raises:
            ValueError: If any tool name is not in the catalog.
        """
        if not tool_names:
            tool_names = [t.name for t in self.list_available_tools()]

        for name in tool_names:
            if self.get_tool(name) is None:
                raise ValueError(f"Unknown tool: {name!r}")

        categories = sorted({self.get_tool(n).category for n in tool_names})  # type: ignore[union-attr]
        return {
            "thegent": {
                "type": "http",
                "url": self._config.url,
                "metadata": {
                    "borrowed_tools": tool_names,
                    "categories": categories,
                },
            }
        }

    def generate_mcp_json(
        self,
        tool_names: list[str],
        output_dir: Path,
        merge: bool = False,
    ) -> Path:
        """Write an mcp.json config file into output_dir.

        Creates output_dir if it does not exist. When merge=True, merges the
        thegent server entry into an existing mcp.json preserving all other
        server entries. Returns the absolute path to the written file.

        Raises:
            ValueError: If any tool name is unknown.
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "mcp.json"

        server_entry = self.export_tool_config(tool_names)["thegent"]

        if merge and output_path.exists():
            existing = json.loads(output_path.read_text(encoding="utf-8"))
            mcp_servers: dict[str, Any] = existing.get("mcpServers", {})
        else:
            mcp_servers = {}

        mcp_servers["thegent"] = server_entry
        output_path.write_text(json.dumps({"mcpServers": mcp_servers}, indent=2), encoding="utf-8")
        return output_path.resolve()

    def generate_claude_md_snippet(self, tool_names: list[str]) -> str:
        """Generate a CLAUDE.md snippet describing the borrowed tools.

        Raises:
            ValueError: If any tool name is unknown.
        """
        if not tool_names:
            tool_names = [t.name for t in self.list_available_tools()]

        for name in tool_names:
            if self.get_tool(name) is None:
                raise ValueError(f"Unknown tool: {name!r}")

        tools = [self.get_tool(n) for n in tool_names]

        lines = [
            "# thegent MCP Tools",
            "",
            "## Usage",
            "",
            f"MCP server URL: `{self._config.url}`",
            "",
            "## Available Tools",
            "",
        ]

        by_category: dict[str, list[ToolManifest]] = {}
        for tool in tools:
            by_category.setdefault(tool.category, []).append(tool)  # type: ignore[union-attr]

        for cat in sorted(by_category):
            display = _CATEGORY_DISPLAY.get(cat, cat.replace("_", " ").title())
            lines.append(f"### {display}")
            lines.append("")
            for tool in sorted(by_category[cat], key=lambda t: t.name):
                annotation = " (read-only)" if tool.read_only else ""
                lines.append(f"- **{tool.name}**{annotation}: {tool.description}")
            lines.append("")

        return "\n".join(lines)

    def validate_server_reachable(self, timeout: float = 2.0) -> bool:
        """Return True if the MCP server responds with HTTP 200."""
        import httpx

        try:
            resp = httpx.get(self._config.url, timeout=timeout)
            return resp.status_code == 200
        except Exception:
            return False
