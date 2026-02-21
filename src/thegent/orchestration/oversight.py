"""Re-export oversight from orchestration.resilience for backward compatibility."""

from thegent.orchestration.resilience.oversight import get_oversight_action, should_trigger_oversight

__all__ = ["get_oversight_action", "should_trigger_oversight"]
