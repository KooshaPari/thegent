"""Helios Benchmarks - Benchmark definitions

Available benchmarks:
- terminal-bench: Software engineering tasks in terminal environments
- swe-bench: Real-world bug fixes from GitHub
- live-code-bench: Coding challenges with tests
"""

__version__ = "0.1.0"

# Import benchmarks to register them
from heliosbench.base import (
    Benchmark,
    BenchmarkMetadata,
    BenchmarkRegistry,
    register_benchmark,
)

# Import benchmark implementations (auto-registers)
from heliosbench import terminal_bench
from heliosbench import swe_bench
from heliosbench import live_code_bench

__all__ = [
    "__version__",
    "Benchmark",
    "BenchmarkMetadata",
    "BenchmarkRegistry",
    "register_benchmark",
]
