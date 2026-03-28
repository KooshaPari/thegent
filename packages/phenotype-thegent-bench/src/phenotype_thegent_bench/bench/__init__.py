"""WL-115 benchmark primitives."""

from .models import BenchRecord
from .runner import run_suite
from .store import append_bench_record, load_bench_records

__all__ = ["BenchRecord", "append_bench_record", "load_bench_records", "run_suite"]
