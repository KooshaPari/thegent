"""Abstract base class for unified harness pattern (Claude/Codex shared behavior)."""

import os
import shutil
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional

from thegent.config import ThegentSettings
from thegent.infra.shim_subprocess import run as shim_run
from thegent.infra.power import wrap_with_caffeinate


class HarnessBase(ABC):
    """Abstract harness base with common binary discovery, config isolation, and env setup."""

    def __init__(self):
        """Initialize harness with settings."""
        self.settings = self._get_settings()
        self.console = self._get_console()

    @staticmethod
    def _get_settings() -> ThegentSettings:
        """Lazy-load settings."""
        from thegent.config import ThegentSettings
        return ThegentSettings()

    @staticmethod
    def _get_console() -> Any:
        """Lazy-load Rich console."""
        from rich.console import Console
        return Console()

    @staticmethod
    def _is_triggered_by_agent_process() -> bool:
        """Check if run is triggered by agent process (not human user)."""
        from thegent.discovery import _is_triggered_by_agent_process as impl
        return impl()

    @abstractmethod
    def get_binary_name(self) -> str:
        """Return binary name (e.g. 'claude', 'codex')."""
        pass

    @abstractmethod
    def get_binary_search_paths(self) -> list[str]:
        """Return ordered list of paths to search for binary."""
        pass

    @abstractmethod
    def find_binary(self, require_native: bool = False) -> Optional[str]:
        """Discover binary path. Can be overridden by subclass."""
        pass

    @abstractmethod
    def get_bypass_flag(self) -> str:
        """Return CLI flag for permission bypass (e.g. '--dangerously-skip-permissions')."""
        pass

    @abstractmethod
    def get_env(self, provider: str, model_override: Optional[str] = None) -> dict[str, str]:
        """Get environment variables for this harness pointing to proxy."""
        pass

    @abstractmethod
    def resolve_provider_for_model(self, model_alias: str) -> str:
        """Resolve provider for model-first routing."""
        pass

    @abstractmethod
    def get_model_alias_map(self) -> dict[str, str]:
        """Return model alias -> canonical mapping."""
        pass

    def ensure_binary_installed(
        self, suggest_alt: bool = False, require_native: bool = False
    ) -> str:
        """Auto-install binary via brew/bun/etc. or raise. Returns path."""
        p = self.find_binary(require_native=require_native)
        if p:
            return p

        bin_name = self.get_binary_name()

        # Try brew
        brew = shutil.which("brew")
        if brew:
            self.console.print(f"[dim]Installing {bin_name} via Homebrew...[/dim]")
            cask_name = "claude-code" if bin_name == "claude" else f"{bin_name}-cli"
            r = shim_run(
                [brew, "install", "--cask", cask_name],
                capture_output=True,
                text=True,
                check=False,
            )
            if r.returncode == 0:
                p = self.find_binary(require_native=require_native)
                if p:
                    return p

        # Try bun
        bun = shutil.which("bun")
        if bun and bin_name == "claude":
            self.console.print("[dim]Installing Claude Code via Bun...[/dim]")
            r = shim_run(
                [bun, "install", "-g", "@anthropic-ai/claude-code"],
                capture_output=True,
                text=True,
                check=False,
            )
            if r.returncode == 0:
                p = self.find_binary(require_native=require_native)
                if p:
                    return p

        if require_native:
            env_var = "THGENT_NATIVE_CLAUDE_BIN" if bin_name == "claude" else "THGENT_NATIVE_CODEX_BIN"
            self.console.print(
                f"[red]Error: native '{bin_name}' CLI not found.[/red]\n"
                f"[dim]Set {env_var}=/absolute/path/to/{bin_name} to force a specific binary.[/dim]"
            )
        else:
            self.console.print(f"[red]Error: '{bin_name}' CLI not found.[/red]")
        if suggest_alt:
            self.console.print(f"[dim]Or use an alternative harness.[/dim]")
        raise SystemExit(1)

    def ensure_config_isolation(self, config_dir: Path) -> None:
        """Ensure isolated config directory (subclasses override as needed)."""
        config_dir.mkdir(parents=True, exist_ok=True)

    def ensure_proxy_running(self) -> None:
        """Ensure cliproxy is running (subclasses override as needed)."""
        from thegent.agents.cliproxy_manager import ensure_proxy_running
        ensure_proxy_running(self.settings)

    def install_harness_link(self, bin_dir: Path, harness: str, force: bool = False) -> bool:
        """Install harness symlink to thegent-shims. Returns True if created/updated."""
        shims_path = shutil.which("thegent-shims")
        if not shims_path:
            candidate = bin_dir / "thegent-shims"
            if candidate.exists():
                shims_path = str(candidate)
        if not shims_path:
            self.console.print(
                "[red]thegent-shims not found.[/red] Install it first with: [dim]thegent install-shims --all[/dim]"
            )
            raise SystemExit(1)

        target = bin_dir / harness
        if target.exists() or target.is_symlink():
            if not force:
                return False
            if target.is_dir() and not target.is_symlink():
                from thegent.errors import print_error
                print_error(f"{target} is a directory. Remove it before reinstalling.")
                raise SystemExit(1)
            target.unlink()

        target.symlink_to(Path(shims_path))
        return True

    def run_interactive(
        self,
        provider: str,
        extra_args: Optional[list[str]] = None,
        model_override: Optional[str] = None,
    ) -> None:
        """Start interactive session. Uses os.execvpe (replaces current process)."""
        env = self.get_env(provider, model_override=model_override)
        binary_path = self.ensure_binary_installed()

        cmd = [binary_path]
        if not self._is_triggered_by_agent_process():
            cmd.append(self.get_bypass_flag())
        if extra_args:
            cmd.extend(extra_args)

        cmd = wrap_with_caffeinate(cmd, self.get_binary_name())
        os.execvpe(cmd[0], cmd, env)

    def run_exec(
        self,
        prompt: str,
        *,
        cd: Optional[Path] = None,
        add_dir: Optional[list[str]] = None,
        model_override: Optional[str] = None,
        timeout_seconds: int = 15,
    ) -> None:
        """Run in headless mode (print response and exit)."""
        raise NotImplementedError("Subclass must implement run_exec")

    def fetch_metrics(self) -> dict[str, Any]:
        """Fetch provider metrics for GLM/etc routing. Default: empty."""
        return {}
