"""TraceRecorder: Asynchronous trace recording with compression and redaction."""

import asyncio
import gzip
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from .schema import (
    SessionRecord,
    create_decision_record,
    create_session_record,
    create_tool_call_record,
)


class TraceRecorder:
    """Records execution traces to compressed JSONL format.

    Features:
    - Async non-blocking recording
    - Sensitive data redaction
    - Result truncation for large outputs
    - GZIP compression
    - TTL-based cleanup
    """

    # Patterns for sensitive data redaction
    SENSITIVE_PATTERNS = [
        r"(?i)(api[_-]?key|api[_-]?token)",
        r"(?i)(password|pwd)",
        r"(?i)(secret|auth[_-]?token)",
        r"(?i)(bearer|authorization)",
        r"(?i)(user[_-]?email|email)",
        r"(?i)(credit[_-]?card|cc[_-]?number)",
        r"(?i)(ssn|social[_-]?security)",
    ]

    def __init__(
        self,
        session_id: str,
        trace_dir: Path | None = None,
        max_result_size: int = 10_000,
        enable_compression: bool = True,
        ttl_days: int = 7,
    ) -> None:
        """Initialize trace recorder.

        Args:
            session_id: Unique session identifier
            trace_dir: Directory for trace files (default: ~/.thegent/traces)
            max_result_size: Max size of result in bytes before truncation
            enable_compression: Whether to compress trace files
            ttl_days: Time-to-live for trace files
        """
        self.session_id = session_id
        self.trace_dir = Path(trace_dir or Path.home() / ".thegent" / "traces")
        self.trace_dir.mkdir(parents=True, exist_ok=True)
        self.trace_file = self.trace_dir / f"trace-{session_id}.jsonl"
        self.max_result_size = max_result_size
        self.enable_compression = enable_compression
        self.ttl_days = ttl_days

        self.call_index = 0
        self._write_queue: asyncio.Queue = asyncio.Queue()
        self._running = False
        self._write_task: asyncio.Task | None = None
        self._file_handle: Any | None = None

    async def start(self) -> None:
        """Start async recording."""
        self._running = True
        self._file_handle = open(self.trace_file, "a")
        self._write_task = asyncio.create_task(self._write_worker())

    async def stop(self) -> None:
        """Stop recording and flush all pending writes."""
        self._running = False

        # Wait for queue to empty
        while not self._write_queue.empty():
            await asyncio.sleep(0.01)

        if self._write_task:
            await self._write_task

        if self._file_handle:
            self._file_handle.close()

        if self.enable_compression:
            await self._compress_trace()

    async def record_tool_call(
        self,
        tool_name: str,
        inputs: dict[str, Any],
        result: Any,
        duration_ms: float,
        tokens_used: int = 0,
        cost: float = 0.0,
        status: str = "success",
        error_msg: str | None = None,
    ) -> None:
        """Record a tool invocation.

        Args:
            tool_name: Name of the tool
            inputs: Input parameters (will be redacted)
            result: Result from tool execution (will be truncated)
            duration_ms: Execution duration in milliseconds
            tokens_used: Token count estimate
            cost: Estimated cost of execution
            status: Execution status (success | error | timeout)
            error_msg: Error message if status is error
        """
        record = create_tool_call_record(
            tool_name=tool_name,
            session_id=self.session_id,
            call_index=self.call_index,
            inputs=self._redact_sensitive_data(tool_name, inputs),
            result=self._truncate_result(result),
            duration_ms=duration_ms,
            tokens_used=tokens_used,
            cost=cost,
            status=status,
            error_msg=error_msg,
        )
        self.call_index += 1
        await self._write_queue.put(record.to_json_line())

    async def record_decision(
        self,
        decision_type: str,
        reasoning: str,
        choice: str,
    ) -> None:
        """Record a decision point.

        Args:
            decision_type: Type of decision (routing | classification | override)
            reasoning: Reasoning for the decision
            choice: The choice made
        """
        record = create_decision_record(
            decision_type=decision_type,
            reasoning=reasoning,
            choice=choice,
            session_id=self.session_id,
        )
        await self._write_queue.put(record.to_json_line())

    async def record_session_start(
        self,
        task_id: str,
        model: str,
        provider: str,
        config: dict[str, Any] | None = None,
    ) -> None:
        """Record session start.

        Args:
            task_id: Task identifier
            model: Model name
            provider: Provider name
            config: Session configuration
        """
        record = create_session_record(
            session_id=self.session_id,
            task_id=task_id,
            model=model,
            provider=provider,
            config=config or {},
            status="started",
        )
        await self._write_queue.put(record.to_json_line())

    async def record_session_end(
        self,
        status: str = "completed",
        total_cost: float = 0.0,
        total_tokens: int = 0,
        total_duration_ms: float = 0.0,
    ) -> None:
        """Record session end.

        Args:
            status: Session status (completed | failed | cancelled)
            total_cost: Total cost for session
            total_tokens: Total tokens used
            total_duration_ms: Total execution time
        """
        record = SessionRecord(
            session_id=self.session_id,
            task_id="",
            model="",
            provider="",
            status=status,
            end_time=datetime.utcnow().isoformat(),
            total_cost=total_cost,
            total_tokens=total_tokens,
            total_duration_ms=total_duration_ms,
        )
        await self._write_queue.put(record.to_json_line())

    def _redact_sensitive_data(self, tool_name: str, inputs: dict[str, Any]) -> dict[str, Any]:
        """Redact sensitive data from inputs.

        Args:
            tool_name: Tool name for context
            inputs: Input parameters

        Returns:
            Redacted copy of inputs
        """
        redacted = {}

        for key, value in inputs.items():
            # Check if key matches sensitive patterns
            if self._is_sensitive_key(key):
                redacted[key] = "***REDACTED***"
            elif isinstance(value, dict):
                redacted[key] = self._redact_sensitive_data(tool_name, value)
            elif isinstance(value, str):
                # Check if value contains sensitive patterns
                if self._contains_sensitive_pattern(value):
                    redacted[key] = "***REDACTED***"
                else:
                    redacted[key] = value
            else:
                redacted[key] = value

        return redacted

    def _is_sensitive_key(self, key: str) -> bool:
        """Check if key name indicates sensitive data."""
        sensitive_keys = [
            "api_key",
            "api_token",
            "password",
            "secret",
            "token",
            "auth",
            "authorization",
            "bearer",
        ]
        return key.lower() in sensitive_keys or any(pattern in key.lower() for pattern in sensitive_keys)

    def _contains_sensitive_pattern(self, value: str) -> bool:
        """Check if value contains sensitive patterns."""
        try:
            for pattern in self.SENSITIVE_PATTERNS:
                if re.search(pattern, value):
                    return True
        except (TypeError, re.error):
            pass
        return False

    def _truncate_result(self, result: Any, max_size: int | None = None) -> Any:
        """Truncate large results to avoid bloat.

        Args:
            result: Result to truncate
            max_size: Max size in characters (default: self.max_result_size)

        Returns:
            Truncated result
        """
        if max_size is None:
            max_size = self.max_result_size

        try:
            if isinstance(result, str):
                if len(result) > max_size:
                    return result[:max_size] + f"... [truncated, original {len(result)} chars]"
                return result
            if isinstance(result, dict):
                result_str = json.dumps(result)
                if len(result_str) > max_size:
                    truncated = result_str[:max_size]
                    return {"_truncated": True, "data": truncated, "original_size": len(result_str)}
                return result
            if isinstance(result, (list, tuple)):
                result_str = json.dumps(list(result))
                if len(result_str) > max_size:
                    return {"_truncated": True, "count": len(result), "original_size": len(result_str)}
                return result
        except (TypeError, json.JSONDecodeError):
            pass

        return result

    async def _write_worker(self) -> None:
        """Async worker for writing trace records.

        Continuously reads from write queue and appends to trace file.
        """
        while self._running or not self._write_queue.empty():
            try:
                line = await asyncio.wait_for(self._write_queue.get(), timeout=1.0)
                if self._file_handle:
                    self._file_handle.write(line + "\n")
                    self._file_handle.flush()
                self._write_queue.task_done()
            except TimeoutError:
                continue
            except Exception as e:
                # Log error but don't crash
                pass

    async def _compress_trace(self) -> None:
        """Compress trace file after recording.

        Creates .gz compressed version of trace file.
        """
        if not self.trace_file.exists():
            return

        try:
            compressed_file = self.trace_file.with_suffix(".jsonl.gz")

            with open(self.trace_file, "rb") as f_in:
                with gzip.open(compressed_file, "wb") as f_out:
                    f_out.writelines(f_in)

            # Optionally remove uncompressed file
            # self.trace_file.unlink()

        except Exception as e:
            pass

    @staticmethod
    async def cleanup_expired_traces(trace_dir: Path | None = None, ttl_days: int = 7) -> int:
        """Clean up expired trace files.

        Args:
            trace_dir: Directory containing traces
            ttl_days: Time-to-live in days

        Returns:
            Number of files deleted
        """
        trace_dir = Path(trace_dir or Path.home() / ".thegent" / "traces")
        if not trace_dir.exists():
            return 0

        cutoff_time = datetime.utcnow() - timedelta(days=ttl_days)
        deleted_count = 0

        for trace_file in trace_dir.glob("trace-*.jsonl*"):
            try:
                mtime = datetime.fromtimestamp(trace_file.stat().st_mtime)
                if mtime < cutoff_time:
                    trace_file.unlink()
                    deleted_count += 1
            except Exception as e:
                pass

        return deleted_count

    @staticmethod
    def get_trace_stats(trace_file: Path) -> dict[str, Any]:
        """Get statistics about a trace file.

        Args:
            trace_file: Path to trace file

        Returns:
            Dictionary with stats
        """
        stats = {
            "file_size": 0,
            "compressed_size": 0,
            "record_count": 0,
            "tool_calls": 0,
            "decisions": 0,
            "errors": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
        }

        if not trace_file.exists():
            return stats

        stats["file_size"] = trace_file.stat().st_size

        # Check for compressed version
        compressed_file = trace_file.with_suffix(".jsonl.gz")
        if compressed_file.exists():
            stats["compressed_size"] = compressed_file.stat().st_size

        # Count records
        try:
            with open(trace_file) as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        record_type = data.get("type")
                        stats["record_count"] += 1

                        if record_type == "tool_call":
                            stats["tool_calls"] += 1
                            if data.get("status") == "error":
                                stats["errors"] += 1
                            stats["total_tokens"] += data.get("tokens_used", 0)
                            stats["total_cost"] += data.get("cost", 0.0)
                        elif record_type == "decision":
                            stats["decisions"] += 1
                    except json.JSONDecodeError:
                        pass
        except OSError:
            pass

        return stats
