"""Composite settings class for thegent.

This module provides the main ThegentSettings class that composes model, path,
and runtime configurations. It maintains backward compatibility with the
original monolithic settings class.
"""

import os
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from phenotype_thegent_core.config_defaults import (
    DEFAULT_MAC_KEEP_AWAKE_AGENTS,
    DEFAULT_SANDBOX_ENV_ALLOWLIST,
    default_cost_budget_by_category,
    default_hitl_checkpoints,
    default_mac_keep_awake_agents,
    default_sandbox_env_allowlist,
    expanded_path_factory,
)
from phenotype_thegent_core.config_parsers import (
    parse_bool_or_env_flag,
    parse_csv_or_list,
    parse_first_nonempty_env,
    parse_optional_path,
    parse_retention_by_domain,
    parse_shell_path,
)
from phenotype_thegent_core.config.model_config import ModelConfig
from phenotype_thegent_core.config.path_config import PathConfig
from phenotype_thegent_core.config.runtime_config import RuntimeConfig


class ThegentSettings(BaseSettings):
    """Composite configuration for thegent CLI.

    This class inherits fields from ModelConfig, PathConfig, and RuntimeConfig,
    providing a single unified interface for all settings while maintaining
    logical separation of concerns internally.
    """

    model_config = SettingsConfigDict(
        env_prefix="THGENT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Model-related settings (from ModelConfig)
    default_cursor_model: str = Field(
        default="gemini-3-flash",
        description="Default model for cursor agent",
    )
    default_gemini_model: str = Field(
        default="gemini-3-flash",
        description="Default model for gemini CLI",
    )
    default_copilot_model: str = Field(
        default="gpt-5-mini",
        description="Default model for copilot",
    )
    default_claude_model: str = Field(
        default="claude-opus-4.6",
        description="Default model for claude",
    )
    default_codex_model: str = Field(
        default="gpt-5.3-codex-spark",
        description="Default model for codex",
    )
    default_codex_model_high: str = Field(
        default="gpt-5.3-codex-high",
        description="Codex high-power model",
    )
    default_antigravity_model: str = Field(
        default="gemini-3-flash",
        description="Default model for antigravity",
    )
    default_kiro_model: str = Field(
        default="claude-haiku-4.5",
        description="Default model for kiro",
    )
    default_timeout: int = Field(
        default=1800,
        ge=10,
        le=3600,
        description="Default agent timeout in seconds",
    )
    default_timeout_claude: int = Field(
        default=1800,
        ge=60,
        le=3600,
        description="Claude agent timeout",
    )
    default_timeout_free: int = Field(
        default=300,
        ge=60,
        le=3600,
        description="Free agent timeout for WP tasks",
    )
    max_idle_seconds: int = Field(
        default=180,
        ge=60,
        le=600,
        description="Activity-based hang detection",
    )
    max_wall_time: int = Field(
        default=0,
        ge=0,
        le=86400,
        description="Optional absolute cap in seconds",
    )
    default_routing: str = Field(
        default="prefer_direct",
        description="Default routing policy",
    )
    routing_enabled: bool = Field(
        default=True,
        description="Enable task routing based on Terminal Bench 2.0",
    )
    routing_constraints_enabled: bool = Field(
        default=True,
        description="Enable hard constraint validation for routing",
    )
    routing_budget_warning_threshold: float = Field(
        default=0.80,
        ge=0.0,
        le=1.0,
        description="Budget utilization threshold for warnings",
    )
    routing_parser_quality_enabled: bool = Field(
        default=True,
        description="Enable parser-quality based routing",
    )
    routing_cost_aware_enabled: bool = Field(
        default=True,
        description="Enable cost_quality routing when budget pressure",
    )
    cost_quality_min_weight: float = Field(
        default=0.1,
        ge=0.0,
        le=2.0,
        description="Minimum cost_weight for cost_quality policy",
    )
    cost_quality_budget_tighten_threshold: float = Field(
        default=0.80,
        ge=0.5,
        le=1.0,
        description="Budget utilization above this tightens quality floor",
    )
    auto_router_enabled: bool = Field(
        default=True,
        description="Enable auto router when agent/model is 'auto'",
    )
    auto_router_classifier_model: str = Field(
        default="gemini-3-flash",
        description="Model for headless task complexity classification",
    )
    auto_router_use_classifier: bool = Field(
        default=True,
        description="Use Gemini Flash to classify prompt",
    )
    auto_router_min_quality: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Minimum quality floor for Pareto selection",
    )
    auto_router_max_cost_weight: float = Field(
        default=2.0,
        ge=0.1,
        le=10.0,
        description="Maximum cost weight for Pareto selection",
    )
    otel_console: bool = Field(
        default=False,
        description="Enable console OpenTelemetry span export for local observability imports",
    )
    watcher_use_shm: bool = Field(
        default=False,
        description="Enable shared-memory health tracking for the native watcher daemon",
    )
    watcher_shm_path: str = Field(
        default="",
        description="Optional shared-memory path override for the native watcher daemon",
    )
    use_native_shm: bool = Field(
        default=False,
        description="Enable native shared-memory state backends when available",
    )

    # Path-related settings (from PathConfig)
    factory_skills_dir: Path = Field(
        default_factory=expanded_path_factory("~/.factory/skills"),
        description="Factory skills directory",
    )
    factory_droids_dir: Path = Field(
        default_factory=expanded_path_factory("~/.factory/droids"),
        description="Factory droids directory",
    )
    cache_dir: Path = Field(
        default_factory=expanded_path_factory("~/.cache/thegent"),
        description="Global cache directory for thegent",
    )
    session_dir: Path = Field(
        default_factory=expanded_path_factory("~/.cache/thegent/sessions"),
        description="Session metadata/log directory for background runs",
    )
    cwd: Path | None = Field(
        default=None,
        description="Working directory (inferred or explicit)",
    )
    session_meta_path: Path | None = Field(
        default=None,
        description="Session metadata path override",
    )
    session_rc_path: Path | None = Field(
        default=None,
        description="Session rc path override",
    )
    health_snapshot_path: Path | None = Field(
        default=None,
        description="Health snapshot path",
    )
    fifo_path: Path | None = Field(
        default=None,
        description="Override path for stdin FIFO",
    )
    holdpty_socket_dir: Path | None = Field(
        default=None,
        description="Directory for holdpty sockets",
    )
    mcp_storage_dir: Path | None = Field(
        default=None,
        description="MCP storage directory override",
    )
    connector_mapping_cache_path: Path | None = Field(
        default=None,
        description="Path override for connector mapping cache",
    )

    # Runtime settings (from RuntimeConfig)
    session_backend: Literal["auto", "zmx", "tmux", "none"] = Field(
        default="auto",
        description="Session persistence backend for agent sessions",
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
        description="Wrap background sessions with holdpty",
    )
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
        description="Retention for run registry",
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
        description="Budget warning threshold",
    )
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
    otel_console: bool = Field(
        default=False,
        description="Enable console OpenTelemetry exporter",
    )
    sandbox_level: str = Field(
        default="none",
        description="macOS sandbox level",
    )
    sandbox_env_filter: bool = Field(
        default=False,
        description="Filter environment variables in sandbox",
    )
    sandbox_env_allowlist: list[str] = Field(
        default_factory=default_sandbox_env_allowlist,
        description="Environment variables allowed in sandbox",
    )
    mac_keep_awake_agents: list[str] = Field(
        default_factory=default_mac_keep_awake_agents,
        description="Agents to keep awake on macOS",
    )

    # Additional settings
    normalization_policy_allow_fallback: bool = Field(
        default=True,
        description="Allow fallback to plain provider if contract fails",
    )
    normalization_policy_min_confidence: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Minimum confidence for contract selection",
    )
    normalization_policy_max_fallback_rate: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Maximum fallback rate before provider is penalized",
    )
    normalization_policy_strict_providers: str = Field(
        default="cursor,claude",
        description="Comma-separated list of strict providers",
    )
    contract_schema_version_minimum: str = Field(
        default="csm-v1",
        description="Minimum supported contract schema version",
    )
    cursor_agent_cmd: str = Field(
        default="cursor",
        description="Cursor API command",
    )
    models_cache_ttl_sec: int = Field(
        default=300,
        ge=60,
        le=3600,
        description="Models cache TTL in seconds",
    )
    health_snapshot_max_lines: int = Field(
        default=1000,
        ge=100,
        le=10000,
        description="Health snapshot max lines",
    )
    terminal_management_enabled: bool = Field(
        default=True,
        description="Enable terminal management",
    )
    input_guardrails_enabled: bool = Field(
        default=False,
        description="Enable input guardrails",
    )
    owner_tag: str | None = Field(
        default=None,
        description="Explicit owner tag override",
    )
    owner_scope: str = Field(
        default="",
        description="Owner scope template",
    )
    output_format: str | None = Field(
        default=None,
        description="Output format override",
    )
    debug: bool = Field(
        default=False,
        description="Enable debug logging",
    )
    debug_keepalive: bool = Field(
        default=False,
        description="Enable keepalive debug logging",
    )
    mcp_host: str = Field(
        default="127.0.0.1",
        description="MCP server bind address",
    )
    mcp_port: int = Field(
        default=3847,
        ge=1,
        le=65535,
        description="MCP server port",
    )
    control_plane_url: str = Field(
        default="http://127.0.0.1:3848",
        description="Control plane server URL",
    )
    control_plane_port: int = Field(
        default=3848,
        ge=1024,
        le=65535,
        description="Control plane server port",
    )
    check_leaks: bool = Field(
        default=False,
        description="Enable resource leak checks in tests",
    )
    testing_mode: bool = Field(
        default=False,
        description="Testing mode flag",
    )
    gh_project_sync_enabled_legacy: bool = Field(
        default=False,
        description="Legacy: enable bidirectional GitHub Projects v2 sync",
    )
    gh_project_owner_legacy: str = Field(
        default="",
        description="Legacy: GitHub project owner",
    )
    gh_project_number_legacy: int = Field(
        default=0,
        ge=0,
        description="Legacy: GitHub project number",
    )
    gh_project_direction_legacy: str = Field(
        default="bidirectional",
        description="Legacy: sync direction",
    )
    gh_project_standalone_mode_legacy: bool = Field(
        default=True,
        description="Legacy: standalone-safe mode for gh sync",
    )
    workstream_autosync_enabled: bool = Field(
        default=False,
        description="Enable automatic workstream reflection background cycle",
    )
    workstream_autosync_interval: int = Field(
        default=300,
        ge=10,
        le=3600,
        description="Cycle interval in seconds",
    )
    github_enabled: bool = Field(
        default=False,
        description="Enable GitHub Projects sync for workstream autosync",
    )
    github_owner: str = Field(
        default="",
        description="GitHub repository owner for workstream autosync",
    )
    github_project_number: int = Field(
        default=0,
        ge=0,
        description="GitHub project number for workstream autosync",
    )
    github_sandbox_mode: bool = Field(
        default=False,
        description="Force writes to sandbox GitHub project target",
    )
    github_sandbox_project_number: int = Field(
        default=0,
        ge=0,
        description="Sandbox GitHub project number for autosync writes",
    )
    github_direction: str = Field(
        default="bidirectional",
        description="GitHub sync direction",
    )
    linear_enabled: bool = Field(
        default=False,
        description="Enable Linear sync for workstream autosync",
    )
    linear_api_key: str = Field(
        default="",
        description="Linear API key for workstream autosync",
    )
    linear_team_key: str = Field(
        default="",
        description="Linear team key for workstream autosync",
    )
    linear_api_url: str = Field(
        default="https://api.linear.app/graphql",
        description="Linear GraphQL endpoint",
    )
    linear_direction: str = Field(
        default="bidirectional",
        description="Linear sync direction",
    )
    workstream_autosync_standalone_mode: bool = Field(
        default=True,
        description="Standalone-safe mode for autosync",
    )
    workstream_adaptive_interval_enabled: bool = Field(
        default=False,
        description="Enable adaptive interval controller",
    )
    workstream_adaptive_interval_min_seconds: int = Field(
        default=30,
        ge=1,
        description="Minimum adaptive interval in seconds",
    )
    workstream_adaptive_interval_max_seconds: int = Field(
        default=900,
        ge=1,
        description="Maximum adaptive interval in seconds",
    )
    metadata_ttl_seconds: int = Field(
        default=3600,
        ge=1,
        description="Metadata freshness TTL in seconds",
    )
    bootstrap_connector: str = Field(
        default="github",
        description="Connector name used for bootstrap field mapping checks",
    )
    bootstrap_required_fields: str = Field(
        default="",
        description="Comma-separated required bootstrap fields",
    )
    sync_max_changes_per_cycle: int = Field(
        default=100,
        ge=1,
        description="Maximum allowed write changes per sync cycle",
    )
    sync_pull_only_on_failure: bool = Field(
        default=False,
        description="Switch sync engine to pull-only mode after write failures",
    )

    @field_validator("retention_by_domain", mode="before")
    @classmethod
    def _parse_retention_by_domain(cls, v: object) -> dict[str, int]:
        return parse_retention_by_domain(v)

    def validate_setup(self) -> None:
        """ROB-013: Configuration validation on startup (fail-fast).

        Ensures directories exist and critical settings are sane.
        """
        # Ensure session directory is writable
        self.session_dir.mkdir(parents=True, exist_ok=True)
        if not os.access(self.session_dir, os.W_OK):
            raise RuntimeError(f"Session directory not writable: {self.session_dir}")

        # Ensure factory directories exist
        if not self.factory_skills_dir.exists():
            raise RuntimeError(
                f"Factory skills directory does not exist: {self.factory_skills_dir}. "
                "Run 'thegent setup' to initialize required directories."
            )

        # Validate timeouts
        if self.default_timeout_claude < self.default_timeout:
            raise RuntimeError(
                f"default_timeout_claude ({self.default_timeout_claude}s) must be >= "
                f"default_timeout ({self.default_timeout}s). Fix your configuration."
            )


def get_settings() -> ThegentSettings:
    """Helper to get cached settings."""
    return ThegentSettings()
