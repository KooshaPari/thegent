"""Shared Memory system for orchestration state.

This module provides a shared memory system for fast inter-process
communication in the orchestration layer.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


class SHMSystem:
    """Shared memory system for orchestration.

    This class manages shared memory regions for fast inter-process
    communication via a native extension with graceful fallback.
    """

    _instance: SHMSystem | None = None
    _interface: Any = None

    def __new__(cls, session_dir: Path) -> SHMSystem:
        """Return the singleton instance, creating on first call."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, session_dir: Path) -> None:
        """Initialize the SHM system.

        Args:
            session_dir: Path to the session directory.
        """
        if hasattr(self, "_initialized"):
            return
        self._initialized = True
        self.session_dir = session_dir
        self.shm_path = session_dir / "state.shm"
        self._interface = None

        from thegent.config import ThegentSettings

        self.use_native = ThegentSettings().use_native_shm
        if self.use_native:
            self._init_native()

    def _init_native(self) -> None:
        """Attempt to load and initialise the native SHM extension."""
        try:
            import thegent_shm

            thegent_shm.py_init_shm(str(self.shm_path))
            self._interface = thegent_shm.SHMInterface(str(self.shm_path))
        except ImportError:
            self._interface = None
        except Exception:
            self._interface = None

    def is_native_active(self) -> bool:
        """Return True when the native SHM interface is available."""
        return self._interface is not None

    def record_failure(self, target: str, category: str) -> None:
        """Record a failure for the circuit breaker.

        Args:
            target: The target identifier.
            category: ``"agent"`` maps to index 0, anything else to 1.
        """
        if self._interface:
            if category == "agent":
                self._interface.record_failure(target, 0)
            else:
                self._interface.record_failure(target, 1)

    def is_open(
        self,
        target: str,
        category: str = "agent",
        threshold: int = 5,
        window_s: int = 300,
        recovery_s: int = 60,
    ) -> bool:
        """Check whether the circuit breaker is open for *target*.

        Args:
            target: The target identifier.
            category: ``"agent"`` maps to index 0, anything else to 1.
            threshold: Failure-count threshold before opening.
            window_s: Sliding window in seconds.
            recovery_s: Cool-down before retry in seconds.

        Returns:
            True if the circuit is open, False otherwise.
        """
        if not self._interface:
            return False
        idx = 0 if category == "agent" else 1
        return self._interface.is_open(target, idx, threshold, window_s, recovery_s)

    def award_xp(self, amount: int) -> None:
        """Award XP through the native interface.

        Args:
            amount: Amount of XP to award.
        """
        if self._interface:
            self._interface.award_xp(amount)

    def get_xp_state(self) -> dict[str, Any] | None:
        """Return the current XP state from native SHM.

        Returns:
            XP state dict, or None when no native interface is active.
        """
        if self._interface:
            return self._interface.get_xp_state()
        return None

    def set_level(self, level: int) -> None:
        """Set the level through the native interface.

        Args:
            level: The level to set.
        """
        if self._interface:
            self._interface.set_level(level)


def get_shm_system(session_dir: Path) -> SHMSystem:
    """Return the :class:`SHMSystem` singleton for *session_dir*.

    Args:
        session_dir: Path to the session directory.

    Returns:
        The singleton :class:`SHMSystem` instance.
    """
    return SHMSystem(session_dir)


__all__ = [
    "SHMSystem",
    "get_shm_system",
]
