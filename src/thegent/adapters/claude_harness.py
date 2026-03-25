"""Claude-specific harness implementation (inherits from HarnessBase)."""

import os
import shutil
from pathlib import Path
from typing import Any, Optional

from thegent.adapters.harness_base import HarnessBase
from thegent.infra.shim_subprocess import run as shim_run


class ClaudeHarness(HarnessBase):
    """Claude Code harness with provider routing and model alias resolution."""

    def get_binary_name(self) -> str:
        return "claude"

    def get_binary_search_paths(self) -> list[str]:
        """Return search paths for claude binary."""
        override = os.environ.get("THGENT_NATIVE_CLAUDE_BIN")
        candidates = []
        if override:
            candidates.append(override)
        candidates.extend([
            str(shutil.which("claude") or ""),
            str(Path.home() / ".local" / "bin" / "claude"),
            str(Path("/opt/homebrew/bin/claude")),
            str(Path("/usr/local/bin/claude")),
            str(Path.home() / ".bun" / "bin" / "claude"),
        ])
        return [c for c in candidates if c]

    def find_binary(self, require_native: bool = False) -> Optional[str]:
        """Find claude binary in standard locations."""
        for candidate in self.get_binary_search_paths():
            p = Path(candidate).expanduser()
            if p.is_file() and os.access(p, os.X_OK):
                return str(p)
        return None

    def get_bypass_flag(self) -> str:
        return "--dangerously-skip-permissions"

    def get_env(self, provider: str, model_override: Optional[str] = None) -> dict[str, str]:
        """Get environment for Claude Code pointing to thegent proxy."""
        self.ensure_proxy_running()

        env = os.environ.copy()
        base = f"http://{self.settings.mcp_host}:{self.settings.cliproxy_port}"
        env["ANTHROPIC_BASE_URL"] = base
        env["ANTHROPIC_API_KEY"] = provider

        config_dir = self.settings.cache_dir / "claude-config"
        config_dir.mkdir(parents=True, exist_ok=True)
        env["CLAUDE_CONFIG_DIR"] = str(config_dir)
        self.ensure_config_isolation(config_dir)

        model_alias_map = self.get_model_alias_map()
        from thegent.clode_model_routing import CLODE_PROVIDER_MODEL
        model = model_override or CLODE_PROVIDER_MODEL.get(provider) or self._model_for_provider(provider)

        env["ANTHROPIC_MODEL"] = model
        env["ANTHROPIC_SONNET_MODEL"] = model
        env["ANTHROPIC_HAIKU_MODEL"] = model
        env["ANTHROPIC_OPUS_MODEL"] = model
        env["ANTHROPIC_DEFAULT_HAIKU_MODEL"] = model
        env["ANTHROPIC_DEFAULT_SONNET_MODEL"] = model
        env["ANTHROPIC_DEFAULT_OPUS_MODEL"] = model
        env["ANTHROPIC_SMALL_FAST_MODEL"] = model
        env["CLAUDE_MODEL"] = model
        env["API_TIMEOUT_MS"] = "300000"

        if provider in ("glm", "auto") or self.settings.sitback:
            env["THGENT_ROUTING"] = "round_robin"

        env["PATH"] = os.environ.get("PATH", "")
        return env

    def resolve_provider_for_model(self, model_alias: str) -> str:
        """Resolve provider for model-first routing with round-robin."""
        from thegent.clode_model_routing import resolve_provider_for_model as impl
        return impl(model_alias)

    def get_model_alias_map(self) -> dict[str, str]:
        """Return Claude model alias mapping."""
        from thegent import clode_model_routing
        return clode_model_routing.MODEL_ALIAS

    def _model_for_provider(self, provider: str) -> str:
        """Get default model for provider."""
        from thegent.clode_model_routing import model_for_provider as impl
        return impl(provider)

    def ensure_config_isolation(self, config_dir: Path) -> None:
        """Ensure isolated config dir for Claude."""
        from thegent.clode_config_isolation import ensure_claude_config_isolation
        ensure_claude_config_isolation(config_dir)

    def fetch_metrics(self) -> dict[str, Any]:
        """Fetch provider metrics for GLM policy routing."""
        try:
            from thegent.agents.cliproxy_manager import fetch_provider_metrics
            return fetch_provider_metrics()
        except Exception:
            return {}
