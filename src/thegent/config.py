"""Pydantic settings for thegent."""

import json
import os
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _expand_path(p: Path) -> Path:
    return p.expanduser().resolve()


class ThegentSettings(BaseSettings):
    """Configuration for thegent CLI."""

    model_config = SettingsConfigDict(
        env_prefix="THGENT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    factory_skills_dir: Path = Field(
        default_factory=lambda: Path("~/.factory/skills").expanduser(),
        description="Factory skills directory",
    )
    factory_droids_dir: Path = Field(
        default_factory=lambda: Path("~/.factory/droids").expanduser(),
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
        default=90,
        ge=10,
        le=3600,
        description="Default agent timeout in seconds",
    )
    default_timeout_claude: int = Field(
        default=300,
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
    models_cache_ttl_sec: int = Field(
        default=300,
        ge=60,
        le=3600,
        description="Models cache TTL in seconds (5–60 min); THGENT_MODELS_CACHE_TTL_SEC",
    )
    cache_dir: Path = Field(
        default_factory=lambda: Path("~/.cache/thegent").expanduser(),
        description="Global cache directory for thegent",
    )
    session_dir: Path = Field(
        default_factory=lambda: Path("~/.cache/thegent/sessions").expanduser(),
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

    @field_validator("retention_by_domain", mode="before")
    @classmethod
    def _parse_retention_by_domain(cls, v: object) -> dict[str, int]:
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, dict):
                    return {str(k): int(val) if isinstance(val, (int, float, str)) else 0 for k, val in parsed.items()}
                return {}
            except (json.JSONDecodeError, ValueError, TypeError):
                return {}
        if isinstance(v, dict):
            return {str(k): int(val) if isinstance(val, (int, float, str)) else 0 for k, val in v.items()}
        return {}

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
        default_factory=lambda: {
            "fast": 50.0,
            "normal": 200.0,
            "complex": 150.0,
            "high_complex": 50.0,
        },
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

        # Ensure factory directories exist (warn if not, but don't fail unless critical)
        if not self.factory_skills_dir.exists():
            # This is expected on first install, so we just log or ignore
            pass

        # Validate timeouts
        if self.default_timeout_claude < self.default_timeout:
            # Mission-Critical Rigor: adjust instead of failing if possible, or warn
            pass

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
    output_format: str = Field(
        default="rich",
        description="Output format for bg/ps: rich (default) or md (agent-friendly markdown); THGENT_OUTPUT_FORMAT",
    )
    debug: bool = Field(
        default=False,
        description="Enable debug logging; THGENT_DEBUG=1",
    )
    debug_keepalive: bool = Field(
        default=False,
        description="Enable keepalive debug logging; THGENT_DEBUG_KEEPALIVE=1",
    )
    terminal_management_enabled: bool = Field(
        default=True,
        description="Enable terminal management features; THGENT_TERMINAL_MANAGEMENT_ENABLED",
    )
    sandbox_env_filter: bool = Field(
        default=False,
        description="Filter sandbox env to allowlist only; THGENT_SANDBOX_ENV_FILTER=1",
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
    cliproxy_binary: str = Field(
        default="cli-proxy-api-plus",
        description="CLIProxyAPIPlus binary (path or cmd); install from github.com/router-for-me/CLIProxyAPIPlus/releases",
    )
    cliproxy_port: int = Field(
        default=8317,
        ge=1,
        le=65535,
        description="Port for thegent's CLIProxyAPIPlus proxy (THGENT_CLIPROXY_PORT)",
    )
    cliproxy_auth_dir: Path = Field(
        default_factory=lambda: Path("~/.cli-proxy-api").expanduser(),
        description="Auth dir for OAuth tokens (shared with vibeproxy); THGENT_CLIPROXY_AUTH_DIR",
    )
    cliproxy_config_path: Path = Field(
        default_factory=lambda: Path("~/.config/thegent/cliproxy-config.yaml").expanduser(),
        description="Generated config for CLIProxyAPIPlus (THGENT_CLIPROXY_CONFIG_PATH)",
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
        default_factory=lambda: ["pre_execution"],
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
        default=10,
        ge=1,
        le=100,
        description="Running sessions above this = spike (WP-5002); traffic shaping applies",
    )
    load_surge_threshold: int = Field(
        default=20,
        ge=5,
        le=200,
        description="Running sessions above this = surge (WP-5002); safe-mode activates",
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
        default_factory=lambda: ["PATH", "HOME", "LANG", "USER", "TERM", "PYTHONUNBUFFERED"],
        description="Environment variables allowed in the agent sandbox (THGENT_SANDBOX_ENV_ALLOWLIST)",
    )

    @field_validator("sandbox_env_allowlist", mode="before")
    @classmethod
    def _parse_env_allowlist(cls, v: object) -> list[str]:
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        if isinstance(v, list):
            return [str(s) for s in v]
        return ["PATH", "HOME", "LANG", "USER", "TERM", "PYTHONUNBUFFERED"]

    # G-GP-02: Input Guardrails
    input_guardrails_enabled: bool = Field(
        default=False,
        description="Enable input guardrails (prompt length, blocklist, agent/cwd allowlist) (THGENT_INPUT_GUARDRAILS_ENABLED)",
    )
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
    zen_base_url: str = Field(
        default="https://api.opencode.ai",
        description="Zen/OpenCode base URL (THGENT_ZEN_BASE_URL)",
    )
    zen_api_key: str = Field(
        default="",
        description="Zen API key (THGENT_ZEN_API_KEY, OPENCODE_API_KEY, ZEN_API_KEY)",
    )
    sharecli_enabled: bool = Field(
        default=True,
        description="Enable sharecli bridge (THGENT_SHARECLI_ENABLED)",
    )
    mac_keep_awake: bool = Field(
        default=True,
        description="Keep Mac awake during claude/codex runs (caffeinate; THGENT_MAC_KEEP_AWAKE)",
    )
    mac_keep_awake_agents: list[str] = Field(
        default=["claude", "codex", "cursor-agent", "opencode"],
        description="Agents that trigger caffeinate when mac_keep_awake (THGENT_MAC_KEEP_AWAKE_AGENTS)",
    )

    @field_validator("mac_keep_awake_agents", mode="before")
    @classmethod
    def _parse_mac_keep_awake_agents(cls, v: object) -> list[str]:
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        if isinstance(v, list):
            return [str(s) for s in v]
        return ["claude", "codex", "cursor-agent", "opencode"]
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
        default=50,
        ge=1,
        le=100,
        description="Maximum concurrent agent runs (ceiling); THGENT_MAX_CONCURRENCY",
    )
    concurrency_load_based: bool = Field(
        default=False,
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
        le=4.0,
        description="Block when load_1m/cpu_count >= this; THGENT_CONCURRENCY_LOAD_PER_CPU_MAX",
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
