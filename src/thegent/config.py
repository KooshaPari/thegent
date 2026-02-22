"""Pydantic settings for thegent."""

import os
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from thegent.config_defaults import (
    DEFAULT_MAC_KEEP_AWAKE_AGENTS,
    DEFAULT_SANDBOX_ENV_ALLOWLIST,
    default_cost_budget_by_category,
    default_hitl_checkpoints,
    default_mac_keep_awake_agents,
    default_sandbox_env_allowlist,
    expanded_path_factory,
)
from thegent.config_parsers import (
    parse_bool_or_env_flag,
    parse_csv_or_list,
    parse_first_nonempty_env,
    parse_optional_path,
    parse_retention_by_domain,
    parse_shell_path,
)


class ThegentSettings(BaseSettings):
    """Configuration for thegent CLI."""

    model_config = SettingsConfigDict(
        env_prefix="THGENT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    factory_skills_dir: Path = Field(
        default_factory=expanded_path_factory("~/.factory/skills"),
        description="Factory skills directory",
    )
    factory_droids_dir: Path = Field(
        default_factory=expanded_path_factory("~/.factory/droids"),
        description="Factory droids directory",
    )
    cursor_agent_cmd: str = Field(
        default="cursor",
        description="Cursor API (wisdgod); set THGENT_CURSOR_AGENT_CMD for legacy compatibility",
    )
    default_cursor_model: str = Field(
        default="gemini-3-flash",
        description="Default model for cursor agent (gemini-3-flash, composer-1.5, auto)",
    )
    default_gemini_model: str = Field(
        default="gemini-3-flash",
        description="Default model for gemini CLI (-m/--model)",
    )
    default_copilot_model: str = Field(
        default="gpt-5-mini",
        description="Default model for copilot (--model); copilot doesn't support flash",
    )
    default_claude_model: str = Field(
        default="claude-opus-4.6",
        description="Default model for claude (--model)",
    )
    default_codex_model: str = Field(
        default="gpt-5.3-codex-spark",
        description="Default model for codex",
    )
    default_codex_model_high: str = Field(
        default="gpt-5.3-codex-high",
        description="Codex high-power model (use with --mode full or --model override)",
    )
    default_antigravity_model: str = Field(
        default="gemini-3-flash",
        description="Default model for antigravity (via CLIProxyAPIPlus); was tstars2.0",
    )
    default_kiro_model: str = Field(
        default="claude-haiku-4.5",
        description="Default model for kiro (claude-haiku-4.5, claude-opus-4.6 via CLIProxyAPIPlus)",
    )
    default_timeout: int = Field(
        default=1800,
        ge=10,
        le=3600,
        description="Default agent timeout in seconds (30m default; agents truly need to run indefinitely, up to 30m)",
    )
    default_timeout_claude: int = Field(
        default=1800,
        ge=60,
        le=3600,
        description="Claude agent timeout (slower API); use THGENT_DEFAULT_TIMEOUT_CLAUDE to override",
    )
    default_timeout_free: int = Field(
        default=300,
        ge=60,
        le=3600,
        description="Free agent (copilot) timeout for WP tasks; use THGENT_DEFAULT_TIMEOUT_FREE to override",
    )
    max_idle_seconds: int = Field(
        default=180,
        ge=60,
        le=600,
        description="Activity-based hang detection: kill only when no stdout/stderr for this many seconds (THGENT_MAX_IDLE_SECONDS)",
    )
    max_wall_time: int = Field(
        default=0,
        ge=0,
        le=86400,
        description="Optional absolute cap in seconds (0=unbounded). Only idle detection kills by default (THGENT_MAX_WALL_TIME)",
    )
    default_routing: str = Field(
        default="prefer_direct",
        description="Default routing policy: prefer_direct | prefer_proxy | failover (THGENT_DEFAULT_ROUTING)",
    )
    use_fifo: bool = Field(
        default=False,
        description="Enable stdin FIFO for background sessions (WP-9004); THGENT_USE_FIFO",
    )
    fifo_path: Path | None = Field(
        default=None,
        description="Override path for stdin FIFO (default: session_dir/ID.in); THGENT_FIFO_PATH",
    )

    use_holdpty: bool = Field(
        default=False,
        description="Wrap background sessions with holdpty for interactive attach (WP-9007); THGENT_USE_HOLDPTY",
    )
    holdpty_socket_dir: Path | None = Field(
        default=None,
        description="Directory for holdpty sockets; defaults to session_dir/ID.sock",
    )

    # Session persistence backend (muxless-zmx-integration)
    session_backend: Literal["auto", "zmx", "tmux", "none"] = Field(
        default="auto",
        description=(
            "Session persistence backend for agent sessions. "
            "'auto' probes for zmx then falls back to tmux/none. "
            "'zmx' requires zmx (Zig muxless) on PATH. "
            "'tmux' uses existing tmux tooling. "
            "'none' disables session persistence. "
            "(THGENT_SESSION_BACKEND)"
        ),
    )
    zmx_bin: str = Field(
        default="zmx",
        description="Path or command name for the zmx binary (THGENT_ZMX_BIN)",
    )

    models_cache_ttl_sec: int = Field(
        default=300,
        ge=60,
        le=3600,
        description="Models cache TTL in seconds (5–60 min); THGENT_MODELS_CACHE_TTL_SEC",
    )
    cache_dir: Path = Field(
        default_factory=expanded_path_factory("~/.cache/thegent"),
        description="Global cache directory for thegent",
    )
    session_dir: Path = Field(
        default_factory=expanded_path_factory("~/.cache/thegent/sessions"),
        description="Session metadata/log directory for background runs",
    )
    retention_days_sessions: int = Field(
        default=30,
        ge=7,
        le=365,
        description="Retention for session dirs (WP-3006 tiered); THGENT_RETENTION_DAYS_SESSIONS",
    )
    retention_default_days: int = Field(
        default=30,
        ge=1,
        le=365,
        description="Default retention in days for history (WP-3006); THGENT_RETENTION_DEFAULT_DAYS",
    )
    retention_days_registry: int = Field(
        default=90,
        ge=30,
        le=730,
        description="Retention for run registry (audit trail); THGENT_RETENTION_DAYS_REGISTRY",
    )
    retention_by_domain: dict[str, int] = Field(
        default_factory=dict,
        description='Per-domain retention days (WP-3006); THGENT_RETENTION_BY_DOMAIN JSON e.g. {"gdpr":365,"soc2":2555}',
    )
    default_domain_tag: str | None = Field(
        default=None,
        description="Default domain tag for runs if not specified (G-GP-07)",
    )
    retention_policy: str | None = Field(
        default=None,
        description="Retention policy string (WP-3006); format: default:30,domain1:10",
    )

    # Budget settings (WP-Y4)
    budget_hourly_limit: float = Field(
        default=10.0,
        ge=0.0,
        description="Hourly budget limit in USD (THGENT_BUDGET_HOURLY_LIMIT)",
    )
    budget_daily_limit: float = Field(
        default=100.0,
        ge=0.0,
        description="Daily budget limit in USD (THGENT_BUDGET_DAILY_LIMIT)",
    )
    budget_run_limit: float = Field(
        default=5.0,
        ge=0.0,
        description="Per-run budget limit in USD (THGENT_BUDGET_RUN_LIMIT)",
    )
    budget_warning_threshold: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Budget warning threshold (0.8 = 80%; THGENT_BUDGET_WARNING_THRESHOLD)",
    )

    @field_validator("retention_by_domain", mode="before")
    @classmethod
    def _parse_retention_by_domain(cls, v: object) -> dict[str, int]:
        return parse_retention_by_domain(v)

    # WP-3001: Policy Evaluation & Normalization
    normalization_policy_allow_fallback: bool = Field(
        default=True,
        description="Allow fallback to plain provider if contract fails (THGENT_NORMALIZATION_POLICY_ALLOW_FALLBACK)",
    )
    normalization_policy_min_confidence: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Minimum confidence for contract selection (THGENT_NORMALIZATION_POLICY_MIN_CONFIDENCE)",
    )
    normalization_policy_max_fallback_rate: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Maximum fallback rate before provider is penalized (THGENT_NORMALIZATION_POLICY_MAX_FALLBACK_RATE)",
    )
    normalization_policy_strict_providers: str = Field(
        default="cursor,claude",
        description="Comma-separated list of providers that must NEVER fallback to plain (THGENT_NORMALIZATION_POLICY_STRICT_PROVIDERS)",
    )

    # G-CA-02 B2: Parser-quality routing
    routing_parser_quality_enabled: bool = Field(
        default=True,
        description="Enable parser-quality based routing (THGENT_ROUTING_PARSER_QUALITY_ENABLED)",
    )

    # G-CA-03 C3: Contract versioning
    contract_schema_version_minimum: str = Field(
        default="csm-v1",
        description="Minimum supported contract schema version (THGENT_CONTRACT_SCHEMA_VERSION_MINIMUM)",
    )

    # WP-Y4: Cost tracking
    cost_tracking_enabled: bool = Field(
        default=True,
        description="Enable cost tracking per run (THGENT_COST_TRACKING_ENABLED)",
    )
    cost_tracking: bool = Field(
        default=False,
        description="Legacy: enable cost tracking via THGENT_COST_TRACKING=1",
    )
    cost_budget_mtd: float = Field(
        default=100.0,
        ge=0.0,
        description="MTD budget for AI providers (THGENT_COST_BUDGET_MTD)",
    )

    # Routing configuration (Terminal Bench 2.0 Pareto frontier)
    routing_enabled: bool = Field(
        default=True,
        description="Enable task routing based on Terminal Bench 2.0 Pareto frontier (THGENT_ROUTING_ENABLED)",
    )
    routing_constraints_enabled: bool = Field(
        default=True,
        description="Enable hard constraint validation for routing (quality, cost, speed) (THGENT_ROUTING_CONSTRAINTS_ENABLED)",
    )
    routing_budget_warning_threshold: float = Field(
        default=0.80,
        ge=0.0,
        le=1.0,
        description="Budget utilization threshold for warnings (0.8 = 80%) (THGENT_ROUTING_BUDGET_WARNING_THRESHOLD)",
    )
    cost_budget_by_category: dict[str, float] = Field(
        default_factory=default_cost_budget_by_category,
        description="Per-category MTD budgets in USD (THGENT_COST_BUDGET_BY_CATEGORY JSON)",
    )
    # WP-5003: Cost-aware routing
    routing_cost_aware_enabled: bool = Field(
        default=True,
        description="Enable cost_quality routing when budget pressure (WP-5003)",
    )
    cost_quality_min_weight: float = Field(
        default=0.1,
        ge=0.0,
        le=2.0,
        description="Minimum cost_weight for cost_quality policy (0.1=gemini flash; WP-5003)",
    )
    cost_quality_budget_tighten_threshold: float = Field(
        default=0.80,
        ge=0.5,
        le=1.0,
        description="Budget utilization above this tightens quality floor (WP-5003)",
    )

    # Auto router: Gemini Flash classifier + Pareto routing
    auto_router_enabled: bool = Field(
        default=True,
        description="Enable auto router when agent/model is 'auto' (THGENT_AUTO_ROUTER_ENABLED)",
    )
    auto_router_classifier_model: str = Field(
        default="gemini-3-flash",
        description="Model for headless task complexity classification (THGENT_AUTO_ROUTER_CLASSIFIER_MODEL)",
    )
    auto_router_use_classifier: bool = Field(
        default=True,
        description="Use Gemini Flash to classify prompt; if False, assume moderate (THGENT_AUTO_ROUTER_USE_CLASSIFIER)",
    )
    auto_router_min_quality: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Minimum quality floor for Pareto selection (THGENT_AUTO_ROUTER_MIN_QUALITY)",
    )
    auto_router_max_cost_weight: float = Field(
        default=2.0,
        ge=0.1,
        le=10.0,
        description="Maximum cost weight for Pareto selection (THGENT_AUTO_ROUTER_MAX_COST_WEIGHT)",
    )

    # Environment variable consolidation (research-library-env-settings)
    owner_tag: str | None = Field(
        default=None,
        description="Explicit owner tag override (THGENT_OWNER_TAG)",
    )
    owner_scope: str = Field(
        default="",
        description="Owner scope template (THGENT_OWNER_SCOPE)",
    )
    output_format: str | None = Field(
        default=None,
        description="Output format override (THGENT_OUTPUT_FORMAT)",
    )
    session_meta_path: Path | None = Field(
        default=None,
        description="Session metadata path override (THGENT_SESSION_META_PATH)",
    )
    session_rc_path: Path | None = Field(
        default=None,
        description="Session rc path override (THGENT_SESSION_RC_PATH)",
    )
    health_snapshot_path: Path | None = Field(
        default=None,
        description="Health snapshot path (THGENT_HEALTH_SNAPSHOT_PATH)",
    )
    health_snapshot_max_lines: int = Field(
        default=1000,
        ge=100,
        le=10000,
        description="Health snapshot max lines (THGENT_HEALTH_SNAPSHOT_MAX_LINES)",
    )
    terminal_management_enabled: bool = Field(
        default=True,
        description="Enable terminal management (THGENT_TERMINAL_MANAGEMENT_ENABLED)",
    )
    input_guardrails_enabled: bool = Field(
        default=False,
        description="Enable input guardrails (THGENT_INPUT_GUARDRAILS_ENABLED)",
    )
    sandbox_level: str = Field(
        default="none",
        description="macOS sandbox level: none, readonly, restricted, networked, full (THGENT_SANDBOX_LEVEL)",
    )
    sandbox_env_filter: bool = Field(
        default=False,
        description="Filter environment variables in sandbox (THGENT_SANDBOX_ENV_FILTER)",
    )

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

    retention_days_health: int = Field(
        default=90,
        ge=7,
        le=365,
        description="Retention for health snapshots; THGENT_RETENTION_DAYS_HEALTH",
    )
    cwd: Path | None = Field(
        default=None,
        description="Working directory (inferred or explicit)",
    )
    debug: bool = Field(
        default=False,
        description="Enable debug logging; THGENT_DEBUG=1",
    )
    debug_keepalive: bool = Field(
        default=False,
        description="Enable keepalive debug logging; THGENT_DEBUG_KEEPALIVE=1",
    )
    mcp_host: str = Field(
        default="127.0.0.1",
        description="MCP server bind address (THGENT_MCP_HOST)",
    )
    mcp_port: int = Field(
        default=3847,
        ge=1,
        le=65535,
        description="MCP server port (THGENT_MCP_PORT)",
    )
    control_plane_url: str = Field(
        default="http://127.0.0.1:3848",
        description="Control plane server URL (THGENT_CONTROL_PLANE_URL)",
    )
    control_plane_port: int = Field(
        default=3848,
        ge=1024,
        le=65535,
        description="Control plane server port (THGENT_CONTROL_PLANE_PORT)",
    )
    mcp_storage_dir: Path | None = Field(
        default=None,
        description="MCP storage directory override (THGENT_MCP_STORAGE_DIR)",
    )
    mergiraf_binary: str | None = Field(
        default=None,
        description="Path to mergiraf binary for AST-aware merging (THGENT_MERGIRAF_BINARY)",
    )
    cliproxy_binary: str = Field(
        default="cli-proxy-api-plus",
        description="CLIProxyAPIPlus binary (path or cmd); install from github.com/kooshapari/cliproxyapi-plusplus/releases",
    )
    cliproxy_port: int = Field(
        default=8317,
        ge=1,
        le=65535,
        description="Port for thegent's CLIProxyAPIPlus proxy (THGENT_CLIPROXY_PORT)",
    )
    cliproxy_auth_dir: Path = Field(
        default_factory=expanded_path_factory("~/.cli-proxy-api"),
        description="Auth dir for OAuth tokens (shared with vibeproxy); THGENT_CLIPROXY_AUTH_DIR",
    )
    cliproxy_config_path: Path = Field(
        default_factory=expanded_path_factory("~/.config/thegent/cliproxy-config.yaml"),
        description="Generated config for CLIProxyAPIPlus (THGENT_CLIPROXY_CONFIG_PATH)",
    )
    custom_models_path: Path = Field(
        default_factory=expanded_path_factory("~/.config/thegent/custom_models.yaml"),
        description="Path to custom models configuration (THGENT_CUSTOM_MODELS_PATH)",
    )
    cliproxy_adapter: bool = Field(
        default=True,
        description="Use adapter (Responses API + WebSocket) for Codex; THGENT_CLIPROXY_ADAPTER=1",
    )
    cursor_api_url: str = Field(
        default="http://127.0.0.1:3000",
        description="cursor-api (wisdgod) base URL; set THGENT_CURSOR_API_URL when running cursor-api",
    )
    cursor_api_token: str = Field(
        default="",
        description="Bearer token for cursor-api; set THGENT_CURSOR_API_TOKEN (from /build-key or AUTH_TOKEN)",
    )
    cursor_token_file: str = Field(
        default="",
        description=(
            "Path to file containing the Cursor sk-... session token "
            "(G-CP-01: Phase 2 token-file provider). "
            "Overrides THGENT_CURSOR_API_TOKEN when set. "
            "Auto-discovered from ~/.cursor-server/ when empty. "
            "THGENT_CURSOR_TOKEN_FILE"
        ),
    )
    cursor_token_refresh_interval: int = Field(
        default=300,
        ge=30,
        le=3600,
        description="How often (seconds) to re-read the cursor token file (G-CP-01); THGENT_CURSOR_TOKEN_REFRESH_INTERVAL",
    )
    environment: str = Field(
        default="development",
        description="Deployment environment: development | staging | production (THGENT_ENVIRONMENT)",
    )
    trust_score_threshold: float = Field(
        default=0.8,
        description="Minimum trust score for automatic execution in production (THGENT_TRUST_SCORE_THRESHOLD)",
    )
    override_ttl_seconds: int = Field(
        default=86400,
        ge=60,
        le=604800,
        description="Override validity window in seconds (default 24h); after expiry, --override must be re-supplied (WP-3003)",
    )
    escalation_sla_minutes: int = Field(
        default=30,
        ge=5,
        le=1440,
        description="Default SLA in minutes for escalation queue when policy denies (WP-3008)",
    )
    escalation_sla_breach_alert: bool = Field(
        default=True,
        description="Enable SLA breach alerts in sweep (G-GP-05)",
    )
    hitl_enabled: bool = Field(
        default=False,
        description="Enable human-in-the-loop (HITL) checkpoints (G-GP-05)",
    )
    hitl_checkpoints: list[str] = Field(
        default_factory=default_hitl_checkpoints,
        description="List of checkpoints where HITL should pause: pre_execution, post_execution",
    )
    mcp_auth_mode: str = Field(
        default="none",
        description="MCP server auth mode: none | bearer (G-FM-01)",
    )
    mcp_bearer_tokens: str = Field(
        default="",
        description="Comma-separated bearer tokens for MCP server auth (THGENT_MCP_BEARER_TOKENS)",
    )
    mcp_mount_flyto: bool = Field(
        default=False,
        description="Mount flyto-core browser tools at namespace 'browser' (THGENT_MCP_MOUNT_FLYTO); requires flyto-core HTTP at localhost:8333 or pip install flyto-core",
    )
    mcp_mount_playwright: bool = Field(
        default=True,
        description="Mount @playwright/mcp at namespace 'browser' (THGENT_MCP_MOUNT_PLAYWRIGHT); required",
    )
    mcp_mount_serena: bool = Field(
        default=True,
        description="Mount Serena (LSP code tools) at namespace 'serena' (THGENT_MCP_MOUNT_SERENA); required; requires uvx",
    )
    serena_backend: Literal["auto", "lsp", "jetbrains"] = Field(
        default="auto",
        description="Serena backend: auto-detect, LSP, or JetBrains plugin (THGENT_SERENA_BACKEND)",
    )
    serena_jetbrains_port: int = Field(
        default=8765,
        description="Port for Serena JetBrains plugin MCP server (THGENT_SERENA_JETBRAINS_PORT)",
    )
    ghostty_enabled: bool = Field(
        default=True,
        description="Enable Ghostty terminal integration (THGENT_GHOSTTY_ENABLED)",
    )
    ide_integration_enabled: bool = Field(
        default=True,
        description="Enable IDE integration auto-setup (format, inspect, etc.) (THGENT_IDE_INTEGRATION_ENABLED)",
    )
    lsp_auto_install: bool = Field(
        default=True,
        description="Auto-install missing LSP servers (THGENT_LSP_AUTO_INSTALL)",
    )
    mcp_mount_octocode: bool = Field(
        default=True,
        description="Mount Octocode (GitHub/code search) at namespace 'octocode' (THGENT_MCP_MOUNT_OCTOCODE); required; requires npx or bun",
    )
    mcp_mount_sequential_thinking: bool = Field(
        default=False,
        description="Mount Sequential Thinking MCP at namespace 'thinking' (THGENT_MCP_MOUNT_SEQUENTIAL_THINKING); optional; requires npx or bun",
    )
    mcp_mount_next_devtools: bool = Field(
        default=False,
        description="Mount Next.js DevTools MCP at namespace 'next' (THGENT_MCP_MOUNT_NEXT_DEVTOOLS); optional; requires npx or bun",
    )
    max_task_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum retries for a DAG task before escalation (G-GP-05)",
    )
    interruption_dedup_window_s: int = Field(
        default=300,
        ge=60,
        le=3600,
        description="Deduplication window in seconds for interruption alerts (WP-4004)",
    )
    interruption_alerts_per_hour_ceiling: int = Field(
        default=20,
        ge=5,
        le=200,
        description="Max alerts per hour before suppression (WP-4004)",
    )
    load_spike_threshold: int = Field(
        default=80,
        ge=1,
        le=200,
        description="Running sessions above this = spike (WP-5002); traffic shaping applies",
    )
    load_surge_threshold: int = Field(
        default=100,
        ge=5,
        le=200,
        description="Running sessions above this = surge/burst (WP-5002); non-critical deferral",
    )

    # MTSP-12: Shadow Workspaces (Isolation via git worktree)
    shadow_workspaces_enabled: bool = Field(
        default=False,
        description="Enable automatic shadow workspace creation for agent runs (git worktree isolation)",
    )
    shadow_workspaces_auto_merge: bool = Field(
        default=True,
        description="Automatically merge changes back from shadow workspace on success",
    )

    # G-GP-01: OPA integration (optional Phase 2)
    opa_url: str = Field(
        default="",
        description="OPA server URL (e.g. http://localhost:8181); when set, PolicyEngine delegates to OPA (THGENT_OPA_URL)",
    )
    opa_timeout_ms: int = Field(
        default=500,
        ge=100,
        le=5000,
        description="OPA request timeout in ms (THGENT_OPA_TIMEOUT_MS)",
    )
    opa_fallback_allow: bool = Field(
        default=False,
        description="If OPA unreachable: allow (True) or deny (False) (THGENT_OPA_FALLBACK_ALLOW)",
    )

    # G-GP-08: Sandboxing (optional Phase 2)
    sandbox_env_allowlist: list[str] = Field(
        default_factory=default_sandbox_env_allowlist,
        description="Environment variables allowed in the agent sandbox (THGENT_SANDBOX_ENV_ALLOWLIST)",
    )

    @field_validator("sandbox_env_allowlist", mode="before")
    @classmethod
    def _parse_env_allowlist(cls, v: object) -> list[str]:
        return parse_csv_or_list(v, DEFAULT_SANDBOX_ENV_ALLOWLIST)

    # G-GP-02: Input Guardrails
    prompt_max_chars: int = Field(
        default=65536,
        ge=100,
        le=2_000_000,
        description="Max prompt chars for guardrails (THGENT_PROMPT_MAX_CHARS)",
    )
    prompt_blocklist_patterns: str = Field(
        default="",
        description="Comma-separated blocklist patterns (THGENT_PROMPT_BLOCKLIST_PATTERNS)",
    )
    agent_allowlist: str = Field(
        default="",
        description="Comma-separated agent allowlist (THGENT_AGENT_ALLOWLIST)",
    )
    cwd_allowed_prefixes: str = Field(
        default="",
        description="Comma-separated CWD path prefixes (THGENT_CWD_ALLOWED_PREFIXES)",
    )
    flyto_url: str = Field(
        default="http://localhost:8333/mcp",
        description="Flyto-core HTTP URL (THGENT_FLYTO_URL)",
    )
    bundle_proxy: bool = Field(
        default=False,
        description="Start CLIProxyAPIPlus with MCP server (THGENT_BUNDLE_PROXY=1)",
    )
    prune_orphan_by_ppid: bool = Field(
        default=True,
        description="Prune only true orphans (no Cursor/Claude/Codex/thegent parent). Set False to prune all matches. (THGENT_PRUNE_ORPHAN_BY_PPID)",
    )
    prune_grace_period: int = Field(
        default=0,
        ge=0,
        le=60,
        description="Grace period in seconds before SIGKILL (THGENT_PRUNE_GRACE_PERIOD)",
    )
    prune_sort_by: str = Field(
        default="rss",
        description="Sort candidates by metric (rss, pid) (THGENT_PRUNE_SORT_BY)",
    )
    prune_sort_order: str = Field(
        default="desc",
        description="Sort order (asc, desc) (THGENT_PRUNE_SORT_ORDER)",
    )

    sitback: bool = Field(
        default=False,
        description="Enable sitback mode (THGENT_SITBACK=1)",
    )
    sitback_harness: bool = Field(
        default=False,
        description="Sitback harness mode (THGENT_SITBACK_HARNESS=1)",
    )
    doctor_from_harness: bool = Field(
        default=False,
        description="Skip harness doctors when set (THGENT_DOCTOR_FROM_HARNESS=1)",
    )
    use_native_resources: bool = Field(
        default=False,
        description="Use thegent-resources Rust binary (THGENT_USE_NATIVE_RESOURCES=1)",
    )
    resources_bin: str | None = Field(
        default=None,
        description="Path to thegent-resources binary (THGENT_RESOURCES_BIN)",
    )
    # Redis settings (swarm-redis-concurrency)
    redis_host: str = Field(
        default="localhost",
        description="Redis host for distributed concurrency (THGENT_REDIS_HOST)",
    )
    redis_port: int = Field(
        default=6379,
        ge=1,
        le=65535,
        description="Redis port for distributed concurrency (THGENT_REDIS_PORT)",
    )
    redis_db: int = Field(
        default=0,
        ge=0,
        le=15,
        description="Redis DB index for distributed concurrency (THGENT_REDIS_DB)",
    )
    redis_password: str | None = Field(
        default=None,
        description="Redis password for distributed concurrency (THGENT_REDIS_PASSWORD)",
    )
    redis_key_prefix: str = Field(
        default="thgent:concurrency",
        description="Redis key namespace for concurrency slots (THGENT_REDIS_KEY_PREFIX)",
    )
    redis_concurrency_limit: int = Field(
        default=10,
        ge=1,
        le=10000,
        description="Max concurrent slots when Redis-backed (THGENT_REDIS_CONCURRENCY_LIMIT)",
    )
    max_parallel: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Maximum parallel operations (THGENT_MAX_PARALLEL)",
    )
    supermemory_api_key: str = Field(
        default="",
        description="Supermemory.ai API key (THGENT_SUPERMEMORY_API_KEY)",
    )
    supermemory_base_url: str = Field(
        default="https://api.supermemory.ai/v3",
        description="Supermemory.ai base URL (THGENT_SUPERMEMORY_BASE_URL)",
    )
    hier_threshold: int = Field(
        default=5,
        ge=1,
        description="Swarm size threshold for hierarchical coordination (THGENT_HIER_THRESHOLD)",
    )
    remote_nodes: str = Field(
        default="",
        description="Comma-separated list of remote node addresses (THGENT_REMOTE_NODES)",
    )
    remote_ssh_user: str | None = Field(
        default=None,
        description="SSH user for remote execution (THGENT_REMOTE_SSH_USER)",
    )
    redlock_nodes: str = Field(
        default="redis://localhost:6379",
        description="Comma-separated Redis URLs for Redlock (THGENT_REDLOCK_NODES)",
    )
    rate_tokens_per_sec: float = Field(
        default=10.0,
        ge=0.0,
        description="Token bucket refill rate (THGENT_RATE_TOKENS_PER_SEC)",
    )
    rate_bucket_size: float = Field(
        default=20.0,
        ge=1.0,
        description="Token bucket capacity (THGENT_RATE_BUCKET_SIZE)",
    )
    sync_remote: str = Field(
        default="<local-stub>",
        description="Default remote sync target (THGENT_SYNC_REMOTE)",
    )
    file_index_ttl: int = Field(
        default=30,
        ge=1,
        description="File index TTL in seconds (THGENT_FILE_INDEX_TTL)",
    )
    zmx_max_sessions: int = Field(
        default=50,
        ge=1,
        description="Maximum concurrent zmx sessions (THGENT_ZMX_MAX_SESSIONS)",
    )
    zmx_session_ttl: int = Field(
        default=3600,
        ge=1,
        description="zmx session TTL in seconds (THGENT_ZMX_SESSION_TTL)",
    )
    zmx_binary: str = Field(
        default="zmx",
        description="zmx binary path or name (THGENT_ZMX_BINARY)",
    )
    maif_enabled: bool = Field(
        default=False,
        description="Enable MAIF runner (THGENT_MAIF_ENABLED)",
    )
    maif_db_path: Path | None = Field(
        default=None,
        description="MAIF database path (THGENT_MAIF_DB_PATH)",
    )

    zen_base_url: str = Field(
        default="https://api.opencode.ai",
        description="Zen/OpenCode base URL (THGENT_ZEN_BASE_URL)",
    )
    zen_api_key: str = Field(
        default="",
        description="Zen API key (THGENT_ZEN_API_KEY, OPENCODE_API_KEY, ZEN_API_KEY)",
    )

    @field_validator("zen_api_key", mode="before")
    @classmethod
    def _parse_zen_api_key(cls, v: object) -> str:
        """Read zen_api_key from THGENT_ZEN_API_KEY, OPENCODE_API_KEY, or ZEN_API_KEY."""
        return parse_first_nonempty_env(v, ["THGENT_ZEN_API_KEY", "OPENCODE_API_KEY", "ZEN_API_KEY"])

    @field_validator("virtual_env", mode="before")
    @classmethod
    def _parse_virtual_env(cls, v: object) -> Path | None:
        """Auto-detect VIRTUAL_ENV from system if not explicitly set."""
        return parse_optional_path(v, "VIRTUAL_ENV")

    @field_validator("shell_path", mode="before")
    @classmethod
    def _parse_shell_path(cls, v: object) -> str:
        """Auto-detect SHELL from system if not explicitly set."""
        return parse_shell_path(v, "SHELL", "/bin/zsh")

    @field_validator("appdata_path", mode="before")
    @classmethod
    def _parse_appdata_path(cls, v: object) -> Path | None:
        """Auto-detect APPDATA from system on Windows if not explicitly set."""
        return parse_optional_path(v, "APPDATA")

    @field_validator("check_leaks", mode="before")
    @classmethod
    def _parse_check_leaks(cls, v: object) -> bool:
        """Parse CHECK_LEAKS environment variable."""
        return parse_bool_or_env_flag(v, "CHECK_LEAKS")

    @field_validator("testing_mode", mode="before")
    @classmethod
    def _parse_testing_mode(cls, v: object) -> bool:
        """Parse THGENT_TESTING environment variable."""
        return parse_bool_or_env_flag(v, "THGENT_TESTING")

    helios_shield_enabled: bool = Field(
        default=True,
        description="Enable heliosShield bridge (THGENT_HELIOS_SHIELD_ENABLED)",
    )
    mac_keep_awake: bool = Field(
        default=True,
        description="Keep Mac awake during claude/codex runs (caffeinate; THGENT_MAC_KEEP_AWAKE)",
    )
    mac_keep_awake_agents: list[str] = Field(
        default_factory=default_mac_keep_awake_agents,
        description="Agents that trigger caffeinate when mac_keep_awake (THGENT_MAC_KEEP_AWAKE_AGENTS)",
    )

    @field_validator("mac_keep_awake_agents", mode="before")
    @classmethod
    def _parse_mac_keep_awake_agents(cls, v: object) -> list[str]:
        return parse_csv_or_list(v, DEFAULT_MAC_KEEP_AWAKE_AGENTS)

    config_dir_override: Path | None = Field(
        default=None,
        description="Override config directory (THGENT_CONFIG_DIR)",
    )
    dev: bool = Field(
        default=False,
        description="Development mode (THGENT_DEV=1)",
    )
    otel_console: bool = Field(
        default=False,
        description="Emit OTEL to console (THGENT_OTEL_CONSOLE=1)",
    )
    use_native_shm: bool = Field(
        default=True,
        description="Use native SHM (THGENT_USE_NATIVE_SHM)",
    )
    watcher_use_shm: bool = Field(
        default=True,
        description="Enable CircuitBreakerShm integration for watcher daemon (THGENT_WATCHER_USE_SHM)",
    )
    watcher_shm_path: Path | None = Field(
        default=None,
        description="Path for watcher daemon SHM file (THGENT_WATCHER_SHM_PATH)",
    )
    use_native_discovery: bool = Field(
        default=True,
        description="Use native discovery (THGENT_USE_NATIVE_DISCOVERY)",
    )
    tee_mock: bool = Field(
        default=False,
        description="TEE mock mode (THGENT_TEE_MOCK=1)",
    )
    tee_required: bool = Field(
        default=False,
        description="Require TEE attestation (THGENT_TEE_REQUIRED=1)",
    )
    use_native_crypto: bool = Field(
        default=True,
        description="Use native crypto (THGENT_USE_NATIVE_CRYPTO)",
    )
    use_native_parser: bool = Field(
        default=False,
        description="Use thegent-parser Rust extension (THGENT_USE_NATIVE_PARSER=1)",
    )
    reload: bool = Field(
        default=False,
        description="Enable reload (THGENT_RELOAD=1)",
    )

    # G-GP-04: Circuit Breakers
    circuit_breaker_enabled: bool = Field(
        default=True,
        description="Enable circuit breakers for agents and models (THGENT_CIRCUIT_BREAKER_ENABLED)",
    )
    circuit_breaker_threshold: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of failures before circuit opens (THGENT_CIRCUIT_BREAKER_THRESHOLD)",
    )
    circuit_breaker_window_s: int = Field(
        default=300,
        ge=10,
        description="Window in seconds for counting failures (THGENT_CIRCUIT_BREAKER_WINDOW_S)",
    )
    circuit_breaker_recovery_s: int = Field(
        default=60,
        ge=0,
        description="Seconds before half-open (trial) (THGENT_CIRCUIT_BREAKER_RECOVERY_S)",
    )

    # Contract canary rollout (G-RV-08, docs/contracts/UPGRADE_PLAYBOOK.md)
    contract_canary_percent: int = Field(
        default=0,
        ge=0,
        le=100,
        description="Percentage of runs using new contract version in canary (0=off); THGENT_CONTRACT_CANARY_PERCENT",
    )
    contract_canary_providers: str = Field(
        default="",
        description="Comma-separated providers in canary (empty=all); THGENT_CONTRACT_CANARY_PROVIDERS",
    )

    # Parser-quality routing (G-CA-02 B2)
    shutdown_wait_s: int = Field(
        default=30,
        ge=0,
        le=60,
        description="Seconds to wait for in-flight requests during MCP server shutdown (ROB-020)",
    )
    shutdown_wait_active_s: int = Field(
        default=30,
        ge=0,
        le=120,
        description="Seconds to poll for active background runs during MCP server shutdown (ROB-020)",
    )
    max_concurrency: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Maximum concurrent agent runs (ceiling); THGENT_MAX_CONCURRENCY",
    )
    critical_lane_slots: int = Field(
        default=2,
        ge=0,
        le=100,
        description="Slots reserved exclusively for critical-priority runs (standard runs cannot use these); THGENT_CRITICAL_LANE_SLOTS",
    )
    concurrency_load_based: bool = Field(
        default=True,  # Default to resource-based limits
        description="Use FD/Mem/CPU gates for dynamic limit (WP-5001); THGENT_CONCURRENCY_LOAD_BASED",
    )
    concurrency_min_slots: int = Field(
        default=1,
        ge=1,
        le=20,
        description="Minimum slots when load-based; THGENT_CONCURRENCY_MIN_SLOTS",
    )
    concurrency_fd_utilization_max: float = Field(
        default=0.75,
        ge=0.5,
        le=0.95,
        description="Block when fd_used/fd_limit >= this; THGENT_CONCURRENCY_FD_UTILIZATION_MAX",
    )
    concurrency_load_per_cpu_max: float = Field(
        default=1.5,
        ge=0.5,
        le=50.0,
        description="Block when load_1m/cpu_count >= this; THGENT_CONCURRENCY_LOAD_PER_CPU_MAX",
    )

    # Hysteresis tuning (WP-Y6 / swarm-hysteresis-env)
    hysteresis_upper: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Upper utilization ratio for scale-up; THGENT_HYSTERESIS_UPPER",
    )
    hysteresis_lower: float = Field(
        default=0.4,
        ge=0.0,
        le=1.0,
        description="Lower utilization ratio for scale-down; THGENT_HYSTERESIS_LOWER",
    )
    hysteresis_dwell: int = Field(
        default=30,
        ge=0,
        le=3600,
        description="Minimum seconds between scaling events; THGENT_HYSTERESIS_DWELL",
    )
    routing_hysteresis_threshold: float = Field(
        default=0.1,
        ge=0.0,
        le=1.0,
        description="Threshold for Pareto routing hysteresis; THGENT_ROUTING_HYSTERESIS_THRESHOLD",
    )
    router_hysteresis_band: float = Field(
        default=0.15,
        ge=0.0,
        le=0.5,
        description="Hysteresis band for thegent-router; THGENT_ROUTER_HYSTERESIS_BAND",
    )
    router_hysteresis_dwell: int = Field(
        default=300,
        ge=0,
        le=86400,
        description="Dwell time for thegent-router hysteresis; THGENT_ROUTER_HYSTERESIS_DWELL",
    )
    router_hysteresis_max_dwell: int = Field(
        default=1800,
        ge=0,
        le=86400,
        description="Max dwell time for thegent-router hysteresis; THGENT_ROUTER_HYSTERESIS_MAX_DWELL",
    )
    router_hysteresis_override: float = Field(
        default=0.20,
        ge=0.0,
        le=1.0,
        description="Override threshold for thegent-router hysteresis; THGENT_ROUTER_HYSTERESIS_OVERRIDE",
    )

    # Phase 3 router configuration (WL-012)
    # Env vars: THGENT_ROUTER_BAND_WIDTH, THGENT_ROUTER_DWELL_TIME,
    #           THGENT_ROUTER_MAX_DWELL, THGENT_ROUTER_OVERRIDE_THRESHOLD,
    #           THGENT_ROUTER_AUDIT_PATH
    # (Prefix THGENT_ applied automatically by SettingsConfigDict env_prefix.)
    router_band_width: float = Field(
        default=0.15,
        ge=0.0,
        le=0.5,
        description=("Hysteresis band width for thegent-router Phase 3. Env: THGENT_ROUTER_BAND_WIDTH."),
    )
    router_dwell_time: int = Field(
        default=300,
        ge=0,
        le=86400,
        description=("Minimum dwell time (seconds) before a routing switch is allowed. Env: THGENT_ROUTER_DWELL_TIME."),
    )
    router_max_dwell: int = Field(
        default=1800,
        ge=0,
        le=86400,
        description=(
            "Maximum dwell time (seconds) before a forced routing re-evaluation. Env: THGENT_ROUTER_MAX_DWELL."
        ),
    )
    router_override_threshold: float = Field(
        default=0.20,
        ge=0.0,
        le=1.0,
        description=(
            "Risk delta required to override dwell and force an immediate routing switch. "
            "Env: THGENT_ROUTER_OVERRIDE_THRESHOLD."
        ),
    )
    router_audit_path: str = Field(
        default="",
        description=(
            "Path to routing_audit.jsonl. Defaults to <session_dir>/routing_audit.jsonl "
            "if empty. Env: THGENT_ROUTER_AUDIT_PATH."
        ),
    )

    # WL-030: Quality gate DAG runner bounds
    quality_max_workers: int = Field(
        default=4,
        ge=1,
        le=32,
        description=(
            "Maximum concurrent quality gate DAG step workers (WL-030). "
            "Caps the ThreadPoolExecutor in quality_runner.py. "
            "QUALITY_MAX_WORKERS"
        ),
        alias="QUALITY_MAX_WORKERS",
    )
    quality_step_timeout_sec: int = Field(
        default=600,
        ge=10,
        le=3600,
        description=(
            "Per-step timeout in seconds for quality gate DAG steps (WL-030). "
            "Each subprocess.run call is bounded by this value. "
            "QUALITY_STEP_TIMEOUT_SEC"
        ),
        alias="QUALITY_STEP_TIMEOUT_SEC",
    )
    quality_shadow_cleanup_hours: int = Field(
        default=24,
        ge=1,
        le=720,
        description=(
            "Age threshold in hours for stale .shadow-* directory cleanup (WL-030). "
            "Directories older than this are removed by quality-gate.sh cleanup. "
            "QUALITY_SHADOW_CLEANUP_HOURS"
        ),
        alias="QUALITY_SHADOW_CLEANUP_HOURS",
    )
    quality_log_retention_days: int = Field(
        default=7,
        ge=1,
        le=365,
        description=(
            "Retention in days for .quality/logs files (WL-030). "
            "Log files older than this are removed by quality-gate.sh cleanup. "
            "QUALITY_LOG_RETENTION_DAYS"
        ),
        alias="QUALITY_LOG_RETENTION_DAYS",
    )

    # AgilePlus autonomous governance loop
    agileplus_enabled: bool = Field(
        default=False,
        description="Enable AgilePlus autonomous governance loop (THGENT_AGILEPLUS_ENABLED)",
    )
    agileplus_interval: int = Field(
        default=300,
        ge=30,
        le=3600,
        description="Seconds between AgilePlus cycles (THGENT_AGILEPLUS_INTERVAL)",
    )
    agileplus_budget_daily_calls: int = Field(
        default=20,
        ge=1,
        le=200,
        description="Maximum agent triggers per day (THGENT_AGILEPLUS_BUDGET_DAILY_CALLS)",
    )
    agileplus_max_rerolls: int = Field(
        default=2,
        ge=0,
        le=10,
        description="Maximum retry attempts per task in a cycle (THGENT_AGILEPLUS_MAX_REROLLS)",
    )
    agileplus_max_tasks_per_cycle: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum tasks dispatched per AgilePlus cycle (THGENT_AGILEPLUS_MAX_TASKS_PER_CYCLE)",
    )
    agileplus_health_threshold: int = Field(
        default=90,
        ge=0,
        le=100,
        description="Health score above which AgilePlus idles (THGENT_AGILEPLUS_HEALTH_THRESHOLD)",
    )

    # LiteLLM Router settings
    use_litellm_router: bool = Field(
        default=False,
        description="Enable LiteLLM router for agent execution (THGENT_USE_LITELLM_ROUTER)",
    )
    litellm_routing_policy: str = Field(
        default="cheapest",
        description="LiteLLM routing policy: cheapest, fastest, round_robin (THGENT_LITELLM_ROUTING_POLICY)",
    )
    litellm_timeout: int = Field(
        default=300,
        ge=10,
        le=3600,
        description="LiteLLM request timeout in seconds (THGENT_LITELLM_TIMEOUT)",
    )
    litellm_num_retries: int = Field(
        default=2,
        ge=0,
        le=10,
        description="Number of retries for LiteLLM requests (THGENT_LITELLM_NUM_RETRIES)",
    )
    litellm_retry_after: int = Field(
        default=5,
        ge=0,
        le=60,
        description="Seconds to wait before retrying after failure (THGENT_LITELLM_RETRY_AFTER)",
    )

    # LiteLLM Enhanced Features
    litellm_enable_cache: bool = Field(
        default=True,
        description="Enable LiteLLM response caching (THGENT_LITELLM_ENABLE_CACHE)",
    )
    litellm_cache_type: str = Field(
        default="in-memory",
        description="Cache type: in-memory, redis, s3 (THGENT_LITELLM_CACHE_TYPE)",
    )
    litellm_redis_url: str | None = Field(
        default=None,
        description="Redis URL for caching when cache_type=redis (THGENT_LITELLM_REDIS_URL)",
    )
    litellm_cooldown_time: int = Field(
        default=60,
        ge=10,
        le=600,
        description="Cooldown seconds after model failure before retry (THGENT_LITELLM_COOLDOWN_TIME)",
    )
    litellm_enable_streaming: bool = Field(
        default=True,
        description="Enable streaming responses for LiteLLM (THGENT_LITELLM_ENABLE_STREAMING)",
    )
    litellm_enable_cost_tracking: bool = Field(
        default=True,
        description="Enable cost tracking for LiteLLM calls (THGENT_LITELLM_ENABLE_COST_TRACKING)",
    )
    litellm_cost_budget: float | None = Field(
        default=None,
        ge=0,
        description="Daily budget limit in USD for LiteLLM calls (THGENT_LITELLM_COST_BUDGET)",
    )
    litellm_alert_webhook: str | None = Field(
        default=None,
        description="Webhook URL for routing alerts (budget exceeded, high latency) (THGENT_LITELLM_ALERT_WEBHOOK)",
    )
    litellm_latency_threshold_ms: float = Field(
        default=500.0,
        ge=0,
        description="Latency threshold in ms for high-latency alerts (THGENT_LITELLM_LATENCY_THRESHOLD_MS)",
    )
    litellm_context_window_validation: bool = Field(
        default=True,
        description="Enable pre-call context window validation (THGENT_LITELLM_CONTEXT_WINDOW_VALIDATION)",
    )
    litellm_fallback_enabled: bool = Field(
        default=True,
        description="Enable automatic fallback to alternative models on failure (THGENT_LITELLM_FALLBACK_ENABLED)",
    )

    # Keepalive settings
    keepalive_interval: int = Field(
        default=30,
        ge=5,
        le=300,
        description="Keepalive interval in seconds (THGENT_KEEPALIVE_INTERVAL)",
    )

    # Agent identification
    agent_id: str = Field(
        default="default-agent",
        description="Current agent ID (THGENT_AGENT_ID)",
    )

    # Dex-specific settings
    dex_force_yolo: bool = Field(
        default=False,
        description="Force YOLO mode: skip permissions, disable sandbox and approvals (THGENT_DEX_FORCE_YOLO)",
    )

    # heliosShield integration settings
    reddit_client_id: str = Field(
        default="",
        description="Reddit API Client ID (THGENT_REDDIT_CLIENT_ID)",
    )
    reddit_client_secret: str = Field(
        default="",
        description="Reddit API Client Secret (THGENT_REDDIT_CLIENT_SECRET)",
    )
    reddit_user_agent: str = Field(
        default="thegent/0.1.0",
        description="Reddit API User Agent (THGENT_REDDIT_USER_AGENT)",
    )
    research_protocol_enabled: bool = Field(
        default=True,
        description="Enable Deep Research Protocol (THGENT_RESEARCH_PROTOCOL_ENABLED)",
    )

    harness_root: Path = Field(
        default_factory=expanded_path_factory("~/.agent-harness"),
        description="heliosShield harness root directory (HARNESS_ROOT)",
    )

    agent_shell: str | None = Field(
        default=None,
        description="Preferred shell for agent-spawned processes (THGENT_AGENT_SHELL)",
    )
    hook_shell: str | None = Field(
        default=None,
        description="Preferred shell for hook execution (THGENT_HOOK_SHELL)",
    )

    # Environment variable consolidation (research-library-env-settings)
    analytics_site_id: str = Field(
        default="thegent",
        description="Analytics site ID (THGENT_ANALYTICS_SITE_ID)",
    )
    siem_endpoint_url: str | None = Field(
        default=None,
        description="SIEM endpoint URL for egress (THGENT_SIEM_ENDPOINT_URL)",
    )
    virtual_env: Path | None = Field(
        default=None,
        description="Virtual environment path (VIRTUAL_ENV); auto-detected from system if not set",
    )
    shell_path: str = Field(
        default="/bin/zsh",
        description="Shell executable path (SHELL); used by installer for sourcing (THGENT_SHELL_PATH)",
    )
    appdata_path: Path | None = Field(
        default=None,
        description="Windows APPDATA path for config (APPDATA); auto-detected on Windows (THGENT_APPDATA_PATH)",
    )
    cliproxy_backend_url: str | None = Field(
        default=None,
        description="CLIProxy backend URL for proxy setup (THGENT_CLIPROXY_BACKEND_URL)",
    )
    gh_project_sync_enabled: bool = Field(
        default=False,
        description="Enable GitHub Project v2 sync helpers (THGENT_GH_PROJECT_SYNC_ENABLED)",
    )
    gh_project_owner: str = Field(
        default="",
        description="GitHub owner/user/org for Project v2 sync (THGENT_GH_PROJECT_OWNER)",
    )
    gh_project_number: int = Field(
        default=0,
        ge=0,
        description="GitHub Project v2 number for sync; 0 disables target (THGENT_GH_PROJECT_NUMBER)",
    )
    gh_project_direction: Literal["pull", "push", "both"] = Field(
        default="both",
        description="Default GitHub Project sync direction (THGENT_GH_PROJECT_DIRECTION)",
    )
    gh_project_standalone_mode: bool = Field(
        default=False,
        description="Run GH project sync in standalone mode with gh + local files only (THGENT_GH_PROJECT_STANDALONE_MODE)",
    )
    workstream_autosync_enabled: bool = Field(
        default=False,
        description="Enable automatic bidirectional sync between WORK_STREAM.md and external trackers (THGENT_WORKSTREAM_AUTOSYNC_ENABLED)",
    )
    workstream_autosync_interval_sec: int = Field(
        default=60,
        ge=10,
        le=3600,
        description="Polling interval in seconds for sync autopilot loop (THGENT_WORKSTREAM_AUTOSYNC_INTERVAL_SEC)",
    )
    linear_sync_enabled: bool = Field(
        default=False,
        description="Enable Linear synchronization in autopilot loop (THGENT_LINEAR_SYNC_ENABLED)",
    )
    linear_api_key: str = Field(
        default="",
        description="Linear API key for GraphQL synchronization (THGENT_LINEAR_API_KEY)",
    )
    linear_team_id: str = Field(
        default="",
        description="Linear team ID for issue synchronization (THGENT_LINEAR_TEAM_ID)",
    )
    linear_project_id: str = Field(
        default="",
        description="Optional Linear project ID filter for synchronization (THGENT_LINEAR_PROJECT_ID)",
    )
    linear_direction: Literal["pull", "push", "both"] = Field(
        default="both",
        description="Default Linear sync direction (THGENT_LINEAR_DIRECTION)",
    )
    linear_api_url: str = Field(
        default="https://api.linear.app/graphql",
        description="Linear GraphQL endpoint (THGENT_LINEAR_API_URL)",
    )
    check_leaks: bool = Field(
        default=False,
        description="Enable resource leak checks in tests (CHECK_LEAKS)",
    )
    testing_mode: bool = Field(
        default=False,
        description="Testing mode flag; set automatically in test environment (THGENT_TESTING)",
    )

    # WL-157: GitHub Projects Bidirectional Sync
    gh_project_sync_enabled: bool = Field(
        default=False,
        description="Enable bidirectional GitHub Projects v2 sync (THGENT_GH_PROJECT_SYNC_ENABLED)",
    )
    gh_project_owner: str = Field(
        default="",
        description="GitHub project owner (username or org; THGENT_GH_PROJECT_OWNER)",
    )
    gh_project_number: int = Field(
        default=0,
        ge=0,
        description="GitHub project number (v2 projects only; THGENT_GH_PROJECT_NUMBER)",
    )
    gh_project_direction: str = Field(
        default="bidirectional",
        description="Sync direction: read_only, write_only, bidirectional (THGENT_GH_PROJECT_DIRECTION)",
    )
    gh_project_standalone_mode: bool = Field(
        default=True,
        description="Standalone-safe mode: skip gracefully when disabled or gh auth missing (THGENT_GH_PROJECT_STANDALONE_MODE)",
    )

    # WL-160: Workstream Autosync (GitHub Projects + Linear)
    workstream_autosync_enabled: bool = Field(
        default=False,
        description="Enable automatic workstream reflection background cycle (THGENT_WORKSTREAM_AUTOSYNC_ENABLED)",
    )
    workstream_autosync_interval: int = Field(
        default=300,
        ge=10,
        le=3600,
        description="Cycle interval in seconds (THGENT_WORKSTREAM_AUTOSYNC_INTERVAL)",
    )
    github_enabled: bool = Field(
        default=False,
        description="Enable GitHub Projects sync for workstream autosync (THGENT_GITHUB_ENABLED)",
    )
    github_owner: str = Field(
        default="",
        description="GitHub repository owner for workstream autosync (THGENT_GITHUB_OWNER)",
    )
    github_project_number: int = Field(
        default=0,
        ge=0,
        description="GitHub project number for workstream autosync (THGENT_GITHUB_PROJECT_NUMBER)",
    )
    github_direction: str = Field(
        default="bidirectional",
        description="GitHub sync direction: read_only, write_only, bidirectional (THGENT_GITHUB_DIRECTION)",
    )
    linear_enabled: bool = Field(
        default=False,
        description="Enable Linear sync for workstream autosync (THGENT_LINEAR_ENABLED)",
    )
    linear_api_key: str = Field(
        default="",
        description="Linear API key for workstream autosync (THGENT_LINEAR_API_KEY)",
    )
    linear_team_key: str = Field(
        default="",
        description="Linear team key for workstream autosync (THGENT_LINEAR_TEAM_KEY)",
    )
    linear_direction: str = Field(
        default="bidirectional",
        description="Linear sync direction: read_only, write_only, bidirectional (THGENT_LINEAR_DIRECTION)",
    )
    workstream_autosync_standalone_mode: bool = Field(
        default=True,
        description="Standalone-safe mode for autosync: skip gracefully on errors (THGENT_AUTOSYNC_STANDALONE_MODE)",
    )


def get_settings() -> ThegentSettings:
    """Helper to get cached settings."""
    return ThegentSettings()


# End of file
