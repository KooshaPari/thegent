"""Unit tests for TraceRecorder."""

import gzip
import json
import tempfile
import time
from pathlib import Path

import pytest

from .recorder import TraceRecorder


@pytest.fixture
def temp_trace_dir():
    """Create temporary directory for traces."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestTraceRecorderBasics:
    """Basic TraceRecorder tests."""

    def test_create_recorder(self, temp_trace_dir):
        """Test creating a trace recorder."""
        recorder = TraceRecorder("s-123", trace_dir=temp_trace_dir)

        assert recorder.session_id == "s-123"
        assert recorder.trace_dir == temp_trace_dir
        assert recorder.trace_file == temp_trace_dir / "trace-s-123.jsonl"

    def test_trace_dir_created(self, temp_trace_dir):
        """Test that trace directory is created on init."""
        test_dir = temp_trace_dir / "new_traces"
        recorder = TraceRecorder("s-123", trace_dir=test_dir)

        assert test_dir.exists()

    @pytest.mark.asyncio
    async def test_start_stop_recorder(self, temp_trace_dir):
        """Test starting and stopping recorder."""
        recorder = TraceRecorder("s-123", trace_dir=temp_trace_dir)

        await recorder.start()
        assert recorder._running
        assert recorder._write_task is not None

        await recorder.stop()
        assert not recorder._running
        assert recorder.trace_file.exists()

    @pytest.mark.asyncio
    async def test_record_single_tool_call(self, temp_trace_dir):
        """Test recording a single tool call."""
        recorder = TraceRecorder("s-123", trace_dir=temp_trace_dir, enable_compression=False)

        await recorder.start()
        await recorder.record_tool_call(
            tool_name="read_file",
            inputs={"path": "test.py"},
            result="content",
            duration_ms=100.0,
            tokens_used=50,
            cost=0.01,
        )
        await recorder.stop()

        # Verify file was created
        assert recorder.trace_file.exists()

        # Verify content
        with open(recorder.trace_file) as f:
            lines = f.readlines()
            assert len(lines) == 1

            data = json.loads(lines[0])
            assert data["tool_name"] == "read_file"
            assert data["session_id"] == "s-123"
            assert data["result"] == "content"

    @pytest.mark.asyncio
    async def test_record_multiple_tool_calls(self, temp_trace_dir):
        """Test recording multiple tool calls."""
        recorder = TraceRecorder("s-123", trace_dir=temp_trace_dir, enable_compression=False)

        await recorder.start()
        for i in range(5):
            await recorder.record_tool_call(
                tool_name=f"tool_{i}",
                inputs={"index": i},
                result=f"result_{i}",
                duration_ms=10.0 * (i + 1),
            )
        await recorder.stop()

        with open(recorder.trace_file) as f:
            lines = [line for line in f if line.strip()]
            assert len(lines) == 5

            for i, line in enumerate(lines):
                data = json.loads(line)
                assert data["tool_name"] == f"tool_{i}"
                assert data["call_index"] == i

    @pytest.mark.asyncio
    async def test_record_decision(self, temp_trace_dir):
        """Test recording a decision."""
        recorder = TraceRecorder("s-123", trace_dir=temp_trace_dir, enable_compression=False)

        await recorder.start()
        await recorder.record_decision(
            decision_type="routing",
            reasoning="Cost optimization",
            choice="cheapest",
        )
        await recorder.stop()

        with open(recorder.trace_file) as f:
            lines = [line for line in f if line.strip()]
            assert len(lines) == 1

            data = json.loads(lines[0])
            assert data["type"] == "decision"
            assert data["decision_type"] == "routing"

    @pytest.mark.asyncio
    async def test_record_session_lifecycle(self, temp_trace_dir):
        """Test recording session start and end."""
        recorder = TraceRecorder("s-123", trace_dir=temp_trace_dir, enable_compression=False)

        await recorder.start()
        await recorder.record_session_start(
            task_id="task-1",
            model="claude-opus",
            provider="anthropic",
            config={"temperature": 0.7},
        )
        await recorder.record_tool_call(
            tool_name="bash",
            inputs={"cmd": "echo hello"},
            result={"stdout": "hello"},
            duration_ms=50.0,
        )
        await recorder.record_session_end(
            status="completed",
            total_cost=0.05,
            total_tokens=500,
            total_duration_ms=50.0,
        )
        await recorder.stop()

        with open(recorder.trace_file) as f:
            lines = [line for line in f if line.strip()]
            assert len(lines) == 3

            # Check session start
            data0 = json.loads(lines[0])
            assert data0["type"] == "session"
            assert data0["status"] == "started"

            # Check tool call
            data1 = json.loads(lines[1])
            assert data1["type"] == "tool_call"

            # Check session end
            data2 = json.loads(lines[2])
            assert data2["type"] == "session"
            assert data2["status"] == "completed"
            assert data2["total_cost"] == 0.05


class TestSensitiveDataRedaction:
    """Tests for sensitive data redaction."""

    def test_redact_api_key_in_inputs(self, temp_trace_dir):
        """Test redaction of API key."""
        recorder = TraceRecorder("s-123", trace_dir=temp_trace_dir)

        inputs = {"api_key": "secret123", "url": "https://example.com"}
        redacted = recorder._redact_sensitive_data("test_tool", inputs)

        assert redacted["api_key"] == "***REDACTED***"
        assert redacted["url"] == "https://example.com"

    def test_redact_password(self, temp_trace_dir):
        """Test redaction of password."""
        recorder = TraceRecorder("s-123", trace_dir=temp_trace_dir)

        inputs = {"password": "mypassword", "username": "user"}
        redacted = recorder._redact_sensitive_data("test_tool", inputs)

        assert redacted["password"] == "***REDACTED***"
        assert redacted["username"] == "user"

    def test_redact_auth_token(self, temp_trace_dir):
        """Test redaction of auth token."""
        recorder = TraceRecorder("s-123", trace_dir=temp_trace_dir)

        inputs = {"auth_token": "token123", "request_id": "req-123"}
        redacted = recorder._redact_sensitive_data("test_tool", inputs)

        assert redacted["auth_token"] == "***REDACTED***"
        assert redacted["request_id"] == "req-123"

    def test_redact_nested_dict(self, temp_trace_dir):
        """Test redaction in nested dictionaries."""
        recorder = TraceRecorder("s-123", trace_dir=temp_trace_dir)

        inputs = {"outer": {"api_key": "secret123", "data": "normal"}}
        redacted = recorder._redact_sensitive_data("test_tool", inputs)

        assert redacted["outer"]["api_key"] == "***REDACTED***"
        assert redacted["outer"]["data"] == "normal"

    def test_no_redaction_when_not_sensitive(self, temp_trace_dir):
        """Test that non-sensitive data is not redacted."""
        recorder = TraceRecorder("s-123", trace_dir=temp_trace_dir)

        inputs = {"path": "/tmp/file.txt", "count": 10}
        redacted = recorder._redact_sensitive_data("test_tool", inputs)

        assert redacted["path"] == "/tmp/file.txt"
        assert redacted["count"] == 10

    def test_is_sensitive_key(self, temp_trace_dir):
        """Test sensitive key detection."""
        recorder = TraceRecorder("s-123", trace_dir=temp_trace_dir)

        assert recorder._is_sensitive_key("api_key")
        assert recorder._is_sensitive_key("API_KEY")
        assert recorder._is_sensitive_key("password")
        assert recorder._is_sensitive_key("auth_token")
        assert not recorder._is_sensitive_key("url")
        assert not recorder._is_sensitive_key("path")


class TestResultTruncation:
    """Tests for result truncation."""

    def test_truncate_short_string(self, temp_trace_dir):
        """Test that short strings are not truncated."""
        recorder = TraceRecorder("s-123", trace_dir=temp_trace_dir, max_result_size=1000)

        result = "short result"
        truncated = recorder._truncate_result(result)

        assert truncated == "short result"

    def test_truncate_long_string(self, temp_trace_dir):
        """Test that long strings are truncated."""
        recorder = TraceRecorder("s-123", trace_dir=temp_trace_dir, max_result_size=50)

        result = "x" * 200
        truncated = recorder._truncate_result(result)

        assert isinstance(truncated, str)
        assert len(truncated) < len(result)
        assert "truncated" in truncated.lower()

    def test_truncate_large_dict(self, temp_trace_dir):
        """Test that large dictionaries are truncated."""
        recorder = TraceRecorder("s-123", trace_dir=temp_trace_dir, max_result_size=100)

        result = {"data": "x" * 500}
        truncated = recorder._truncate_result(result)

        assert isinstance(truncated, dict)
        assert truncated.get("_truncated") is True

    def test_truncate_large_list(self, temp_trace_dir):
        """Test that large lists are truncated."""
        recorder = TraceRecorder("s-123", trace_dir=temp_trace_dir, max_result_size=100)

        result = list(range(1000))
        truncated = recorder._truncate_result(result)

        assert isinstance(truncated, dict)
        assert truncated.get("_truncated") is True
        assert truncated.get("count") == 1000


class TestCompression:
    """Tests for trace file compression."""

    @pytest.mark.asyncio
    async def test_compression_enabled(self, temp_trace_dir):
        """Test that compression is applied when enabled."""
        recorder = TraceRecorder(
            "s-123",
            trace_dir=temp_trace_dir,
            enable_compression=True,
        )

        await recorder.start()
        await recorder.record_tool_call(
            tool_name="read_file",
            inputs={"path": "test.py"},
            result="x" * 1000,
            duration_ms=100.0,
        )
        await recorder.stop()

        # Check that .gz file exists
        compressed_file = temp_trace_dir / "trace-s-123.jsonl.gz"
        assert compressed_file.exists()

        # Verify compression worked
        with gzip.open(compressed_file, "rt") as f:
            content = f.read()
            assert "read_file" in content

    @pytest.mark.asyncio
    async def test_compression_ratio(self, temp_trace_dir):
        """Test that compression achieves good ratio."""
        recorder = TraceRecorder(
            "s-123",
            trace_dir=temp_trace_dir,
            enable_compression=True,
        )

        await recorder.start()
        for i in range(100):
            await recorder.record_tool_call(
                tool_name="read_file",
                inputs={"path": f"file_{i}.py"},
                result="x" * 500,
                duration_ms=100.0,
            )
        await recorder.stop()

        uncompressed_size = recorder.trace_file.stat().st_size
        compressed_file = temp_trace_dir / "trace-s-123.jsonl.gz"
        compressed_size = compressed_file.stat().st_size

        compression_ratio = compressed_size / uncompressed_size
        # Should achieve >50% compression for repetitive data
        assert compression_ratio < 0.5


class TestCleanup:
    """Tests for TTL cleanup."""

    @pytest.mark.asyncio
    async def test_cleanup_expired_traces(self, temp_trace_dir):
        """Test cleanup of expired traces."""
        import os

        # Create old trace file
        old_file = temp_trace_dir / "trace-old.jsonl"
        old_file.write_text("old trace")

        # Set modification time to old date (10 days ago)
        old_time = time.time() - (10 * 24 * 3600)
        os.utime(old_file, (old_time, old_time))

        # Create recent trace file
        recent_file = temp_trace_dir / "trace-recent.jsonl"
        recent_file.write_text("recent trace")

        # Cleanup with 7 day TTL
        deleted = await TraceRecorder.cleanup_expired_traces(trace_dir=temp_trace_dir, ttl_days=7)

        assert deleted >= 1
        assert not old_file.exists()
        assert recent_file.exists()


class TestTraceStats:
    """Tests for trace statistics."""

    def test_get_trace_stats_empty_file(self, temp_trace_dir):
        """Test stats for empty trace file."""
        trace_file = temp_trace_dir / "trace.jsonl"
        trace_file.write_text("")

        stats = TraceRecorder.get_trace_stats(trace_file)

        assert stats["record_count"] == 0
        assert stats["tool_calls"] == 0

    def test_get_trace_stats_with_records(self, temp_trace_dir):
        """Test stats for trace file with records."""
        trace_file = temp_trace_dir / "trace.jsonl"

        with open(trace_file, "w") as f:
            # Write 3 tool calls and 1 decision
            for i in range(3):
                record = {
                    "type": "tool_call",
                    "tool_name": f"tool_{i}",
                    "session_id": "s-123",
                    "call_index": i,
                    "inputs": {},
                    "result": None,
                    "duration_ms": 100.0,
                    "tokens_used": 50,
                    "cost": 0.01,
                    "status": "success",
                }
                f.write(json.dumps(record) + "\n")

            record = {
                "type": "decision",
                "decision_type": "routing",
                "session_id": "s-123",
            }
            f.write(json.dumps(record) + "\n")

        stats = TraceRecorder.get_trace_stats(trace_file)

        assert stats["record_count"] == 4
        assert stats["tool_calls"] == 3
        assert stats["decisions"] == 1
        assert stats["total_tokens"] == 150
        assert stats["total_cost"] == 0.03

    def test_get_trace_stats_nonexistent_file(self):
        """Test stats for nonexistent file."""
        stats = TraceRecorder.get_trace_stats(Path("/nonexistent/trace.jsonl"))

        assert stats["record_count"] == 0
        assert stats["tool_calls"] == 0
