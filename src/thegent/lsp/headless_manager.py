"""Headless LSP Server Manager - Full-featured LSP infrastructure."""

import json
import logging
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Comprehensive LSP server registry
LSP_SERVERS: dict[str, dict[str, Any]] = {
    "python": {
        "command": "pyright-langserver",
        "args": ["--stdio"],
        "install": "npm install -g pyright",
        "supports_multi_client": True,
        "supports_multi_root": True,
    },
    "typescript": {
        "command": "typescript-language-server",
        "args": ["--stdio"],
        "install": "npm install -g typescript-language-server typescript",
        "supports_multi_client": True,
        "supports_multi_root": True,
    },
    "rust": {
        "command": "rust-analyzer",
        "args": [],
        "install": "rustup component add rust-analyzer",
        "supports_multi_client": True,
        "supports_multi_root": True,
    },
    "go": {
        "command": "gopls",
        "args": ["-mode=stdio"],
        "install": "go install golang.org/x/tools/gopls@latest",
        "supports_multi_client": True,
        "supports_multi_root": True,
    },
    "java": {
        "command": "jdtls",  # Eclipse JDT Language Server
        "args": [],
        "install": "brew install jdtls  # macOS\napt-get install jdtls  # Linux",
        "supports_multi_client": True,
        "supports_multi_root": True,
    },
    "cpp": {
        "command": "clangd",
        "args": [],
        "install": "brew install llvm  # or apt-get install clangd",
        "supports_multi_client": True,
        "supports_multi_root": True,
    },
    "bash": {
        "command": "bash-language-server",
        "args": ["start"],
        "install": "npm install -g bash-language-server",
        "supports_multi_client": True,
        "supports_multi_root": True,
    },
    "yaml": {
        "command": "yaml-language-server",
        "args": ["--stdio"],
        "install": "npm install -g yaml-language-server",
        "supports_multi_client": True,
        "supports_multi_root": True,
    },
    "json": {
        "command": "vscode-json-languageserver",
        "args": ["--stdio"],
        "install": "npm install -g vscode-json-languageserver",
        "supports_multi_client": True,
        "supports_multi_root": True,
    },
}


class HeadlessLSPServer:
    """Manages a single LSP server process."""

    def __init__(self, language: str, config: dict[str, Any]) -> None:
        self.language = language
        self.config = config
        self.process: subprocess.Popen[str] | None = None
        self.pid: int | None = None
        self.started_at: float | None = None
        self.clients: list[str] = []  # Client IDs

    def start(self) -> bool:
        """Start LSP server process."""
        command = self.config["command"]
        args = self.config.get("args", [])

        # Check if command exists, auto-install if missing
        cmd_path = shutil.which(command)
        if not cmd_path:
            # Try auto-install
            from thegent.lsp.auto_install import ensure_lsp_server_installed

            logger.info(f"LSP server '{command}' not found, attempting auto-install...")
            if ensure_lsp_server_installed(self.language, auto_install=True):
                cmd_path = shutil.which(command)
                if not cmd_path:
                    logger.error(
                        f"LSP server '{command}' not found after auto-install. "
                        f"Manual install: {self.config.get('install', 'N/A')}"
                    )
                    return False
            else:
                logger.error(
                    f"LSP server '{command}' not found and auto-install failed. "
                    f"Manual install: {self.config.get('install', 'N/A')}"
                )
                return False

        try:
            self.process = subprocess.Popen(
                [cmd_path, *args],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            self.pid = self.process.pid
            self.started_at = time.time()
            logger.info(f"Started LSP server: {self.language} (PID: {self.pid})")
            return True
        except Exception as e:
            logger.error(f"Failed to start LSP server {self.language}: {e}")
            return False

    def stop(self) -> None:
        """Stop LSP server process."""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                if self.process:
                    self.process.kill()
            self.process = None
            self.pid = None

    def is_running(self) -> bool:
        """Check if server is running."""
        if not self.process:
            return False
        return self.process.poll() is None


class HeadlessLSPManager:
    """Manages multiple LSP servers in headless mode."""

    def __init__(self, cache_dir: Path | None = None) -> None:
        self.cache_dir = cache_dir or (Path.home() / ".cache" / "thegent" / "lsp")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.servers: dict[str, HeadlessLSPServer] = {}
        self.lockfile = self.cache_dir / "manager.lock"
        self._load_state()

    def _load_state(self) -> None:
        """Load manager state from lockfile."""
        if not self.lockfile.exists():
            return

        try:
            state = json.loads(self.lockfile.read_text())
            # Note: We don't restore processes (they're dead), just for reference
            logger.debug(f"Loaded LSP manager state: {len(state.get('servers', {}))} servers")
        except Exception as e:
            logger.warning(f"Failed to load LSP manager state: {e}")

    def ensure_server(self, language: str, auto_install: bool | None = None) -> HeadlessLSPServer | None:
        """Ensure LSP server is running for language, auto-installing if needed.

        Args:
            language: Language name
            auto_install: Auto-install LSP server if missing (None = use config default)

        Returns:
            HeadlessLSPServer instance or None
        """
        # Check config for auto-install default
        if auto_install is None:
            from thegent.config import ThegentSettings

            settings = ThegentSettings()
            auto_install = settings.lsp_auto_install

        # Check if already running
        if language in self.servers:
            server = self.servers[language]
            if server.is_running():
                return server
            # Clean up dead server
            del self.servers[language]

        # Start new server
        config = LSP_SERVERS.get(language)
        if not config:
            logger.error(f"Unknown language: {language}")
            return None

        # Auto-install if missing
        if auto_install:
            from thegent.lsp.auto_install import ensure_lsp_server_installed

            if not ensure_lsp_server_installed(language, auto_install=True):
                logger.warning(
                    f"LSP server for {language} not available and auto-install failed. "
                    f"Install manually: {config.get('install', 'N/A')}"
                )

        server = HeadlessLSPServer(language, config)
        if server.start():
            self.servers[language] = server
            self._save_state()
            return server
        return None

    def stop_server(self, language: str) -> None:
        """Stop LSP server for language."""
        if language in self.servers:
            self.servers[language].stop()
            del self.servers[language]
            self._save_state()

    def stop_all(self) -> None:
        """Stop all LSP servers."""
        for server in self.servers.values():
            server.stop()
        self.servers.clear()
        self._save_state()

    def list_servers(self) -> dict[str, dict[str, Any]]:
        """List all running servers."""
        return {
            lang: {
                "pid": server.pid,
                "running": server.is_running(),
                "started_at": server.started_at,
                "clients": len(server.clients),
            }
            for lang, server in self.servers.items()
        }

    def _save_state(self) -> None:
        """Save manager state to lockfile."""
        state = {
            "servers": {
                lang: {
                    "pid": server.pid,
                    "started_at": server.started_at,
                }
                for lang, server in self.servers.items()
            },
            "updated_at": time.time(),
        }
        self.lockfile.write_text(json.dumps(state, indent=2))
