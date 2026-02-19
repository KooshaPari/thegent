"""Unit tests for ShareCLI Bridge (WP-16003, WP-16004).

Tests for:
- ShareCLIBridge: Task coordination and intent broadcasting
- SmartMerge: AST-aware conflict resolution
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from thegent.governance.sharecli_bridge import ShareCLIBridge, SmartMerge


class TestShareCLIBridge:
    """Test ShareCLIBridge functionality (WP-16003)."""

    @pytest.fixture
    def harness_root(self, tmp_path):
        """Create a temporary harness root directory."""
        return tmp_path / ".agent-harness"

    @pytest.fixture
    def bridge(self, harness_root, monkeypatch):
        """Create a ShareCLIBridge instance with mocked harness root."""
        monkeypatch.setenv("HARNESS_ROOT", str(harness_root))
        return ShareCLIBridge()

    def test_is_available_false_when_not_initialized(self, tmp_path, monkeypatch):
        """Test is_available returns False when harness root doesn't exist."""
        monkeypatch.setenv("HARNESS_ROOT", str(tmp_path / "nonexistent"))
        bridge = ShareCLIBridge()
        assert bridge.is_available() is False

    def test_is_available_true_when_initialized(self, bridge, harness_root):
        """Test is_available returns True when var directory exists."""
        # is_available checks if task_dir.parent (var/) exists
        var_dir = harness_root / "var"
        var_dir.mkdir(parents=True, exist_ok=True)
        assert bridge.is_available() is True

    def test_is_available_uses_default_path(self, tmp_path, monkeypatch):
        """Test is_available uses default ~/.agent-harness when HARNESS_ROOT not set."""
        monkeypatch.delenv("HARNESS_ROOT", raising=False)
        monkeypatch.setattr(Path, "expanduser", lambda self: tmp_path / ".agent-harness")
        bridge = ShareCLIBridge()
        (tmp_path / ".agent-harness").mkdir(parents=True, exist_ok=True)
        assert bridge.is_available() is True

    def test_create_shared_task_success(self, bridge, harness_root):
        """Test creating a shared task successfully."""
        harness_root.mkdir(parents=True, exist_ok=True)
        task_dir = harness_root / "var" / "tasks"
        task_dir.mkdir(parents=True, exist_ok=True)

        result = bridge.create_shared_task(
            task_id="test-task-123",
            description="Test task description",
            depends_on=["task-1", "task-2"],
        )

        assert result is True
        task_file = task_dir / "test-task-123"
        assert task_file.exists()

        content = task_file.read_text()
        assert "id=test-task-123" in content
        assert "description=Test task description" in content
        assert "depends_on=task-1,task-2" in content
        assert "status=pending" in content
        assert "created_at=" in content

    def test_create_shared_task_creates_directories(self, bridge, harness_root):
        """Test that create_shared_task creates necessary directories."""
        harness_root.mkdir(parents=True, exist_ok=True)

        result = bridge.create_shared_task(task_id="test-task-456", description="Another test task")

        assert result is True
        task_file = harness_root / "var" / "tasks" / "test-task-456"
        assert task_file.exists()

    def test_create_shared_task_no_depends_on(self, bridge, harness_root):
        """Test creating a task without dependencies."""
        harness_root.mkdir(parents=True, exist_ok=True)

        result = bridge.create_shared_task(task_id="test-task-789", description="Task without deps")

        assert result is True
        task_file = harness_root / "var" / "tasks" / "test-task-789"
        content = task_file.read_text()
        assert "depends_on=" in content

    def test_create_shared_task_fails_when_not_available(self, tmp_path, monkeypatch):
        """Test create_shared_task returns False when ShareCLI not available."""
        monkeypatch.setenv("HARNESS_ROOT", str(tmp_path / "nonexistent"))
        bridge = ShareCLIBridge()
        result = bridge.create_shared_task(task_id="test-task", description="Should fail")
        assert result is False

    def test_broadcast_intent_success(self, bridge, harness_root):
        """Test broadcasting an intent successfully."""
        harness_root.mkdir(parents=True, exist_ok=True)
        intent_dir = harness_root / "var" / "intents"
        intent_dir.mkdir(parents=True, exist_ok=True)

        result = bridge.broadcast_intent(agent_id="test-agent", intent_type="delegate", target="teammate-1")

        assert result is True
        # Intent file name format: {pid}_{agent_id}_{intent_type}
        intent_files = list(intent_dir.glob("*"))
        assert len(intent_files) == 1

        content = intent_files[0].read_text()
        assert "agent=test-agent" in content
        assert "type=delegate" in content
        assert "target=teammate-1" in content
        assert "status=active" in content
        assert "started=" in content

    def test_broadcast_intent_creates_directories(self, bridge, harness_root):
        """Test that broadcast_intent creates necessary directories."""
        harness_root.mkdir(parents=True, exist_ok=True)

        result = bridge.broadcast_intent(agent_id="test-agent", intent_type="read", target="file.py")

        assert result is True
        intent_dir = harness_root / "var" / "intents"
        assert intent_dir.exists()
        assert len(list(intent_dir.glob("*"))) == 1

    def test_broadcast_intent_fails_when_not_available(self, tmp_path, monkeypatch):
        """Test broadcast_intent returns False when ShareCLI not available."""
        monkeypatch.setenv("HARNESS_ROOT", str(tmp_path / "nonexistent"))
        bridge = ShareCLIBridge()
        result = bridge.broadcast_intent(agent_id="test-agent", intent_type="write", target="file.py")
        assert result is False

    def test_get_session_state_empty_when_not_available(self, tmp_path, monkeypatch):
        """Test get_session_state returns empty state when ShareCLI not available."""
        monkeypatch.setenv("HARNESS_ROOT", str(tmp_path / "nonexistent"))
        bridge = ShareCLIBridge()
        state = bridge.get_session_state("session-123")
        assert state == {"claims": [], "intents": [], "tasks": []}

    def test_get_session_state_finds_intents(self, bridge, harness_root):
        """Test get_session_state finds matching intents."""
        harness_root.mkdir(parents=True, exist_ok=True)
        intent_dir = harness_root / "var" / "intents"
        intent_dir.mkdir(parents=True, exist_ok=True)

        # Create an intent file with session ID
        intent_file = intent_dir / "session-123_agent_delegate"
        intent_file.write_text("agent=test-agent\ntype=delegate\ntarget=teammate-1\n")

        state = bridge.get_session_state("session-123")
        assert len(state["intents"]) == 1

    def test_get_session_state_finds_tasks(self, bridge, harness_root):
        """Test get_session_state finds matching tasks."""
        harness_root.mkdir(parents=True, exist_ok=True)
        task_dir = harness_root / "var" / "tasks"
        task_dir.mkdir(parents=True, exist_ok=True)

        # Create a task file assigned to session
        task_file = task_dir / "task-123"
        task_file.write_text("id=task-123\nassigned_to=session-456\nstatus=pending\n")

        state = bridge.get_session_state("session-456")
        assert len(state["tasks"]) == 1

    def test_get_session_state_handles_missing_directories(self, bridge, harness_root):
        """Test get_session_state handles missing directories gracefully."""
        harness_root.mkdir(parents=True, exist_ok=True)
        # Don't create var/ subdirectories

        state = bridge.get_session_state("session-123")
        assert state == {"claims": [], "intents": [], "tasks": []}

    def test_get_session_state_handles_file_read_errors(self, bridge, harness_root):
        """Test get_session_state handles file read errors gracefully."""
        harness_root.mkdir(parents=True, exist_ok=True)
        intent_dir = harness_root / "var" / "intents"
        intent_dir.mkdir(parents=True, exist_ok=True)

        # Create a directory that can't be read as a file
        (intent_dir / "not-a-file").mkdir()

        # Should not raise, just skip problematic files
        state = bridge.get_session_state("session-123")
        assert isinstance(state, dict)


class TestSmartMerge:
    """Test SmartMerge functionality (WP-16004)."""

    @pytest.fixture
    def smart_merge(self):
        """Create a SmartMerge instance."""
        return SmartMerge()

    @pytest.fixture
    def merge_files(self, tmp_path):
        """Create test files for merging."""
        base = tmp_path / "base.txt"
        ours = tmp_path / "ours.txt"
        theirs = tmp_path / "theirs.txt"
        output = tmp_path / "output.txt"

        base.write_text("line 1\nline 2\nline 3\n")
        ours.write_text("line 1\nline 2\nline 3\nours addition\n")
        theirs.write_text("line 1\ntheirs change\nline 2\nline 3\n")

        return base, ours, theirs, output

    def test_smart_merge_uses_mergiraf_when_available(self, smart_merge, merge_files, monkeypatch):
        """Test SmartMerge uses mergiraf when available."""
        base, ours, theirs, output = merge_files

        # Mock mergiraf path
        smart_merge.mergiraf_path = "/usr/bin/mergiraf"

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = smart_merge.merge_files(base, ours, theirs, output)

            assert mock_run.called
            cmd = mock_run.call_args[0][0]
            assert cmd[0] == "/usr/bin/mergiraf"
            assert "merge" in cmd
            assert "--git" in cmd

    def test_smart_merge_falls_back_to_git_when_mergiraf_missing(self, smart_merge, merge_files):
        """Test SmartMerge falls back to git merge-file when mergiraf is missing."""
        base, ours, theirs, output = merge_files

        # Force mergiraf to be None
        smart_merge.mergiraf_path = None

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="merged content\n")
            result = smart_merge.merge_files(base, ours, theirs, output)

            assert mock_run.called
            cmd = mock_run.call_args[0][0]
            assert cmd[0] == "git"
            assert "merge-file" in cmd

            # Verify output was written
            assert output.exists()

    def test_smart_merge_handles_mergiraf_failure(self, smart_merge, merge_files):
        """Test SmartMerge handles mergiraf execution failure."""
        base, ours, theirs, output = merge_files

        smart_merge.mergiraf_path = "/usr/bin/mergiraf"

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1)
            result = smart_merge.merge_files(base, ours, theirs, output)

            assert result is False

    def test_smart_merge_handles_git_failure(self, smart_merge, merge_files):
        """Test SmartMerge handles git merge-file execution failure."""
        base, ours, theirs, output = merge_files

        smart_merge.mergiraf_path = None

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout="")
            result = smart_merge.merge_files(base, ours, theirs, output)

            assert result is False

    def test_smart_merge_handles_exception(self, smart_merge, merge_files):
        """Test SmartMerge handles exceptions gracefully."""
        base, ours, theirs, output = merge_files

        smart_merge.mergiraf_path = "/usr/bin/mergiraf"

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = Exception("Unexpected error")
            result = smart_merge.merge_files(base, ours, theirs, output)

            assert result is False

    def test_smart_merge_initializes_mergiraf_path(self, tmp_path):
        """Test SmartMerge initializes mergiraf_path correctly."""
        with patch("shutil.which") as mock_which:
            mock_which.return_value = "/usr/local/bin/mergiraf"
            merge = SmartMerge()
            assert merge.mergiraf_path == "/usr/local/bin/mergiraf"

    def test_smart_merge_handles_no_mergiraf_in_path(self, tmp_path):
        """Test SmartMerge handles mergiraf not found in PATH."""
        with patch("shutil.which") as mock_which:
            mock_which.return_value = None
            merge = SmartMerge()
            assert merge.mergiraf_path is None
