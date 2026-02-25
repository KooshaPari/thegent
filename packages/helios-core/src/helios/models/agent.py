"""Agent-related models"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class AgentInfo:
    """Information about an agent"""
    name: str
    version: str | None = None
    model_name: str | None = None
    model_provider: str | None = None


@dataclass
class AgentContext:
    """Context passed to agent for execution"""
    task_id: str
    instruction: str
    working_dir: Path
    output_dir: Path
    env_vars: dict[str, str] = field(default_factory=dict)
    mcp_servers: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class AgentResult:
    """Result from agent execution"""
    success: bool
    trajectory_path: Path | None = None
    metrics: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    output: str = ""
