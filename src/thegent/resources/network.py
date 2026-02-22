"""Network bandwidth monitoring for thegent resource management."""

import logging
import time
from dataclasses import dataclass, field
from types import ModuleType

logger = logging.getLogger(__name__)

_psutil: ModuleType | None = None
_PSUTIL_AVAILABLE = False

try:
    import psutil as _psutil_mod

    _psutil = _psutil_mod
    _PSUTIL_AVAILABLE = True
except ImportError:
    logger.warning("psutil not available; network monitoring returns empty/zero results")


@dataclass
class NetworkStats:
    """Raw I/O counters for a single network interface at a point in time."""

    interface: str
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int
    timestamp: float = field(default_factory=time.time)


@dataclass
class BandwidthSample:
    """Calculated bandwidth for a single network interface over a sampling interval."""

    interface: str
    send_bps: float
    recv_bps: float
    timestamp: float = field(default_factory=time.time)


class NetworkMonitor:
    """Monitor network bandwidth using psutil.

    Falls back to returning empty/zero results when psutil is unavailable.
    """

    def get_stats(self, interface: str | None = None) -> list[NetworkStats]:
        """Return current I/O counters per interface.

        Args:
            interface: If provided, return stats only for this interface.
                If None, return stats for all available interfaces.

        Returns:
            List of NetworkStats, one per matching interface.
            Returns an empty list when psutil is unavailable.
        """
        if not _PSUTIL_AVAILABLE or _psutil is None:
            return []

        try:
            counters = _psutil.net_io_counters(pernic=True)
        except Exception:
            logger.exception("Failed to read network I/O counters")
            return []

        now = time.time()
        result: list[NetworkStats] = []

        interfaces = [interface] if interface is not None else list(counters.keys())
        for iface in interfaces:
            if iface not in counters:
                continue
            c = counters[iface]
            result.append(
                NetworkStats(
                    interface=iface,
                    bytes_sent=c.bytes_sent,
                    bytes_recv=c.bytes_recv,
                    packets_sent=c.packets_sent,
                    packets_recv=c.packets_recv,
                    timestamp=now,
                )
            )
        return result

    def sample_bandwidth(self, interval_s: float = 1.0) -> list[BandwidthSample]:
        """Measure bandwidth by taking two samples separated by *interval_s* seconds.

        Args:
            interval_s: Seconds between the two counter snapshots.
                Must be positive; values <= 0 are clamped to 0.01 s.

        Returns:
            List of BandwidthSample (send_bps / recv_bps) per interface.
            Returns an empty list when psutil is unavailable.
        """
        if not _PSUTIL_AVAILABLE:
            return []

        interval_s = max(interval_s, 0.01)

        before = self.get_stats()
        if not before:
            return []

        time.sleep(interval_s)

        after_map: dict[str, NetworkStats] = {s.interface: s for s in self.get_stats()}

        samples: list[BandwidthSample] = []
        for b in before:
            a = after_map.get(b.interface)
            if a is None:
                continue
            elapsed = max(a.timestamp - b.timestamp, 1e-9)
            samples.append(
                BandwidthSample(
                    interface=b.interface,
                    send_bps=(a.bytes_sent - b.bytes_sent) / elapsed,
                    recv_bps=(a.bytes_recv - b.bytes_recv) / elapsed,
                    timestamp=a.timestamp,
                )
            )
        return samples

    def get_total_bandwidth(self) -> tuple[float, float]:
        """Return (send_bps, recv_bps) summed across all interfaces.

        Takes two counter snapshots with a 1-second interval.

        Returns:
            Tuple of (total_send_bps, total_recv_bps).
            Returns (0.0, 0.0) when psutil is unavailable or no interfaces found.
        """
        samples = self.sample_bandwidth(interval_s=1.0)
        if not samples:
            return (0.0, 0.0)
        send_total = sum(s.send_bps for s in samples)
        recv_total = sum(s.recv_bps for s in samples)
        return (send_total, recv_total)

    def list_interfaces(self, *, include_diagnostics: bool = False) -> list[str] | dict[str, object]:
        """Return interface names, with optional diagnostics payload.

        Returns:
            If include_diagnostics=False (default): list[str].
            If include_diagnostics=True: dict with keys:
              - interfaces: list[str]
              - status: "ok" | "empty" | "unavailable" | "error"
              - error: None or {"type": str, "message": str}
        """
        payload: dict[str, object] = {
            "interfaces": [],
            "status": "ok",
            "error": None,
        }
        if not _PSUTIL_AVAILABLE or _psutil is None:
            payload["status"] = "unavailable"
            payload["error"] = {"type": "psutil_unavailable", "message": "psutil is not available"}
            return payload if include_diagnostics else []

        try:
            counters = _psutil.net_io_counters(pernic=True)
            interfaces = list(counters.keys())
            payload["interfaces"] = interfaces
            payload["status"] = "empty" if not interfaces else "ok"
            return payload if include_diagnostics else interfaces
        except Exception as exc:
            logger.exception("Failed to list network interfaces")
            payload["status"] = "error"
            payload["error"] = {"type": type(exc).__name__, "message": str(exc)}
            return payload if include_diagnostics else []
