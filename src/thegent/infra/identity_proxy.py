"""SSH Identity Proxy Bridge.

Allows isolated L2 agents to use host SSH keys for Git operations
without exposing private keys to the guest environment.
"""

import logging
import os
import socket
import threading
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class SSHIdentityProxy:
    """
    Acts as a secure bridge between the host's SSH agent and isolated L2 agents.
    Uses Unix Domain Sockets to forward signing requests.
    """

    def __init__(self, proxy_socket_path: Path) -> None:
        self.proxy_socket_path = proxy_socket_path
        self.host_ssh_auth_sock = os.environ.get("SSH_AUTH_SOCK")
        self._running = False
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        """Start the proxy server."""
        if not self.host_ssh_auth_sock:
            logger.warning("SSH_AUTH_SOCK not set on host. Identity proxy disabled.")
            return

        if self.proxy_socket_path.exists():
            self.proxy_socket_path.unlink()

        self.proxy_socket_path.parent.mkdir(parents=True, exist_ok=True)

        self._running = True
        self._thread = threading.Thread(target=self._server_loop, daemon=True)
        self._thread.start()
        logger.info(f"SSH Identity Proxy started at {self.proxy_socket_path}")

    def stop(self) -> None:
        """Stop the proxy server."""
        self._running = False
        if self.proxy_socket_path.exists():
            self.proxy_socket_path.unlink()
        logger.info("SSH Identity Proxy stopped.")

    def _server_loop(self) -> None:
        """Listen for connections from isolated L2 agents."""
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.bind(str(self.proxy_socket_path))
            s.listen(5)
            s.settimeout(1.0)

            while self._running:
                try:  # noqa: PERF203 -- socket accept loop, exception handling required for timeout
                    conn, _addr = s.accept()
                    threading.Thread(target=self._handle_client, args=(conn,), daemon=True).start()
                except TimeoutError:
                    continue
                except Exception as e:
                    if self._running:
                        logger.error(f"Proxy server error: {e}")

    def _handle_client(self, client_conn: socket.socket) -> None:
        """Forward requests to the host SSH agent."""
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as host_conn:
                host_conn.connect(self.host_ssh_auth_sock)

                # Bidirectional forwarding loop
                client_conn.setblocking(False)
                host_conn.setblocking(False)

                def _forward_recv(src: socket.socket, dst: socket.socket) -> bool:
                    """Forward data from src to dst. Returns False if connection closed."""
                    try:
                        data = src.recv(4096)
                        if not data:
                            return False
                        dst.sendall(data)
                    except BlockingIOError:
                        pass
                    return True

                while self._running:
                    # Very basic pump - in production, use select/poll
                    if not _forward_recv(client_conn, host_conn):
                        break
                    if not _forward_recv(host_conn, client_conn):
                        break

                    import time

                    time.sleep(0.001)  # Avoid 100% CPU
        except Exception as e:
            logger.error(f"Proxy handler error: {e}")
        finally:
            client_conn.close()

    def get_env(self) -> dict[str, str]:
        """Return the environment variable for L2 agents to use this proxy."""
        return {"SSH_AUTH_SOCK": str(self.proxy_socket_path), "THEGENT_IDENTITY_PROXY": "1"}
