"""Runtime execution configuration settings for thegent.

Settings related to sandboxing, budgets, retention, and execution behavior.
"""

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from thegent_config.defaults import (
    default_cost_budget_by_category,
    default_hitl_checkpoints,
    default_mac_keep_awake_agents,
    default_sandbox_env_allowlist,
)
from thegent_config.parsers import parse_retention_by_domain


class RuntimeConfig(BaseSettings):
    """Runtime execution, sandboxing, and budget configuration."""

    model_config = SettingsConfigDict(
        env_prefix="THGENT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Session backend configuration
    session_backend: Literal["auto", "zmx", "tmux", "none"] = Field(
        default="auto",
        description="Session persistence backend for agent sessions.",
    )
    zmx_bin: str = Field(
        default="zmx",
        description="Path or command name for the zmx binary",
    )
    use_fifo: bool = Field(
        default=False,
        description="Enable stdin FIFO for background sessions",
    )
    use_holdpty: bool = Field(
        default=False,
        description="Wrap background sessions with holdpty for interactive attach",
    )

    # Retention policy
    retention_days_sessions: int = Field(
        default=30,
        ge=7,
        le=365,
        description="Retention for session dirs",
    )
    retention_default_days: int = Field(
        default=30,
        ge=1,
        le=365,
        description="Default retention in days for history",
    )
    retention_days_registry: int = Field(
        default=90,
        ge=30,
        le=730,
        description="Retention for run registry (audit trail)",
    )
    retention_days_health: int = Field(
        default=90,
        ge=7,
        le=365,
        description="Retention for health snapshots",
    )
    retention_by_domain: dict[str, int] = Field(
        default_factory=dict,
        description="Per-domain retention days",
    )
    default_domain_tag: str | None = Field(
        default=None,
        description="Default domain tag for runs if not specified",
    )
    retention_policy: str | None = Field(
        default=None,
        description="Retention policy string",
    )

    # Budget settings
    budget_hourly_limit: float = Field(
        default=10.0,
        ge=0.0,
        description="Hourly budget limit in USD",
    )
    budget_daily_limit: float = Field(
        default=100.0,
        ge=0.0,
        description="Daily budget limit in USD",
    )
    budget_run_limit: float = Field(
        default=5.0,
        ge=0.0,
        description="Per-run budget limit in USD",
    )
    budget_warning_threshold: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Budget warning threshold (0.8 = 80%)",
    )

    # Cost tracking
    cost_tracking_enabled: bool = Field(
        default=True,
        description="Enable cost tracking per run",
    )
    cost_tracking: bool = Field(
        default=False,
        description="Legacy: enable cost tracking",
    )
    cost_budget_mtd: float = Field(
        default=100.0,
        ge=0.0,
        description="MTD budget for AI providers",
    )
    cost_budget_by_category: dict[str, float] = Field(
        default_factory=default_cost_budget_by_category,
        description="Per-category MTD budgets in USD",
    )

    # Sandbox configuration
    sandbox_level: str = Field(
        default="none",
        description="macOS sandbox level: none, readonly, restricted, networked, full",
    )
    sandbox_env_filter: bool = Field(
        default=False,
        description="Filter environment variables in sandbox",
    )
    sandbox_env_allowlist: list[str] = Field(
        default_factory=default_sandbox_env_allowlist,
        description="Environment variables allowed in sandbox",
    )

    # Keep-alive agents (macOS)
    mac_keep_awake_agents: list[str] = Field(
        default_factory=default_mac_keep_awake_agents,
        description="Agents to keep awake on macOS",
    )

    # Validation and retention parsing
    @staticmethod
    def parse_retention_by_domain_validator(v: object) -> dict[str, int]:
        """Validate retention_by_domain."""
        return parse_retention_by_domain(v)

    retention_policy_parse: str | None = Field(
        default=None,
        description="Parsed retention policy for compatibility",
    )
