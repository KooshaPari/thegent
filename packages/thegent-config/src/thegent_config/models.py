"""Configuration models for different settings groups.

Split from config.py for maintainability.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings


class PathSettings(BaseSettings):
    """Path and directory configuration."""

    factory_skills_dir: Path = Field(
        default=Path("~/.thegent/skills").expanduser(),
        description="Directory for factory skills",
    )
    factory_droids_dir: Path = Field(
        default=Path("~/.thegent/droids").expanduser(),
        description="Directory for factory droids",
    )
    cache_dir: Path = Field(
        default=Path("~/.thegent/cache").expanduser(),
        description="Cache directory",
    )
    session_dir: Path = Field(
        default=Path("~/.thegent/sessions").expanduser(),
        description="Session directory",
    )
    fifo_path: Path | None = Field(
        default=None,
        description="Path to FIFO for communication",
    )
    holdpty_socket_dir: Path | None = Field(
        default=None,
        description="Directory for holdpty sockets",
    )
    session_meta_path: Path | None = Field(
        default=None,
        description="Path to session metadata",
    )
    session_rc_path: Path | None = Field(
        default=None,
        description="Path to session RC file",
    )
    health_snapshot_path: Path | None = Field(
        default=None,
        description="Path to health snapshots",
    )
    mcp_storage_dir: Path | None = Field(
        default=None,
        description="MCP storage directory",
    )
    cwd: Path | None = Field(
        default=None,
        description="Current working directory override",
    )


class ModelDefaultsSettings(BaseSettings):
    """Default model configuration."""

    cursor_agent_cmd: str = Field(
        default="cursor-agent",
        description="Cursor agent command",
    )
    default_cursor_model: str = Field(
        default="claude-3-5-sonnet-20241022",
        description="Default model for Cursor",
    )
    default_gemini_model: str = Field(
        default="gemini-2.0-flash",
        description="Default model for Gemini",
    )
    default_copilot_model: str = Field(
        default="gpt-4o",
        description="Default model for Copilot",
    )
    default_claude_model: str = Field(
        default="claude-3-5-sonnet-20241022",
        description="Default model for Claude",
    )
    default_codex_model: str = Field(
        default="o4-mini",
        description="Default model for Codex",
    )
    default_codex_model_high: str = Field(
        default="o3",
        description="High-tier model for Codex",
    )
    default_antigravity_model: str = Field(
        default="claude-3-5-sonnet-20241022",
        description="Default model for Antigravity",
    )
    default_kiro_model: str = Field(
        default="claude-3-5-sonnet-20241022",
        description="Default model for Kiro",
    )


class TimeoutSettings(BaseSettings):
    """Timeout configuration."""

    default_timeout: int = Field(
        default=300,
        description="Default timeout in seconds",
    )
    default_timeout_claude: int = Field(
        default=300,
        description="Default timeout for Claude in seconds",
    )
    default_timeout_free: int = Field(
        default=120,
        description="Default timeout for free models in seconds",
    )
    max_idle_seconds: int = Field(
        default=180,
        description="Maximum idle seconds before termination",
    )
    max_wall_time: int = Field(
        default=3600,
        description="Maximum wall time in seconds",
    )


class SessionSettings(BaseSettings):
    """Session and backend configuration."""

    session_backend: Literal["auto", "zmx", "tmux", "none"] = Field(
        default="auto",
        description="Session backend to use",
    )
    zmx_bin: str = Field(
        default="zmx",
        description="ZMX binary path",
    )
    use_fifo: bool = Field(
        default=False,
        description="Use FIFO for communication",
    )
    use_holdpty: bool = Field(
        default=False,
        description="Use holdpty for terminal management",
    )


class RetentionSettings(BaseSettings):
    """Retention policy configuration."""

    models_cache_ttl_sec: int = Field(
        default=86400,
        description="Models cache TTL in seconds",
    )
    retention_days_sessions: int = Field(
        default=7,
        description="Retention days for sessions",
    )
    retention_default_days: int = Field(
        default=30,
        description="Default retention days",
    )
    retention_days_registry: int = Field(
        default=30,
        description="Retention days for registry",
    )
    retention_days_health: int = Field(
        default=7,
        description="Retention days for health snapshots",
    )
    retention_by_domain: dict[str, int] = Field(
        default_factory=dict,
        description="Retention days by domain",
    )
    default_domain_tag: str | None = Field(
        default=None,
        description="Default domain tag",
    )
    retention_policy: str | None = Field(
        default=None,
        description="Retention policy name",
    )
    health_snapshot_max_lines: int = Field(
        default=1000,
        description="Maximum lines in health snapshot",
    )


class BudgetSettings(BaseSettings):
    """Budget and cost tracking configuration."""

    budget_hourly_limit: float = Field(
        default=10.0,
        description="Hourly budget limit in USD",
    )
    budget_daily_limit: float = Field(
        default=100.0,
        description="Daily budget limit in USD",
    )
    budget_run_limit: float = Field(
        default=50.0,
        description="Per-run budget limit in USD",
    )
    budget_warning_threshold: float = Field(
        default=0.8,
        description="Budget warning threshold (fraction)",
    )
    cost_tracking_enabled: bool = Field(
        default=True,
        description="Enable cost tracking",
    )
    cost_tracking: bool = Field(
        default=True,
        description="Enable cost tracking (alias)",
    )
    cost_budget_mtd: float = Field(
        default=1000.0,
        description="Month-to-date budget in USD",
    )
    cost_budget_by_category: dict[str, float] = Field(
        default_factory=dict,
        description="Budget by category",
    )


class RoutingSettings(BaseSettings):
    """Routing configuration."""

    default_routing: str = Field(
        default="pareto",
        description="Default routing strategy",
    )
    routing_enabled: bool = Field(
        default=True,
        description="Enable routing",
    )
    routing_constraints_enabled: bool = Field(
        default=True,
        description="Enable routing constraints",
    )
    routing_budget_warning_threshold: float = Field(
        default=0.8,
        description="Routing budget warning threshold",
    )
    routing_cost_aware_enabled: bool = Field(
        default=True,
        description="Enable cost-aware routing",
    )
    cost_quality_min_weight: float = Field(
        default=0.3,
        description="Minimum weight for quality in cost routing",
    )
    cost_quality_budget_tighten_threshold: float = Field(
        default=0.7,
        description="Threshold to tighten budget",
    )
    auto_router_enabled: bool = Field(
        default=False,
        description="Enable auto router",
    )
    auto_router_classifier_model: str = Field(
        default="claude-3-5-haiku-20241022",
        description="Model for auto router classification",
    )
    auto_router_use_classifier: bool = Field(
        default=True,
        description="Use classifier in auto router",
    )
    auto_router_min_quality: float = Field(
        default=0.7,
        description="Minimum quality threshold",
    )
    auto_router_max_cost_weight: float = Field(
        default=0.5,
        description="Maximum cost weight",
    )


class GovernanceSettings(BaseSettings):
    """Governance and normalization configuration."""

    normalization_policy_allow_fallback: bool = Field(
        default=True,
        description="Allow fallback in normalization",
    )
    normalization_policy_min_confidence: float = Field(
        default=0.8,
        description="Minimum confidence for normalization",
    )
    normalization_policy_max_fallback_rate: float = Field(
        default=0.1,
        description="Maximum fallback rate",
    )
    normalization_policy_strict_providers: str = Field(
        default="",
        description="Comma-separated list of strict providers",
    )
    routing_parser_quality_enabled: bool = Field(
        default=True,
        description="Enable parser quality routing",
    )
    contract_schema_version_minimum: str = Field(
        default="1.0.0",
        description="Minimum contract schema version",
    )


class OwnerSettings(BaseSettings):
    """Owner and scope configuration."""

    owner_tag: str | None = Field(
        default=None,
        description="Owner tag for resources",
    )
    owner_scope: str = Field(
        default="user",
        description="Owner scope",
    )


class OutputSettings(BaseSettings):
    """Output configuration."""

    output_format: str | None = Field(
        default=None,
        description="Output format",
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode",
    )
    debug_keepalive: bool = Field(
        default=False,
        description="Enable debug keepalive",
    )


class MCPSettings(BaseSettings):
    """MCP and control plane configuration."""

    mcp_host: str = Field(
        default="127.0.0.1",
        description="MCP server host",
    )
    mcp_port: int = Field(
        default=8765,
        description="MCP server port",
    )
    control_plane_url: str = Field(
        default="http://127.0.0.1",
        description="Control plane URL",
    )
    control_plane_port: int = Field(
        default=8766,
        description="Control plane port",
    )


class SecuritySettings(BaseSettings):
    """Security configuration."""

    terminal_management_enabled: bool = Field(
        default=True,
        description="Enable terminal management",
    )
    input_guardrails_enabled: bool = Field(
        default=True,
        description="Enable input guardrails",
    )
    sandbox_level: str = Field(
        default="standard",
        description="Sandbox level",
    )
    sandbox_env_filter: bool = Field(
        default=True,
        description="Enable sandbox environment filtering",
    )


class BinarySettings(BaseSettings):
    """Binary paths configuration."""

    mergiraf_binary: str | None = Field(
        default=None,
        description="Path to mergiraf binary",
    )
    cliproxy_binary: str = Field(
        default="cliproxy",
        description="Path to cliproxy binary",
    )
    cliproxy_port: int = Field(
        default=8317,
        description="CLIPROXY server port",
    )


__all__ = [
    "PathSettings",
    "ModelDefaultsSettings",
    "TimeoutSettings",
    "SessionSettings",
    "RetentionSettings",
    "BudgetSettings",
    "RoutingSettings",
    "GovernanceSettings",
    "OwnerSettings",
    "OutputSettings",
    "MCPSettings",
    "SecuritySettings",
    "BinarySettings",
]
