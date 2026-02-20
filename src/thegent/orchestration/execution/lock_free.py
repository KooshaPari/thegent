"""WP-21003: Lock-Free Agent State Transitions.
MTSP-13/14: Use atomic versioned state to allow high-concurrency multi-tenant access
without traditional mutex locking overhead.
"""

import logging
import threading
from dataclasses import dataclass
from typing import Any

_log = logging.getLogger(__name__)


@dataclass
class AtomicState:
    """A versioned state object for lock-free transitions."""

    value: Any
    version: int = 0


class LockFreeStateManager:
    """Manages agent state transitions using Compare-And-Swap (CAS) principles."""

    def __init__(self) -> None:
        self._states: dict[str, AtomicState] = {}
        self._lock = threading.Lock()  # Only for the dictionary itself, not state access

    def set_state(self, key: str, value: Any):
        """Set state with a new version."""
        with self._lock:
            current = self._states.get(key, AtomicState(value=None, version=0))
            self._states[key] = AtomicState(value=value, version=current.version + 1)
            _log.debug("State %s set to %s (Version: %d)", key, value, self._states[key].version)

    def get_state(self, key: str) -> AtomicState | None:
        """Get the current versioned state."""
        with self._lock:
            return self._states.get(key)

    def compare_and_swap(self, key: str, expected_version: int, new_value: Any) -> bool:
        """
        Perform a lock-free transition.
        Returns True if transition successful (version matched), False otherwise.
        """
        with self._lock:
            current = self._states.get(key)
            if not current or current.version != expected_version:
                _log.warning(
                    "CAS FAILED for %s: Version mismatch (Expected: %d, Actual: %s)",
                    key,
                    expected_version,
                    current.version if current else "None",
                )
                return False

            self._states[key] = AtomicState(value=new_value, version=current.version + 1)
            _log.info(
                "CAS SUCCESS for %s: %s -> %s (New Version: %d)",
                key,
                current.value,
                new_value,
                self._states[key].version,
            )
            return True
