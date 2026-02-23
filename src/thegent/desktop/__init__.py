"""Desktop GUI Application - High-performance multi-agent interface."""

from dataclasses import dataclass, field
from enum import Enum
import time


class AppMode(Enum):
    STANDALONE = "standalone"
    TUI_TANDEM = "tui_tandem"
    TRAY_TANDEM = "tray_tandem"


@dataclass
class AgentSession:
    id: str
    name: str
    agent_type: str
    status: str = "idle"
    started_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    messages: list = field(default_factory=list)
    output: str = ""


@dataclass
class DesktopAppConfig:
    mode: AppMode = AppMode.STANDALONE
    window_size: tuple = (1400, 900)
    theme: str = "dark"
    font_size: int = 14


class DesktopApp:
    def __init__(self, config=None):
        self._config = config or DesktopAppConfig()
        self._sessions = {}
        self._active_session = None
        self._tui_connected = False
        self._tray_connected = False

    @property
    def config(self):
        return self._config

    @property
    def sessions(self):
        return self._sessions

    @property
    def active_session(self):
        if self._active_session:
            return self._sessions.get(self._active_session)
        return None

    def create_session(self, name: str, agent_type: str) -> AgentSession:
        sid = f"{agent_type}_{name}_{int(time.time() * 1000)}"
        session = AgentSession(id=sid, name=name, agent_type=agent_type)
        self._sessions[sid] = session
        if not self._active_session:
            self._active_session = sid
        return session

    def get_session(self, sid: str):
        return self._sessions.get(sid)

    def list_sessions(self):
        return list(self._sessions.values())

    def close_session(self, sid: str) -> bool:
        if sid in self._sessions:
            del self._sessions[sid]
            if self._active_session == sid:
                self._active_session = next(iter(self._sessions.keys()), None)
            return True
        return False

    def set_active_session(self, sid: str) -> bool:
        if sid in self._sessions:
            self._active_session = sid
            return True
        return False

    def append_output(self, sid: str, output: str):
        session = self._sessions.get(sid)
        if session:
            session.output += output


_desktop_app_manager = None


def get_desktop_app_manager():
    global _desktop_app_manager
    if _desktop_app_manager is None:

        class Manager:
            def __init__(self):
                self._apps = {}

            def create_app(self, config=None, name="default"):
                app = DesktopApp(config)
                self._apps[name] = app
                return app

            def get_app(self, name):
                return self._apps.get(name)

        _desktop_app_manager = Manager()
    return _desktop_app_manager


def get_desktop_app(name="default"):
    mgr = get_desktop_app_manager()
    app = mgr.get_app(name)
    if app is None:
        app = mgr.create_app(name=name)
    return app
