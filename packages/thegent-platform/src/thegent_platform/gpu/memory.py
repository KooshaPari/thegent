"""
GPU Memory Manager

Manages GPU memory allocation and cleanup.
"""

from dataclasses import dataclass
from typing import Optional
import time


@dataclass
class MemoryStats:
    """GPU memory statistics."""
    total: int
    used: int
    free: int
    reserved: int

    @property
    def utilization(self) -> float:
        if self.total == 0:
            return 0.0
        return self.used / self.total


class GPUMemoryManager:
    """Manages GPU memory."""

    def __init__(self, device_index: int = 0):
        self.device_index = device_index
        self._torch = None

        try:
            import torch
            self._torch = torch
        except ImportError:
            pass

    def stats(self) -> MemoryStats:
        """Get current memory statistics."""
        if not self._torch or not self._torch.cuda.is_available():
            return MemoryStats(0, 0, 0, 0)

        self._torch.cuda.set_device(self.device_index)

        return MemoryStats(
            total=self._torch.cuda.get_device_properties(self.device_index).total_memory,
            used=self._torch.cuda.memory_allocated(self.device_index),
            free=self._torch.cuda.memory_reserved(self.device_index) - self._torch.cuda.memory_allocated(self.device_index),
            reserved=self._torch.cuda.memory_reserved(self.device_index)
        )

    def clear_cache(self) -> None:
        """Clear GPU cache."""
        if self._torch and self._torch.cuda.is_available():
            self._torch.cuda.empty_cache()

    def reset_peak(self) -> None:
        """Reset peak memory tracking."""
        if self._torch and self._torch.cuda.is_available():
            self._torch.cuda.reset_peak_memory_stats(self.device_index)

    def get_peak(self) -> int:
        """Get peak memory usage."""
        if not self._torch or not self._torch.cuda.is_available():
            return 0
        return self._torch.cuda.max_memory_allocated(self.device_index)

    def optimize(self) -> dict:
        """Optimize GPU memory usage."""
        before = self.stats()
        self.clear_cache()
        after = self.stats()

        return {
            "before_utilization": before.utilization,
            "after_utilization": after.utilization,
            "freed_bytes": before.reserved - after.reserved
        }

    def with_memory_tracking(self, func: callable) -> tuple:
        """Execute function with memory tracking."""
        self.reset_peak()
        start_stats = self.stats()

        start_time = time.time()
        result = func()
        duration = time.time() - start_time

        end_stats = self.stats()
        peak = self.get_peak()

        return result, {
            "duration": duration,
            "memory_start": start_stats.used,
            "memory_end": end_stats.used,
            "memory_peak": peak,
            "memory_delta": end_stats.used - start_stats.used
        }
