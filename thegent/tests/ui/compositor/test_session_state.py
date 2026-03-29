"""Tests for SessionState."""

import tempfile
from pathlib import Path

from thegent.compositor.session_state import SessionState


class TestSessionState:
    """Tests for SessionState functionality."""

    def test_session_state_initialization(self) -> None:
        """Test that SessionState initializes correctly."""
        state = SessionState("test-session")
        assert state.session_name == "test-session"
        assert state.session_dir.exists()

    def test_save_session(self) -> None:
        """Test saving session."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state = SessionState("test-session")
            state.session_dir = Path(tmpdir)
            state.session_file = state.session_dir / "test-session.yaml"

            layout = {"type": "pane", "id": "root", "working_dir": "/tmp"}
            result = state.save_session(layout)

            assert result is True
            assert state.session_file.exists()

    def test_load_session(self) -> None:
        """Test loading session."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state = SessionState("test-session")
            state.session_dir = Path(tmpdir)
            state.session_file = state.session_dir / "test-session.yaml"

            layout = {"type": "pane", "id": "root", "working_dir": "/tmp"}
            state.save_session(layout)

            loaded = state.load_session()
            assert loaded is not None
            assert loaded.get("type") == "pane"

    def test_load_nonexistent_session(self) -> None:
        """Test loading nonexistent session."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state = SessionState("nonexistent")
            state.session_dir = Path(tmpdir)
            state.session_file = state.session_dir / "nonexistent.yaml"

            loaded = state.load_session()
            assert loaded is None

    def test_delete_session(self) -> None:
        """Test deleting session."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state = SessionState("test-session")
            state.session_dir = Path(tmpdir)
            state.session_file = state.session_dir / "test-session.yaml"

            layout = {"type": "pane", "id": "root", "working_dir": "/tmp"}
            state.save_session(layout)

            assert state.session_file.exists()
            result = state.delete_session()

            assert result is True
            assert not state.session_file.exists()

    def test_list_sessions(self) -> None:
        """Test listing sessions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state1 = SessionState("session1")
            state1.session_dir = Path(tmpdir)
            state1.session_file = state1.session_dir / "session1.yaml"

            state2 = SessionState("session2")
            state2.session_dir = Path(tmpdir)
            state2.session_file = state2.session_dir / "session2.yaml"

            layout = {"type": "pane"}
            state1.save_session(layout)
            state2.save_session(layout)

            state = SessionState()
            state.session_dir = Path(tmpdir)
            sessions = state.list_sessions()

            assert "session1" in sessions
            assert "session2" in sessions

    def test_session_exists(self) -> None:
        """Test checking if session exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state = SessionState("test-session")
            state.session_dir = Path(tmpdir)
            state.session_file = state.session_dir / "test-session.yaml"

            assert not state.session_exists()

            layout = {"type": "pane"}
            state.save_session(layout)

            assert state.session_exists()

    def test_session_round_trip(self) -> None:
        """Test saving and loading a session."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state = SessionState("test-session")
            state.session_dir = Path(tmpdir)
            state.session_file = state.session_dir / "test-session.yaml"

            original_layout = {
                "type": "branch",
                "direction": "H",
                "children": [
                    {"type": "pane", "id": "pane1", "working_dir": "/tmp"},
                    {"type": "pane", "id": "pane2", "working_dir": "/home"},
                ],
            }

            state.save_session(original_layout)
            loaded = state.load_session()

            assert loaded == original_layout
