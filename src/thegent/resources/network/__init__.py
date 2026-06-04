"""Stub module."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

try:
    import psutil as _psutil

    _PSUTIL_AVAILABLE = True
except Exception:  # pragma: no cover - platform dependency
    _psutil = None
    _PSUTIL_AVAILABLE = False


class NetworkMonitor:
    """Monitor for network resources."""

    def __init__(self) -> None:
        self.latency_ms: float = 0.0

    def get_status(self) -> dict[str, Any]:
        """Get network status."""
        return {"latency_ms": self.latency_ms, "connected": True}

    def measure_latency(self, host: str) -> float:
        """Measure latency to a host."""
        return 0.0

    def list_interfaces(self, include_diagnostics: bool = False) -> dict[str, Any]:
        """List network interfaces with optional diagnostics."""
        if not _PSUTIL_AVAILABLE or _psutil is None:
            return {"status": "unavailable", "interfaces": {}, "error": {"type": "psutil_unavailable"}}
        try:
            counters = _psutil.net_io_counters(pernic=True)
        except Exception as exc:
            payload: dict[str, Any] = {"status": "error", "interfaces": {}}
            if include_diagnostics:
                payload["error"] = {"type": type(exc).__name__, "message": str(exc)}
            return payload
        status = "ok" if counters else "empty"
        return {"status": status, "interfaces": counters}


__all__ = ["NetworkMonitor", "BandwidthSample", "NetworkStats", "_PSUTIL_AVAILABLE", "_psutil"]


@dataclass
class BandwidthSample:
    """A bandwidth measurement sample."""

    timestamp: str
    download_bps: float = 0.0
    upload_bps: float = 0.0
    latency_ms: float = 0.0

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class NetworkStats:
    """Network statistics."""

    bytes_sent: int = 0
    bytes_received: int = 0
    packets_sent: int = 0
    packets_received: int = 0
    errors_in: int = 0
    errors_out: int = 0
    timestamp: str = ""
