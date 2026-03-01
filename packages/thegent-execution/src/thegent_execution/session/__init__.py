"""Session persistence backends for thegent agent sessions."""

from thegent_execution.session.conversation_dumper import ConversationDumper, get_dumper
from thegent_execution.session.manager import (
    InvalidTurnIndexError,
    RollbackOutOfRangeError,
    SessionAlreadyExistsError,
    SessionManager,
    SessionManagerError,
    SessionNotFoundError,
)
from thegent_execution.session.zmx_backend import ZmxBackend, ZmxSession, resolve_session_backend

__all__ = [
    "ConversationDumper",
    "InvalidTurnIndexError",
    "RollbackOutOfRangeError",
    "SessionAlreadyExistsError",
    "SessionManager",
    "SessionManagerError",
    "SessionNotFoundError",
    "ZmxBackend",
    "ZmxSession",
    "get_dumper",
    "resolve_session_backend",
]
