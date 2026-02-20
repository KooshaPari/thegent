"""Performance optimization & benchmarking."""

import logging
import platform
import time
from collections.abc import Callable
from typing import Any

import psutil

logger = logging.getLogger(__name__)


class CrossPlatformPerformance:
    """Cross-platform performance optimization."""

    def __init__(self) -> None:
        """Initialize performance optimizer."""
        self.system = platform.system()
        self.benchmarks: dict[str, float] = {}

    def benchmark(self, operation: Callable[..., Any], name: str, *args: Any, **kwargs: Any) -> float:
        """Benchmark an operation.

        Args:
            operation: Operation to benchmark
            name: Benchmark name
            *args: Arguments for the operation
            **kwargs: Keyword arguments for the operation

        Returns:
            Execution time in seconds
        """
        logger.info(f"Running benchmark '{name}' on {self.system}")
        start = time.perf_counter()
        try:
            operation(*args, **kwargs)
        except Exception as e:
            logger.error(f"Benchmark {name} failed: {e}")
            return -1.0
        elapsed = time.perf_counter() - start

        self.benchmarks[name] = elapsed
        logger.info(f"Benchmark {name}: {elapsed:.4f}s")
        return elapsed

    def get_system_metrics(self) -> dict[str, Any]:
        """Get current system performance metrics.

        Returns:
            Dictionary with metrics
        """
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage("/").percent,
            "system": self.system,
        }

    def optimize(self, target: str) -> dict[str, Any]:
        """Optimize a target operation.

        Args:
            target: Target to optimize

        Returns:
            Optimization results
        """
        logger.info(f"Optimizing {target} for {self.system}")

        result = {"target": target, "optimized": False, "actions": []}

        if target == "memory":
            # Basic memory cleanup (e.g. GC)
            import gc

            gc.collect()
            result["optimized"] = True
            result["actions"].append("Collected garbage")

        elif target == "process":
            # Adjust process priority
            try:
                p = psutil.Process()
                if self.system == "Windows":
                    p.nice(psutil.HIGH_PRIORITY_CLASS)
                else:
                    p.nice(-10)  # Higher priority on POSIX
                result["optimized"] = True
                result["actions"].append("Increased process priority")
            except Exception as e:
                logger.error(f"Optimize process failed: {e}")

        return result
