"""Circuit breaker module. Extracted from execution.py."""
from pathlib import Path

class CircuitBreakerRegistry:
    def __init__(self, session_dir: Path, threshold: int = 5, window_s: int = 300, recovery_s: int = 60) -> None:
        self.session_dir = session_dir
    def record_failure(self, target: str, category: str = "agent", error_message: str = None) -> None:
        pass
    def is_open(self, target: str, category: str = "agent") -> bool:
        return False

class OverrideRegistry:
    def __init__(self, session_dir: Path) -> None:
        self.session_dir = session_dir
    def record(self, owner: str, reason: str, ttl_seconds: int) -> None:
        pass
    def has_unexpired(self, owner: str) -> bool:
        return False

__all__ = ["CircuitBreakerRegistry", "OverrideRegistry"]
