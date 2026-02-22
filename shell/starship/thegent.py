"""
Starship module for thegent integration.

Shows:
- Agent status (running/idle)
- Current work stream
- Active LSP servers

Configuration in starship.toml:
  [thegent]
  symbol = "🤖"
  format = "[$symbol($status )($work_stream )($lsp )]($style)"
  style = "bold green"
  disabled = false

  # Enable work stream display
  show_work_stream = true

  # Enable LSP status
  show_lsp = true

Install:
1. Copy this file to ~/.config/starship/modules/ or ~/.starship/modules/
2. Add to starship.toml
3. Or use: starship config thegent.disabled false
"""

from __future__ import annotations

import subprocess
import os
import re
from typing import Optional


def get_thegent_status() -> str:
    """Get thegent agent status."""
    try:
        # Try to get session info
        result = subprocess.run(
            ["thegent", "ps", "--json"],
            capture_output=True,
            text=True,
            timeout=5,
            env={**os.environ, "NO_COLOR": "1"},
        )

        if result.returncode == 0 and result.stdout.strip():
            # Parse active sessions
            sessions = result.stdout.strip()
            if sessions and sessions != "[]":
                return "running"

        return "idle"
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return "idle"
    except Exception:
        return "idle"


def get_work_stream() -> Optional[str]:
    """Get current work stream item."""
    try:
        # Check work stream file
        stream_path = os.path.expanduser("~/thegent/docs/reference/WORK_STREAM.md")

        if not os.path.exists(stream_path):
            return None

        with open(stream_path) as f:
            content = f.read()

        # Find next uncompleted item
        lines = content.split("\n")
        in_claimed = False

        for line in lines:
            if line.strip().startswith("## CLAIMED"):
                in_claimed = True
            elif line.strip().startswith("## COMPLETED"):
                in_claimed = False
            elif in_claimed and line.strip().startswith("- [ ]"):
                # Extract task name
                task = line.strip()[5:].strip()
                if task:
                    # Truncate long task names
                    if len(task) > 30:
                        task = task[:27] + "..."
                    return task

        return None
    except Exception:
        return None


def get_lsp_servers() -> Optional[str]:
    """Get active LSP servers."""
    try:
        # Check for active LSP processes
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode != 0:
            return None

        # Count LSP-related processes
        lsp_patterns = ["pyright", "ruff", "typescript-language", "gopls", "rust-analyzer", "clangd"]
        servers = []

        for pattern in lsp_patterns:
            if pattern in result.stdout:
                servers.append(pattern)

        if servers:
            # Return abbreviated names
            abbrevs = {
                "pyright": "py",
                "ruff": "ruff",
                "typescript-language": "ts",
                "gopls": "go",
                "rust-analyzer": "rs",
                "clangd": "c",
            }
            return "[" + " ".join(abbrevs.get(s, s) for s in servers[:3]) + "]"

        return None
    except Exception:
        return None


def get_mcp_status() -> Optional[str]:
    """Get MCP server status."""
    try:
        result = subprocess.run(
            ["thegent", "mcp", "status"],
            capture_output=True,
            text=True,
            timeout=5,
            env={**os.environ, "NO_COLOR": "1"},
        )

        if result.returncode == 0 and "running" in result.stdout.lower():
            return "mcp"

        return None
    except Exception:
        return None


def get_context() -> dict:
    """Get all context for the module."""
    return {
        "status": get_thegent_status(),
        "work_stream": get_work_stream(),
        "lsp": get_lsp_servers(),
        "mcp": get_mcp_status(),
    }


def format_module(status: str, work_stream: Optional[str] = None, lsp: Optional[str] = None, mcp: Optional[str] = None) -> str:
    """Format the module output."""
    parts = []

    # Status
    if status == "running":
        parts.append("●")
    else:
        parts.append("○")

    # Work stream
    if work_stream:
        parts.append(f"📋{work_stream}")

    # LSP servers
    if lsp:
        parts.append(f"lsp:{lsp}")

    # MCP status
    if mcp:
        parts.append(mcp)

    return " ".join(parts)


# For testing
if __name__ == "__main__":
    ctx = get_context()
    output = format_module(
        ctx["status"],
        ctx["work_stream"],
        ctx["lsp"],
        ctx["mcp"],
    )
    print(f"thegent: {output}")

    # Detailed output
    print(f"\nStatus: {ctx['status']}")
    if ctx["work_stream"]:
        print(f"Work: {ctx['work_stream']}")
    if ctx["lsp"]:
        print(f"LSP: {ctx['lsp']}")
    if ctx["mcp"]:
        print(f"MCP: {ctx['mcp']}")
