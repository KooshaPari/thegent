"""Re-export failure_modes from orchestration.resilience for backward compatibility."""

from thegent.orchestration.resilience.failure_modes import FailureMode, classify_failure

__all__ = ["FailureMode", "classify_failure"]
