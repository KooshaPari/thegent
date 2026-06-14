# ruff: noqa: A005
"""Windows-compatible fallback for the Unix resource module."""

from __future__ import annotations

RLIMIT_AS = 1
RLIMIT_NPROC = 2
RLIMIT_NOFILE = 3
RLIM_INFINITY = -1

_LIMITS: dict[int, tuple[int, int]] = {
    RLIMIT_AS: (RLIM_INFINITY, RLIM_INFINITY),
    RLIMIT_NPROC: (RLIM_INFINITY, RLIM_INFINITY),
    RLIMIT_NOFILE: (4096, 4096),
}


class error(OSError):
    """Resource module compatible error type."""


def getrlimit(kind: int) -> tuple[int, int]:
    return _LIMITS.get(kind, (RLIM_INFINITY, RLIM_INFINITY))


def setrlimit(kind: int, limits: tuple[int, int]) -> None:
    _LIMITS[kind] = limits


__all__ = [
    "RLIM_INFINITY",
    "RLIMIT_AS",
    "RLIMIT_NOFILE",
    "RLIMIT_NPROC",
    "error",
    "getrlimit",
    "setrlimit",
]
