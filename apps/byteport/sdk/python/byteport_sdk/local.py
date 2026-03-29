"""Local deployment helpers backed by the KInfra runtime."""

from __future__ import annotations

import contextlib
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Generator, Optional

from .exceptions import MissingKInfraError


@dataclass
class LocalDeploymentConfig:
    """Configuration for running a service locally with a public tunnel."""

    service_name: str
    local_port: Optional[int] = None
    domain: Optional[str] = None


@dataclass
class LocalTunnelInfo:
    """Information about the running tunnel."""

    service_name: str
    port: int
    url: str
    tunnel_id: Optional[str] = None
    hostname: Optional[str] = None


def _resolve_kinfra_path() -> Optional[str]:
    path = os.getenv('BYTEPORT_KINFRA_PATH')
    if path:
        libs = Path(path).expanduser().resolve() / 'libraries' / 'python'
        if libs.exists():
            return str(libs)
    return None


def _import_kinfra():
    kinfra_path = _resolve_kinfra_path()
    if kinfra_path and kinfra_path not in sys.path:
        sys.path.insert(0, kinfra_path)

    try:
        from kinfra import KInfra, TunnelInfo  # type: ignore
    except ImportError as exc:  # pragma: no cover - requires external dependency
        raise MissingKInfraError(
            'KInfra is not available. Install it or set BYTEPORT_KINFRA_PATH to the repository root.'
        ) from exc
    return KInfra, TunnelInfo


class LocalDeploymentManager:
    """Manage local deployments using KInfra for tunnel + port allocation."""

    def __init__(self, domain: str = 'kooshapari.com') -> None:
        KInfra, _ = _import_kinfra()
        self._kinfra = KInfra(domain=domain)

    def _ensure_port(self, config: LocalDeploymentConfig) -> int:
        if config.local_port is not None:
            return config.local_port
        return self._kinfra.allocate_port(config.service_name)

    @contextlib.contextmanager
    def start_local_tunnel(self, config: LocalDeploymentConfig) -> Generator[LocalTunnelInfo, None, None]:
        """Start a tunnel and yield connection details."""

        port = self._ensure_port(config)
        _, TunnelInfo = _import_kinfra()
        tunnel: TunnelInfo = self._kinfra.start_tunnel(config.service_name, port, config.domain)

        info = LocalTunnelInfo(
            service_name=config.service_name,
            port=port,
            url=getattr(tunnel, 'url', f'https://{getattr(tunnel, "hostname", "localhost")}'),
            tunnel_id=getattr(tunnel, 'tunnel_id', None),
            hostname=getattr(tunnel, 'hostname', None),
        )

        try:
            yield info
        finally:
            try:
                self._kinfra.tunnel_manager.stop_tunnel(config.service_name)  # type: ignore[attr-defined]
            except Exception:
                # Stopping is best-effort; KInfra cleans up on exit as well.
                pass


__all__ = ['LocalDeploymentConfig', 'LocalDeploymentManager', 'LocalTunnelInfo']
