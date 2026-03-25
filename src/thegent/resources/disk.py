"""Disk I/O queue depth monitoring for thegent resource management.

@trace FR-RESOURCE-001
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

try:
    import psutil

    _PSUTIL_AVAILABLE = True
except ImportError:
    _PSUTIL_AVAILABLE = False


@dataclass
class DiskIoStats:
    """Per-device disk I/O counters from the OS.

    All ``*_count`` and ``*_bytes`` fields reflect cumulative totals
    since boot (monotonically increasing), matching the semantics of
    ``psutil.disk_io_counters()``.
    """

    device: str
    read_count: int
    write_count: int
    read_bytes: int
    write_bytes: int
    read_time_ms: int
    write_time_ms: int
    busy_time_ms: int | None = None


@dataclass
class DiskQueueSample:
    """Estimated queue depth and utilization for one block device.

    ``queue_depth`` is derived from Little's Law applied to the busy-time
    delta between two ``DiskIoStats`` samples:

        queue_depth = (busy_time_delta_ms / elapsed_ms)
                      * (io_count_delta / max(io_count_delta, 1))

    When ``busy_time_ms`` is unavailable (e.g. macOS), ``utilization_pct``
    is still computed from the combined read/write time delta.
    """

    device: str
    queue_depth: float
    utilization_pct: float
    timestamp: float = field(default_factory=time.time)


class DiskMonitor:
    """Monitors disk I/O statistics and estimates queue depth.

    Uses ``psutil.disk_io_counters(perdisk=True)`` as the data source.
    If psutil is not installed, all methods return empty results rather
    than raising, keeping callers resilient to missing dependencies.

    Usage::

        monitor = DiskMonitor()
        stats = monitor.get_io_stats()           # snapshot I/O counters
        samples = monitor.sample_queue_depth()   # estimate queue depth
        devices = monitor.list_devices()         # enumerate block devices
        usage = monitor.get_disk_usage("/")      # wrapper for disk_usage
    """

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_io_stats(self, device: str | None = None) -> list[DiskIoStats]:
        """Return per-device I/O counters.

        Args:
            device: If given, return only stats for that device name.
                    ``None`` returns all devices.

        Returns:
            List of :class:`DiskIoStats`, one per block device.
            Returns ``[]`` when psutil is unavailable.
        """
        if not _PSUTIL_AVAILABLE:
            return []

        try:
            raw: dict[str, Any] = psutil.disk_io_counters(perdisk=True) or {}
        except Exception:
            return []

        results: list[DiskIoStats] = []
        for dev_name, counters in raw.items():
            if device is not None and dev_name != device:
                continue
            results.append(
                DiskIoStats(
                    device=dev_name,
                    read_count=getattr(counters, "read_count", 0),
                    write_count=getattr(counters, "write_count", 0),
                    read_bytes=getattr(counters, "read_bytes", 0),
                    write_bytes=getattr(counters, "write_bytes", 0),
                    read_time_ms=getattr(counters, "read_time", 0),
                    write_time_ms=getattr(counters, "write_time", 0),
                    busy_time_ms=getattr(counters, "busy_time", None),
                )
            )
        return results

    def sample_queue_depth(self, interval_s: float = 1.0) -> list[DiskQueueSample]:
        """Estimate I/O queue depth by comparing two snapshots.

        Takes two ``get_io_stats()`` snapshots separated by ``interval_s``
        seconds and derives:

        - ``utilization_pct``: fraction of the interval the device was busy
          (using ``busy_time_ms`` when available, otherwise ``read_time_ms +
          write_time_ms`` saturated at ``interval_s * 1000`` ms).
        - ``queue_depth``: average number of pending I/O requests during the
          interval, estimated as ``utilization_fraction * io_rate``.

        Args:
            interval_s: Sampling window in seconds (must be > 0).

        Returns:
            List of :class:`DiskQueueSample`, one per device seen in both
            snapshots.  Returns ``[]`` when psutil is unavailable.
        """
        if not _PSUTIL_AVAILABLE:
            return []

        if interval_s <= 0:
            interval_s = 1.0

        before = {s.device: s for s in self.get_io_stats()}
        time.sleep(interval_s)
        after = {s.device: s for s in self.get_io_stats()}

        elapsed_ms = interval_s * 1000.0
        samples: list[DiskQueueSample] = []
        ts = time.time()

        for dev_name, a in after.items():
            if dev_name not in before:
                continue
            b = before[dev_name]

            io_delta = (a.read_count - b.read_count) + (a.write_count - b.write_count)

            # Prefer dedicated busy_time; fall back to sum of r/w times.
            if a.busy_time_ms is not None and b.busy_time_ms is not None:
                busy_delta_ms = float(a.busy_time_ms - b.busy_time_ms)
            else:
                busy_delta_ms = float((a.read_time_ms - b.read_time_ms) + (a.write_time_ms - b.write_time_ms))

            # Clamp to [0, elapsed_ms] to handle counter wrap-arounds.
            busy_delta_ms = max(0.0, min(busy_delta_ms, elapsed_ms))

            utilization = busy_delta_ms / elapsed_ms if elapsed_ms > 0 else 0.0
            utilization_pct = utilization * 100.0

            # Queue depth = utilization * IO ops per second  (Little's Law proxy)
            io_rate = io_delta / interval_s if interval_s > 0 else 0.0
            queue_depth = utilization * io_rate

            samples.append(
                DiskQueueSample(
                    device=dev_name,
                    queue_depth=queue_depth,
                    utilization_pct=utilization_pct,
                    timestamp=ts,
                )
            )

        return samples

    def list_devices(self) -> list[str]:
        """Return names of all block devices reported by the OS.

        Returns:
            Sorted list of device name strings (e.g. ``["disk0", "disk1"]``
            on macOS or ``["sda", "sdb"]`` on Linux).
            Returns ``[]`` when psutil is unavailable.
        """
        if not _PSUTIL_AVAILABLE:
            return []

        try:
            raw = psutil.disk_io_counters(perdisk=True) or {}
        except Exception:
            return []

        return sorted(raw.keys())

    def get_disk_usage(self, path: str = "/") -> dict[str, Any]:
        """Return disk usage statistics for the filesystem at *path*.

        Wraps ``psutil.disk_usage(path)`` and converts the named-tuple to a
        plain dictionary with keys ``total``, ``used``, ``free``, and
        ``percent``.

        Args:
            path: Mount point or any path on the target filesystem.

        Returns:
            Dict with keys ``total``, ``used``, ``free``, ``percent``.
            Returns ``{}`` when psutil is unavailable or the path is invalid.
        """
        if not _PSUTIL_AVAILABLE:
            return {}

        try:
            usage = psutil.disk_usage(path)
        except OSError, ValueError:
            return {}

        return {
            "total": usage.total,
            "used": usage.used,
            "free": usage.free,
            "percent": usage.percent,
        }
