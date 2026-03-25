"""Codex-specific harness implementation (inherits from HarnessBase)."""

import os
import shutil
from pathlib import Path
from typing import Any, Optional

from thegent.adapters.harness_base import HarnessBase
from thegent.infra.shim_subprocess import run as shim_run


class CodexHarness(HarnessBase):
    """Codex harness with model-first routing (no provider filter)."""

    def get_binary_name(self) -> str:
        return "codex"

    def get_binary_search_paths(self) -> list[str]:
        """Return search paths for codex binary."""
        override = os.environ.get("THGENT_NATIVE_CODEX_BIN")
        candidates = []
        if override:
            candidates.append(override)
        candidates.extend([
            str(shutil.which("codex") or ""),
            str(Path.home() / ".factory" / "bin" / "codex"),
            str(Path("/opt/homebrew/bin/codex")),
            str(Path("/usr/local/bin/codex")),
            str(Path.home() / ".bun" / "bin" / "codex"),
        ])
        return [c for c in candidates if c]

    def find_binary(self, require_native: bool = False) -> Optional[str]:
        """Find codex binary, filtering out thegent-shims."""
        for candidate in self.get_binary_search_paths():
            p = Path(candidate).expanduser()
            if p.is_file() and os.access(p, os.X_OK):
                if not self._is_thegent_shim(str(p)):
                    return str(p)
        return None

    @staticmethod
    def _is_thegent_shim(path: str) -> bool:
        """Check if path is thegent-shims symlink."""
        p = Path(path)
        if "thegent-shims" in p.name:
            return True
        try:
            if p.is_symlink() and "thegent-shims" in str(p.readlink()):
                return True
        except OSError:
            pass
        return False

    def get_bypass_flag(self) -> str:
        return "--dangerously-bypass-approvals-and-sandbox"

    def get_env(self, provider: str, model_override: Optional[str] = None) -> dict[str, str]:
        """Get environment for Codex pointing to thegent proxy."""
        from thegent.agents.cliproxy_manager import _ensure_config, _has_provider_credentials

        _ensure_config(self.settings)
        self.ensure_proxy_running()

        # Handle cursor/zen provider fallback
        import yaml
        config_path = self.settings.cliproxy_config_path.expanduser().resolve()
        if config_path.exists():
            try:
                config = yaml.safe_load(config_path.read_text())
                if isinstance(config, dict) and not _has_provider_credentials(config, provider):
                    if provider == "cursor":
                        fallback = "minimax" if _has_provider_credentials(config, "minimax") else "glm"
                        if _has_provider_credentials(config, fallback):
                            self.console.print(
                                f"[yellow]Warning: Cursor not configured. Falling back to {fallback}.[/yellow]"
                            )
                            provider = fallback
                    elif provider == "zen":
                        self.console.print(
                            "[red]Zen not configured for gemini-3-flash.[/red] "
                            "Set THGENT_ZEN_API_KEY or run: thegent cliproxy login zen"
                        )
                        raise SystemExit(1)
            except Exception:
                pass

        env = os.environ.copy()
        env["THGENT_CLIPROXY_ADAPTER"] = "1"
        if self.settings.cliproxy_backend_url:
            env["THGENT_CLIPROXY_BACKEND_URL"] = self.settings.cliproxy_backend_url
        base = f"http://{self.settings.mcp_host}:{self.settings.cliproxy_port}/v1"
        env["OPENAI_BASE_URL"] = base
        env["OPENAI_API_KEY"] = provider
        env["API_TIMEOUT_MS"] = "300000"

        # Clean malloc noise
        env.pop("MallocStackLogging", None)
        env.pop("MallocStackLoggingNoCompact", None)
        env.pop("MallocStackLoggingDirectory", None)

        # Prepend ~/.local/bin for git shim
        local_bin = str(Path.home() / ".local" / "bin")
        path = os.environ.get("PATH", "")
        first_in_path = path.split(os.pathsep)[0] if path else ""
        env["PATH"] = f"{local_bin}{os.pathsep}{path}" if first_in_path != local_bin else path

        return env

    def resolve_provider_for_model(self, model_alias: str) -> str:
        """Resolve provider for model-first routing (Codex always returns 'auto')."""
        from thegent.dex_cli_helpers import canonical_model
        _ = canonical_model(model_alias, self.get_model_alias_map())
        return "auto"

    def get_model_alias_map(self) -> dict[str, str]:
        """Return Codex model alias mapping."""
        from thegent.agents.routing_contracts import GEMINI_FLASH_MODEL
        return {
            "dex": "gpt-5.3-codex",
            "codex": "gpt-5.3-codex",
            "composer": "composer-1.5",
            "composer1.5": "composer-1.5",
            "comp": "composer-1.5",
            "max": "minimax-m2.5",
            "m2.5": "minimax-m2.5",
            "glm": "glm-5",
            "glm5": "glm-5",
            "haiku": "claude-haiku-4.5",
            "opus": "claude-opus-4.6",
            "sonnet": "claude-sonnet-4.5",
            "sonnet1m": "claude-sonnet-4.5-1m",
            "step": "step-3.5-flash",
            "step3.5": "step-3.5-flash",
            "flash": GEMINI_FLASH_MODEL,
            "high": "gpt-5.3-codex-high",
            "xhigh": "gpt-5.3-codex-xhigh",
            "mini": "gpt-5-mini",
            "gpt5mini": "gpt-5-mini",
        }

    def ensure_proxy_running(self) -> None:
        """Ensure cliproxy running, with error handling."""
        from thegent.agents.cliproxy_manager import ensure_proxy_running
        try:
            ensure_proxy_running(self.settings)
        except (RuntimeError, FileNotFoundError) as e:
            from thegent.errors import print_error
            print_error(str(e))
            raise SystemExit(1)
