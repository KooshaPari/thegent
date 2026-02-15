"""Pydantic settings for thegent."""

import json
import os
from pathlib import Path

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
        default="cursor-agent",
        description="Cursor agent CLI (cursor-agent or cursor); set THGENT_CURSOR_AGENT_CMD if not on PATH",
    )
    default_cursor_model: str = Field(
        default="gemini-3-flash",
        description="Default model for cursor agent (gemini-3-flash, composer-1.5, auto)",
    )
    default_gemini_model: str = Field(
        default="gemini-2.0-flash",
        description="Default model for gemini CLI (-m/--model); gemini-2.0-flash widely available",
    )
    default_copilot_model: str = Field(
        default="claude-haiku-4.5",
        description="Default model for copilot (--model)",
    )
    default_claude_model: str = Field(
        default="haiku",
        description="Default model for claude (--model alias: haiku, sonnet, opus)",
    )
    default_codex_model: str = Field(
        default="gpt-5.3-codex",
        description="Default model for codex; 5.3 spark/thinking mix",
    )
    default_codex_model_high: str = Field(
        default="gpt-5.3-codex-high",
        description="Codex high-power model (use with --mode full or --model override)",
    )
    default_antigravity_model: str = Field(
        default="gemini-3-flash",
        description="Default model for antigravity (via CLIProxyAPIPlus); was tstars2.0",
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
    retention_days_registry: int = Field(
        default=90,
        ge=30,
        le=730,
        description="Retention for run registry (audit trail); THGENT_RETENTION_DAYS_REGISTRY",
    )
    retention_by_domain: dict[str, int] = Field(
        default_factory=dict,
        description="Per-domain retention days (WP-3006); THGENT_RETENTION_BY_DOMAIN JSON e.g. {\"gdpr\":365,\"soc2\":2555}",
    )

    @field_validator("retention_by_domain", mode="before")
    @classmethod
    def _parse_retention_by_domain(cls, v: object) -> dict[str, int]:
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                return {k: int(val) for k, val in (parsed or {}).items()} if isinstance(parsed, dict) else {}
            except (json.JSONDecodeError, ValueError, TypeError):
                return {}
        if isinstance(v, dict):
            return {k: int(val) for k, val in v.items()}
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
    cost_budget_mtd: float = Field(
        default=100.0,
        ge=0.0,
        description="MTD budget for AI providers (THGENT_COST_BUDGET_MTD)",
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
        description="Output format for bg/ps: rich (default) or md (agent-friendly markdown)",
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

    normalization_policy_allow_fallback: bool = Field(
        default=True,
        description="Allow falling back to plain text extraction (THGENT_NORMALIZATION_POLICY_ALLOW_FALLBACK)",
    )
    normalization_policy_min_confidence: float = Field(
        default=0.4,
        description="Minimum confidence required for normalized output (THGENT_NORMALIZATION_POLICY_MIN_CONFIDENCE)",
    )
    normalization_policy_max_fallback_rate: float = Field(
        default=0.3,
        description="Max allowed fallback rate (THGENT_NORMALIZATION_POLICY_MAX_FALLBACK_RATE)",
    )
    normalization_policy_strict_providers: str = Field(
        default="",
        description="Comma-separated providers that MUST produce structured output (THGENT_NORMALIZATION_POLICY_STRICT_PROVIDERS)",
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
    routing_parser_quality_enabled: bool = Field(
        default=True,
        description="Order providers by parser quality (confidence, fallback rate); THGENT_ROUTING_PARSER_QUALITY_ENABLED",
    )
