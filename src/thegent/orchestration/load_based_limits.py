"""WP-5001: Load-based concurrency limits (FD, memory, CPU, load average).

Replaces fixed max_concurrency with dynamic, resource-aware limits that scale
as a load balancer: allow more slots when system headroom exists, throttle when
gates are near capacity.

BKM-04: When THGENT_USE_NATIVE_RESOURCES=1, uses thegent-resources Rust binary
instead of psutil. Set THGENT_RESOURCES_BIN to override path.
"""

import json
import logging
import multiprocessing
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import psutil

_log = logging.getLogger(__name__)


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
    """Return (used_fds, limit). Uses psutil (num_fds on Unix, fallback to resource limit)."""
    try:
        proc = psutil.Process()
        used = proc.num_fds()
        limit = 1024
        try:
            import resource

            soft, _hard = resource.getrlimit(resource.RLIMIT_NOFILE)
            if soft != resource.RLIM_INFINITY:
                limit = soft
        except (ImportError, AttributeError, ValueError):
            pass
        return used, limit
    except (AttributeError, OSError, psutil.NoSuchProcess, psutil.AccessDenied):
        try:
            import resource

            soft, _hard = resource.getrlimit(resource.RLIMIT_NOFILE)
            limit = soft if soft != resource.RLIM_INFINITY else 1024
        except (ImportError, AttributeError, ValueError):
            limit = 1024
        return 0, limit


def _get_memory_mb() -> tuple[float, float]:
    """Return (rss_mb, available_mb). Uses psutil for cross-platform metrics."""
    rss_mb = 0.0
    available_mb = 512.0
    try:
        proc = psutil.Process()
        rss_mb = proc.memory_info().rss / (1024 * 1024)
    except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
        pass
    try:
        vmem = psutil.virtual_memory()
        available_mb = vmem.available / (1024 * 1024)
    except (AttributeError, OSError):
        pass
    return rss_mb, available_mb


def _get_load_avg() -> tuple[float, float, float]:
    """Return (1m, 5m, 15m) load average. Uses psutil for cross-platform support."""
    try:
        return psutil.getloadavg()
    except (AttributeError, OSError):
        return 0.0, 0.0, 0.0


def _sample_resources_native() -> ResourceSnapshot | None:
    """BKM-04: Sample via thegent-resources Rust binary. Returns None if unavailable."""
    from thegent.config import ThegentSettings

    settings = ThegentSettings()
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
        out = subprocess.run(
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
        network_connections = len(proc.connections())
        
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
        """Build config from dict (e.g. settings)."""
        if not d:
            return cls()  # Use defaults with 5%/15% buffers
        return cls(
            fd_utilization_max=d.get("fd_utilization_max", 0.95),
            fd_utilization_warn=d.get("fd_utilization_warn", 0.85),
            mem_utilization_max=d.get("mem_utilization_max", 0.95),
            mem_utilization_warn=d.get("mem_utilization_warn", 0.85),
            cpu_utilization_max=d.get("cpu_utilization_max", 0.95),
            cpu_utilization_warn=d.get("cpu_utilization_warn", 0.85),
            load_per_cpu_max=d.get("load_per_cpu_max", 0.95),
            load_per_cpu_warn=d.get("load_per_cpu_warn", 0.85),
            mem_available_min_mb=d.get("mem_available_min_mb", 128.0),
            mem_available_warn_mb=d.get("mem_available_warn_mb", 512.0),
            min_slots=d.get("min_slots", 1),
            max_slots=d.get("max_slots", 10000),
            slots_per_cpu=d.get("slots_per_cpu", 50.0),
            fd_headroom_per_slot=d.get("fd_headroom_per_slot", 50),
            mem_mb_per_slot=d.get("mem_mb_per_slot", 128.0),
        )


def compute_dynamic_limit(
    snapshot: ResourceSnapshot,
    config: LimitGateConfig | None = None,
    running_count: int = 0,
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
        elif fd_util >= cfg.fd_utilization_warn:
            # At 85% (15% buffer) - throttle but allow some growth
            headroom = int((cfg.fd_utilization_max - fd_util) * snapshot.fd_limit)
            fd_slots = max(0, headroom // cfg.fd_headroom_per_slot)
            details["fd_gate"] = "throttled_15pct_buffer"
        else:
            # Below 85% - scale freely
            headroom = int((cfg.fd_utilization_max - fd_util) * snapshot.fd_limit)
            fd_slots = max(0, headroom // cfg.fd_headroom_per_slot)
            details["fd_gate"] = "normal"
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
        elif snapshot.mem_available_mb < cfg.mem_available_warn_mb:
            # Below 15% buffer equivalent - throttle
            mem_slots = max(0, int((snapshot.mem_available_mb - cfg.mem_available_min_mb) / cfg.mem_mb_per_slot))
            details["mem_gate"] = "throttled_15pct_buffer"
        else:
            # Above 15% buffer - scale freely
            mem_slots = max(0, int((snapshot.mem_available_mb - cfg.mem_available_min_mb) / cfg.mem_mb_per_slot))
            details["mem_gate"] = "normal"
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
        elif load_per_cpu >= cfg.load_per_cpu_warn:
            # At 85% (15% buffer) - throttle
            scale = max(0, (cfg.load_per_cpu_max - load_per_cpu) / (cfg.load_per_cpu_max - cfg.load_per_cpu_warn))
            load_slots = max(0, int(cpu_slots * scale))
            details["load_gate"] = "throttled_15pct_buffer"
        else:
            # Below 85% - scale freely
            load_slots = cpu_slots
            details["load_gate"] = "normal"
        details["load_slots"] = load_slots

    # Effective limit = min of all gates (most restrictive)
    # No hard cap - resource gates provide the limits
    effective = min(cpu_slots, fd_slots, mem_slots, load_slots)
    effective = max(cfg.min_slots, effective)  # Only enforce minimum, no maximum
    details["effective"] = effective
    details["resource_based"] = True
    details["buffers"] = {
        "minimum_5pct": "Hard limit prevents crashes",
        "discretionary_15pct": "Soft limit allows scaling"
    }

    return effective, details


class HysteresisController:
    """WP-Y6: Prevents thrashing by using upper/lower thresholds and dwell time."""

    def __init__(self, upper_threshold: float = 0.8, lower_threshold: float = 0.4, dwell_time_s: int = 30) -> None:

        self.upper_threshold = upper_threshold
        self.lower_threshold = lower_threshold
        self.dwell_time_s = dwell_time_s
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
