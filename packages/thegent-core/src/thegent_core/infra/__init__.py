"""Core infra compatibility exports."""

from .fast_subprocess import run_subprocess_optimized
from .shim_subprocess import run

__all__ = ["run", "run_subprocess_optimized"]
