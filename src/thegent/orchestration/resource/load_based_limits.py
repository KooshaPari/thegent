"""WP-5001: Load-based concurrency limits (FD, memory, CPU, load average).

Replaces fixed max_concurrency with dynamic, resource-aware limits that scale
as a load balancer: allow more slots when system headroom exists, throttle when
gates are near capacity.

BKM-04: When THGENT_USE_NATIVE_RESOURCES=1, uses thegent-resources Rust binary
instead of psutil. Set THGENT_RESOURCES_BIN to override path.

Hysteresis tuning environment variables (WP-Y6):
  THGENT_HYSTERESIS_UPPER  - Utilization ratio above which scale-up is triggered
                             (default: 0.8). Float in range (0, 1].
  THGENT_HYSTERESIS_LOWER  - Utilization ratio below which scale-down is triggered
                             (default: 0.4). Float in range [0, 1).
  THGENT_HYSTERESIS_DWELL  - Minimum seconds between consecutive scaling events,
                             prevents rapid thrashing (default: 30). Integer >= 0.

Soft deadline support (swarm-soft-deadlines):
  SoftDeadline tracks a preferred completion time for a run.
  DeadlineMonitor is a daemon thread that checks all registered deadlines
  at a configurable interval and emits structured log events:
    - WARNING when elapsed > deadline_ts * warn_at_pct
    - ERROR   when elapsed > deadline_ts (past soft deadline)
  Soft deadlines NEVER cancel tasks — they only warn and record state.
"""

import orjson as json
import logging
import multiprocessing
import os
import platform
import re
import subprocess
from thegent.infra.shim_subprocess import run as shim_run
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import psutil

_log = logging.getLogger(__name__)

import structlog as _structlog

_slog = _structlog.get_logger(__name__)


@dataclass
class ResourceSnapshot:
    """Current system resource usage for limit calculation."""

    fd_used: int = 0
    fd_limit: int = 0
    mem_rss_mb: float = 0.0
    mem_available_mb: float = 0.0
    cpu_count: int = 1
    load_1m: float = 0.0
    load_5m: float = 0.0
    load_15m: float = 0.0
    gates: dict[str, Any] = field(default_factory=dict)

    # Extended indices (optional, populated if available)
    network_bytes_sent: int = 0
    network_bytes_recv: int = 0
    network_connections: int = 0
    disk_read_bytes: int = 0
    disk_write_bytes: int = 0
    process_count: int = 0
    thread_count: int = 0
    swap_used_mb: float = 0.0
    swap_total_mb: float = 0.0


def _get_fd_usage() -> tuple[int, int]:
    """Return (used_fds, limit). Uses psutil exclusively — psutil is a required dependency."""
    import resource

    proc = psutil.Process()
    used = proc.num_fds()

    soft, _ = resource.getrlimit(resource.RLIMIT_NOFILE)
    limit = soft if soft != resource.RLIM_INFINITY else 1024

    return used, limit


def _get_memory_mb_macos_vm_stat() -> float:
    """Return available_mb on macOS by parsing vm_stat output.

    vm_stat output example:
        Mach Virtual Memory Statistics: (page size of 4096 bytes)
        Pages free:                              12345.
        Pages active:                            67890.
        Pages inactive:                         11111.
        ...

    available_memory approximation: (pages_free + pages_inactive + pages_speculative + pages_purgeable) * page_size.
    Page size is read from ``sysctl hw.pagesize`` or parsed from ``vm_stat`` output; falls back to 4096 bytes.

    Returns 1024.0 as a conservative sentinel on any parse or subprocess failure (increased from 512.0).
    """
    try:
        # Determine actual page size via sysctl (usually 4096, but M-series can differ)
        page_size = 4096
        try:
            ps_out = shim_run(
                ["sysctl", "-n", "hw.pagesize"],
                capture_output=True,
                text=True,
                timeout=2,
                check=False,
            )
            if ps_out.returncode == 0 and ps_out.stdout.strip().isdigit():
                page_size = int(ps_out.stdout.strip())
        except (OSError, subprocess.TimeoutExpired, ValueError):
            pass  # Keep the 4096 default

        out = shim_run(
            ["vm_stat"],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
        if out.returncode != 0 or not out.stdout:
            return 1024.0

        pages_free = 0
        pages_inactive = 0
        pages_speculative = 0
        pages_purgeable = 0

        for line in out.stdout.splitlines():
            line = line.strip()
            if not line:
                continue

            # Try to parse page size from the first line if not already set correctly
            if "page size of" in line.lower():
                m = re.search(r"page size of (\d+) bytes", line.lower())
                if m:
                    page_size = int(m.group(1))
                continue

            if ":" not in line:
                continue

            label, _, val = line.partition(":")
            # Handle potential quotes and trailing periods
            label = label.strip().strip('"').strip("'")
            val = val.strip().rstrip(".")

            if not val.isdigit():
                continue

            num = int(val)
            if label == "Pages free":
                pages_free = num
            elif label == "Pages inactive":
                pages_inactive = num
            elif label == "Pages speculative":
                pages_speculative = num
            elif label == "Pages purgeable":
                pages_purgeable = num

        # Available memory on macOS: Free + Inactive + Speculative + Purgeable
        # This is the same formula used by modern psutil on macOS.
        available_bytes = (pages_free + pages_inactive + pages_speculative + pages_purgeable) * page_size
        return available_bytes / (1024 * 1024)
    except Exception as e:
        _log.debug("Failed to sample macOS vm_stat: %s", e)
        return 1024.0


def _get_memory_mb() -> tuple[float, float]:
    """Return (rss_mb, available_mb). Uses psutil for cross-platform metrics.

    Fallback strategy when psutil.virtual_memory() is unavailable:
    - macOS: parse ``vm_stat`` (pages_free + pages_inactive + pages_speculative + pages_purgeable) * page_size
    - Linux: ``/proc/meminfo`` MemAvailable field
    - Other: conservative 1024 MB sentinel
    """
    rss_mb = 0.0
    available_mb = 1024.0
    try:
        proc = psutil.Process()
        rss_mb = proc.memory_info().rss / (1024 * 1024)
    except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError, OSError):
        # Fallback for RSS on macOS if psutil fails
        if platform.system() == "Darwin":
            try:
                # ps -o rss= -p PID returns RSS in KB
                out = shim_run(
                    ["ps", "-o", "rss=", "-p", str(os.getpid())],
                    capture_output=True,
                    text=True,
                    timeout=2,
                    check=False,
                )
                if out.returncode == 0 and out.stdout.strip().isdigit():
                    rss_mb = int(out.stdout.strip()) / 1024.0
            except (OSError, subprocess.SubprocessError, ValueError):
                pass
    try:
        vmem = psutil.virtual_memory()
        available_mb = vmem.available / (1024 * 1024)
    except (AttributeError, OSError):
        # psutil unavailable or failed — use OS-native fallback
        system = platform.system()
        if system == "Darwin":
            available_mb = _get_memory_mb_macos_vm_stat()
        elif system == "Linux":
            try:
                with open("/proc/meminfo") as fh:
                    for line in fh:
                        if line.startswith("MemAvailable:"):
                            kb = int(line.split()[1])
                            available_mb = kb / 1024.0
                            break
            except (OSError, ValueError, IndexError):
                pass  # Keep sentinel 1024.0
    return rss_mb, available_mb


def _get_load_avg() -> tuple[float, float, float]:
    """Return (1m, 5m, 15m) load average. Uses psutil for cross-platform support."""
    try:
        return psutil.getloadavg()
    except (AttributeError, OSError):
        return 0.0, 0.0, 0.0


def _sample_resources_native() -> ResourceSnapshot | None:
    """BKM-04: Sample via thegent-resources Rust binary. Returns None if unavailable."""
    from thegent.config import get_settings

    settings = get_settings()
    if not settings.use_native_resources:
        return None
    bin_path = settings.resources_bin
    if not bin_path:
        # Development: crates/target/release/thegent-resources relative to repo root
        mod_path = Path(__file__).resolve()
        repo_root = mod_path.parents[3]  # orchestration -> thegent -> src -> repo
        bin_path = repo_root / "crates" / "target" / "release" / "thegent-resources"
        if not bin_path.is_file():
            return None
        bin_path = str(bin_path)
    try:
        out = shim_run(
            [bin_path],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
        if out.returncode != 0 or not out.stdout:
            return None
        data = json.loads(out.stdout)
        return ResourceSnapshot(
            fd_used=data.get("fd_used", 0),
            fd_limit=data.get("fd_limit", 1024),
            mem_rss_mb=float(data.get("mem_rss_mb", 0)),
            mem_available_mb=float(data.get("mem_available_mb", 0)),
            cpu_count=int(data.get("cpu_count", 1)),
            load_1m=float(data.get("load_1m", 0)),
            load_5m=float(data.get("load_5m", 0)),
            load_15m=float(data.get("load_15m", 0)),
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError, OSError) as e:
        _log.debug("Native resources unavailable: %s", e)
        return None


def sample_resources() -> ResourceSnapshot:
    """Sample current system resources. Cross-platform where possible.

    Uses thegent-resources Rust binary when THGENT_USE_NATIVE_RESOURCES=1;
    otherwise falls back to Python (lsof/vm_stat on macOS, /proc on Linux).
    """
    snapshot = _sample_resources_native()
    if snapshot is not None:
        return snapshot
    fd_used, fd_limit = _get_fd_usage()
    rss_mb, available_mb = _get_memory_mb()
    cpu_count = max(1, multiprocessing.cpu_count())
    load_1m, load_5m, load_15m = _get_load_avg()

    # Extended indices (if psutil available)
    network_bytes_sent = 0
    network_bytes_recv = 0
    network_connections = 0
    disk_read_bytes = 0
    disk_write_bytes = 0
    process_count = 0
    thread_count = 0
    swap_used_mb = 0.0
    swap_total_mb = 0.0

    try:
        proc = psutil.Process()
        net_io = psutil.net_io_counters()
        if net_io:
            network_bytes_sent = net_io.bytes_sent
            network_bytes_recv = net_io.bytes_recv
        network_connections = len(proc.net_connections())

        disk_io = psutil.disk_io_counters()
        if disk_io:
            disk_read_bytes = disk_io.read_bytes
            disk_write_bytes = disk_io.write_bytes

        process_count = len(psutil.pids())
        thread_count = proc.num_threads()

        swap = psutil.swap_memory()
        swap_used_mb = swap.used / (1024 * 1024)
        swap_total_mb = swap.total / (1024 * 1024)
    except Exception:
        pass  # Extended indices optional

    return ResourceSnapshot(
        fd_used=fd_used,
        fd_limit=fd_limit,
        mem_rss_mb=rss_mb,
        mem_available_mb=available_mb,
        cpu_count=cpu_count,
        load_1m=load_1m,
        load_5m=load_5m,
        load_15m=load_15m,
        network_bytes_sent=network_bytes_sent,
        network_bytes_recv=network_bytes_recv,
        network_connections=network_connections,
        disk_read_bytes=disk_read_bytes,
        disk_write_bytes=disk_write_bytes,
        process_count=process_count,
        thread_count=thread_count,
        swap_used_mb=swap_used_mb,
        swap_total_mb=swap_total_mb,
    )


@dataclass
class LimitGateConfig:
    """Configuration for each resource gate. Thresholds are 0.0–1.0 (utilization).

    Uses resource-based limits with safety buffers:
    - Minimum buffer: 5% (hard limit, prevents crashes)
    - Discretionary buffer: 15% (soft limit, allows scaling)
    - No fixed concurrent limit - scales with available resources
    """

    # Resource utilization thresholds (leave buffers)
    fd_utilization_max: float = 0.95  # Block at 95% (5% minimum buffer)
    mem_utilization_max: float = 0.95  # Block at 95% (5% minimum buffer)
    cpu_utilization_max: float = 0.95  # Block at 95% (5% minimum buffer)
    load_per_cpu_max: float = 0.95  # Block when load_1m / cpu_count >= 0.95

    # Discretionary thresholds (15% buffer for scaling)
    fd_utilization_warn: float = 0.85  # Warn/throttle at 85% (15% discretionary buffer)
    mem_utilization_warn: float = 0.85  # Warn/throttle at 85%
    cpu_utilization_warn: float = 0.85  # Warn/throttle at 85%
    load_per_cpu_warn: float = 0.85  # Warn/throttle at 85%

    # Memory thresholds
    mem_available_min_mb: float = 128.0  # Absolute minimum (5% buffer equivalent)
    mem_available_warn_mb: float = 512.0  # Warning threshold (15% buffer equivalent)

    # Dynamic scaling (no fixed max)
    min_slots: int = 1
    max_slots: int = 10000  # Very high ceiling, resource gates will limit
    slots_per_cpu: float = 50.0  # High multiplier, resource gates will throttle
    fd_headroom_per_slot: int = 50  # Est. FDs per agent run
    mem_mb_per_slot: float = 128.0  # Est. MB per agent run

    @classmethod
    def from_dict(cls, d: dict | None) -> "LimitGateConfig":
        """Build config from dict (e.g. settings). Supports concurrency_ prefix."""
        if not d:
            return cls()  # Use defaults with 5%/15% buffers

        def _as_float(value: Any, default: float) -> float:
            try:
                return float(value)
            except (TypeError, ValueError):
                return default

        def _as_int(value: Any, default: int) -> int:
            try:
                return int(value)
            except (TypeError, ValueError):
                return default

        return cls(
            fd_utilization_max=_as_float(
                d.get("concurrency_fd_utilization_max", d.get("fd_utilization_max", 0.95)),
                0.95,
            ),
            fd_utilization_warn=_as_float(
                d.get("concurrency_fd_utilization_warn", d.get("fd_utilization_warn", 0.85)),
                0.85,
            ),
            mem_utilization_max=_as_float(
                d.get("concurrency_mem_utilization_max", d.get("mem_utilization_max", 0.95)),
                0.95,
            ),
            mem_utilization_warn=_as_float(
                d.get("concurrency_mem_utilization_warn", d.get("mem_utilization_warn", 0.85)),
                0.85,
            ),
            cpu_utilization_max=_as_float(
                d.get("concurrency_cpu_utilization_max", d.get("cpu_utilization_max", 0.95)),
                0.95,
            ),
            cpu_utilization_warn=_as_float(
                d.get("concurrency_cpu_utilization_warn", d.get("cpu_utilization_warn", 0.85)),
                0.85,
            ),
            load_per_cpu_max=_as_float(
                d.get("concurrency_load_per_cpu_max", d.get("load_per_cpu_max", 0.95)),
                0.95,
            ),
            load_per_cpu_warn=_as_float(
                d.get("concurrency_load_per_cpu_warn", d.get("load_per_cpu_warn", 0.85)),
                0.85,
            ),
            mem_available_min_mb=_as_float(
                d.get("concurrency_mem_available_min_mb", d.get("mem_available_min_mb", 128.0)),
                128.0,
            ),
            mem_available_warn_mb=_as_float(
                d.get("concurrency_mem_available_warn_mb", d.get("mem_available_warn_mb", 512.0)),
                512.0,
            ),
            min_slots=_as_int(d.get("concurrency_min_slots", d.get("min_slots", 1)), 1),
            max_slots=_as_int(d.get("max_concurrency", d.get("max_slots", 10000)), 10000),
            slots_per_cpu=_as_float(d.get("concurrency_slots_per_cpu", d.get("slots_per_cpu", 50.0)), 50.0),
            fd_headroom_per_slot=_as_int(
                d.get("concurrency_fd_headroom_per_slot", d.get("fd_headroom_per_slot", 50)),
                50,
            ),
            mem_mb_per_slot=_as_float(d.get("concurrency_mem_mb_per_slot", d.get("mem_mb_per_slot", 128.0)), 128.0),
        )


def compute_dynamic_limit(
    snapshot: ResourceSnapshot,
    config: LimitGateConfig | None = None,
) -> tuple[int, dict[str, Any]]:
    """
    Compute max concurrent slots from resource gates. Resource-based scaling:
    - No fixed limit - scales with available resources
    - 5% minimum buffer (hard limit, prevents crashes)
    - 15% discretionary buffer (soft limit, allows scaling)
    - Uses CPU, memory, FD, and load average

    Returns (effective_limit, gate_details).
    """
    cfg = config or LimitGateConfig()
    details: dict[str, Any] = {}

    # Base: CPU-bound slots (scales with CPU count, no hard cap)
    cpu_slots = max(cfg.min_slots, int(snapshot.cpu_count * cfg.slots_per_cpu))
    details["cpu_slots"] = cpu_slots

    # FD gate: calculate slots based on FD utilization with buffers
    fd_slots = cfg.max_slots
    if snapshot.fd_limit > 0 and cfg.fd_headroom_per_slot > 0:
        fd_util = snapshot.fd_used / snapshot.fd_limit
        details["fd_utilization"] = fd_util

        if fd_util >= cfg.fd_utilization_max:
            # At 95% (5% buffer) - hard stop
            fd_slots = 0
            details["fd_gate"] = "blocked_5pct_buffer"
            _log.debug(
                "gate blocked: gate=fd_count value=%.2f limit=%.2f",
                fd_util,
                cfg.fd_utilization_max,
            )
        elif fd_util >= cfg.fd_utilization_warn:
            # At 85% (15% buffer) - throttle but allow some growth
            headroom = int((cfg.fd_utilization_max - fd_util) * snapshot.fd_limit)
            fd_slots = max(0, headroom // cfg.fd_headroom_per_slot)
            details["fd_gate"] = "throttled_15pct_buffer"
            _log.debug(
                "gate passed: gate=fd_count value=%.2f limit=%.2f",
                fd_util,
                cfg.fd_utilization_warn,
            )
        else:
            # Below 85% - scale freely
            headroom = int((cfg.fd_utilization_max - fd_util) * snapshot.fd_limit)
            fd_slots = max(0, headroom // cfg.fd_headroom_per_slot)
            details["fd_gate"] = "normal"
            _log.debug(
                "gate passed: gate=fd_count value=%.2f limit=%.2f",
                fd_util,
                cfg.fd_utilization_warn,
            )
        details["fd_slots"] = fd_slots

    # Memory gate: calculate slots based on available memory with buffers
    mem_slots = cfg.max_slots
    if cfg.mem_mb_per_slot > 0:
        # Calculate memory utilization (approximate)
        total_mem_mb = snapshot.mem_available_mb + snapshot.mem_rss_mb
        mem_util = snapshot.mem_rss_mb / total_mem_mb if total_mem_mb > 0 else 0.0
        details["mem_utilization"] = mem_util
        details["mem_available_mb"] = snapshot.mem_available_mb

        if snapshot.mem_available_mb < cfg.mem_available_min_mb:
            # Below 5% buffer equivalent - hard stop
            mem_slots = 0
            details["mem_gate"] = "blocked_5pct_buffer"
            _log.debug(
                "gate blocked: gate=memory_mb value=%.2f limit=%.2f",
                snapshot.mem_available_mb,
                cfg.mem_available_min_mb,
            )
        elif snapshot.mem_available_mb < cfg.mem_available_warn_mb:
            # Below 15% buffer equivalent - throttle
            mem_slots = max(0, int((snapshot.mem_available_mb - cfg.mem_available_min_mb) / cfg.mem_mb_per_slot))
            details["mem_gate"] = "throttled_15pct_buffer"
            _log.debug(
                "gate passed: gate=memory_mb value=%.2f limit=%.2f",
                snapshot.mem_available_mb,
                cfg.mem_available_warn_mb,
            )
        else:
            # Above 15% buffer - scale freely
            mem_slots = max(0, int((snapshot.mem_available_mb - cfg.mem_available_min_mb) / cfg.mem_mb_per_slot))
            details["mem_gate"] = "normal"
            _log.debug(
                "gate passed: gate=memory_mb value=%.2f limit=%.2f",
                snapshot.mem_available_mb,
                cfg.mem_available_warn_mb,
            )
        details["mem_slots"] = mem_slots

    # Load gate: CPU load average with buffers
    load_slots = cfg.max_slots
    if snapshot.cpu_count > 0 and snapshot.load_1m > 0:
        load_per_cpu = snapshot.load_1m / snapshot.cpu_count
        details["load_per_cpu"] = load_per_cpu

        if load_per_cpu >= cfg.load_per_cpu_max:
            # At 95% (5% buffer) - hard stop
            load_slots = 0
            details["load_gate"] = "blocked_5pct_buffer"
            _log.debug(
                "gate blocked: gate=load_avg_1m value=%.2f limit=%.2f",
                load_per_cpu,
                cfg.load_per_cpu_max,
            )
        elif load_per_cpu >= cfg.load_per_cpu_warn:
            # At 85% (15% buffer) - throttle
            scale = max(0, (cfg.load_per_cpu_max - load_per_cpu) / (cfg.load_per_cpu_max - cfg.load_per_cpu_warn))
            load_slots = max(0, int(cpu_slots * scale))
            details["load_gate"] = "throttled_15pct_buffer"
            _log.debug(
                "gate passed: gate=load_avg_1m value=%.2f limit=%.2f",
                load_per_cpu,
                cfg.load_per_cpu_warn,
            )
        else:
            # Below 85% - scale freely
            load_slots = cpu_slots
            details["load_gate"] = "normal"
            _log.debug(
                "gate passed: gate=load_avg_1m value=%.2f limit=%.2f",
                load_per_cpu,
                cfg.load_per_cpu_warn,
            )
        details["load_slots"] = load_slots

    # Effective limit = min of all gates (most restrictive)
    # No hard cap - resource gates provide the limits
    effective = min(cpu_slots, fd_slots, mem_slots, load_slots)
    effective = max(cfg.min_slots, effective)  # Only enforce minimum, no maximum
    details["effective"] = effective
    details["resource_based"] = True
    details["buffers"] = {
        "minimum_5pct": "Hard limit prevents crashes",
        "discretionary_15pct": "Soft limit allows scaling",
    }

    return effective, details


class HysteresisController:
    """WP-Y6: Prevents thrashing by using upper/lower thresholds and dwell time.

    Uses settings from ThegentSettings (mapped to THGENT_HYSTERESIS_* env vars).
    """

    def __init__(
        self,
        upper_threshold: float | None = None,
        lower_threshold: float | None = None,
        dwell_time_s: int | None = None,
    ) -> None:
        from thegent.config import get_settings

        settings = get_settings()
        self.upper_threshold = upper_threshold if upper_threshold is not None else settings.hysteresis_upper
        self.lower_threshold = lower_threshold if lower_threshold is not None else settings.hysteresis_lower
        self.dwell_time_s = dwell_time_s if dwell_time_s is not None else settings.hysteresis_dwell
        self.last_scale_time = 0.0

    def get_limit(self, current_limit: int, running_count: int, target_limit: int) -> int:
        """
        Apply hysteresis to determine the new limit.
        Returns the new limit (either changed or held).
        """
        import time

        now = time.time()
        if now - self.last_scale_time < self.dwell_time_s:
            return current_limit

        utilization = running_count / current_limit if current_limit > 0 else 1.0

        if utilization > self.upper_threshold and target_limit > current_limit:
            # Scale UP
            self.last_scale_time = now
            return target_limit
        if utilization < self.lower_threshold and target_limit < current_limit:
            # Scale DOWN
            self.last_scale_time = now
            return target_limit

        # HOLD in dead zone
        return current_limit


@dataclass
class OwnerStats:
    """Per-owner usage statistics for fairness tracking."""

    owner: str
    active_count: int = 0
    total_runs: int = 0
    total_elapsed_ms: float = 0.0

    @property
    def avg_elapsed_ms(self) -> float:
        """Average elapsed time per completed run in milliseconds."""
        if self.total_runs == 0:
            return 0.0
        return self.total_elapsed_ms / self.total_runs

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dict for CLI/MCP display."""
        return {
            "owner": self.owner,
            "active_count": self.active_count,
            "total_runs": self.total_runs,
            "total_elapsed_ms": self.total_elapsed_ms,
            "avg_elapsed_ms": self.avg_elapsed_ms,
        }


class UsageTracker:
    """Thread-safe per-owner resource usage tracker for fairness enforcement.

    Tracks active concurrency and historical run statistics per owner
    (agent id, user, project, etc.) so that ConcurrencyController can
    surface fairness data and optionally enforce per-owner quotas.

    All public methods are thread-safe via a single ``threading.Lock``
    (not asyncio.Lock — ConcurrencyController is synchronous).
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._stats: dict[str, OwnerStats] = {}

    def _ensure(self, owner: str) -> OwnerStats:
        """Return (creating if needed) the OwnerStats entry. Must hold _lock."""
        if owner not in self._stats:
            self._stats[owner] = OwnerStats(owner=owner)
        return self._stats[owner]

    def record_start(self, owner: str, run_id: str) -> None:  # noqa: ARG002  (run_id reserved for future per-run tracking)
        """Increment active count for *owner* at the start of a run.

        Args:
            owner:  Identifier for the owning agent/user/project.
            run_id: Unique identifier for this run (reserved; logged for tracing).
        """
        with self._lock:
            stats = self._ensure(owner)
            stats.active_count += 1
            _log.debug("usage_tracker: start owner=%s run_id=%s active=%d", owner, run_id, stats.active_count)

    def record_end(self, owner: str, run_id: str, elapsed_ms: float) -> None:  # noqa: ARG002
        """Decrement active count and accumulate elapsed time for *owner*.

        Args:
            owner:      Identifier for the owning agent/user/project.
            run_id:     Unique identifier for this run.
            elapsed_ms: Wall-clock duration of the run in milliseconds.
        """
        with self._lock:
            stats = self._ensure(owner)
            stats.active_count = max(0, stats.active_count - 1)
            stats.total_runs += 1
            stats.total_elapsed_ms += elapsed_ms
            _log.debug(
                "usage_tracker: end owner=%s run_id=%s active=%d total=%d elapsed_ms=%.1f",
                owner,
                run_id,
                stats.active_count,
                stats.total_runs,
                elapsed_ms,
            )

    def get_stats(self, owner: str) -> OwnerStats:
        """Return a *snapshot* of the OwnerStats for *owner*.

        Returns a zero-initialized OwnerStats if *owner* has never been seen.
        The returned object is a copy — mutations do not affect internal state.
        """
        with self._lock:
            existing = self._stats.get(owner)
            if existing is None:
                return OwnerStats(owner=owner)
            # Return a shallow copy so callers can't mutate internal state.
            return OwnerStats(
                owner=existing.owner,
                active_count=existing.active_count,
                total_runs=existing.total_runs,
                total_elapsed_ms=existing.total_elapsed_ms,
            )

    def get_all_stats(self) -> dict[str, OwnerStats]:
        """Return a snapshot of all tracked owners as ``{owner: OwnerStats}``."""
        with self._lock:
            return {
                owner: OwnerStats(
                    owner=s.owner,
                    active_count=s.active_count,
                    total_runs=s.total_runs,
                    total_elapsed_ms=s.total_elapsed_ms,
                )
                for owner, s in self._stats.items()
            }

    def reset(self, owner: str | None = None) -> None:
        """Reset statistics for a specific *owner* or for all owners (if None).

        Primarily useful for testing; production code should generally not call this.
        """
        with self._lock:
            if owner is None:
                self._stats.clear()
            elif owner in self._stats:
                del self._stats[owner]


# Module-level singleton so that ConcurrencyController instances in the same
# process share usage data without requiring explicit dependency injection.
_usage_tracker: UsageTracker = UsageTracker()


def get_usage_tracker() -> UsageTracker:
    """Return the module-level UsageTracker singleton."""
    return _usage_tracker


# ---------------------------------------------------------------------------
# Soft deadline support (swarm-soft-deadlines)
# ---------------------------------------------------------------------------


@dataclass
class SoftDeadline:
    """Preferred completion time for a single agent run.

    A soft deadline records *when* a run was registered and what its
    preferred budget is.  It does NOT cancel the run — violation only
    triggers structured log events via :class:`DeadlineMonitor`.

    Attributes:
        run_id:       Unique identifier of the run (matches registry token).
        deadline_ts:  Budget in seconds from the moment the run started.
        warn_at_pct:  Fraction of ``deadline_ts`` at which a WARNING is
                      emitted (default 0.8 → 80 % of budget elapsed).
        _started_at:  Wall-clock timestamp (``time.time()``) recorded when
                      the deadline is registered.
        _warned:      Set to ``True`` after the WARNING has been emitted to
                      avoid duplicate log spam on subsequent checks.
        _overdue:     Set to ``True`` after the ERROR has been emitted.
    """

    run_id: str
    deadline_ts: float
    warn_at_pct: float = 0.8
    _started_at: float = field(default_factory=time.time)
    _warned: bool = field(default=False)
    _overdue: bool = field(default=False)

    def elapsed(self) -> float:
        """Return seconds elapsed since this deadline was registered."""
        return time.time() - self._started_at

    def warn_threshold(self) -> float:
        """Return the elapsed seconds at which a WARNING should be emitted."""
        return self.deadline_ts * self.warn_at_pct

    def is_warn_zone(self) -> bool:
        """Return ``True`` when elapsed has passed the warn threshold."""
        return self.elapsed() >= self.warn_threshold()

    def is_overdue(self) -> bool:
        """Return ``True`` when elapsed has passed the full soft deadline."""
        return self.elapsed() >= self.deadline_ts


_DEADLINE_MONITOR_INTERVAL_DEFAULT: float = 5.0  # seconds


class DeadlineMonitor:
    """Background daemon thread that checks active runs against soft deadlines.

    Emits structured log events via structlog (falls back to stdlib logging):
    - WARNING when a run's elapsed time exceeds ``deadline_ts * warn_at_pct``
    - ERROR   when a run's elapsed time exceeds ``deadline_ts``

    Soft deadlines **never cancel** tasks; they only emit log events.

    Usage::

        monitor = DeadlineMonitor()
        monitor.start()

        dl = monitor.register("run-123", deadline_ts=300.0, warn_at_pct=0.8)
        # ... run proceeds ...
        monitor.unregister("run-123")

        monitor.stop()

    The monitor thread is a daemon thread and will stop automatically when the
    main process exits.  Call :meth:`stop` for graceful shutdown.
    """

    def __init__(self, interval_s: float = _DEADLINE_MONITOR_INTERVAL_DEFAULT) -> None:
        """Create a DeadlineMonitor.

        Args:
            interval_s: How often (in seconds) to scan all registered deadlines.
                        Defaults to 5 s; lower values increase precision at the
                        cost of CPU overhead.
        """
        self._interval_s = interval_s
        self._deadlines: dict[str, SoftDeadline] = {}
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def register(
        self,
        run_id: str,
        deadline_ts: float,
        warn_at_pct: float = 0.8,
    ) -> SoftDeadline:
        """Register a soft deadline for *run_id*.

        If *run_id* is already registered the existing entry is replaced.

        Args:
            run_id:       Unique run identifier.
            deadline_ts:  Budget in seconds from now.
            warn_at_pct:  Fraction of budget at which to warn (default 0.8).

        Returns:
            The newly created :class:`SoftDeadline` instance.
        """
        dl = SoftDeadline(run_id=run_id, deadline_ts=deadline_ts, warn_at_pct=warn_at_pct)
        with self._lock:
            self._deadlines[run_id] = dl
        _slog.debug(  # type: ignore[call-arg]  # pyright: ignore[reportCallIssue]
            "soft_deadline registered",
            run_id=run_id,  # pyright: ignore[reportCallIssue]
            deadline_ts=deadline_ts,  # pyright: ignore[reportCallIssue]
            warn_at_pct=warn_at_pct,  # pyright: ignore[reportCallIssue]
        ) if hasattr(_slog, "debug") else _log.debug(
            "soft_deadline registered: run_id=%s deadline_ts=%.1f warn_at_pct=%.2f",
            run_id,
            deadline_ts,
            warn_at_pct,
        )
        return dl

    def unregister(self, run_id: str) -> None:
        """Remove the soft deadline for *run_id* (e.g. when a run completes).

        No-op if *run_id* was never registered.
        """
        with self._lock:
            self._deadlines.pop(run_id, None)
        _log.debug("soft_deadline unregistered: run_id=%s", run_id)

    def active_deadlines(self) -> dict[str, SoftDeadline]:
        """Return a shallow copy of the current deadline registry."""
        with self._lock:
            return dict(self._deadlines)

    # ------------------------------------------------------------------
    # Thread lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start the background monitor daemon thread.

        Idempotent — calling :meth:`start` while already running is a no-op.
        """
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run,
            name="DeadlineMonitor",
            daemon=True,
        )
        self._thread.start()
        _log.debug("DeadlineMonitor: started (interval_s=%.1f)", self._interval_s)

    def stop(self, timeout: float = 10.0) -> None:
        """Request graceful shutdown of the monitor thread.

        Sets the stop event and waits up to *timeout* seconds for the thread
        to finish.  Safe to call even if the monitor was never started.

        Args:
            timeout: Maximum seconds to wait for the thread to exit.
        """
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=timeout)
            self._thread = None
        _log.debug("DeadlineMonitor: stopped")

    def is_running(self) -> bool:
        """Return ``True`` if the monitor thread is alive."""
        return self._thread is not None and self._thread.is_alive()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _run(self) -> None:
        """Main loop executed by the daemon thread."""
        while not self._stop_event.wait(timeout=self._interval_s):
            self._check_all()

    def _check_all(self) -> None:
        """Iterate over all registered deadlines and emit log events as needed."""
        with self._lock:
            deadlines = list(self._deadlines.values())

        for dl in deadlines:
            elapsed = dl.elapsed()

            if dl.is_overdue() and not dl._overdue:  # noqa: SLF001 -- DeadlineMonitor owns the mutable flag
                dl._overdue = True  # noqa: SLF001 -- DeadlineMonitor owns the mutable flag
                self._emit_overdue(dl, elapsed)
            elif dl.is_warn_zone() and not dl._warned:  # noqa: SLF001 -- DeadlineMonitor owns the mutable flag
                dl._warned = True  # noqa: SLF001 -- DeadlineMonitor owns the mutable flag
                self._emit_warn(dl, elapsed)

    @staticmethod
    def _emit_warn(dl: SoftDeadline, elapsed: float) -> None:
        """Emit a structured WARNING when a run is approaching its soft deadline."""
        pct = int(dl.warn_at_pct * 100)
        msg = (
            f"soft_deadline approaching: run_id={dl.run_id} "
            f"elapsed={elapsed:.1f}s deadline={dl.deadline_ts:.1f}s "
            f"({pct}% threshold reached)"
        )
        try:
            _slog.warning(  # type: ignore[union-attr,call-arg]  # pyright: ignore[reportCallIssue]
                "soft_deadline_approaching",
                run_id=dl.run_id,  # pyright: ignore[reportCallIssue]
                elapsed_s=round(elapsed, 2),  # pyright: ignore[reportCallIssue]
                deadline_s=dl.deadline_ts,  # pyright: ignore[reportCallIssue]
                warn_at_pct=dl.warn_at_pct,  # pyright: ignore[reportCallIssue]
            )
        except Exception:
            _log.warning(msg)

    @staticmethod
    def _emit_overdue(dl: SoftDeadline, elapsed: float) -> None:
        """Emit a structured ERROR when a run has exceeded its soft deadline."""
        msg = f"soft_deadline exceeded: run_id={dl.run_id} elapsed={elapsed:.1f}s deadline={dl.deadline_ts:.1f}s"
        try:
            _slog.error(  # type: ignore[union-attr,call-arg]  # pyright: ignore[reportCallIssue]
                "soft_deadline_exceeded",
                run_id=dl.run_id,  # pyright: ignore[reportCallIssue]
                elapsed_s=round(elapsed, 2),  # pyright: ignore[reportCallIssue]
                deadline_s=dl.deadline_ts,  # pyright: ignore[reportCallIssue]
                overdue_by_s=round(elapsed - dl.deadline_ts, 2),  # pyright: ignore[reportCallIssue]
            )
        except Exception:
            _log.error(msg)


# Module-level singleton so the monitor can be shared across calls to
# ConcurrencyController.acquire() within the same process.
_deadline_monitor: DeadlineMonitor = DeadlineMonitor()
_deadline_monitor.start()


def get_deadline_monitor() -> DeadlineMonitor:
    """Return the module-level :class:`DeadlineMonitor` singleton.

    The singleton is started automatically on first module import.
    Use :func:`get_deadline_monitor` to register and unregister deadlines
    from any part of the system.
    """
    return _deadline_monitor
