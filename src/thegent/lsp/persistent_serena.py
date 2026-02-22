"""Persistent Serena LSP daemon (MTSP-04).

Consolidates code intelligence into a single persistent Serena daemon
to reduce the overhead of spawning separate LSP servers per agent session.
"""

import asyncio
import logging
import socket

from thegent.config import ThegentSettings

_log = logging.getLogger(__name__)


class PersistentSerenaDaemon:
    """Persistent Serena LSP daemon (MTSP-04)."""

    def __init__(
        self,
        port: int = 3848,
        host: str = "127.0.0.1",
    ) -> None:
        settings = ThegentSettings()
        self.port = port
        self.host = host
        self.log_file = settings.cache_dir / "serena_daemon.log"
        self._proc = None

    async def start(self) -> None:
        """Start the persistent Serena daemon."""
        _log.info("MTSP-04: Starting persistent Serena daemon on %s:%d", self.host, self.port)

        # Command for starting Serena with SSE transport and multiplexing
        cmd = [
            "uvx",
            "--from",
            "git+https://github.com/oraios/serena",
            "serena",
            "start-mcp-server",
            "--transport",
            "sse",
            "--port",
            str(self.port),
            "--host",
            self.host,
            "--context",
            "ide",
            "--project-from-cwd",
            "--open-web-dashboard",
            "false",
        ]

        try:
            with self.log_file.open("a") as f:
                self._proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=f,
                    stderr=f,
                    start_new_session=True,
                )
            _log.info("Serena daemon started with PID %d", self._proc.pid)
        except Exception as e:
            _log.error("Failed to start Serena daemon: %s", e)
            raise

    async def stop(self) -> None:
        """Stop the persistent Serena daemon."""
        if self._proc:
            _log.info("Stopping Serena daemon (PID %d)", self._proc.pid)
            try:
                self._proc.terminate()
                await self._proc.wait()
            except ProcessLookupError:
                pass
            self._proc = None

    def is_running(self) -> bool:
        """Check if the Serena daemon is running."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((self.host, self.port))
                return True
            except OSError:
                return False

    def get_mcp_config(self) -> dict:
        """Get the MCP configuration to connect to this persistent daemon."""
        return {
            "name": "serena-persistent",
            "url": f"http://{self.host}:{self.port}/mcp",
            "transport": "sse",
        }
