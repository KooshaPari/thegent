"""Integration tests for TraceRecorder with simulated agent workflows."""

import asyncio
import json
import tempfile
from pathlib import Path

import pytest

from .recorder import TraceRecorder
from .schema import TraceValidator


@pytest.fixture
def temp_trace_dir():
    """Create temporary directory for traces."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestTraceRecorderIntegration:
    """Integration tests for TraceRecorder."""

    @pytest.mark.asyncio
    async def test_realistic_workflow_recording(self, temp_trace_dir):
        """Test recording a realistic multi-step workflow."""
        recorder = TraceRecorder("s-workflow-1", trace_dir=temp_trace_dir, enable_compression=False)

        await recorder.start()

        # Simulate workflow
        await recorder.record_session_start(
            task_id="task-refactor-auth",
            model="claude-opus-4.6",
            provider="anthropic",
            config={"temperature": 0.7, "max_tokens": 4096},
        )

        # Step 1: Read file
        await recorder.record_tool_call(
            tool_name="read_file",
            inputs={"path": "src/auth.py"},
            result="# Auth module\nclass Auth:\n    pass",
            duration_ms=150.0,
            tokens_used=200,
            cost=0.001,
        )

        # Step 2: LLM analysis
        await recorder.record_decision(
            decision_type="routing",
            reasoning="Task involves code analysis - using high-capability model",
            choice="claude-opus-4.6",
        )

        await recorder.record_tool_call(
            tool_name="llm_call",
            inputs={"prompt": "Analyze this code...", "model": "claude-opus-4.6"},
            result="The auth module needs refactoring...",
            duration_ms=5000.0,
            tokens_used=2000,
            cost=0.05,
        )

        # Step 3: Write refactored file
        await recorder.record_tool_call(
            tool_name="write_file",
            inputs={"path": "src/auth.py", "content": "# Refactored Auth..."},
            result="success",
            duration_ms=100.0,
            tokens_used=0,
            cost=0.0,
        )

        # Step 4: Run tests
        await recorder.record_tool_call(
            tool_name="bash",
            inputs={"cmd": "pytest tests/test_auth.py -v"},
            result={
                "stdout": "tests/test_auth.py::test_login PASSED",
                "stderr": "",
                "returncode": 0,
            },
            duration_ms=3000.0,
            tokens_used=0,
            cost=0.0,
        )

        await recorder.record_session_end(
            status="completed",
            total_cost=0.051,
            total_tokens=2200,
            total_duration_ms=8250.0,
        )

        await recorder.stop()

        # Verify trace file
        assert recorder.trace_file.exists()

        with open(recorder.trace_file) as f:
            lines = [line for line in f if line.strip()]
            assert len(lines) == 7  # 1 session start + 5 tool calls + 1 session end

        # Validate file format
        is_valid, errors = TraceValidator.validate_jsonl_file(str(recorder.trace_file))
        assert is_valid, f"Trace validation failed: {errors}"

    @pytest.mark.asyncio
    async def test_workflow_with_errors(self, temp_trace_dir):
        """Test recording workflow with errors and fallbacks."""
        recorder = TraceRecorder("s-workflow-error", trace_dir=temp_trace_dir, enable_compression=False)

        await recorder.start()

        await recorder.record_session_start(
            task_id="task-error-handling",
            model="claude-sonnet-4.5",
            provider="anthropic",
        )

        # First attempt fails
        await recorder.record_tool_call(
            tool_name="read_file",
            inputs={"path": "nonexistent.py"},
            result=None,
            duration_ms=50.0,
            status="error",
            error_msg="File not found: nonexistent.py",
        )

        # Fallback decision
        await recorder.record_decision(
            decision_type="fallback",
            reasoning="File not found, trying alternate path",
            choice="use_default_template",
        )

        # Second attempt succeeds
        await recorder.record_tool_call(
            tool_name="read_file",
            inputs={"path": "templates/default.py"},
            result="# Default template",
            duration_ms=80.0,
            tokens_used=100,
            cost=0.001,
        )

        await recorder.record_session_end(
            status="completed",
            total_cost=0.001,
            total_tokens=100,
        )

        await recorder.stop()

        # Verify trace
        with open(recorder.trace_file) as f:
            lines = [line for line in f if line.strip()]
            data = [json.loads(line) for line in lines]

            # Find error record
            error_records = [d for d in data if d.get("status") == "error"]
            assert len(error_records) == 1
            assert "not found" in error_records[0]["error_msg"].lower()

            # Find fallback decision
            decisions = [d for d in data if d.get("type") == "decision"]
            fallback_decisions = [d for d in decisions if d.get("decision_type") == "fallback"]
            assert len(fallback_decisions) == 1

    @pytest.mark.asyncio
    async def test_sensitive_data_in_workflow(self, temp_trace_dir):
        """Test that sensitive data is redacted in realistic workflow."""
        recorder = TraceRecorder("s-sensitive", trace_dir=temp_trace_dir, enable_compression=False)

        await recorder.start()

        await recorder.record_tool_call(
            tool_name="api_call",
            inputs={
                "url": "https://api.example.com/data",
                "api_key": "sk-1234567890abcdef",
                "headers": {
                    "Authorization": "Bearer token123",
                    "User-Agent": "thegent/1.0",
                },
            },
            result={"status": "success", "data": [1, 2, 3]},
            duration_ms=500.0,
        )

        await recorder.stop()

        # Verify redaction
        with open(recorder.trace_file) as f:
            line = f.readline()
            data = json.loads(line)

            # API key should be redacted
            assert data["inputs"]["api_key"] == "***REDACTED***"
            # URL and User-Agent should be preserved
            assert "api.example.com" in data["inputs"]["url"]
            assert "thegent/1.0" in data["inputs"]["headers"]["User-Agent"]
            # Authorization should be redacted
            assert data["inputs"]["headers"]["Authorization"] == "***REDACTED***"

    @pytest.mark.asyncio
    async def test_high_volume_recording_performance(self, temp_trace_dir):
        """Test performance with high-volume recording (100+ calls)."""
        import time

        recorder = TraceRecorder("s-perf", trace_dir=temp_trace_dir, enable_compression=False)

        await recorder.start()

        start_time = time.time()

        # Record 100 tool calls
        for i in range(100):
            await recorder.record_tool_call(
                tool_name=f"tool_{i % 5}",
                inputs={"index": i, "data": "x" * 100},
                result=f"result_{i}" * 10,
                duration_ms=10.0 + i,
                tokens_used=50 + i,
                cost=0.001 * (i + 1),
            )

        await recorder.stop()

        elapsed = time.time() - start_time

        # Verify all records were written
        with open(recorder.trace_file) as f:
            lines = [line for line in f if line.strip()]
            assert len(lines) == 100

        # Overhead should be minimal (recording should be fast)
        # Estimate: ~100 calls at ~10ms each = 1s, plus recorder overhead
        assert elapsed < 10.0  # Should be well under 10 seconds

    @pytest.mark.asyncio
    async def test_concurrent_tool_calls_recording(self, temp_trace_dir):
        """Test that concurrent tool calls are recorded correctly."""
        recorder = TraceRecorder("s-concurrent", trace_dir=temp_trace_dir, enable_compression=False)

        await recorder.start()

        # Create concurrent tasks
        tasks = []
        for i in range(10):
            task = recorder.record_tool_call(
                tool_name="parallel_task",
                inputs={"id": i},
                result=f"result_{i}",
                duration_ms=50.0,
            )
            tasks.append(task)

        # Wait for all to complete
        await asyncio.gather(*tasks)
        await recorder.stop()

        # Verify all calls were recorded
        with open(recorder.trace_file) as f:
            lines = [line for line in f if line.strip()]
            assert len(lines) == 10

        # Verify call indices are sequential
        with open(recorder.trace_file) as f:
            for i, line in enumerate(f):
                if line.strip():
                    data = json.loads(line)
                    # Call indices might not be in order due to async,
                    # but each should be unique and 0-9
                    assert 0 <= data["call_index"] < 10

    @pytest.mark.asyncio
    async def test_trace_compression_ratio_realistic(self, temp_trace_dir):
        """Test compression ratio on realistic trace data."""
        recorder = TraceRecorder("s-compress", trace_dir=temp_trace_dir, enable_compression=True)

        await recorder.start()

        # Record realistic workflow
        await recorder.record_session_start(
            task_id="task-large",
            model="claude-opus-4.6",
            provider="anthropic",
            config={"temperature": 0.7, "max_tokens": 4096},
        )

        for i in range(50):
            await recorder.record_tool_call(
                tool_name="read_file",
                inputs={"path": f"src/module_{i}.py"},
                result="# Module {}\n" * 50,  # Repeating content for compression
                duration_ms=100.0 + i,
                tokens_used=500 + i,
                cost=0.01 + i * 0.001,
            )

        await recorder.record_session_end(
            status="completed",
            total_cost=0.5,
            total_tokens=25000,
        )

        await recorder.stop()

        # Check compression ratio
        uncompressed_size = recorder.trace_file.stat().st_size
        compressed_file = temp_trace_dir / "trace-s-compress.jsonl.gz"
        compressed_size = compressed_file.stat().st_size

        compression_ratio = compressed_size / uncompressed_size

        # Should achieve >50% compression
        assert compression_ratio < 0.5, f"Compression only {compression_ratio:.2%}, expected >50%"

    @pytest.mark.asyncio
    async def test_replay_compatibility(self, temp_trace_dir):
        """Test that recorded traces are compatible with replay (structure check)."""
        recorder = TraceRecorder("s-replay-compat", trace_dir=temp_trace_dir, enable_compression=False)

        await recorder.start()

        # Record session with various record types
        await recorder.record_session_start(
            task_id="task-test",
            model="test-model",
            provider="test-provider",
        )

        await recorder.record_tool_call(
            tool_name="test_tool",
            inputs={"param": "value"},
            result="test_result",
            duration_ms=100.0,
        )

        await recorder.record_decision(
            decision_type="test",
            reasoning="test reasoning",
            choice="test_choice",
        )

        await recorder.record_session_end(status="completed")

        await recorder.stop()

        # Load and verify records can be deserialized
        from .schema import DecisionRecord, SessionRecord, ToolCallRecord

        with open(recorder.trace_file) as f:
            for line in f:
                if not line.strip():
                    continue

                data = json.loads(line)
                record_type = data.get("type")

                if record_type == "tool_call":
                    record = ToolCallRecord.from_json_line(line)
                    assert record.tool_name == "test_tool"
                elif record_type == "decision":
                    record = DecisionRecord.from_json_line(line)
                    assert record.decision_type == "test"
                elif record_type == "session":
                    record = SessionRecord.from_json_line(line)
                    assert record.task_id in ["", "task-test"]
