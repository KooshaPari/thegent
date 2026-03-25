"""BKM-05: State-SHM -- CircuitBreaker + XP tracker in memory-mapped Rust.

This module provides ``CircuitBreakerShm`` and ``XpTracker``, backed by the
``thegent_shm`` PyO3 Rust extension when available.  When the native extension
is not compiled/installed, a pure-Python in-process fallback is used so that
all callers continue to work without any code change.

Usage::

    from thegent_platform.native.state_shm import CircuitBreakerShm, XpTracker

    shm_path = session_dir / "state.shm"
    cb  = CircuitBreakerShm(shm_path)
    xp  = XpTracker(shm_path)

    cb.record_failure("gpt-4o", category="model")
    if cb.is_open("gpt-4o", category="model"):
        ...  # circuit open, skip

    xp.award(100)
    level = xp.level

Environment variables:
  THGENT_USE_NATIVE_SHM=0   Force pure-Python fallback even if extension available.

Native extension layout (crates/thegent-shm):
  SHMInterface.record_failure(target, category_int)
  SHMInterface.is_open(target, category_int, threshold, window_s, recovery_s)
  SHMInterface.award_xp(amount)
  SHMInterface.get_xp_state()  -> {"total_xp": int, "level": int} | None
  SHMInterface.set_level(level)
  SHMInterface.set_health_score(score)
  SHMInterface.get_health_score()
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any

_log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Native extension probe
# ---------------------------------------------------------------------------


def _is_native_enabled() -> bool:
    """Check if native SHM is enabled via settings."""
    from thegent_core.config import ThegentSettings

    settings = ThegentSettings()
    return settings.use_native_shm


_NATIVE_ENABLED: bool = _is_native_enabled()


def _try_import_native() -> Any | None:
    """Attempt to import the optional thegent_shm Rust extension."""
    try:
        import thegent_shm

        return thegent_shm
    except ImportError:
        return None


_native_module: Any | None = _try_import_native() if _NATIVE_ENABLED else None

if _NATIVE_ENABLED and _native_module is None:
    _log.debug(
        "thegent_shm native extension not found. Using pure-Python state_shm fallback. "
        "To enable native SHM, build crates/thegent-shm with maturin and install the wheel."
    )


def is_native_available() -> bool:
    """Return True if the Rust thegent_shm extension is loaded and usable."""
    return _native_module is not None


# ---------------------------------------------------------------------------
# Category helpers
# ---------------------------------------------------------------------------

_CATEGORY_MAP: dict[str, int] = {
    "agent": 0,
    "model": 1,
    "provider": 2,
    "tool": 3,
}


def _category_int(category: str) -> int:
    return _CATEGORY_MAP.get(category, 0)


# ---------------------------------------------------------------------------
# Pure-Python fallback state
# ---------------------------------------------------------------------------


class _PurePythonBreakerStore:
    """In-process dict-backed circuit breaker state (fallback when native unavailable)."""

    def __init__(self) -> None:
        # "target:category" -> list of failure timestamps
        self._failures: dict[str, list[float]] = {}

    def record_failure(self, target: str, category: str) -> None:
        key = f"{target}:{category}"
        self._failures.setdefault(key, []).append(time.time())

    def is_open(
        self,
        target: str,
        category: str,
        threshold: int,
        window_s: float,
        recovery_s: float,
    ) -> bool:
        key = f"{target}:{category}"
        now = time.time()
        records = [ts for ts in self._failures.get(key, []) if (now - ts) < window_s]
        if len(records) >= threshold:
            latest = max(records)
            # Half-open: if enough time elapsed since last failure, allow trial
            if (now - latest) > recovery_s:
                return False
            return True
        return False

    def clear(self, target: str | None = None) -> None:
        if target is None:
            self._failures.clear()
        else:
            keys_to_clear = [k for k in self._failures if k.startswith(f"{target}:")]
            for k in keys_to_clear:
                del self._failures[k]


class _PurePythonXpStore:
    """In-process dict-backed XP/level state (fallback when native unavailable)."""

    def __init__(self) -> None:
        self.total_xp: int = 0
        self.level: int = 1

    def award(self, amount: int) -> None:
        self.total_xp += amount
        self.level = self.total_xp // 1000 + 1

    def state(self) -> dict[str, int]:
        return {"total_xp": self.total_xp, "level": self.level}


# ---------------------------------------------------------------------------
# CircuitBreakerShm
# ---------------------------------------------------------------------------


class CircuitBreakerShm:
    """Circuit breaker state backed by memory-mapped Rust SHM or pure-Python fallback.

    States (mirroring Rust enum):
      CLOSED   (0) -- normal, requests flow through
      OPEN     (1) -- too many failures, requests blocked
      HALF_OPEN (2)-- recovery window, one trial allowed

    When the native extension is available, state is persisted to a memory-mapped
    file at ``path`` (created automatically, size determined by Rust crate constants).
    Multiple Python processes sharing the same ``path`` share state without locks.

    When native is unavailable, state lives in process memory only (no cross-process
    sharing) and is lost on restart -- identical semantics to the existing
    ``CircuitBreakerRegistry`` but without file I/O.

    Args:
        path: Path to the SHM backing file (e.g. session_dir / "state.shm").
        threshold: Number of failures in ``window_s`` before tripping. Default 5.
        window_s: Sliding window seconds for failure counting. Default 300.
        recovery_s: Seconds after last failure before half-open trial. Default 60.
    """

    # State constants matching Rust u8 layout
    CLOSED: int = 0
    OPEN: int = 1
    HALF_OPEN: int = 2

    def __init__(
        self,
        path: Path | str,
        threshold: int = 5,
        window_s: float = 300.0,
        recovery_s: float = 60.0,
    ) -> None:
        self._path = Path(path)
        self.threshold = threshold
        self.window_s = window_s
        self.recovery_s = recovery_s
        self._native_iface: Any | None = None
        self._fallback = _PurePythonBreakerStore()

        if _native_module is not None:
            try:
                self._path.parent.mkdir(parents=True, exist_ok=True)
                self._native_iface = _native_module.SHMInterface(str(self._path))
                _log.debug("CircuitBreakerShm: native SHM at %s", self._path)
            except Exception as exc:
                _log.warning(
                    "CircuitBreakerShm: native SHM init failed (%s). Using pure-Python fallback.",
                    exc,
                )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def is_native(self) -> bool:
        """True when backed by the Rust memory-mapped extension."""
        return self._native_iface is not None

    def record_failure(self, target: str, category: str = "agent") -> None:
        """Record one failure event for ``target`` in ``category``.

        Increments the failure counter in the SHM region (or in-process dict).
        Thread-safe via Rust atomics when native; GIL-protected when fallback.
        """
        if self._native_iface is not None:
            try:
                self._native_iface.record_failure(target, _category_int(category))
                return
            except Exception as exc:
                _log.warning("CircuitBreakerShm.record_failure native error: %s. Using fallback.", exc)
        self._fallback.record_failure(target, category)

    def record_success(self, target: str, category: str = "agent") -> None:
        """Record a success -- clears the fallback window for target.

        The native Rust SHM does not track successes independently (the sliding
        window expires naturally); this method is a no-op on the native path and
        clears the fallback store for the given target.
        """
        if self._native_iface is None:
            self._fallback.clear(target)

    def is_open(self, target: str, category: str = "agent") -> bool:
        """Return True when the circuit is OPEN (requests should be blocked).

        Returns False when CLOSED (normal) or HALF_OPEN (trial allowed).
        """
        if self._native_iface is not None:
            try:
                return bool(
                    self._native_iface.is_open(
                        target,
                        _category_int(category),
                        self.threshold,
                        self.window_s,
                        self.recovery_s,
                    )
                )
            except Exception as exc:
                _log.warning("CircuitBreakerShm.is_open native error: %s. Using fallback.", exc)
        return self._fallback.is_open(target, category, self.threshold, self.window_s, self.recovery_s)

    def should_allow(self, target: str, category: str = "agent") -> bool:
        """Return True when the circuit is CLOSED or HALF_OPEN (request may proceed)."""
        return not self.is_open(target, category)

    def state_int(self, target: str, category: str = "agent") -> int:
        """Return integer state code (CLOSED=0, OPEN=1, HALF_OPEN=2).

        HALF_OPEN is approximated: if ``is_open`` returns False but failures
        were recently at threshold, state is CLOSED (trial allowed).
        """
        if self.is_open(target, category):
            return self.OPEN
        return self.CLOSED

    def set_health_score(self, score: float) -> None:
        """Write a global health score [0.0, 1.0] to SHM (native only, no-op on fallback)."""
        if self._native_iface is not None:
            try:
                self._native_iface.set_health_score(score)
            except Exception as exc:
                _log.debug("set_health_score native error: %s", exc)

    def get_health_score(self) -> float:
        """Read global health score from SHM. Returns 0.0 on fallback or error."""
        if self._native_iface is not None:
            try:
                return float(self._native_iface.get_health_score())
            except Exception as exc:
                _log.debug("get_health_score native error: %s", exc)
        return 0.0


# ---------------------------------------------------------------------------
# XpTracker
# ---------------------------------------------------------------------------


class XpTracker:
    """Experience points / level tracker backed by memory-mapped Rust SHM or pure-Python.

    Provides a persistent XP accumulator: ``award(amount)`` increments total_xp and
    recomputes ``level`` (1000 XP per level).  When native, the value is persisted
    across process restarts via the mmap'd file.

    Args:
        path: Path to the SHM backing file (shared with CircuitBreakerShm if same path).
    """

    XP_PER_LEVEL: int = 1000

    def __init__(self, path: Path | str) -> None:
        self._path = Path(path)
        self._native_iface: Any | None = None
        self._fallback = _PurePythonXpStore()

        if _native_module is not None:
            try:
                self._path.parent.mkdir(parents=True, exist_ok=True)
                self._native_iface = _native_module.SHMInterface(str(self._path))
                _log.debug("XpTracker: native SHM at %s", self._path)
            except Exception as exc:
                _log.warning("XpTracker: native SHM init failed (%s). Using pure-Python fallback.", exc)

    @property
    def is_native(self) -> bool:
        """True when backed by the Rust memory-mapped extension."""
        return self._native_iface is not None

    def award(self, amount: int) -> None:
        """Add ``amount`` XP. Level is recomputed automatically."""
        if self._native_iface is not None:
            try:
                self._native_iface.award_xp(amount)
                return
            except Exception as exc:
                _log.warning("XpTracker.award native error: %s. Using fallback.", exc)
        self._fallback.award(amount)

    @property
    def total_xp(self) -> int:
        """Total accumulated XP."""
        if self._native_iface is not None:
            state = self._get_native_state()
            if state is not None:
                return int(state.get("total_xp", 0))
        return self._fallback.total_xp

    @property
    def level(self) -> int:
        """Current level (1-based; increments every XP_PER_LEVEL points)."""
        if self._native_iface is not None:
            state = self._get_native_state()
            if state is not None:
                return int(state.get("level", 1))
        return self._fallback.level

    def state(self) -> dict[str, int]:
        """Return ``{"total_xp": int, "level": int}``."""
        if self._native_iface is not None:
            native_state = self._get_native_state()
            if native_state is not None:
                return {
                    "total_xp": int(native_state.get("total_xp", 0)),
                    "level": int(native_state.get("level", 1)),
                }
        return self._fallback.state()

    def set_level(self, level: int) -> None:
        """Directly override level (useful for migration/seeding)."""
        if self._native_iface is not None:
            try:
                self._native_iface.set_level(level)
                return
            except Exception as exc:
                _log.debug("XpTracker.set_level native error: %s", exc)
        self._fallback.level = level

    def _get_native_state(self) -> dict[str, Any] | None:
        try:
            return self._native_iface.get_xp_state()
        except Exception as exc:
            _log.debug("XpTracker._get_native_state error: %s", exc)
            return None


# ---------------------------------------------------------------------------
# Convenience: open_shm factory
# ---------------------------------------------------------------------------


def open_shm(
    path: Path | str,
    *,
    threshold: int = 5,
    window_s: float = 300.0,
    recovery_s: float = 60.0,
) -> tuple[CircuitBreakerShm, XpTracker]:
    """Open (or create) an SHM region and return (CircuitBreakerShm, XpTracker).

    Both objects share the same backing file so the Rust crate's single
    ``SHMInterface`` layout is used for all regions (breakers + XP + health).

    Example::

        cb, xp = open_shm(session_dir / "state.shm")
        cb.record_failure("claude-3-opus", category="model")
        xp.award(50)
    """
    path = Path(path)
    cb = CircuitBreakerShm(path, threshold=threshold, window_s=window_s, recovery_s=recovery_s)
    xp = XpTracker(path)
    return cb, xp
