"""TraceRecorder: Async, non-blocking trace recording for agent execution.

Records ToolCallRecord, DecisionRecord events to JSONL files with:
- Async write worker (non-blocking)
- Sensitive data redaction (API keys, passwords)
- Result truncation (>10MB cap)
- File I/O with optional compression
- TTL-based cleanup
"""

import asyncio
import json
import logging
import re
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .schema import DecisionRecord, ToolCallRecord, TraceFile

logger = logging.getLogger(__name__)


# Sensitive field patterns (regex)
SENSITIVE_FIELD_PATTERNS = [
    r"api[_-]?key",
    r"token",
    r"secret",
    r"password",
    r"authorization",
    r"Bearer",
    r"aws[_-]?access[_-]?key",
    r"aws[_-]?secret[_-]?key",
    r"openai[_-]?api[_-]?key",
    r"anthropic[_-]?api[_-]?key",
    r"stripe[_-]?key",
    r"github[_-]?token",
]

# Compile patterns
SENSITIVE_PATTERNS = [re.compile(p, re.IGNORECASE) for p in SENSITIVE_FIELD_PATTERNS]


@dataclass
class RedactionConfig:
    """Configuration for sensitive data redaction."""

    enabled: bool = True
    patterns: list | None = None  # Override default patterns
    replace_with: str = "[REDACTED]"
    fields_to_always_redact: set[str] | None = None

    def __post_init__(self) -> None:
        """Set defaults after initialization."""
        if self.fields_to_always_redact is None:
            self.fields_to_always_redact = {
                "api_key",
                "apikey",
                "token",
                "secret",
                "password",
                "authorization",
                "aws_access_key_id",
                "aws_secret_access_key",
            }


@dataclass
class TruncationConfig:
    """Configuration for result truncation."""

    enabled: bool = True
    max_bytes: int = 10 * 1024 * 1024  # 10MB
    indicator: str = "... (truncated, see original trace)"


@dataclass
class RecorderConfig:
    """Configuration for TraceRecorder."""

    trace_dir: str = "./traces"
    compression: str | None = "gzip"  # gzip, zstd, or None
    redaction: RedactionConfig = None
    truncation: TruncationConfig = None
    async_write: bool = True
    queue_size: int = 1000  # Max pending records
    flush_interval_ms: int = 5000  # Flush every N milliseconds
    ttl_days: int = 7  # Keep traces for N days

    def __post_init__(self) -> None:
        """Set defaults after initialization."""
        if self.redaction is None:
            self.redaction = RedactionConfig()
        if self.truncation is None:
            self.truncation = TruncationConfig()


class TraceRecorder:
    """Records agent execution traces with async non-blocking writes."""

    def __init__(self, session_id: str, config: RecorderConfig | None = None) -> None:
        """
        Initialize recorder.

        Args:
            session_id: Unique session identifier
            config: RecorderConfig for customization
        """
        self.session_id = session_id
        self.config = config or RecorderConfig()
        self.trace_dir = Path(self.config.trace_dir)
        self.trace_dir.mkdir(parents=True, exist_ok=True)

        # Trace file path
        self.trace_file = TraceFile(
            str(self.trace_dir / f"{session_id}.jsonl"),
            compression=self.config.compression,
        )

        # Async write queue
        self.write_queue: asyncio.Queue = asyncio.Queue(maxsize=self.config.queue_size)
        self.write_task: asyncio.Task | None = None
        self.running = False

        # Sequence counter
        self._sequence_id = 0
        self._lock = asyncio.Lock()

        logger.info(f"TraceRecorder initialized: {session_id} -> {self.trace_file.path}")

    async def start(self) -> None:
        """Start the async write worker."""
        if self.running:
            return

        self.running = True
        self.write_task = asyncio.create_task(self._write_worker())
        logger.debug(f"TraceRecorder write worker started for {self.session_id}")

    async def stop(self) -> None:
        """Stop the recorder and flush all pending writes."""
        self.running = False

        # Signal completion
        await self.write_queue.put(None)

        # Wait for worker to finish
        if self.write_task:
            try:
                await asyncio.wait_for(self.write_task, timeout=5.0)
            except TimeoutError:
                logger.warning(f"Write worker timeout for {self.session_id}")
                self.write_task.cancel()

    async def record_tool_call(
        self,
        tool: str,
        tool_name: str,
        args: dict[str, Any],
        result: dict[str, Any],
        duration_ms: float,
        error: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Record a tool call.

        Args:
            tool: Tool type (bash, file_io, llm, etc.)
            tool_name: Specific tool name
            args: Input arguments
            result: Output result
            duration_ms: Execution time
            error: Error message if failed
            metadata: Custom metadata
        """
        async with self._lock:
            self._sequence_id += 1
            seq = self._sequence_id

        # Redact sensitive data
        redacted_args = self._redact_data(args)
        redacted_result = self._redact_data(result)

        # Track which fields were redacted
        redacted_fields = self._find_redacted_fields(args)

        # Truncate large results
        if self.config.truncation.enabled:
            redacted_result = self._truncate_result(redacted_result)

        record = ToolCallRecord(
            timestamp=datetime.now(timezone.utc).isoformat() + "Z",
            sequence_id=seq,
            tool=tool,
            tool_name=tool_name,
            args=redacted_args,
            result=redacted_result,
            duration_ms=duration_ms,
            error=error,
            redacted_fields=redacted_fields or None,
            metadata=metadata or {},
        )

        # Enqueue for async write
        if self.config.async_write:
            try:
                self.write_queue.put_nowait(record)
            except asyncio.QueueFull:
                # Fallback to synchronous write if queue full
                logger.warning("Write queue full, falling back to sync write")
                self.trace_file.write_record(record)
        else:
            # Synchronous write
            self.trace_file.write_record(record)

    async def record_decision(
        self,
        decision_type: str,
        context: str,
        selected_value: Any,
        alternatives: list | None = None,
        reasoning: str | None = None,
        confidence: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Record an LLM decision or routing choice.

        Args:
            decision_type: Type of decision (model_choice, routing, etc.)
            context: Description of decision
            selected_value: The decision made
            alternatives: Other options considered
            reasoning: Why this decision was made
            confidence: Confidence score (0.0-1.0)
            metadata: Custom metadata
        """
        async with self._lock:
            self._sequence_id += 1
            seq = self._sequence_id

        record = DecisionRecord(
            timestamp=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            sequence_id=seq,
            decision_type=decision_type,
            context=context,
            selected_value=selected_value,
            alternatives=alternatives,
            reasoning=reasoning,
            confidence=confidence,
            metadata=metadata or {},
        )

        if self.config.async_write:
            try:
                self.write_queue.put_nowait(record)
            except asyncio.QueueFull:
                logger.warning("Write queue full, falling back to sync write")
                self.trace_file.write_record(record)
        else:
            self.trace_file.write_record(record)

    def _redact_data(self, data: Any) -> Any:
        """Redact sensitive fields from data."""
        if not self.config.redaction.enabled:
            return data

        if isinstance(data, dict):
            redacted = {}
            for key, value in data.items():
                if self._is_sensitive_field(key):
                    redacted[key] = self.config.redaction.replace_with
                elif isinstance(value, (dict, list)):
                    redacted[key] = self._redact_data(value)
                else:
                    redacted[key] = value
            return redacted
        if isinstance(data, list):
            return [self._redact_data(item) for item in data]
        return data

    def _is_sensitive_field(self, field_name: str) -> bool:
        """Check if field name matches sensitive patterns."""
        # Check explicit list first
        if field_name.lower() in self.config.redaction.fields_to_always_redact:
            return True

        # Check regex patterns
        return any(pattern.search(field_name) for pattern in SENSITIVE_PATTERNS)

    def _find_redacted_fields(self, original: Any, parent_key: str = "") -> list:
        """Find which fields were redacted."""
        redacted = []

        if isinstance(original, dict):
            for key, value in original.items():
                full_key = f"{parent_key}.{key}" if parent_key else key
                if self._is_sensitive_field(key):
                    redacted.append(full_key)
                elif isinstance(value, (dict, list)):
                    redacted.extend(self._find_redacted_fields(value, full_key))

        return redacted

    def _truncate_result(self, result: dict[str, Any]) -> dict[str, Any]:
        """Truncate large results to max size."""
        # Try to serialize to check size
        try:
            serialized = json.dumps(result)
            if len(serialized.encode()) > self.config.truncation.max_bytes:
                # Truncate large fields
                truncated = result.copy()
                for key in ["stdout", "stderr", "content", "response", "body"]:
                    if key in truncated and isinstance(truncated[key], str):
                        original_size = len(truncated[key])
                        truncated[key] = truncated[key][: self.config.truncation.max_bytes // 10]
                        truncated[key] += f"\n{self.config.truncation.indicator} (original size: {original_size} bytes)"
                        truncated[f"{key}_truncated_original_size"] = original_size

                return truncated
        except (TypeError, ValueError):
            # If serialization fails, return as-is
            pass

        return result

    async def _write_worker(self) -> None:
        """Async worker that writes records from queue to file."""
        batch = []
        last_flush = asyncio.get_event_loop().time()

        while self.running or not self.write_queue.empty():
            try:
                # Wait for record with timeout
                timeout = self.config.flush_interval_ms / 1000.0
                record = await asyncio.wait_for(self.write_queue.get(), timeout=timeout)

                if record is None:
                    # Flush signal
                    self._flush_batch(batch)
                    batch = []
                    break

                batch.append(record)

                # Flush if batch gets large
                if len(batch) >= 100:
                    self._flush_batch(batch)
                    batch = []
                    last_flush = asyncio.get_event_loop().time()

            except TimeoutError:
                # Flush periodically even if no records
                if batch:
                    self._flush_batch(batch)
                    batch = []
                last_flush = asyncio.get_event_loop().time()

        # Final flush
        if batch:
            self._flush_batch(batch)

    def _flush_batch(self, batch: list) -> None:
        """Write batch of records to trace file."""
        for record in batch:
            try:
                self.trace_file.write_record(record)
            except Exception as e:
                logger.error(f"Error writing record: {e}")

    def get_trace_file_size(self) -> int:
        """Get current trace file size in bytes."""
        return self.trace_file.get_file_size()

    def delete_trace(self) -> None:
        """Delete the trace file."""
        self.trace_file.delete()
        logger.info(f"Deleted trace file: {self.trace_file.path}")


class TraceCleanup:
    """TTL-based cleanup of old trace files."""

    def __init__(self, trace_dir: str = "./traces", ttl_days: int = 7) -> None:
        """
        Initialize cleanup manager.

        Args:
            trace_dir: Directory containing trace files
            ttl_days: Keep traces for N days
        """
        self.trace_dir = Path(trace_dir)
        self.ttl_days = ttl_days

    async def cleanup_expired_traces(self) -> int:
        """
        Remove traces older than TTL.

        Returns:
            Number of traces deleted
        """
        if not self.trace_dir.exists():
            return 0

        deleted_count = 0
        cutoff_time = datetime.now(UTC) - timedelta(days=self.ttl_days)

        for trace_file in self.trace_dir.glob("*.jsonl*"):
            try:
                mtime = datetime.fromtimestamp(trace_file.stat().st_mtime, tz=timezone.utc)
                if mtime < cutoff_time:
                    trace_file.unlink()
                    deleted_count += 1
                    logger.info(f"Deleted expired trace: {trace_file.name}")
            except Exception as e:
                logger.error(f"Error deleting trace {trace_file.name}: {e}")

        return deleted_count

    async def periodic_cleanup(self, interval_hours: int = 24) -> None:
        """Run cleanup periodically."""
        while True:
            await asyncio.sleep(interval_hours * 3600)
            deleted = await self.cleanup_expired_traces()
            logger.info(f"Periodic cleanup deleted {deleted} expired traces")
