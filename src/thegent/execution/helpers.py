"""Execution run metadata and registry for thegent orchestration."""

import contextlib
import hashlib
import orjson as json
import logging
import os
import socket
import time
import uuid
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from pathlib import Path
from typing import Any

import httpx
from pydantic import BaseModel, Field, ValidationError

from thegent.config import ThegentSettings
from thegent.execution_coercion_helpers import as_bool as _as_bool_impl
from thegent.execution_coercion_helpers import as_float as _as_float_impl
from thegent.execution_coercion_helpers import as_int as _as_int_impl
from thegent.execution_event_builders import (
    build_feedback_event,
    build_finish_event,
    build_pause_event,
    build_resume_event,
    build_schema_marker_event,
)
from thegent.execution_hash_helpers import calculate_stable_record_hash
from thegent.execution_jsonl_parsers import parse_checkpoint_by_id as _parse_checkpoint_by_id_impl
from thegent.execution_jsonl_parsers import parse_checkpoint_line as _parse_checkpoint_line_impl
from thegent.execution_jsonl_parsers import parse_circuit_failure as _parse_circuit_failure_impl
from thegent.execution_jsonl_parsers import parse_dlq_item as _parse_dlq_item_impl
from thegent.execution_jsonl_parsers import parse_fatigue_line as _parse_fatigue_line_impl
from thegent.execution_jsonl_parsers import parse_override_unexpired as _parse_override_unexpired_impl
from thegent.execution_jsonl_parsers import process_dlq_line as _process_dlq_line_impl
from thegent.execution_run_scan_helpers import check_session_id as _check_session_id_impl
from thegent.execution_run_scan_helpers import extract_domain_tag as _extract_domain_tag_impl
from thegent.execution_run_scan_helpers import extract_run_id as _extract_run_id_impl
from thegent.execution_run_scan_helpers import extract_session_id as _extract_session_id_impl
from thegent.execution_run_scan_helpers import filter_expired_record as _filter_expired_record_impl
from thegent.execution_run_scan_helpers import process_calibration_entry as _process_calibration_entry_impl
from thegent.execution_run_scan_helpers import process_run_entry as _process_run_entry_impl
from thegent.execution_run_scan_helpers import process_token_match as _process_token_match_impl
from thegent.execution_run_scan_helpers import update_run_state as _update_run_state_impl

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


def _warn_bounded(message: str, *args: object) -> None:
    global _execution_warning_count
    _execution_warning_count += 1
    if _execution_warning_count <= _EXECUTION_WARNING_LIMIT:
        _log.warning(message, *args)


def _as_float(value: Any, default: float) -> float:
    """Coerce arbitrary values to float with a safe default."""
    return _as_float_impl(value, default)


def _as_int(value: Any, default: int) -> int:
    """Coerce arbitrary values to int with a safe default."""
    return _as_int_impl(value, default)


def _as_bool(value: Any, default: bool) -> bool:
    """Coerce arbitrary values to bool with a safe default."""
    return _as_bool_impl(value, default)


