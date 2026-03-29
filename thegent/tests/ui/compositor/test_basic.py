"""Basic tests for compositor components."""

from pathlib import Path

from thegent.ui.compositor import CompositApp, PaneManager, SessionState, TerminalPane


def test_composite_app_init(app: CompositApp) -> None:
    """Test CompositApp initialization."""
    assert app.TITLE == "Thegent Compositor"
    assert len(app.BINDINGS) > 0


def test_terminal_pane_init(terminal_pane: TerminalPane) -> None:
    """Test TerminalPane initialization."""
    assert terminal_pane.pane_id == "test-pane-1"
    assert terminal_pane.working_dir == "/tmp"
    assert terminal_pane.process is None


def test_pane_manager_init(pane_manager: PaneManager) -> None:
    """Test PaneManager initialization."""
    assert pane_manager.root is None
    assert pane_manager.current_pane_id is None


def test_session_state_init(session_state: SessionState) -> None:
    """Test SessionState initialization."""
    assert session_state.session_id == "test-session"
    assert session_state.session_dir.exists()


def test_pane_manager_create_root(pane_manager: PaneManager) -> None:
    """Test creating root pane."""
    root = pane_manager.create_root_pane("root-pane")
    assert root is not None
    assert root.pane_id == "root-pane"
    assert root.is_leaf is True
    assert pane_manager.current_pane_id == "root-pane"


def test_session_state_save_and_load(session_state: SessionState) -> None:
    """Test saving and loading session state."""
    state_data = {"layout": "single", "panes": []}
    assert session_state.save(state_data) is True

    loaded = session_state.load()
    assert loaded is not None
    assert loaded["session_id"] == "test-session"
    assert loaded["layout"] == "single"


def test_session_state_list_sessions(temp_session_dir: Path) -> None:
    """Test listing sessions."""
    session1 = SessionState("session1", session_dir=temp_session_dir)
    session2 = SessionState("session2", session_dir=temp_session_dir)

    session1.save({"layout": "single"})
    session2.save({"layout": "split"})

    sessions = session1.list_sessions()
    assert len(sessions) >= 2
    assert "session1" in sessions
    assert "session2" in sessions


def test_terminal_pane_placeholder(terminal_pane: TerminalPane) -> None:
    """Test TerminalPane placeholder rendering."""
    output = terminal_pane._render_placeholder()
    assert "test-pane-1" in output
    assert "/tmp" in output


def test_pane_manager_save_layout(pane_manager: PaneManager) -> None:
    """Test saving empty layout."""
    layout = pane_manager.save_layout()
    assert layout == {}


def test_pane_manager_save_layout_with_root(pane_manager: PaneManager) -> None:
    """Test saving layout with root pane."""
    pane_manager.create_root_pane("root")
    layout = pane_manager.save_layout()

    assert layout["pane_id"] == "root"
    assert layout["is_leaf"] is True
    assert layout["direction"] is None
