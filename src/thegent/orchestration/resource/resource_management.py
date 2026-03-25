"""Advanced resource management with extended indices, prediction, and harness modeling.

Features:
- Extended resource indices (CPU, memory, FD, network, disk, GPU, etc.)
- Statistical distributions (min, avg, peak, stddev, percentiles) for all resources
- Prediction engine for forecasting resource needs
- Harness card system for modeling harness usage with statistical models
- Leak detection (memory leaks, FD leaks, child process leaks)
- Child process and thread tracking
- Bottleneck detection and analysis
- Speculative execution strategies
- Work chunking and parallelization
"""

import orjson as json
import logging
import statistics
import time
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import psutil

_log = logging.getLogger(__name__)


@dataclass
class ResourceDistribution:
    """Statistical distribution for a resource metric."""

    min: float = 0.0
    avg: float = 0.0
    peak: float = 0.0
    stddev: float = 0.0
    p50: float = 0.0  # Median
    p95: float = 0.0
    p99: float = 0.0
    count: int = 0  # Sample count

    def update(self, value: float) -> None:
        """Update distribution with a new value."""
        if self.count == 0:
            self.min = self.avg = self.peak = self.p50 = value
            self.count = 1
            return

        self.count += 1
        self.min = min(self.min, value)
        self.peak = max(self.peak, value)

        # Running average
        self.avg = ((self.avg * (self.count - 1)) + value) / self.count

        # Note: stddev, p50, p95, p99 require full history - computed separately

    def compute_stats(self, values: list[float]) -> None:
        """Compute full statistics from a list of values."""
        if not values:
            return

        self.count = len(values)
        self.min = min(values)
        self.peak = max(values)
        self.avg = statistics.mean(values)

        if len(values) > 1:
            self.stddev = statistics.stdev(values) if len(values) > 1 else 0.0

        sorted_vals = sorted(values)
        self.p50 = sorted_vals[int(len(sorted_vals) * 0.50)]
        self.p95 = sorted_vals[int(len(sorted_vals) * 0.95)] if len(sorted_vals) > 1 else sorted_vals[0]
        self.p99 = sorted_vals[int(len(sorted_vals) * 0.99)] if len(sorted_vals) > 1 else sorted_vals[-1]


@dataclass
class LeakMetrics:
    """Metrics for detecting resource leaks."""

    memory_leak_rate_mb_per_hour: float = 0.0  # MB/hour growth
    fd_leak_rate_per_hour: float = 0.0  # FD/hour growth
    child_process_leak_rate_per_hour: float = 0.0  # Processes/hour growth
    thread_leak_rate_per_hour: float = 0.0  # Threads/hour growth
    socket_leak_rate_per_hour: float = 0.0  # Sockets/hour growth

    memory_leak_detected: bool = False
    fd_leak_detected: bool = False
    child_process_leak_detected: bool = False

    leak_severity: str = "none"  # none, low, medium, high, critical


@dataclass
class ExtendedResourceSnapshot:
    """Extended resource snapshot with comprehensive system metrics."""

    # Core resources (existing)
    fd_used: int = 0
    fd_limit: int = 0
    mem_rss_mb: float = 0.0
    mem_available_mb: float = 0.0
    cpu_count: int = 1
    load_1m: float = 0.0
    load_5m: float = 0.0
    load_15m: float = 0.0

    # Extended indices
    network_bytes_sent: int = 0
    network_bytes_recv: int = 0
    network_connections: int = 0
    disk_read_bytes: int = 0
    disk_write_bytes: int = 0
    disk_io_wait: float = 0.0
    process_count: int = 0
    thread_count: int = 0
    socket_count: int = 0
    swap_used_mb: float = 0.0
    swap_total_mb: float = 0.0
    cache_hit_rate: float = 0.0  # Approximate from page cache

    # Child process tracking
    child_process_count: int = 0
    child_process_memory_mb: float = 0.0
    child_process_fd_count: int = 0
    zombie_process_count: int = 0

    # Thread tracking
    active_thread_count: int = 0
    blocked_thread_count: int = 0

    # Network detail
    tcp_connections: int = 0
    udp_connections: int = 0
    unix_sockets: int = 0
    established_connections: int = 0

    # System-level metrics
    context_switches: int = 0
    interrupts: int = 0
    page_faults: int = 0

    # GPU (if available)
    gpu_available: bool = False
    gpu_memory_used_mb: float = 0.0
    gpu_memory_total_mb: float = 0.0
    gpu_utilization: float = 0.0

    # Leak detection
    leak_metrics: LeakMetrics = field(default_factory=LeakMetrics)

    # Per-harness resource usage (if tracked)
    harness_usage: dict[str, dict[str, Any]] = field(default_factory=dict)

    timestamp: float = field(default_factory=time.time)


@dataclass
class HarnessCard:
    """Model for individual harness type resource usage with statistical distributions."""

    harness_type: str  # codex, claude, droid, cursor-agent

    # Memory: statistical distribution
    memory_base: ResourceDistribution = field(default_factory=ResourceDistribution)
    memory_per_session: ResourceDistribution = field(default_factory=ResourceDistribution)

    # File descriptors: statistical distribution
    fd_base: ResourceDistribution = field(default_factory=ResourceDistribution)
    fd_per_session: ResourceDistribution = field(default_factory=ResourceDistribution)

    # CPU: statistical distribution
    cpu_base: ResourceDistribution = field(default_factory=ResourceDistribution)
    cpu_per_session: ResourceDistribution = field(default_factory=ResourceDistribution)

    # Child processes: statistical distribution
    child_process_base: ResourceDistribution = field(default_factory=ResourceDistribution)
    child_process_per_session: ResourceDistribution = field(default_factory=ResourceDistribution)

    # Threads: statistical distribution
    thread_base: ResourceDistribution = field(default_factory=ResourceDistribution)
    thread_per_session: ResourceDistribution = field(default_factory=ResourceDistribution)

    # Network: statistical distribution
    network_bytes_per_request: ResourceDistribution = field(default_factory=ResourceDistribution)
    network_connections_per_session: ResourceDistribution = field(default_factory=ResourceDistribution)

    # Sockets: statistical distribution
    socket_base: ResourceDistribution = field(default_factory=ResourceDistribution)
    socket_per_session: ResourceDistribution = field(default_factory=ResourceDistribution)

    # Latency: statistical distribution
    latency: ResourceDistribution = field(default_factory=ResourceDistribution)

    # Leak rates
    leak_rates: LeakMetrics = field(default_factory=LeakMetrics)

    # Isolation vs multi-harness
    isolation_overhead: float = 1.0  # 1.0 = no overhead, >1.0 = overhead when isolated
    multi_harness_efficiency: float = 0.9  # Efficiency when running multiple harnesses

    # Historical usage patterns
    usage_history: deque = field(default_factory=lambda: deque(maxlen=1000))

    def estimate_resources(
        self, session_count: int, isolated: bool = False, use_peak: bool = False, use_p95: bool = True
    ) -> dict[str, Any]:
        """Estimate resource usage for N sessions using statistical distributions.

        Args:
            session_count: Number of sessions
            isolated: Whether sessions run in isolation
            use_peak: Use peak values instead of average (conservative)
            use_p95: Use p95 values instead of average (recommended)
        """
        overhead = self.isolation_overhead if isolated else 1.0
        efficiency = self.multi_harness_efficiency if not isolated else 1.0

        # Select value from distribution
        def _select_value(dist: ResourceDistribution) -> float:
            if use_peak:
                return dist.peak
            if use_p95 and dist.p95 > 0:
                return dist.p95
            return dist.avg

        mem_base = _select_value(self.memory_base)
        mem_per_session = _select_value(self.memory_per_session)
        fd_base = _select_value(self.fd_base)
        fd_per_session = _select_value(self.fd_per_session)
        cpu_base = _select_value(self.cpu_base)
        cpu_per_session = _select_value(self.cpu_per_session)
        child_base = _select_value(self.child_process_base)
        child_per_session = _select_value(self.child_process_per_session)
        thread_base = _select_value(self.thread_base)
        thread_per_session = _select_value(self.thread_per_session)
        socket_base = _select_value(self.socket_base)
        socket_per_session = _select_value(self.socket_per_session)
        network_per_req = _select_value(self.network_bytes_per_request)
        network_conn_per_session = _select_value(self.network_connections_per_session)
        latency_p95 = _select_value(self.latency) if self.latency.p95 > 0 else self.latency.avg

        return {
            "memory_mb": {
                "min": (mem_base + session_count * self.memory_per_session.min) * overhead,
                "avg": (mem_base + session_count * mem_per_session) * overhead,
                "peak": (self.memory_base.peak + session_count * self.memory_per_session.peak) * overhead,
                "p95": (mem_base + session_count * self.memory_per_session.p95) * overhead,
            },
            "fd_count": {
                "min": int(fd_base + session_count * self.fd_per_session.min),
                "avg": int(fd_base + session_count * fd_per_session),
                "peak": int(self.fd_base.peak + session_count * self.fd_per_session.peak),
                "p95": int(fd_base + session_count * self.fd_per_session.p95),
            },
            "cpu_percent": {
                "min": (cpu_base + session_count * self.cpu_per_session.min) * overhead / efficiency,
                "avg": (cpu_base + session_count * cpu_per_session) * overhead / efficiency,
                "peak": (self.cpu_base.peak + session_count * self.cpu_per_session.peak) * overhead / efficiency,
                "p95": (cpu_base + session_count * self.cpu_per_session.p95) * overhead / efficiency,
            },
            "child_process_count": {
                "min": int(child_base + session_count * self.child_process_per_session.min),
                "avg": int(child_base + session_count * child_per_session),
                "peak": int(self.child_process_base.peak + session_count * self.child_process_per_session.peak),
                "p95": int(child_base + session_count * self.child_process_per_session.p95),
            },
            "thread_count": {
                "min": int(thread_base + session_count * self.thread_per_session.min),
                "avg": int(thread_base + session_count * thread_per_session),
                "peak": int(self.thread_base.peak + session_count * self.thread_per_session.peak),
                "p95": int(thread_base + session_count * self.thread_per_session.p95),
            },
            "socket_count": {
                "min": int(socket_base + session_count * self.socket_per_session.min),
                "avg": int(socket_base + session_count * socket_per_session),
                "peak": int(self.socket_base.peak + session_count * self.socket_per_session.peak),
                "p95": int(socket_base + session_count * self.socket_per_session.p95),
            },
            "network_bytes": {
                "min": int(session_count * self.network_bytes_per_request.min),
                "avg": int(session_count * network_per_req),
                "peak": int(session_count * self.network_bytes_per_request.peak),
                "p95": int(session_count * self.network_bytes_per_request.p95),
            },
            "network_connections": {
                "min": int(session_count * self.network_connections_per_session.min),
                "avg": int(session_count * network_conn_per_session),
                "peak": int(session_count * self.network_connections_per_session.peak),
                "p95": int(session_count * self.network_connections_per_session.p95),
            },
            "estimated_latency_p95_ms": latency_p95 * (1.0 / efficiency),
            "leak_rates": {
                "memory_mb_per_hour": self.leak_rates.memory_leak_rate_mb_per_hour * session_count,
                "fd_per_hour": self.leak_rates.fd_leak_rate_per_hour * session_count,
                "child_process_per_hour": self.leak_rates.child_process_leak_rate_per_hour * session_count,
            },
        }


class ResourcePredictionEngine:
    """Predict future resource needs based on historical patterns."""

    def __init__(self, history_file: Path | None = None) -> None:
        self.history_file = history_file or Path.home() / ".thegent" / "resource_history.jsonl"
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self.history: deque[ExtendedResourceSnapshot] = deque(maxlen=1000)
        self._load_history()

    def _load_history(self) -> None:
        """Load historical resource snapshots."""
        if not self.history_file.exists():
            return
        try:
            with open(self.history_file) as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        snapshot = ExtendedResourceSnapshot(**data)
                        self.history.append(snapshot)
        except Exception as e:
            _log.warning("Failed to load resource history: %s", e)

    def record(self, snapshot: ExtendedResourceSnapshot) -> None:
        """Record a resource snapshot and detect leaks."""
        self.history.append(snapshot)

        # Detect leaks from history
        if len(self.history) >= 2:
            snapshot.leak_metrics = detect_leaks(self.history, snapshot)

        try:
            # Convert to JSON-serializable dict (handle LeakMetrics)
            snapshot_dict = snapshot.__dict__.copy()
            if isinstance(snapshot_dict.get("leak_metrics"), LeakMetrics):
                leak_metrics = snapshot_dict["leak_metrics"]
                snapshot_dict["leak_metrics"] = {
                    "memory_leak_rate_mb_per_hour": leak_metrics.memory_leak_rate_mb_per_hour,
                    "fd_leak_rate_per_hour": leak_metrics.fd_leak_rate_per_hour,
                    "child_process_leak_rate_per_hour": leak_metrics.child_process_leak_rate_per_hour,
                    "thread_leak_rate_per_hour": leak_metrics.thread_leak_rate_per_hour,
                    "socket_leak_rate_per_hour": leak_metrics.socket_leak_rate_per_hour,
                    "memory_leak_detected": leak_metrics.memory_leak_detected,
                    "fd_leak_detected": leak_metrics.fd_leak_detected,
                    "child_process_leak_detected": leak_metrics.child_process_leak_detected,
                    "leak_severity": leak_metrics.leak_severity,
                }

            with open(self.history_file, "ab") as f:
                f.write(json.dumps(snapshot_dict))
                f.write(b"\n")
        except Exception as e:
            _log.warning("Failed to save resource snapshot: %s", e)

    def predict_next_interval(self, interval_seconds: int = 60) -> dict[str, Any]:
        """Predict resource usage for next interval."""
        if len(self.history) < 10:
            return {"confidence": 0.0, "prediction": {}}

        # Simple trend-based prediction
        recent = list(self.history)[-10:]
        trends = {}

        # Calculate trends for key metrics
        for metric in ["mem_rss_mb", "fd_used", "process_count", "load_1m"]:
            values = [getattr(s, metric) for s in recent]
            if len(values) > 1:
                trend = (values[-1] - values[0]) / len(values)
                trends[metric] = {
                    "current": values[-1],
                    "trend": trend,
                    "predicted": values[-1] + trend * (interval_seconds / 60),
                }

        confidence = min(1.0, len(self.history) / 100.0)
        return {"confidence": confidence, "prediction": trends}

    def should_throttle_speculative(self, new_branches: int = 1, min_mem_available_mb: float = 512.0) -> bool:
        """
        Determine if new speculative branches should be throttled based on resource trends.
        """
        if not self.history:
            return False

        current = self.history[-1]

        # 1. Immediate check: Are we already below the safety margin?
        if current.mem_available_mb < min_mem_available_mb:
            _log.warning(
                f"Throttling speculative: available memory {current.mem_available_mb:.1f}MB < {min_mem_available_mb}MB"
            )
            return True

        # 2. Trend check: Is memory declining rapidly?
        prediction = self.predict_next_interval(60)
        if prediction["confidence"] > 0.5:
            mem_pred = prediction["prediction"].get("mem_rss_mb", {})
            if mem_pred.get("trend", 0) > 50.0:  # Growing more than 50MB/minute
                _log.warning(
                    f"Throttling speculative: high memory growth trend detected ({mem_pred['trend']:.1f}MB/min)"
                )
                return True

        # 3. Load check
        if current.load_1m > current.cpu_count * 1.5:
            _log.warning(f"Throttling speculative: high system load ({current.load_1m:.2f})")
            return True

        return False

    def detect_anomalies(self, current: ExtendedResourceSnapshot) -> list[dict[str, Any]]:
        """Detect anomalous resource usage patterns."""
        if len(self.history) < 20:
            return []

        recent = list(self.history)[-20:]
        anomalies = []

        # Check for sudden spikes
        for metric in ["mem_rss_mb", "fd_used", "process_count"]:
            values = [getattr(s, metric) for s in recent]
            if not values:
                continue
            avg = sum(values) / len(values)
            std = (sum((v - avg) ** 2 for v in values) / len(values)) ** 0.5
            current_val = getattr(current, metric)

            if std > 0 and abs(current_val - avg) > 3 * std:
                anomalies.append(
                    {
                        "metric": metric,
                        "current": current_val,
                        "expected": avg,
                        "severity": "high" if abs(current_val - avg) > 5 * std else "medium",
                    }
                )

        return anomalies


class BottleneckDetector:
    """Detect bottlenecks in agent execution loops."""

    def __init__(self) -> None:
        self.loop_timings: dict[str, list[float]] = {}
        self.resource_contention: list[dict[str, Any]] = []

    def record_loop_timing(self, loop_id: str, duration_ms: float) -> None:
        """Record timing for an agent loop iteration."""
        if loop_id not in self.loop_timings:
            self.loop_timings[loop_id] = []
        self.loop_timings[loop_id].append(duration_ms)
        if len(self.loop_timings[loop_id]) > 100:
            self.loop_timings[loop_id].pop(0)

    def identify_slow_points(self) -> list[dict[str, Any]]:
        """Identify slow points in agent loops."""
        slow_points = []

        for loop_id, timings in self.loop_timings.items():
            if len(timings) < 5:
                continue

            avg = sum(timings) / len(timings)
            p95 = sorted(timings)[int(len(timings) * 0.95)]
            p99 = sorted(timings)[int(len(timings) * 0.99)]

            if p95 > avg * 2:  # Significant tail latency
                slow_points.append(
                    {
                        "loop_id": loop_id,
                        "avg_ms": avg,
                        "p95_ms": p95,
                        "p99_ms": p99,
                        "tail_latency_ratio": p95 / avg,
                        "severity": "high" if p95 > avg * 3 else "medium",
                    }
                )

        return sorted(slow_points, key=lambda x: x["tail_latency_ratio"], reverse=True)

    def detect_resource_contention(
        self, snapshot: ExtendedResourceSnapshot, harness_cards: dict[str, HarnessCard]
    ) -> list[dict[str, Any]]:
        """Detect resource contention between harnesses."""
        contentions = []

        # Check FD contention
        if snapshot.fd_used > snapshot.fd_limit * 0.8:
            contentions.append(
                {
                    "resource": "file_descriptors",
                    "utilization": snapshot.fd_used / snapshot.fd_limit,
                    "severity": "high",
                    "suggestion": "Reduce concurrent sessions or increase FD limit",
                }
            )

        # Check memory contention
        total_mem = snapshot.mem_available_mb + snapshot.mem_rss_mb
        if snapshot.mem_rss_mb > total_mem * 0.85:
            contentions.append(
                {
                    "resource": "memory",
                    "utilization": snapshot.mem_rss_mb / total_mem,
                    "severity": "high",
                    "suggestion": "Reduce memory per session or scale down",
                }
            )

        # Check harness-specific contention
        for harness_type, card in harness_cards.items():
            estimated = card.estimate_resources(10, use_p95=True)  # Example: 10 sessions, use p95
            # Extract p95 memory estimate (or fallback to avg)
            mem_estimate = estimated["memory_mb"].get("p95", estimated["memory_mb"].get("avg", 0))
            if mem_estimate > snapshot.mem_available_mb * 0.5:
                contentions.append(
                    {
                        "resource": f"memory_{harness_type}",
                        "harness": harness_type,
                        "estimated_mb": mem_estimate,
                        "estimated_mb_p95": estimated["memory_mb"].get("p95", 0),
                        "estimated_mb_peak": estimated["memory_mb"].get("peak", 0),
                        "available_mb": snapshot.mem_available_mb,
                        "severity": "medium",
                        "suggestion": f"Reduce {harness_type} sessions or use isolation",
                    }
                )

        return contentions


def sample_extended_resources() -> ExtendedResourceSnapshot:
    """Sample extended system resources including child processes, threads, sockets, and leak indicators."""
    snapshot = ExtendedResourceSnapshot()

    try:
        proc = psutil.Process()

        # Core resources
        snapshot.fd_used = proc.num_fds() if hasattr(proc, "num_fds") else 0
        try:
            import resource

            snapshot.fd_limit = resource.getrlimit(resource.RLIMIT_NOFILE)[0]
        except Exception:
            snapshot.fd_limit = 1024

        snapshot.mem_rss_mb = proc.memory_info().rss / (1024 * 1024)
        vmem = psutil.virtual_memory()
        snapshot.mem_available_mb = vmem.available / (1024 * 1024)
        snapshot.cpu_count = psutil.cpu_count() or 1
        snapshot.load_1m, snapshot.load_5m, snapshot.load_15m = psutil.getloadavg()

        # Extended indices
        net_io = psutil.net_io_counters()
        snapshot.network_bytes_sent = net_io.bytes_sent
        snapshot.network_bytes_recv = net_io.bytes_recv

        connections = proc.connections()
        snapshot.network_connections = len(connections)
        snapshot.socket_count = len(connections)

        # Network detail
        tcp_count = udp_count = unix_count = established_count = 0
        for conn in connections:
            if conn.status == psutil.CONN_ESTABLISHED:
                established_count += 1
            import socket

            if conn.type == socket.SOCK_STREAM:
                tcp_count += 1
            elif conn.type == socket.SOCK_DGRAM:
                udp_count += 1
            elif conn.type == socket.SOCK_SEQPACKET:
                unix_count += 1
        snapshot.tcp_connections = tcp_count
        snapshot.udp_connections = udp_count
        snapshot.unix_sockets = unix_count
        snapshot.established_connections = established_count

        disk_io = psutil.disk_io_counters()
        if disk_io:
            snapshot.disk_read_bytes = disk_io.read_bytes
            snapshot.disk_write_bytes = disk_io.write_bytes

        snapshot.process_count = len(psutil.pids())
        snapshot.thread_count = proc.num_threads()

        # Child process tracking
        try:
            children = proc.children(recursive=True)
            snapshot.child_process_count = len(children)
            snapshot.child_process_memory_mb = sum(c.memory_info().rss / (1024 * 1024) for c in children)
            snapshot.child_process_fd_count = sum(c.num_fds() if hasattr(c, "num_fds") else 0 for c in children)

            # Count zombie processes
            snapshot.zombie_process_count = sum(1 for c in children if c.status() == psutil.STATUS_ZOMBIE)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            snapshot.child_process_count = 0

        # Thread tracking
        try:
            threads = proc.threads()
            snapshot.active_thread_count = len(threads)
            # Estimate blocked threads (simplified - would need more detailed analysis)
            snapshot.blocked_thread_count = 0  # Placeholder
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            snapshot.active_thread_count = proc.num_threads()

        swap = psutil.swap_memory()
        snapshot.swap_used_mb = swap.used / (1024 * 1024)
        snapshot.swap_total_mb = swap.total / (1024 * 1024)

        # System-level metrics
        try:
            ctx_switches = proc.num_ctx_switches()
            snapshot.context_switches = ctx_switches.voluntary + ctx_switches.involuntary
        except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
            snapshot.context_switches = 0

        try:
            io_counters = proc.io_counters()
            if io_counters:
                snapshot.page_faults = getattr(io_counters, "read_chars", 0) + getattr(
                    io_counters, "write_chars", 0
                )  # Approximate; Linux-only attrs
        except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
            snapshot.page_faults = 0

        # GPU detection (basic - would need nvidia-ml-py or similar)
        snapshot.gpu_available = False  # Placeholder

    except Exception as e:
        _log.warning("Failed to sample extended resources: %s", e)

    snapshot.timestamp = time.time()
    return snapshot


def detect_leaks(
    history: deque[ExtendedResourceSnapshot], current: ExtendedResourceSnapshot, window_hours: float = 1.0
) -> LeakMetrics:
    """Detect resource leaks from historical snapshots."""
    leaks = LeakMetrics()

    if len(history) < 2:
        return leaks

    # Filter snapshots within window
    window_seconds = window_hours * 3600
    recent = [s for s in history if current.timestamp - s.timestamp <= window_seconds]

    if len(recent) < 2:
        return leaks

    # Calculate leak rates
    oldest = recent[0]
    newest = recent[-1]
    time_diff_hours = (newest.timestamp - oldest.timestamp) / 3600.0

    if time_diff_hours <= 0:
        return leaks

    # Memory leak rate
    mem_diff = newest.mem_rss_mb - oldest.mem_rss_mb
    leaks.memory_leak_rate_mb_per_hour = mem_diff / time_diff_hours

    # FD leak rate
    fd_diff = newest.fd_used - oldest.fd_used
    leaks.fd_leak_rate_per_hour = fd_diff / time_diff_hours

    # Child process leak rate
    child_diff = newest.child_process_count - oldest.child_process_count
    leaks.child_process_leak_rate_per_hour = child_diff / time_diff_hours

    # Thread leak rate
    thread_diff = newest.thread_count - oldest.thread_count
    leaks.thread_leak_rate_per_hour = thread_diff / time_diff_hours

    # Socket leak rate
    socket_diff = newest.socket_count - oldest.socket_count
    leaks.socket_leak_rate_per_hour = socket_diff / time_diff_hours

    # Detect leaks (thresholds)
    leaks.memory_leak_detected = leaks.memory_leak_rate_mb_per_hour > 10.0  # 10MB/hour
    leaks.fd_leak_detected = leaks.fd_leak_rate_per_hour > 1.0  # 1 FD/hour
    leaks.child_process_leak_detected = leaks.child_process_leak_rate_per_hour > 0.1  # 0.1 proc/hour

    # Determine severity
    leak_count = sum(
        [
            leaks.memory_leak_detected,
            leaks.fd_leak_detected,
            leaks.child_process_leak_detected,
        ]
    )

    if leak_count == 0:
        leaks.leak_severity = "none"
    elif leak_count == 1:
        leaks.leak_severity = "low"
    elif leak_count == 2:
        leaks.leak_severity = "medium"
    elif leaks.memory_leak_rate_mb_per_hour > 100 or leaks.fd_leak_rate_per_hour > 10:
        leaks.leak_severity = "critical"
    else:
        leaks.leak_severity = "high"

    return leaks


def _create_distribution(
    min_val: float,
    avg_val: float,
    peak_val: float,
    stddev: float | None = None,
    p50: float | None = None,
    p95: float | None = None,
    p99: float | None = None,
) -> ResourceDistribution:
    """Helper to create a ResourceDistribution with statistical values."""
    dist = ResourceDistribution()
    dist.min = min_val
    dist.avg = avg_val
    dist.peak = peak_val
    dist.stddev = stddev or (peak_val - avg_val) * 0.5  # Estimate if not provided
    dist.p50 = p50 or avg_val
    dist.p95 = p95 or (avg_val + dist.stddev * 1.645)  # Approximate p95
    dist.p99 = p99 or (avg_val + dist.stddev * 2.326)  # Approximate p99
    dist.count = 100  # Assume sufficient samples
    return dist


def create_harness_cards() -> dict[str, HarnessCard]:
    """Create default harness cards with statistical distributions for all resources."""

    # Codex harness card
    codex_card = HarnessCard(
        harness_type="codex",
        memory_base=_create_distribution(200.0, 256.0, 400.0, 50.0, 250.0, 350.0, 380.0),
        memory_per_session=_create_distribution(100.0, 128.0, 200.0, 25.0, 125.0, 170.0, 190.0),
        fd_base=_create_distribution(15, 20, 35, 5.0, 20, 30, 33),
        fd_per_session=_create_distribution(8, 10, 18, 3.0, 10, 15, 17),
        cpu_base=_create_distribution(5.0, 10.0, 20.0, 4.0, 9.5, 16.0, 18.5),
        cpu_per_session=_create_distribution(3.0, 5.0, 12.0, 2.5, 4.8, 9.0, 11.0),
        child_process_base=_create_distribution(0, 1, 3, 1.0, 1, 2, 3),
        child_process_per_session=_create_distribution(0, 0.5, 2, 0.5, 0, 1, 2),
        thread_base=_create_distribution(5, 8, 15, 3.0, 8, 12, 14),
        thread_per_session=_create_distribution(2, 4, 8, 2.0, 4, 6, 7),
        socket_base=_create_distribution(5, 10, 20, 4.0, 10, 16, 19),
        socket_per_session=_create_distribution(3, 5, 12, 3.0, 5, 9, 11),
        network_bytes_per_request=_create_distribution(1024, 2048, 8192, 1500.0, 2000, 6000, 7500),
        network_connections_per_session=_create_distribution(1, 2, 5, 1.2, 2, 4, 5),
        latency=_create_distribution(200.0, 300.0, 800.0, 150.0, 300.0, 1500.0, 3000.0),
        leak_rates=LeakMetrics(
            memory_leak_rate_mb_per_hour=0.5,
            fd_leak_rate_per_hour=0.05,
            child_process_leak_rate_per_hour=0.01,
        ),
        isolation_overhead=1.1,
        multi_harness_efficiency=0.85,
    )

    # Claude harness card
    claude_card = HarnessCard(
        harness_type="claude",
        memory_base=_create_distribution(400.0, 512.0, 800.0, 100.0, 500.0, 700.0, 780.0),
        memory_per_session=_create_distribution(200.0, 256.0, 450.0, 60.0, 250.0, 380.0, 430.0),
        fd_base=_create_distribution(25, 30, 50, 8.0, 30, 42, 48),
        fd_per_session=_create_distribution(12, 15, 28, 5.0, 15, 23, 26),
        cpu_base=_create_distribution(10.0, 15.0, 30.0, 6.0, 14.5, 24.0, 28.0),
        cpu_per_session=_create_distribution(6.0, 8.0, 18.0, 4.0, 7.8, 14.0, 16.5),
        child_process_base=_create_distribution(0, 2, 5, 1.5, 2, 4, 5),
        child_process_per_session=_create_distribution(0, 1, 3, 1.0, 1, 2, 3),
        thread_base=_create_distribution(8, 12, 25, 5.0, 12, 20, 23),
        thread_per_session=_create_distribution(4, 6, 12, 3.0, 6, 10, 11),
        socket_base=_create_distribution(8, 15, 30, 7.0, 15, 24, 28),
        socket_per_session=_create_distribution(4, 7, 15, 4.0, 7, 12, 14),
        network_bytes_per_request=_create_distribution(2048, 4096, 16384, 3000.0, 4000, 12000, 15000),
        network_connections_per_session=_create_distribution(2, 3, 8, 2.0, 3, 6, 7),
        latency=_create_distribution(300.0, 500.0, 1500.0, 300.0, 500.0, 2000.0, 5000.0),
        leak_rates=LeakMetrics(
            memory_leak_rate_mb_per_hour=1.0,
            fd_leak_rate_per_hour=0.1,
            child_process_leak_rate_per_hour=0.02,
        ),
        isolation_overhead=1.2,
        multi_harness_efficiency=0.8,
    )

    # Droid harness card
    droid_card = HarnessCard(
        harness_type="droid",
        memory_base=_create_distribution(100.0, 128.0, 200.0, 30.0, 125.0, 170.0, 190.0),
        memory_per_session=_create_distribution(50.0, 64.0, 120.0, 20.0, 62.0, 95.0, 110.0),
        fd_base=_create_distribution(10, 15, 25, 5.0, 15, 22, 24),
        fd_per_session=_create_distribution(3, 5, 12, 3.0, 5, 9, 11),
        cpu_base=_create_distribution(3.0, 5.0, 12.0, 3.0, 4.8, 9.5, 11.0),
        cpu_per_session=_create_distribution(1.5, 2.0, 6.0, 1.5, 2.0, 4.5, 5.5),
        child_process_base=_create_distribution(0, 0, 1, 0.3, 0, 1, 1),
        child_process_per_session=_create_distribution(0, 0, 1, 0.2, 0, 0, 1),
        thread_base=_create_distribution(3, 5, 10, 2.5, 5, 8, 9),
        thread_per_session=_create_distribution(1, 2, 5, 1.5, 2, 4, 5),
        socket_base=_create_distribution(2, 5, 12, 3.5, 5, 9, 11),
        socket_per_session=_create_distribution(1, 2, 6, 2.0, 2, 5, 6),
        network_bytes_per_request=_create_distribution(512, 1024, 4096, 800.0, 1000, 3200, 3800),
        network_connections_per_session=_create_distribution(0, 1, 3, 1.0, 1, 2, 3),
        latency=_create_distribution(100.0, 200.0, 600.0, 120.0, 200.0, 1000.0, 2000.0),
        leak_rates=LeakMetrics(
            memory_leak_rate_mb_per_hour=0.2,
            fd_leak_rate_per_hour=0.02,
            child_process_leak_rate_per_hour=0.005,
        ),
        isolation_overhead=1.05,
        multi_harness_efficiency=0.9,
    )

    # Cursor-agent harness card
    cursor_card = HarnessCard(
        harness_type="cursor-agent",
        memory_base=_create_distribution(300.0, 384.0, 600.0, 80.0, 380.0, 520.0, 580.0),
        memory_per_session=_create_distribution(150.0, 192.0, 350.0, 50.0, 190.0, 280.0, 330.0),
        fd_base=_create_distribution(20, 25, 45, 8.0, 25, 38, 43),
        fd_per_session=_create_distribution(10, 12, 22, 4.0, 12, 18, 21),
        cpu_base=_create_distribution(8.0, 12.0, 25.0, 5.0, 11.5, 20.0, 23.5),
        cpu_per_session=_create_distribution(4.0, 6.0, 14.0, 3.5, 5.8, 11.0, 13.0),
        child_process_base=_create_distribution(0, 1, 4, 1.2, 1, 3, 4),
        child_process_per_session=_create_distribution(0, 0.5, 2, 0.7, 0, 1, 2),
        thread_base=_create_distribution(6, 10, 20, 4.5, 10, 16, 19),
        thread_per_session=_create_distribution(3, 5, 10, 2.5, 5, 8, 9),
        socket_base=_create_distribution(6, 12, 25, 6.0, 12, 20, 23),
        socket_per_session=_create_distribution(3, 6, 14, 4.0, 6, 11, 13),
        network_bytes_per_request=_create_distribution(1536, 3072, 12288, 2500.0, 3000, 9000, 11000),
        network_connections_per_session=_create_distribution(1, 2, 6, 1.8, 2, 5, 6),
        latency=_create_distribution(250.0, 400.0, 1200.0, 250.0, 400.0, 1800.0, 4000.0),
        leak_rates=LeakMetrics(
            memory_leak_rate_mb_per_hour=0.8,
            fd_leak_rate_per_hour=0.08,
            child_process_leak_rate_per_hour=0.015,
        ),
        isolation_overhead=1.15,
        multi_harness_efficiency=0.82,
    )

    return {
        "codex": codex_card,
        "claude": claude_card,
        "droid": droid_card,
        "cursor-agent": cursor_card,
        "cursor": cursor_card,  # Alias
    }
