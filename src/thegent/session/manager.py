"""In-memory SessionManager scaffolding for fork/rollback APIs (WL-106)."""

from __future__ import annotations

import copy
import uuid
from dataclasses import dataclass, field
from typing import Any


class SessionManagerError(RuntimeError):
    """Base exception for session manager failures."""


class SessionNotFoundError(SessionManagerError):
    """Raised when a session ID does not exist."""


class InvalidTurnIndexError(SessionManagerError):
    """Raised when a fork index is outside valid bounds."""


class RollbackOutOfRangeError(SessionManagerError):
    """Raised when rollback exceeds available history."""


class SessionAlreadyExistsError(SessionManagerError):
    """Raised when creating/forking into an existing session ID."""


@dataclass
class SessionState:
    session_id: str
    turns: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class SessionManager:
    """Minimal in-memory session registry with fork/rollback APIs."""

    def __init__(self) -> None:
        self._sessions: dict[str, SessionState] = {}

    def create_session(self, *, session_id: str | None = None, metadata: dict[str, Any] | None = None) -> str:
        new_id = session_id or str(uuid.uuid4())
        if new_id in self._sessions:
            raise SessionAlreadyExistsError(f"Session already exists: {new_id}")
        self._sessions[new_id] = SessionState(session_id=new_id, metadata=dict(metadata or {}))
        return new_id

    def get_session(self, session_id: str) -> SessionState:
        session = self._sessions.get(session_id)
        if session is None:
            raise SessionNotFoundError(f"Session not found: {session_id}")
        return session

    def append_turn(self, session_id: str, turn: dict[str, Any]) -> int:
        session = self.get_session(session_id)
        session.turns.append(copy.deepcopy(turn))
        return len(session.turns)

    def fork_session(
        self,
        session_id: str,
        *,
        from_turn: int | None = None,
        new_session_id: str | None = None,
    ) -> str:
        source = self.get_session(session_id)
        cutoff = len(source.turns) if from_turn is None else from_turn
        if cutoff < 0 or cutoff > len(source.turns):
            raise InvalidTurnIndexError(f"from_turn out of range: {cutoff} (valid: 0..{len(source.turns)})")

        fork_id = new_session_id or str(uuid.uuid4())
        if fork_id in self._sessions:
            raise SessionAlreadyExistsError(f"Session already exists: {fork_id}")
        self._sessions[fork_id] = SessionState(
            session_id=fork_id,
            turns=copy.deepcopy(source.turns[:cutoff]),
            metadata=copy.deepcopy(source.metadata),
        )
        return fork_id

    def rollback_session(self, session_id: str, *, n_turns: int) -> int:
        if n_turns <= 0:
            raise RollbackOutOfRangeError("n_turns must be > 0")
        session = self.get_session(session_id)
        current = len(session.turns)
        if n_turns > current:
            raise RollbackOutOfRangeError(f"Cannot rollback {n_turns} turns from {current}-turn session")
        del session.turns[current - n_turns :]
        return len(session.turns)
