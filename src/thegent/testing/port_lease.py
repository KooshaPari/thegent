"""Test runner port leasing (MTSP-16).

Provides a mechanism to lease unique ports for parallel test execution
to avoid port collisions.
"""

import fcntl
import logging
import os
import socket
import time
from pathlib import Path
from typing import Any

from thegent.config import ThegentSettings

_log = logging.getLogger(__name__)


class PortLeaseManager:
    """Manages port leasing for parallel test execution (MTSP-16)."""

    def __init__(
        self,
        lease_dir: Path | None = None,
        port_range: tuple[int, int] = (9000, 9999),
    ) -> None:
        settings = ThegentSettings()
        self.lease_dir = lease_dir or settings.cache_dir / "port_leases"
        self.lease_dir.mkdir(parents=True, exist_ok=True)
        self.port_min, self.port_max = port_range

    def _is_port_free(self, port: int) -> bool:
        """Check if a port is free on the system."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return True
            except OSError:
                return False

    def lease_port(self, timeout: int = 30) -> int:
        """Lease a unique port. Returns the port number."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            for port in range(self.port_min, self.port_max + 1):
                lease_file = self.lease_dir / f"{port}.lock"

                # Try to get a file lock on the lease file
                try:
                    f = lease_file.open("w")
                    fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)

                    # Double check if port is actually free
                    if self._is_port_free(port):
                        # Successfully leased
                        f.write(f"{os.getpid()}\n")
                        f.flush()
                        # We keep the file handle open to maintain the lock
                        self._active_leases[port] = f
                        _log.info("MTSP-16: Leased port %d", port)
                        return port

                    # Port not free, release lock and close
                    fcntl.flock(f, fcntl.LOCK_UN)
                    f.close()
                except OSError:
                    # Lock held by someone else or other error
                    continue

            time.sleep(0.5)

        raise TimeoutError(f"Could not lease a port in range {self.port_min}-{self.port_max} within {timeout}s")

    def release_port(self, port: int) -> None:
        """Release a previously leased port."""
        if hasattr(self, "_active_leases") and port in self._active_leases:
            f = self._active_leases.pop(port)
            try:
                fcntl.flock(f, fcntl.LOCK_UN)
                f.close()
                _log.info("MTSP-16: Released port %d", port)

                # Optional: remove the lock file
                lease_file = self.lease_dir / f"{port}.lock"
                if lease_file.exists():
                    lease_file.unlink()
            except OSError:
                pass

    @property
    def _active_leases(self) -> dict[int, Any]:
        if not hasattr(self, "_active_leases_dict"):
            self._active_leases_dict = {}
        return self._active_leases_dict
