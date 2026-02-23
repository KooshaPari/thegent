"""SimulationReplay: replay agent sessions for debugging and regression testing.

Provides:
- ReplayEvent: a single recorded event from an agent session.
- ReplaySession: a full session loaded from a .json session file.
- SimulationReplayEngine: load, replay, compare and test-fixture generation.

FR-REPLAY-001: Engine must load .json session files from .thegent/sessions/.
FR-REPLAY-002: replay() must yield events in timestamp order, respecting speed multiplier.
FR-REPLAY-003: compare_sessions() must return a structured diff with added/removed/changed keys.
FR-REPLAY-004: generate_test_fixture() must produce a valid pytest fixture file.
FR-REPLAY-005: extract_tool_calls() must return only "tool_call" typed events' data.
"""

from __future__ import annotations

import orjson as json
import textwrap
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING
from datetime import UTC

if TYPE_CHECKING:
    from collections.abc import Iterator

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class ReplayEvent:
    """A single event recorded during an agent session.

    # @trace FR-REPLAY-001
    """

    timestamp: float
    event_type: str  # "tool_call" | "response" | "error" | "state_change"
    data: dict


@dataclass
class ReplaySession:
    """A full agent session loaded from a .json session meta file + stdout log.

    # @trace FR-REPLAY-001
    """

    session_id: str
    events: list[ReplayEvent]
    metadata: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------


class SimulationReplayEngine:
    """Load and replay agent sessions for debugging and regression testing.

    # @trace FR-REPLAY-001, FR-REPLAY-002, FR-REPLAY-003, FR-REPLAY-004, FR-REPLAY-005
    """

    # Default sessions root, relative to project root
    _DEFAULT_SESSIONS_ROOT = Path(".thegent") / "sessions"

    def __init__(self, sessions_root: Path | None = None) -> None:
        """Initialise with an optional override sessions root.

        Args:
            sessions_root: Directory that contains session subdirectories.
                           Defaults to .thegent/sessions relative to cwd.
        """
        self.sessions_root: Path = sessions_root or self._DEFAULT_SESSIONS_ROOT

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load_session(self, session_file: Path) -> ReplaySession:
        """Load a session from a .json session meta file.

        The file must be the JSON metadata file produced by thegent (contains
        at least a ``session_id`` key).  Additional events are synthesised from
        the sibling ``.stdout.log`` file when present.

        Args:
            session_file: Absolute or relative path to the ``*.json`` meta file.

        Returns:
            A populated ``ReplaySession``.

        Raises:
            FileNotFoundError: When *session_file* does not exist.
            ValueError: When the file cannot be parsed or lacks a ``session_id``.

        # @trace FR-REPLAY-001
        """
        session_file = Path(session_file)
        if not session_file.exists():
            raise FileNotFoundError(f"Session file not found: {session_file}")

        raw = session_file.read_text(encoding="utf-8")
        try:
            meta: dict = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Cannot parse session file {session_file}: {exc}") from exc

        session_id: str = meta.get("session_id", "")
        if not session_id:
            raise ValueError(f"Session file {session_file} missing 'session_id'")

        events: list[ReplayEvent] = self._synthesise_events(meta, session_file)

        return ReplaySession(session_id=session_id, events=events, metadata=meta)

    def replay(self, session: ReplaySession, speed: float = 1.0) -> Iterator[ReplayEvent]:
        """Yield events in timestamp order, sleeping between events per *speed*.

        Args:
            session: The session to replay.
            speed: Playback speed multiplier.  1.0 = real-time; 0 = no sleep.

        Yields:
            ReplayEvent in chronological order.

        # @trace FR-REPLAY-002
        """
        if not session.events:
            return
        sorted_events = sorted(session.events, key=lambda e: e.timestamp)
        prev_ts: float | None = None
        for event in sorted_events:
            if speed > 0 and prev_ts is not None:
                gap = (event.timestamp - prev_ts) / speed
                if gap > 0:
                    time.sleep(gap)
            yield event
            prev_ts = event.timestamp

    def replay_from_event(self, session: ReplaySession, event_index: int) -> Iterator[ReplayEvent]:
        """Replay starting from *event_index* (0-based), no sleep.

        Args:
            session: The session to replay.
            event_index: The index of the first event to yield.

        Yields:
            ReplayEvent from *event_index* onward (chronological order).

        Raises:
            IndexError: When *event_index* is out of range.

        # @trace FR-REPLAY-002
        """
        sorted_events = sorted(session.events, key=lambda e: e.timestamp)
        if event_index < 0 or event_index >= len(sorted_events):
            raise IndexError(f"event_index {event_index} out of range (session has {len(sorted_events)} events)")
        yield from sorted_events[event_index:]

    def compare_sessions(self, session_a: ReplaySession, session_b: ReplaySession) -> dict:
        """Return a structured diff between two sessions.

        Compares metadata fields and event sequences.  Events are matched
        positionally (same index).  Tool-call sequences are compared separately.

        Args:
            session_a: Reference session (the "before").
            session_b: Comparison session (the "after").

        Returns:
            dict with keys:
              - ``metadata_diff``: {field: {a: ..., b: ...}} for changed keys.
              - ``events_added``: list of events present in B but not A (by index).
              - ``events_removed``: list of events present in A but not B (by index).
              - ``events_changed``: list of {index, a_event, b_event} for changed events.
              - ``tool_calls_diff``: {added: [...], removed: [...], changed: [...]}.

        # @trace FR-REPLAY-003
        """
        metadata_diff: dict[str, dict] = {}
        all_meta_keys = set(session_a.metadata) | set(session_b.metadata)
        for key in sorted(all_meta_keys):
            va = session_a.metadata.get(key)
            vb = session_b.metadata.get(key)
            if va != vb:
                metadata_diff[key] = {"a": va, "b": vb}

        events_a = sorted(session_a.events, key=lambda e: e.timestamp)
        events_b = sorted(session_b.events, key=lambda e: e.timestamp)
        len_a, len_b = len(events_a), len(events_b)
        max_shared = min(len_a, len_b)

        events_changed: list[dict] = []
        for i in range(max_shared):
            ea, eb = events_a[i], events_b[i]
            if ea.event_type != eb.event_type or ea.data != eb.data:
                events_changed.append(
                    {
                        "index": i,
                        "a_event": _event_to_dict(ea),
                        "b_event": _event_to_dict(eb),
                    }
                )

        events_removed = [_event_to_dict(events_a[i]) for i in range(max_shared, len_a)]
        events_added = [_event_to_dict(events_b[i]) for i in range(max_shared, len_b)]

        tool_calls_diff = self._diff_tool_calls(session_a, session_b)

        return {
            "metadata_diff": metadata_diff,
            "events_added": events_added,
            "events_removed": events_removed,
            "events_changed": events_changed,
            "tool_calls_diff": tool_calls_diff,
        }

    def extract_tool_calls(self, session: ReplaySession) -> list[dict]:
        """Return the data payload of every ``tool_call`` event in the session.

        Args:
            session: The session to inspect.

        Returns:
            List of dicts (each is the ``data`` field of a tool_call event),
            ordered by timestamp.

        # @trace FR-REPLAY-005
        """
        return [e.data for e in sorted(session.events, key=lambda e: e.timestamp) if e.event_type == "tool_call"]

    def generate_test_fixture(self, session: ReplaySession, output: Path) -> None:
        """Write a pytest fixture file derived from a session's replay data.

        The generated file contains:
        - A ``session_metadata`` fixture with the raw metadata dict.
        - A ``replay_events`` fixture with a list of event dicts.
        - A ``tool_calls`` fixture with extracted tool-call payloads.
        - A ``replay_session`` fixture that assembles a ReplaySession.

        Args:
            session: The session to derive the fixture from.
            output: Path to write the ``.py`` fixture file (will be created or
                    overwritten).

        # @trace FR-REPLAY-004
        """
        output = Path(output)
        output.parent.mkdir(parents=True, exist_ok=True)

        meta_repr = _safe_repr(session.metadata)
        events_repr = _safe_repr([_event_to_dict(e) for e in session.events])
        tool_calls_repr = _safe_repr(self.extract_tool_calls(session))
        session_id_repr = repr(session.session_id)

        fixture_src = textwrap.dedent(f"""\
            \"\"\"Pytest fixtures for session {session.session_id}.

            Auto-generated by SimulationReplayEngine.generate_test_fixture().
            Do NOT edit by hand — regenerate from the source session file.
            \"\"\"

            from __future__ import annotations

            import pytest

            from thegent.simulation.replay import ReplayEvent, ReplaySession


            SESSION_ID: str = {session_id_repr}

            _RAW_METADATA: dict = {meta_repr}

            _RAW_EVENTS: list[dict] = {events_repr}

            _TOOL_CALLS: list[dict] = {tool_calls_repr}


            @pytest.fixture()
            def session_metadata() -> dict:
                \"\"\"Raw metadata dict for session {session.session_id}.\"\"\"
                return dict(_RAW_METADATA)


            @pytest.fixture()
            def replay_events() -> list[dict]:
                \"\"\"Raw event dicts for session {session.session_id}.\"\"\"
                return list(_RAW_EVENTS)


            @pytest.fixture()
            def tool_calls() -> list[dict]:
                \"\"\"Extracted tool-call data for session {session.session_id}.\"\"\"
                return list(_TOOL_CALLS)


            @pytest.fixture()
            def replay_session(session_metadata: dict, replay_events: list[dict]) -> ReplaySession:
                \"\"\"Assembled ReplaySession for session {session.session_id}.\"\"\"
                events = [
                    ReplayEvent(
                        timestamp=ev.get("timestamp", 0.0),
                        event_type=ev.get("event_type", "unknown"),
                        data=ev.get("data", {{}}),
                    )
                    for ev in replay_events
                ]
                return ReplaySession(
                    session_id=SESSION_ID,
                    events=events,
                    metadata=session_metadata,
                )
            """)

        output.write_text(fixture_src, encoding="utf-8")

    def list_sessions(self) -> list[Path]:
        """Return all session .json meta files found under sessions_root.

        Returns:
            Sorted list of ``*.json`` paths.
        """
        root = Path(self.sessions_root)
        if not root.exists():
            return []
        return sorted(root.rglob("*.json"))

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _synthesise_events(self, meta: dict, session_file: Path) -> list[ReplayEvent]:
        """Build events from meta + optional sibling log files."""
        events: list[ReplayEvent] = []

        # Base timestamp from session start
        started_at = meta.get("started_at_utc", "")
        base_ts = _parse_iso_to_float(started_at) if started_at else 0.0

        # state_change: session started
        events.append(
            ReplayEvent(
                timestamp=base_ts,
                event_type="state_change",
                data={
                    "state": "started",
                    "session_id": meta.get("session_id", ""),
                    "agent": meta.get("agent", ""),
                    "mode": meta.get("mode", ""),
                },
            )
        )

        # Parse stdout log for tool-call and response lines
        stdout_path = Path(meta.get("paths", {}).get("stdout", str(session_file.with_suffix(".stdout.log"))))
        if stdout_path.exists():
            events.extend(self._parse_log_events(stdout_path, base_ts, "response"))

        stderr_path = Path(meta.get("paths", {}).get("stderr", str(session_file.with_suffix(".stderr.log"))))
        if stderr_path.exists():
            events.extend(self._parse_log_events(stderr_path, base_ts + 0.001, "error"))

        # state_change: session finished (if status is known)
        status = meta.get("status", "")
        if status and status != "running":
            events.append(
                ReplayEvent(
                    timestamp=base_ts + 1.0,
                    event_type="state_change",
                    data={"state": "finished", "status": status},
                )
            )

        return events

    @staticmethod
    def _parse_log_events(log_path: Path, base_ts: float, default_type: str) -> list[ReplayEvent]:
        """Parse a log file into ReplayEvent objects.

        Each non-blank line becomes a single event.  Lines that look like JSON
        are decoded into the event ``data``.  Tool-call markers (lines starting
        with ``TOOL_CALL:``) are given ``event_type="tool_call"``.
        """
        events: list[ReplayEvent] = []
        try:
            content = log_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return events

        for idx, line in enumerate(content.splitlines()):
            line = line.strip()
            if not line:
                continue
            ts = base_ts + idx * 0.01
            if line.startswith("TOOL_CALL:"):
                payload_str = line[len("TOOL_CALL:") :].strip()
                data = _try_parse_json(payload_str) or {"raw": payload_str}
                events.append(ReplayEvent(timestamp=ts, event_type="tool_call", data=data))
            elif line.startswith(("ERROR:", "Error:")):
                events.append(
                    ReplayEvent(
                        timestamp=ts,
                        event_type="error",
                        data={"message": line},
                    )
                )
            else:
                data = _try_parse_json(line) or {"raw": line}
                events.append(ReplayEvent(timestamp=ts, event_type=default_type, data=data))
        return events

    def _diff_tool_calls(self, session_a: ReplaySession, session_b: ReplaySession) -> dict:
        """Diff the tool-call sequences of two sessions."""
        calls_a = self.extract_tool_calls(session_a)
        calls_b = self.extract_tool_calls(session_b)
        len_a, len_b = len(calls_a), len(calls_b)
        max_shared = min(len_a, len_b)

        changed = [
            {"index": i, "a": calls_a[i], "b": calls_b[i]} for i in range(max_shared) if calls_a[i] != calls_b[i]
        ]
        removed = calls_a[max_shared:]
        added = calls_b[max_shared:]
        return {"added": added, "removed": removed, "changed": changed}


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------


def _event_to_dict(event: ReplayEvent) -> dict:
    return {
        "timestamp": event.timestamp,
        "event_type": event.event_type,
        "data": event.data,
    }


def _try_parse_json(text: str) -> dict | None:
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
        return {"value": parsed}
    except (json.JSONDecodeError, ValueError):
        return None


def _parse_iso_to_float(iso: str) -> float:
    """Parse an ISO-8601 string to a Unix timestamp float, returning 0.0 on failure.

    Handles the common thegent formats, e.g.:
      2026-02-19T22:00:00.000000+00:00
      2026-02-19T22:00:00Z
      2026-02-19T22:00:00.123456Z
    """
    from datetime import datetime, timezone

    # Normalise Z suffix to +00:00 so fromisoformat handles it on Python < 3.11
    normalised = iso.rstrip()
    if normalised.endswith("Z"):
        normalised = normalised[:-1] + "+00:00"

    try:
        dt = datetime.fromisoformat(normalised)
        # fromisoformat may return naive datetime if no offset present
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt.timestamp()
    except (ValueError, AttributeError):
        return 0.0


def _safe_repr(obj: object) -> str:
    """Return a repr string that is safe to embed in Python source."""
    import pprint

    return pprint.pformat(obj, width=100)
