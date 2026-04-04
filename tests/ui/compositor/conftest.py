"""Fixtures for compositor tests."""

import tempfile
from pathlib import Path

import pytest
from thegent.ui.compositor import CompositApp, PaneManager, SessionState, TerminalPane


@pytest.fixture
def temp_session_dir() -> Path:
    """Create a temporary session directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def session_state(temp_session_dir: Path) -> SessionState:
    """Create a test SessionState instance."""
    return SessionState("test-session", session_dir=temp_session_dir)


@pytest.fixture
def pane_manager() -> PaneManager:
    """Create a test PaneManager instance."""
    return PaneManager()


@pytest.fixture
def app() -> CompositApp:
    """Create a test CompositApp instance."""
    return CompositApp()


@pytest.fixture
def terminal_pane() -> TerminalPane:
    """Create a test TerminalPane instance."""
    return TerminalPane(pane_id="test-pane-1", working_dir="/tmp")
