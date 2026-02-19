"""Trace data model and JSONL schema for deterministic replay system."""

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum, StrEnum
from typing import Any, Union


class RecordType(StrEnum):
    """Valid trace record types."""

    SESSION = "session"
    TOOL_CALL = "tool_call"
    DECISION = "decision"


class ToolStatus(StrEnum):
    """Tool execution status."""

    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    SKIPPED = "skipped"


class DecisionType(StrEnum):
    """Types of decision points in execution."""

    ROUTING = "routing"
    CLASSIFICATION = "classification"
    OVERRIDE = "override"
    FALLBACK = "fallback"


@dataclass
class ToolCallRecord:
    """Record of a single tool invocation."""

    type: str = RecordType.TOOL_CALL
    tool_name: str = ""
    tool_id: str = ""
    session_id: str = ""
    call_index: int = 0
    inputs: dict[str, Any] = field(default_factory=dict)
    result: Any | None = None
    duration_ms: float = 0.0
    tokens_used: int = 0
    cost: float = 0.0
    status: str = ToolStatus.SUCCESS
    error_msg: str | None = None
    timestamp: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_json_line(self) -> str:
        """Serialize to JSON line format."""
        return json.dumps(asdict(self), default=str)

    @staticmethod
    def from_json_line(line: str) -> "ToolCallRecord":
        """Deserialize from JSON line format."""
        data = json.loads(line)
        return ToolCallRecord(**data)


@dataclass
class DecisionRecord:
    """Record of a decision point in execution."""

    type: str = RecordType.DECISION
    decision_type: str = ""
    reasoning: str = ""
    choice: str = ""
    session_id: str = ""
    timestamp: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_json_line(self) -> str:
        """Serialize to JSON line format."""
        return json.dumps(asdict(self), default=str)

    @staticmethod
    def from_json_line(line: str) -> "DecisionRecord":
        """Deserialize from JSON line format."""
        data = json.loads(line)
        return DecisionRecord(**data)


@dataclass
class SessionRecord:
    """Record of session metadata (start/end)."""

    type: str = RecordType.SESSION
    session_id: str = ""
    task_id: str = ""
    model: str = ""
    provider: str = ""
    config: dict[str, Any] = field(default_factory=dict)
    status: str = "started"  # started | completed | failed
    start_time: str = ""
    end_time: str | None = None
    total_cost: float = 0.0
    total_tokens: int = 0
    total_duration_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_json_line(self) -> str:
        """Serialize to JSON line format."""
        return json.dumps(asdict(self), default=str)

    @staticmethod
    def from_json_line(line: str) -> "SessionRecord":
        """Deserialize from JSON line format."""
        data = json.loads(line)
        return SessionRecord(**data)


# Union type for any trace record
TraceRecord = Union[ToolCallRecord, DecisionRecord, SessionRecord]


class TraceValidator:
    """Validates trace records and files."""

    @staticmethod
    def validate_tool_call_record(record: ToolCallRecord) -> bool:
        """Validate tool call record."""
        if not record.tool_name:
            return False
        if not record.session_id:
            return False
        if record.call_index < 0:
            return False
        if record.duration_ms < 0:
            return False
        if record.tokens_used < 0:
            return False
        if record.cost < 0:
            return False
        return True

    @staticmethod
    def validate_decision_record(record: DecisionRecord) -> bool:
        """Validate decision record."""
        if not record.decision_type:
            return False
        if not record.session_id:
            return False
        return True

    @staticmethod
    def validate_session_record(record: SessionRecord) -> bool:
        """Validate session record."""
        if not record.session_id:
            return False
        if not record.model:
            return False
        if not record.provider:
            return False
        return True

    @staticmethod
    def validate_jsonl_file(file_path: str, max_errors: int = 10) -> tuple[bool, list[str]]:
        """Validate JSONL trace file format."""
        errors = []

        try:
            with open(file_path) as f:
                for line_num, line in enumerate(f, 1):
                    if not line.strip():
                        continue

                    try:
                        data = json.loads(line)
                        record_type = data.get("type")

                        if record_type == RecordType.TOOL_CALL:
                            record = ToolCallRecord(**data)
                            if not TraceValidator.validate_tool_call_record(record):
                                errors.append(f"Line {line_num}: Invalid ToolCallRecord")
                        elif record_type == RecordType.DECISION:
                            record = DecisionRecord(**data)
                            if not TraceValidator.validate_decision_record(record):
                                errors.append(f"Line {line_num}: Invalid DecisionRecord")
                        elif record_type == RecordType.SESSION:
                            record = SessionRecord(**data)
                            if not TraceValidator.validate_session_record(record):
                                errors.append(f"Line {line_num}: Invalid SessionRecord")
                        else:
                            errors.append(f"Line {line_num}: Unknown record type: {record_type}")

                    except (json.JSONDecodeError, TypeError) as e:
                        errors.append(f"Line {line_num}: {e!s}")

                    if len(errors) >= max_errors:
                        break

        except OSError as e:
            errors.append(f"File read error: {e!s}")
            return False, errors

        return len(errors) == 0, errors


def create_tool_call_record(
    tool_name: str,
    session_id: str,
    call_index: int,
    inputs: dict[str, Any],
    result: Any,
    duration_ms: float,
    tokens_used: int = 0,
    cost: float = 0.0,
    status: str = ToolStatus.SUCCESS,
    error_msg: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> ToolCallRecord:
    """Create a tool call record with defaults."""
    return ToolCallRecord(
        type=RecordType.TOOL_CALL,
        tool_name=tool_name,
        tool_id=f"{tool_name}-{call_index}",
        session_id=session_id,
        call_index=call_index,
        inputs=inputs,
        result=result,
        duration_ms=duration_ms,
        tokens_used=tokens_used,
        cost=cost,
        status=status,
        error_msg=error_msg,
        timestamp=datetime.utcnow().isoformat(),
        metadata=metadata or {},
    )


def create_decision_record(
    decision_type: str,
    session_id: str,
    reasoning: str,
    choice: str,
    metadata: dict[str, Any] | None = None,
) -> DecisionRecord:
    """Create a decision record with defaults."""
    return DecisionRecord(
        type=RecordType.DECISION,
        decision_type=decision_type,
        reasoning=reasoning,
        choice=choice,
        session_id=session_id,
        timestamp=datetime.utcnow().isoformat(),
        metadata=metadata or {},
    )


def create_session_record(
    session_id: str,
    task_id: str,
    model: str,
    provider: str,
    config: dict[str, Any] | None = None,
    status: str = "started",
    metadata: dict[str, Any] | None = None,
) -> SessionRecord:
    """Create a session record with defaults."""
    return SessionRecord(
        type=RecordType.SESSION,
        session_id=session_id,
        task_id=task_id,
        model=model,
        provider=provider,
        config=config or {},
        status=status,
        start_time=datetime.utcnow().isoformat(),
        metadata=metadata or {},
    )
