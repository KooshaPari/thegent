"""
Resource Monitor

Samples system resources for dynamic scaling decisions.
"""

from dataclasses import dataclass
from typing import Optional
import time

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


@dataclass
class ResourceSample:
    """Resource sample at a point in time."""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    load_avg: float
    fd_count: Optional[int] = None

    @property
    def pressure_score(self) -> float:
        """Combined pressure score (0-1)."""
        return max(self.cpu_percent / 100, self.memory_percent / 100, self.load_avg)


class ResourceMonitor:
    """Monitors system resources."""

    def __init__(self, sample_interval: float = 1.0):
        self.sample_interval = sample_interval
        self._samples: list[ResourceSample] = []
        self._max_samples = 60

    def sample(self) -> ResourceSample:
        """Take a resource sample."""
        now = time.time()

        if HAS_PSUTIL:
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory().percent
            load = psutil.getloadavg()[0] / psutil.cpu_count() if psutil.cpu_count() else 0
            try:
                fd_count = len(psutil.Process().open_files())
            except:
                fd_count = None
        else:
            cpu = 50.0
            memory = 50.0
            load = 0.5
            fd_count = None

        sample = ResourceSample(
            timestamp=now,
            cpu_percent=cpu,
            memory_percent=memory,
            load_avg=load,
            fd_count=fd_count
        )

        self._samples.append(sample)
        if len(self._samples) > self._max_samples:
            self._samples.pop(0)

        return sample

    def average_pressure(self, window: int = 5) -> float:
        """Get average pressure over window."""
        if not self._samples:
            return 0.0

        recent = self._samples[-window:]
        return sum(s.pressure_score for s in recent) / len(recent)

    def latest(self) -> Optional[ResourceSample]:
        """Get latest sample."""
        return self._samples[-1] if self._samples else None
