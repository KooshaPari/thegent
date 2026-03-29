"""
Test suite for policy-gate CLI.

Tests cover:
- Request submission (valid/invalid)
- Status updates (approve/deny)
- Status checking
- History retrieval
- Database integrity
"""

import pytest
import sqlite3
import json
from unittest.mock import patch
from typer.testing import CliRunner
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app, ensure_db, generate_request_id


@pytest.fixture
def temp_db(tmp_path):
    """Create a temporary database for testing."""
    db_path = tmp_path / "policy-requests.db"
    with patch("main.DB_PATH", db_path):
        with patch("main.DB_DIR", tmp_path):
            yield db_path


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_db(temp_db):
    """Mock the database path for all tests."""
    with patch("main.DB_PATH", temp_db):
        with patch("main.DB_DIR", temp_db.parent):
            yield temp_db


class TestDatabaseSetup:
    """Tests for database creation and initialization."""

    def test_ensure_db_creates_directory(self, tmp_path):
        """Ensure database creation creates parent directory."""
        with patch("main.DB_PATH", tmp_path / "subdir" / "policy.db"):
            with patch("main.DB_DIR", tmp_path / "subdir"):
                ensure_db()
                assert (tmp_path / "subdir").exists()

    def test_ensure_db_creates_schema(self, temp_db):
        """Ensure database schema is created correctly."""
        with patch("main.DB_PATH", temp_db):
            ensure_db()
            conn = sqlite3.connect(temp_db)
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='policy_requests'"
            )
            assert cursor.fetchone() is not None
            conn.close()

    def test_schema_has_required_columns(self, temp_db):
        """Verify all required columns exist in schema."""
        with patch("main.DB_PATH", temp_db):
            ensure_db()
            conn = sqlite3.connect(temp_db)
            cursor = conn.execute("PRAGMA table_info(policy_requests)")
            columns = {row[1] for row in cursor.fetchall()}

            required = {
                "id", "policy_name", "change_description", "requester",
                "status", "requested_at", "reviewed_by", "reviewed_at",
                "review_reason", "metadata"
            }
            assert required.issubset(columns)
            conn.close()


class TestRequestGeneration:
    """Tests for request ID generation."""

    def test_request_id_format(self):
        """Request ID should follow POL-{POLICY}-{HASH} format."""
        req_id = generate_request_id("agent-escalation", "2026-03-28T12:00:00Z")
        assert req_id.startswith("POL-")
        # Format: POL-{POLICY_PART}-{HASH}, policy with dashes creates extra dashes
        assert req_id.count("-") >= 2
        assert len(req_id) > 15  # POL- (4) + policy part + hash (8) and dashes

    def test_request_id_uniqueness(self):
        """Different timestamps should generate different IDs."""
        id1 = generate_request_id("test-policy", "2026-03-28T12:00:00Z")
        id2 = generate_request_id("test-policy", "2026-03-28T12:00:01Z")
        assert id1 != id2

    def test_request_id_policy_in_name(self):
        """Policy name should be in request ID."""
        id1 = generate_request_id("dataretention", "2026-03-28T12:00:00Z")
        id2 = generate_request_id("agentescalation", "2026-03-28T12:00:00Z")
        # Both should have policy names (different first parts)
        assert "DATAR" in id1
        assert "AGENT" in id2


class TestSubmitRequest:
    """Tests for request submission."""

    def test_submit_valid_request(self, runner, mock_db):
        """Submit a valid policy change request."""
        result = runner.invoke(app, [
            "request",
            "--policy", "agent-escalation",
            "--change", "Allow agents to request elevated access",
            "--requester", "planner-agent-001",
        ])
        assert result.exit_code == 0
        assert "Request submitted" in result.stdout
        assert "POL-" in result.stdout

    def test_submit_request_with_metadata(self, runner, mock_db):
        """Submit request with JSON metadata."""
        metadata = json.dumps({"priority": "high", "tags": ["security", "audit"]})
        result = runner.invoke(app, [
            "request",
            "--policy", "data-retention",
            "--change", "Extend retention to 90 days",
            "--requester", "impl-agent-002",
            "--metadata", metadata,
        ])
        assert result.exit_code == 0

    def test_submit_request_invalid_metadata(self, runner, mock_db):
        """Submit request with invalid JSON metadata."""
        result = runner.invoke(app, [
            "request",
            "--policy", "test",
            "--change", "test",
            "--requester", "agent",
            "--metadata", "{invalid json}",
        ])
        assert result.exit_code == 1
        assert "invalid JSON metadata" in result.stdout

    def test_submit_request_required_fields(self, runner, mock_db):
        """All required fields must be provided."""
        # Missing required option
        result = runner.invoke(app, [
            "request",
            "--policy", "test-policy",
        ])
        assert result.exit_code != 0

    def test_submit_request_creates_db_entry(self, runner, mock_db):
        """Submitted request should be in database."""
        runner.invoke(app, [
            "request",
            "--policy", "test-policy",
            "--change", "Test change",
            "--requester", "test-agent",
        ])

        with patch("main.DB_PATH", mock_db):
            conn = sqlite3.connect(mock_db)
            cursor = conn.execute("SELECT COUNT(*) FROM policy_requests")
            count = cursor.fetchone()[0]
            assert count == 1
            conn.close()

    def test_submit_request_sets_status_pending(self, runner, mock_db):
        """Submitted request should have pending status."""
        result = runner.invoke(app, [
            "request",
            "--policy", "test-policy",
            "--change", "Test change",
            "--requester", "test-agent",
        ])

        # Extract ID from output
        lines = result.stdout.split("\n")
        req_id = None
        for line in lines:
            if "ID:" in line:
                req_id = line.split(":")[-1].strip()
                break

        assert req_id

        with patch("main.DB_PATH", mock_db):
            conn = sqlite3.connect(mock_db)
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT status FROM policy_requests WHERE id = ?", (req_id,))
            row = cursor.fetchone()
            assert row["status"] == "pending"
            conn.close()


class TestListRequests:
    """Tests for listing requests."""

    def test_list_no_requests(self, runner, mock_db):
        """Listing with no requests shows message."""
        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "No requests found" in result.stdout

    def test_list_pending_requests(self, runner, mock_db):
        """List shows pending requests by default."""
        # Create a pending request
        runner.invoke(app, [
            "request",
            "--policy", "test-policy",
            "--change", "Test change",
            "--requester", "test-agent",
        ])

        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "test-policy" in result.stdout
        assert "pending" in result.stdout

    def test_list_filter_by_status(self, runner, mock_db):
        """List can filter by status."""
        with patch("main.DB_PATH", mock_db):
            # Create a pending request
            result = runner.invoke(app, [
                "request",
                "--policy", "policy-1",
                "--change", "Change 1",
                "--requester", "agent-1",
            ])
            assert result.exit_code == 0

            # Extract the actual ID from the request output
            lines = result.stdout.split("\n")
            req_id = None
            for line in lines:
                if "ID:" in line:
                    req_id = line.split(":")[-1].strip()
                    break

            assert req_id is not None

            # Approve the request
            result = runner.invoke(app, ["approve", req_id])
            assert result.exit_code == 0

            # After approve, list --status pending should be empty
            result = runner.invoke(app, ["list", "--status", "pending"])
            assert "No requests found" in result.stdout

            # List --status approved should show the request
            result = runner.invoke(app, ["list", "--status", "approved"])
            assert result.exit_code == 0
            assert "policy-1" in result.stdout

    def test_list_filter_by_policy(self, runner, mock_db):
        """List can filter by policy name."""
        # Create requests for different policies
        runner.invoke(app, [
            "request",
            "--policy", "policy-a",
            "--change", "Change A",
            "--requester", "agent-1",
        ])
        runner.invoke(app, [
            "request",
            "--policy", "policy-b",
            "--change", "Change B",
            "--requester", "agent-2",
        ])

        result = runner.invoke(app, ["list", "--policy", "policy-a"])
        assert result.exit_code == 0
        assert "policy-a" in result.stdout
        # policy-b might still appear in header, but not in data rows


class TestApproveRequest:
    """Tests for approving requests."""

    def test_approve_valid_request(self, runner, mock_db):
        """Approve a pending request."""
        # Create request
        result = runner.invoke(app, [
            "request",
            "--policy", "test-policy",
            "--change", "Test change",
            "--requester", "test-agent",
        ])

        lines = result.stdout.split("\n")
        req_id = None
        for line in lines:
            if "ID:" in line:
                req_id = line.split(":")[-1].strip()
                break

        # Approve it
        result = runner.invoke(app, ["approve", req_id])
        assert result.exit_code == 0
        assert "Request approved" in result.stdout

    def test_approve_request_updates_status(self, runner, mock_db):
        """Approving a request updates its status."""
        # Create and get request ID
        result = runner.invoke(app, [
            "request",
            "--policy", "test-policy",
            "--change", "Test change",
            "--requester", "test-agent",
        ])
        lines = result.stdout.split("\n")
        req_id = None
        for line in lines:
            if "ID:" in line:
                req_id = line.split(":")[-1].strip()
                break

        # Approve
        runner.invoke(app, ["approve", req_id])

        # Check in DB
        with patch("main.DB_PATH", mock_db):
            conn = sqlite3.connect(mock_db)
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT status FROM policy_requests WHERE id = ?", (req_id,))
            row = cursor.fetchone()
            assert row["status"] == "approved"
            conn.close()

    def test_approve_nonexistent_request(self, runner, mock_db):
        """Approving a nonexistent request fails."""
        result = runner.invoke(app, ["approve", "POL-FAKE-12345678"])
        assert result.exit_code == 1
        assert "not found" in result.stdout

    def test_approve_already_approved_request(self, runner, mock_db):
        """Can't re-approve an already approved request."""
        result = runner.invoke(app, [
            "request",
            "--policy", "test",
            "--change", "test",
            "--requester", "agent",
        ])
        lines = result.stdout.split("\n")
        req_id = None
        for line in lines:
            if "ID:" in line:
                req_id = line.split(":")[-1].strip()
                break

        # Approve once
        runner.invoke(app, ["approve", req_id])

        # Try to approve again
        result = runner.invoke(app, ["approve", req_id])
        assert result.exit_code == 1
        assert "already" in result.stdout.lower()

    def test_approve_with_custom_reviewer(self, runner, mock_db):
        """Approve with custom reviewer name."""
        result = runner.invoke(app, [
            "request",
            "--policy", "test",
            "--change", "test",
            "--requester", "agent",
        ])
        lines = result.stdout.split("\n")
        req_id = None
        for line in lines:
            if "ID:" in line:
                req_id = line.split(":")[-1].strip()
                break

        result = runner.invoke(app, ["approve", req_id, "--reviewer", "human-reviewer-1"])
        assert result.exit_code == 0
        assert "human-reviewer-1" in result.stdout


class TestDenyRequest:
    """Tests for denying requests."""

    def test_deny_valid_request(self, runner, mock_db):
        """Deny a pending request."""
        result = runner.invoke(app, [
            "request",
            "--policy", "test",
            "--change", "test",
            "--requester", "agent",
        ])
        lines = result.stdout.split("\n")
        req_id = None
        for line in lines:
            if "ID:" in line:
                req_id = line.split(":")[-1].strip()
                break

        result = runner.invoke(app, ["deny", req_id, "--reason", "Security concern"])
        assert result.exit_code == 0
        assert "Request denied" in result.stdout

    def test_deny_request_updates_status(self, runner, mock_db):
        """Denying a request updates its status."""
        result = runner.invoke(app, [
            "request",
            "--policy", "test",
            "--change", "test",
            "--requester", "agent",
        ])
        lines = result.stdout.split("\n")
        req_id = None
        for line in lines:
            if "ID:" in line:
                req_id = line.split(":")[-1].strip()
                break

        runner.invoke(app, ["deny", req_id, "--reason", "Not approved"])

        with patch("main.DB_PATH", mock_db):
            conn = sqlite3.connect(mock_db)
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT status FROM policy_requests WHERE id = ?", (req_id,))
            row = cursor.fetchone()
            assert row["status"] == "denied"
            conn.close()

    def test_deny_nonexistent_request(self, runner, mock_db):
        """Denying a nonexistent request fails."""
        result = runner.invoke(app, ["deny", "POL-FAKE-12345678"])
        assert result.exit_code == 1

    def test_deny_already_denied_request(self, runner, mock_db):
        """Can't re-deny an already denied request."""
        result = runner.invoke(app, [
            "request",
            "--policy", "test",
            "--change", "test",
            "--requester", "agent",
        ])
        lines = result.stdout.split("\n")
        req_id = None
        for line in lines:
            if "ID:" in line:
                req_id = line.split(":")[-1].strip()
                break

        runner.invoke(app, ["deny", req_id])
        result = runner.invoke(app, ["deny", req_id])
        assert result.exit_code == 1


class TestCheckRequest:
    """Tests for checking request status."""

    def test_check_pending_request(self, runner, mock_db):
        """Check a pending request returns exit code 1."""
        result = runner.invoke(app, [
            "request",
            "--policy", "test",
            "--change", "test",
            "--requester", "agent",
        ])
        lines = result.stdout.split("\n")
        req_id = None
        for line in lines:
            if "ID:" in line:
                req_id = line.split(":")[-1].strip()
                break

        result = runner.invoke(app, ["check", req_id])
        assert result.exit_code == 1
        assert "pending" in result.stdout

    def test_check_approved_request(self, runner, mock_db):
        """Check an approved request returns exit code 0."""
        result = runner.invoke(app, [
            "request",
            "--policy", "test",
            "--change", "test",
            "--requester", "agent",
        ])
        lines = result.stdout.split("\n")
        req_id = None
        for line in lines:
            if "ID:" in line:
                req_id = line.split(":")[-1].strip()
                break

        runner.invoke(app, ["approve", req_id])

        result = runner.invoke(app, ["check", req_id])
        assert result.exit_code == 0
        assert "approved" in result.stdout

    def test_check_denied_request(self, runner, mock_db):
        """Check a denied request returns exit code 2."""
        result = runner.invoke(app, [
            "request",
            "--policy", "test",
            "--change", "test",
            "--requester", "agent",
        ])
        lines = result.stdout.split("\n")
        req_id = None
        for line in lines:
            if "ID:" in line:
                req_id = line.split(":")[-1].strip()
                break

        runner.invoke(app, ["deny", req_id])

        result = runner.invoke(app, ["check", req_id])
        assert result.exit_code == 2
        assert "denied" in result.stdout

    def test_check_nonexistent_request(self, runner, mock_db):
        """Check a nonexistent request returns exit code 1."""
        result = runner.invoke(app, ["check", "POL-FAKE-12345678"])
        assert result.exit_code == 1

    def test_check_quiet_mode(self, runner, mock_db):
        """Check with --quiet suppresses output."""
        result = runner.invoke(app, [
            "request",
            "--policy", "test",
            "--change", "test",
            "--requester", "agent",
        ])
        lines = result.stdout.split("\n")
        req_id = None
        for line in lines:
            if "ID:" in line:
                req_id = line.split(":")[-1].strip()
                break

        result = runner.invoke(app, ["check", req_id, "--quiet"])
        assert result.exit_code == 1
        # Should be minimal output
        assert len(result.stdout) < 20  # Minimal output


class TestHistory:
    """Tests for policy history."""

    def test_history_no_requests(self, runner, mock_db):
        """History for nonexistent policy shows message."""
        result = runner.invoke(app, ["history", "nonexistent-policy"])
        assert result.exit_code == 0
        assert "No history found" in result.stdout

    def test_history_shows_all_statuses(self, runner, mock_db):
        """History shows requests regardless of status."""
        # Create multiple requests for same policy
        for i in range(3):
            runner.invoke(app, [
                "request",
                "--policy", "test-policy",
                "--change", f"Change {i}",
                "--requester", f"agent-{i}",
            ])

        result = runner.invoke(app, ["list"])
        lines = result.stdout.split("\n")
        req_ids = []
        for line in lines:
            if "POL-TEST" in line:
                parts = line.split()
                if parts:
                    req_ids.append(parts[0])

        # Approve first, deny second
        if len(req_ids) >= 2:
            runner.invoke(app, ["approve", req_ids[0]])
            runner.invoke(app, ["deny", req_ids[1]])

        result = runner.invoke(app, ["history", "test-policy"])
        assert result.exit_code == 0
        assert "test-policy" in result.stdout


class TestIntegrationScenarios:
    """Integration tests for common workflows."""

    def test_agent_request_workflow(self, runner, mock_db):
        """Agent submits request, human approves, agent checks status."""
        # Agent submits
        result = runner.invoke(app, [
            "request",
            "--policy", "escalation-approval",
            "--change", "Agent X needs elevated access to debug session Y",
            "--requester", "impl-agent-003",
        ])
        assert result.exit_code == 0

        lines = result.stdout.split("\n")
        req_id = None
        for line in lines:
            if "ID:" in line:
                req_id = line.split(":")[-1].strip()
                break

        assert req_id

        # Agent checks (should be pending)
        result = runner.invoke(app, ["check", req_id, "--quiet"])
        assert result.exit_code == 1

        # Human approves
        result = runner.invoke(app, ["approve", req_id, "--reviewer", "security-lead"])
        assert result.exit_code == 0

        # Agent checks (should be approved)
        result = runner.invoke(app, ["check", req_id, "--quiet"])
        assert result.exit_code == 0

    def test_agent_request_denied_workflow(self, runner, mock_db):
        """Agent submits, human denies, agent sees denial."""
        result = runner.invoke(app, [
            "request",
            "--policy", "data-access",
            "--change", "Agent needs access to production user data",
            "--requester", "impl-agent-004",
        ])

        lines = result.stdout.split("\n")
        req_id = None
        for line in lines:
            if "ID:" in line:
                req_id = line.split(":")[-1].strip()
                break

        # Human denies
        runner.invoke(app, [
            "deny", req_id,
            "--reason", "Production data access requires audit trail"
        ])

        # Agent checks (should be denied)
        result = runner.invoke(app, ["check", req_id, "--quiet"])
        assert result.exit_code == 2
