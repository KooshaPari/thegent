"""Trace data model and schema definitions.

Defines JSONL trace format with three core record types:
- ToolCallRecord: Captures tool invocations (bash, read, write, etc.)
- DecisionRecord: Captures LLM decisions (model, routing, parameters)
- SessionRecord: Metadata about a trace session
"""

import gzip
import orjson as json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from phenotype_thegent_sync.integrations.base import SerializableMixin


@dataclass
class ToolCallRecord(SerializableMixin):
    """Record of a single tool invocation.

    Examples:
    - Bash command: tool=bash, tool_name=bash, args={command: "ls -la"}
    - File read: tool=file_io, tool_name=read, args={file_path: "/path/to/file"}
    - LLM call: tool=llm, tool_name=claude, args={model: "claude-opus", ...}
    """

    timestamp: str  # ISO 8601 format
    sequence_id: int  # Unique within session
    tool: str  # Tool type: bash, file_io, llm, http, etc.
    tool_name: str  # Specific tool: curl, read_file, claude, etc.
    args: dict[str, Any]  # Input arguments (sensitive data redacted)
    result: dict[str, Any]  # Output result (truncated if >10MB)
    duration_ms: float  # Execution time in milliseconds
    error: str | None = None  # Error message if failed
    redacted_fields: list[str] | None = None  # Fields that were redacted
    metadata: dict[str, Any] = field(default_factory=dict)  # Extra context

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "ToolCallRecord":
        """Construct from dictionary (e.g., JSON parsed)."""
        data_copy = data.copy()
        data_copy.pop("__type__", None)
        return ToolCallRecord(**data_copy)


@dataclass
class DecisionRecord(SerializableMixin):
    """Record of an LLM decision or routing choice.

    Examples:
    - Model selection: type=model_choice, model=claude-opus, provider=claude
    - Routing decision: type=routing, policy=cheapest, selected_model=gemini-3-flash
    - Parameter adjustment: type=param_adjustment, param=temperature, value=0.7
    """

    timestamp: str  # ISO 8601 format
    sequence_id: int  # Unique within session
    decision_type: str  # model_choice, routing, param_adjustment, etc.
    context: str  # Brief description (e.g., "Route inference call to cheapest provider")
    selected_value: Any  # The decision made (model name, routing policy, param value)
    alternatives: list[Any] | None = None  # Other options considered
    reasoning: str | None = None  # Why this decision was made
    confidence: float | None = None  # Confidence score (0.0-1.0) if applicable
    metadata: dict[str, Any] = field(default_factory=dict)  # Extra context

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "DecisionRecord":
        """Construct from dictionary."""
        data_copy = data.copy()
        data_copy.pop("__type__", None)
        return DecisionRecord(**data_copy)


@dataclass
class SessionRecord(SerializableMixin):
    """Metadata about a trace session.

    Appears once at the start of each trace file.
    """

    session_id: str  # Unique session identifier
    agent_id: str  # Agent/process running this session
    started_at: str  # ISO 8601 timestamp
    model_versions: dict[str, str] = field(default_factory=dict)  # Models used (claude-opus, gpt-5, etc.)
    config: dict[str, Any] = field(default_factory=dict)  # Configuration snapshot
    environment: dict[str, str] = field(default_factory=dict)  # Environment variables (redacted)
    metadata: dict[str, Any] = field(default_factory=dict)  # Extra context

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "SessionRecord":
        """Construct from dictionary."""
        data_copy = data.copy()
        data_copy.pop("__type__", None)
        return SessionRecord(**data_copy)


class TraceRecord:
    """Union type for any trace record (ToolCall, Decision, Session)."""

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Any:
        """Infer record type and construct from dictionary."""
        record_type = data.get("__type__")

        if record_type == "ToolCallRecord":
            return ToolCallRecord.from_dict(data)
        if record_type == "DecisionRecord":
            return DecisionRecord.from_dict(data)
        if record_type == "SessionRecord":
            return SessionRecord.from_dict(data)
        # Try to infer from field presence
        if "tool" in data and "result" in data:
            return ToolCallRecord.from_dict(data)
        if "decision_type" in data:
            return DecisionRecord.from_dict(data)
        if "session_id" in data and "started_at" in data:
            return SessionRecord.from_dict(data)
        raise ValueError(f"Cannot infer record type from: {data}")


class TraceFile:
    """JSONL trace file reader/writer with optional compression."""

    def __init__(self, path: str, compression: str | None = "gzip") -> None:
        """
        Initialize trace file handler.

        Args:
            path: File path for trace
            compression: 'gzip', 'zstd', or None for uncompressed
        """
        self.path = Path(path)
        self.compression = compression

        if compression == "gzip":
            self.extension = ".jsonl.gz"
        elif compression == "zstd":
            self.extension = ".jsonl.zst"
        else:
            self.extension = ".jsonl"

    def write_record(self, record: Any) -> None:
        """Append a record to the trace file."""
        data = record.to_dict() if hasattr(record, "to_dict") else record
        data["__type__"] = record.__class__.__name__

        line = json.dumps(data, default=str).decode() + "\n"

        if self.compression == "gzip":
            with gzip.open(self.path, "at", encoding="utf-8") as f:
                f.write(line)
        elif self.compression == "zstd":
            # zstd compression requires zstandard library; fallback to gzip for now
            with gzip.open(self.path, "at", encoding="utf-8") as f:
                f.write(line)
        else:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(line)

    def read_records(self) -> list[Any]:
        """Read all records from trace file."""
        records = []

        if self.compression == "gzip":
            with gzip.open(self.path, "rt", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        records.append(TraceRecord.from_dict(data))
        elif self.compression == "zstd":
            # Fallback to gzip for now
            with gzip.open(self.path, "rt", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        records.append(TraceRecord.from_dict(data))
        else:
            with open(self.path, encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        records.append(TraceRecord.from_dict(data))

        return records

    def get_file_size(self) -> int:
        """Get trace file size in bytes."""
        if self.path.exists():
            return self.path.stat().st_size
        return 0

    def delete(self) -> None:
        """Delete trace file."""
        if self.path.exists():
            self.path.unlink()


def validate_record(record: Any) -> bool:
    """Validate a trace record.

    Checks:
    - Required fields present
    - Types correct
    - Timestamps valid ISO 8601

    Returns True if valid, False otherwise.
    """
    if isinstance(record, ToolCallRecord):
        return (
            isinstance(record.timestamp, str)
            and isinstance(record.sequence_id, int)
            and isinstance(record.tool, str)
            and isinstance(record.tool_name, str)
            and isinstance(record.args, dict)
            and isinstance(record.result, dict)
        )
    if isinstance(record, DecisionRecord):
        return (
            isinstance(record.timestamp, str)
            and isinstance(record.sequence_id, int)
            and isinstance(record.decision_type, str)
        )
    if isinstance(record, SessionRecord):
        return isinstance(record.session_id, str) and isinstance(record.started_at, str)
    return False
