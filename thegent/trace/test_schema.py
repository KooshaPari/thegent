"""Unit tests for trace schema."""

import json
from datetime import datetime

from .schema import (
    DecisionRecord,
    SessionRecord,
    ToolCallRecord,
    ToolStatus,
    TraceValidator,
    create_decision_record,
    create_session_record,
    create_tool_call_record,
)


class TestToolCallRecord:
    """Tests for ToolCallRecord."""

    def test_create_basic(self):
        """Test creating a basic tool call record."""
        record = ToolCallRecord(
            tool_name="read_file",
            session_id="s-123",
            call_index=0,
            inputs={"path": "test.py"},
            result="content",
            duration_ms=100.0,
        )
        assert record.tool_name == "read_file"
        assert record.session_id == "s-123"
        assert record.status == ToolStatus.SUCCESS

    def test_to_json_line(self):
        """Test serialization to JSON line."""
        record = ToolCallRecord(
            tool_name="bash",
            session_id="s-123",
            call_index=0,
            inputs={"cmd": "ls"},
            result={"stdout": "file.txt", "returncode": 0},
            duration_ms=50.0,
        )
        json_line = record.to_json_line()
        data = json.loads(json_line)

        assert data["tool_name"] == "bash"
        assert data["session_id"] == "s-123"
        assert data["status"] == ToolStatus.SUCCESS

    def test_from_json_line(self):
        """Test deserialization from JSON line."""
        json_line = json.dumps(
            {
                "type": "tool_call",
                "tool_name": "read_file",
                "session_id": "s-123",
                "call_index": 0,
                "inputs": {"path": "test.py"},
                "result": "content",
                "duration_ms": 100.0,
                "tokens_used": 0,
                "cost": 0.0,
                "status": "success",
                "error_msg": None,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": {},
            }
        )
        record = ToolCallRecord.from_json_line(json_line)

        assert record.tool_name == "read_file"
        assert record.call_index == 0
        assert record.result == "content"

    def test_round_trip_serialization(self):
        """Test serialization and deserialization round-trip."""
        original = ToolCallRecord(
            tool_name="bash",
            session_id="s-456",
            call_index=5,
            inputs={"cmd": "pytest"},
            result={"stdout": "PASSED", "returncode": 0},
            duration_ms=2000.0,
            tokens_used=100,
            cost=0.05,
        )

        json_line = original.to_json_line()
        deserialized = ToolCallRecord.from_json_line(json_line)

        assert deserialized.tool_name == original.tool_name
        assert deserialized.session_id == original.session_id
        assert deserialized.call_index == original.call_index
        assert deserialized.result == original.result

    def test_error_status(self):
        """Test recording tool error."""
        record = ToolCallRecord(
            tool_name="read_file",
            session_id="s-123",
            call_index=0,
            inputs={"path": "nonexistent.py"},
            result=None,
            duration_ms=50.0,
            status=ToolStatus.ERROR,
            error_msg="File not found",
        )
        assert record.status == ToolStatus.ERROR
        assert record.error_msg == "File not found"


class TestDecisionRecord:
    """Tests for DecisionRecord."""

    def test_create_routing_decision(self):
        """Test creating a routing decision record."""
        record = DecisionRecord(
            decision_type="routing",
            reasoning="Task has low complexity",
            choice="lifecycle_loop",
            session_id="s-123",
        )
        assert record.decision_type == "routing"
        assert record.choice == "lifecycle_loop"

    def test_to_json_line(self):
        """Test serialization to JSON line."""
        record = DecisionRecord(
            decision_type="classification",
            reasoning="Content is secure",
            choice="approved",
            session_id="s-123",
        )
        json_line = record.to_json_line()
        data = json.loads(json_line)

        assert data["decision_type"] == "classification"
        assert data["choice"] == "approved"

    def test_round_trip_serialization(self):
        """Test serialization and deserialization round-trip."""
        original = DecisionRecord(
            decision_type="routing",
            reasoning="Cost optimization",
            choice="cheapest",
            session_id="s-456",
        )

        json_line = original.to_json_line()
        deserialized = DecisionRecord.from_json_line(json_line)

        assert deserialized.decision_type == original.decision_type
        assert deserialized.reasoning == original.reasoning
        assert deserialized.choice == original.choice


class TestSessionRecord:
    """Tests for SessionRecord."""

    def test_create_session_start(self):
        """Test creating a session start record."""
        record = SessionRecord(
            session_id="s-123",
            task_id="task-refactor",
            model="claude-opus-4.6",
            provider="anthropic",
            status="started",
        )
        assert record.session_id == "s-123"
        assert record.task_id == "task-refactor"
        assert record.status == "started"

    def test_create_session_end(self):
        """Test creating a session end record."""
        record = SessionRecord(
            session_id="s-123",
            task_id="task-refactor",
            model="claude-opus-4.6",
            provider="anthropic",
            status="completed",
            total_cost=0.50,
            total_tokens=5000,
        )
        assert record.status == "completed"
        assert record.total_cost == 0.50
        assert record.total_tokens == 5000

    def test_to_json_line(self):
        """Test serialization to JSON line."""
        record = SessionRecord(
            session_id="s-123",
            task_id="task-test",
            model="gpt-5-mini",
            provider="openai",
            status="completed",
        )
        json_line = record.to_json_line()
        data = json.loads(json_line)

        assert data["session_id"] == "s-123"
        assert data["task_id"] == "task-test"

    def test_round_trip_serialization(self):
        """Test serialization and deserialization round-trip."""
        original = SessionRecord(
            session_id="s-789",
            task_id="task-xyz",
            model="gemini-3-flash",
            provider="google",
            config={"temperature": 0.7},
            status="completed",
            total_cost=0.25,
            total_tokens=2500,
        )

        json_line = original.to_json_line()
        deserialized = SessionRecord.from_json_line(json_line)

        assert deserialized.session_id == original.session_id
        assert deserialized.task_id == original.task_id
        assert deserialized.total_cost == original.total_cost


class TestTraceValidator:
    """Tests for TraceValidator."""

    def test_validate_valid_tool_call_record(self):
        """Test validation of valid tool call record."""
        record = ToolCallRecord(
            tool_name="read_file",
            session_id="s-123",
            call_index=0,
            inputs={"path": "test.py"},
            result="content",
            duration_ms=100.0,
        )
        assert TraceValidator.validate_tool_call_record(record)

    def test_validate_invalid_tool_call_record_missing_name(self):
        """Test validation fails with missing tool name."""
        record = ToolCallRecord(
            tool_name="",
            session_id="s-123",
            call_index=0,
        )
        assert not TraceValidator.validate_tool_call_record(record)

    def test_validate_invalid_tool_call_record_negative_index(self):
        """Test validation fails with negative call index."""
        record = ToolCallRecord(
            tool_name="read_file",
            session_id="s-123",
            call_index=-1,
        )
        assert not TraceValidator.validate_tool_call_record(record)

    def test_validate_valid_decision_record(self):
        """Test validation of valid decision record."""
        record = DecisionRecord(
            decision_type="routing",
            reasoning="test",
            choice="choice",
            session_id="s-123",
        )
        assert TraceValidator.validate_decision_record(record)

    def test_validate_invalid_decision_record_missing_type(self):
        """Test validation fails with missing decision type."""
        record = DecisionRecord(
            decision_type="",
            reasoning="test",
            choice="choice",
            session_id="s-123",
        )
        assert not TraceValidator.validate_decision_record(record)

    def test_validate_valid_session_record(self):
        """Test validation of valid session record."""
        record = SessionRecord(
            session_id="s-123",
            task_id="task",
            model="claude",
            provider="anthropic",
        )
        assert TraceValidator.validate_session_record(record)

    def test_validate_invalid_session_record_missing_model(self):
        """Test validation fails with missing model."""
        record = SessionRecord(
            session_id="s-123",
            task_id="task",
            model="",
            provider="anthropic",
        )
        assert not TraceValidator.validate_session_record(record)

    def test_validate_jsonl_file_valid(self, tmp_path):
        """Test validation of valid JSONL file."""
        trace_file = tmp_path / "trace.jsonl"

        records = [
            ToolCallRecord(
                tool_name="read_file",
                session_id="s-123",
                call_index=0,
                inputs={"path": "test.py"},
                result="content",
                duration_ms=100.0,
            ),
            DecisionRecord(
                decision_type="routing",
                reasoning="test",
                choice="choice",
                session_id="s-123",
            ),
        ]

        with open(trace_file, "w") as f:
            f.writelines(record.to_json_line() + "\n" for record in records)

        is_valid, errors = TraceValidator.validate_jsonl_file(str(trace_file))
        assert is_valid
        assert len(errors) == 0

    def test_validate_jsonl_file_invalid_json(self, tmp_path):
        """Test validation detects invalid JSON."""
        trace_file = tmp_path / "trace.jsonl"

        with open(trace_file, "w") as f:
            f.write('{"invalid json\n')

        is_valid, errors = TraceValidator.validate_jsonl_file(str(trace_file))
        assert not is_valid
        assert len(errors) > 0

    def test_validate_jsonl_file_missing_file(self):
        """Test validation handles missing file."""
        is_valid, errors = TraceValidator.validate_jsonl_file("/nonexistent/trace.jsonl")
        assert not is_valid
        assert len(errors) > 0


class TestHelperFunctions:
    """Tests for helper factory functions."""

    def test_create_tool_call_record(self):
        """Test creating tool call record with helper."""
        record = create_tool_call_record(
            tool_name="bash",
            session_id="s-123",
            call_index=0,
            inputs={"cmd": "ls"},
            result={"stdout": "file.txt"},
            duration_ms=100.0,
            tokens_used=50,
            cost=0.01,
        )
        assert record.tool_name == "bash"
        assert record.tokens_used == 50
        assert record.cost == 0.01
        assert record.timestamp  # Should be set automatically

    def test_create_decision_record(self):
        """Test creating decision record with helper."""
        record = create_decision_record(
            decision_type="routing",
            session_id="s-123",
            reasoning="Cost optimization",
            choice="cheapest",
        )
        assert record.decision_type == "routing"
        assert record.choice == "cheapest"
        assert record.timestamp  # Should be set automatically

    def test_create_session_record(self):
        """Test creating session record with helper."""
        record = create_session_record(
            session_id="s-123",
            task_id="task",
            model="claude",
            provider="anthropic",
            config={"temperature": 0.7},
        )
        assert record.session_id == "s-123"
        assert record.config["temperature"] == 0.7
        assert record.start_time  # Should be set automatically
        assert record.status == "started"
