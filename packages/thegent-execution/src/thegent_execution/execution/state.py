"""Execution run metadata and registry for thegent orchestration.

DEPRECATED: Domain entities are now in thegent.domain.entities.run.
This module is kept for backward compatibility and CalibrationRegistry.
"""

import contextlib
import orjson as json
import logging
import warnings
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from thegent_core.domain.entities.run import (
    AgentSource,
    CheckpointMeta,
    ContinuityPacket,
    InteractivityMode,
    MAIFArtifact,
    RunMeta,
    RunState,
)
from thegent.execution_coercion_helpers import as_bool as _as_bool_impl
from thegent.execution_coercion_helpers import as_float as _as_float_impl
from thegent.execution_coercion_helpers import as_int as _as_int_impl

_log = logging.getLogger(__name__)
_EXECUTION_WARNING_LIMIT = 3
_execution_warning_count = 0
_admission_import_warning_once: set[str] = set()
_execution_diagnostics: dict[str, Any] = {
    "optional_gate_import_failures": 0,
    "optional_gate_last_error_type": None,
    "optional_gate_last_error_message": None,
    "deadline_unregister": {
        "import_failures": 0,
        "runtime_failures": 0,
        "last_error_type": None,
        "last_error_message": None,
    },
    "message_parse": {
        "invalid_rows": 0,
        "non_pending_rows": 0,
        "last_error_type": None,
        "last_error_message": None,
    },
}


def _warn_bounded(message: str, *args: object) -> None:
    global _execution_warning_count
    _execution_warning_count += 1
    if _execution_warning_count <= _EXECUTION_WARNING_LIMIT:
        _log.warning(message, *args)


def get_execution_diagnostics() -> dict[str, Any]:
    """Return diagnostics snapshot for execution-path degradation."""
    return {
        "optional_gate_import_failures": _execution_diagnostics["optional_gate_import_failures"],
        "optional_gate_last_error_type": _execution_diagnostics["optional_gate_last_error_type"],
        "optional_gate_last_error_message": _execution_diagnostics["optional_gate_last_error_message"],
        "deadline_unregister": dict(_execution_diagnostics["deadline_unregister"]),
        "message_parse": dict(_execution_diagnostics["message_parse"]),
    }


def reset_execution_diagnostics() -> None:
    """Reset execution diagnostics (test helper)."""
    global _execution_warning_count
    _execution_warning_count = 0
    _admission_import_warning_once.clear()
    _execution_diagnostics["optional_gate_import_failures"] = 0
    _execution_diagnostics["optional_gate_last_error_type"] = None
    _execution_diagnostics["optional_gate_last_error_message"] = None
    _execution_diagnostics["deadline_unregister"] = {
        "import_failures": 0,
        "runtime_failures": 0,
        "last_error_type": None,
        "last_error_message": None,
    }
    _execution_diagnostics["message_parse"] = {
        "invalid_rows": 0,
        "non_pending_rows": 0,
        "last_error_type": None,
        "last_error_message": None,
    }


def _as_float(value: Any, default: float) -> float:
    """Coerce arbitrary values to float with a safe default."""
    return _as_float_impl(value, default)


def _as_int(value: Any, default: int) -> int:
    """Coerce arbitrary values to int with a safe default."""
    return _as_int_impl(value, default)


def _as_bool(value: Any, default: bool) -> bool:
    """Coerce arbitrary values to bool with a safe default."""
    return _as_bool_impl(value, default)

# Domain entity classes are now imported from thegent.domain.entities.run
# They are re-exported here for backward compatibility


class CalibrationRegistry:
    """WP-4008: Persists calibration factors and curves for agents (G-GP-09)."""

    def __init__(self, session_dir: Path) -> None:
        self.session_dir = session_dir
        self.path = session_dir / "calibration_registry.json"

    def get_factor(self, agent: str) -> float:
        """Return the persisted calibration factor for an agent."""
        if not self.path.exists():
            return 1.0
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return data.get(agent, {}).get("factor", 1.0)
        except Exception:
            return 1.0

    def update_agent(self, agent: str, factor: float, sample_size: int) -> None:
        """Persist a new calibration factor for an agent."""
        data = {}
        if self.path.exists():
            with contextlib.suppress(Exception):
                data = json.loads(self.path.read_text(encoding="utf-8"))
        data[agent] = {
            "factor": factor,
            "sample_size": sample_size,
            "updated_at_utc": datetime.now(UTC).isoformat(),
        }
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")


# Export public API for backward compatibility
__all__ = [
    # Imported from domain layer
    "RunState",
    "MAIFArtifact",
    "ContinuityPacket",
    "AgentSource",
    "InteractivityMode",
    "RunMeta",
    "CheckpointMeta",
    # Infrastructure
    "CalibrationRegistry",
]

# Issue deprecation warning on import
warnings.warn(
    "Importing domain entities from thegent.execution.state is deprecated. "
    "Please import from thegent.domain.entities.run instead.",
    DeprecationWarning,
    stacklevel=2,
)
