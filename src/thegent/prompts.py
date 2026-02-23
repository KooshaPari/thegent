"""Aggregate prompt/response management from Cursor, Codex, and Claude.

Unified interface for:
- Harvesting $idea/$defer/$pending from all sources
- Listing prompts by session, by project, by source
- Dumping full conversations for recovery and extension
"""

from __future__ import annotations

import orjson as json
import os
import sqlite3
import subprocess
from thegent.infra.shim_subprocess import run as shim_run
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Default paths (match harvest-idea-seeds.sh)
CLAUDE_HISTORY = Path(os.environ.get("CLAUDE_HISTORY", Path("~/.claude/history.jsonl").expanduser()))
CODEX_HISTORY = Path(os.environ.get("CODEX_HISTORY", Path("~/.codex/history.jsonl").expanduser()))
CODEX_STATE_DB = Path(os.environ.get("CODEX_STATE_DB", Path("~/.codex/state_5.sqlite").expanduser()))
# Match harvest-idea-seeds.sh: CURSOR_PROJECTS= explicitly skips
_cursor_raw = os.environ.get("CURSOR_PROJECTS")
if _cursor_raw == "":
    CURSOR_PROJECTS: Path | None = None
else:
    CURSOR_PROJECTS = Path(_cursor_raw or Path("~/.cursor/projects").expanduser())


@dataclass
class PromptEntry:
    """Single prompt or message entry."""

    source: str  # claude, codex, cursor
    role: str  # user, assistant
    text: str
    timestamp: str | None
    session_id: str | None
    project: str | None
    line_num: int | None = None


@dataclass
class SessionInfo:
    """Session metadata for listing."""

    source: str
    session_id: str
    project: str | None
    last_ts: str | None
    prompt_count: int
    path: str | None = None


def _parse_line(line: str) -> dict[str, Any] | None:
    """Parse a single JSON line from history."""
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        return None


def _list_claude_sessions() -> list[SessionInfo]:
    """List sessions from Claude history.jsonl."""
    sessions: dict[str, SessionInfo] = {}
    if not CLAUDE_HISTORY.exists():
        return []
    with open(CLAUDE_HISTORY) as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            obj = _parse_line(line)
            if not obj:
                continue
            display = obj.get("display") or ""
            if not display:
                continue
            session_id = obj.get("sessionId") or f"claude-{line_num}"
            project = obj.get("project")
            ts = obj.get("timestamp")
            ts_str = datetime.fromtimestamp(ts / 1000, tz=timezone.utc).isoformat() + "Z" if ts else None
            if session_id not in sessions:
                sessions[session_id] = SessionInfo(
                    source="claude",
                    session_id=session_id,
                    project=project,
                    last_ts=ts_str,
                    prompt_count=0,
                    path=str(CLAUDE_HISTORY),
                )
            s = sessions[session_id]
            s.prompt_count += 1
            s.last_ts = ts_str
            s.project = project or s.project
    return list(sessions.values())


def _list_codex_sessions() -> list[SessionInfo]:
    """List sessions from Codex history.jsonl."""
    sessions: dict[str, SessionInfo] = {}
    if not CODEX_HISTORY.exists():
        return []
    cwd_map: dict[str, str] = {}
    if CODEX_STATE_DB.exists():
        try:
            conn = sqlite3.connect(str(CODEX_STATE_DB))
            cur = conn.execute("SELECT id, cwd FROM threads")
            for row in cur:
                cwd_map[str(row[0])] = str(row[1]) if row[1] else ""
            conn.close()
        except Exception:
            pass
    with open(CODEX_HISTORY) as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            obj = _parse_line(line)
            if not obj:
                continue
            session_id = obj.get("session_id") or f"codex-{line_num}"
            ts = obj.get("ts")
            ts_str = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat() + "Z" if ts else None
            cwd = cwd_map.get(session_id, "")
            if session_id not in sessions:
                sessions[session_id] = SessionInfo(
                    source="codex",
                    session_id=session_id,
                    project=cwd or None,
                    last_ts=ts_str,
                    prompt_count=0,
                    path=str(CODEX_HISTORY),
                )
            s = sessions[session_id]
            s.prompt_count += 1
            s.last_ts = ts_str
    return list(sessions.values())


def _read_file_safe(f: Path) -> str | None:
    """Read a file safely, ignoring errors."""
    try:
        return f.read_text(errors="ignore")
    except Exception:
        return None


def _cursor_project_path(folder: str) -> str | None:
    """Resolve Cursor project folder to workspace path."""
    if CURSOR_PROJECTS is None:
        return None
    proj_dir = CURSOR_PROJECTS / folder
    if not proj_dir.exists():
        return None
    # Try decode: path segments joined by -
    parts = folder.split("-")
    candidate = "/" + "/".join(parts) if parts else ""
    if candidate and Path(candidate).exists():
        return candidate
    last_seg = parts[-1] if parts else ""
    if not last_seg:
        return None
    for pattern in ["agent-tools/*.txt", "agent-transcripts/*.jsonl"]:
        for f in proj_dir.glob(pattern):
            content = _read_file_safe(f)
            if not content:
                continue
            for seg in content.split():
                if f"/{last_seg}" in seg and Path(seg.split()[0] if " " in seg else seg).exists():
                    return seg.split()[0] if " " in seg else seg
    return None


def _list_cursor_sessions() -> list[SessionInfo]:
    """List sessions from Cursor agent-transcripts."""
    sessions: list[SessionInfo] = []
    if not CURSOR_PROJECTS or not CURSOR_PROJECTS.exists():
        return []
    for proj_dir in sorted(CURSOR_PROJECTS.iterdir()):
        if not proj_dir.is_dir():
            continue
        agent_dir = proj_dir / "agent-transcripts"
        if not agent_dir.exists():
            continue
        project_path = _cursor_project_path(proj_dir.name)
        for jsonl in agent_dir.glob("*.jsonl"):
            session_id = jsonl.stem
            count = 0
            last_ts = None
            try:
                with open(jsonl) as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        obj = _parse_line(line)
                        if not obj:
                            continue
                        if obj.get("role") == "user":
                            count += 1
            except Exception:
                pass
            sessions.append(
                SessionInfo(
                    source="cursor",
                    session_id=session_id,
                    project=project_path,
                    last_ts=last_ts,
                    prompt_count=count,
                    path=str(jsonl),
                )
            )
    return sessions


def list_sessions(
    source: str | None = None,
    project: str | None = None,
) -> list[SessionInfo]:
    """List all sessions from Claude, Codex, Cursor. Filter by source and/or project."""
    all_sessions: list[SessionInfo] = []
    if source in (None, "claude"):
        all_sessions.extend(_list_claude_sessions())
    if source in (None, "codex"):
        all_sessions.extend(_list_codex_sessions())
    if source in (None, "cursor"):
        all_sessions.extend(_list_cursor_sessions())
    if project:
        proj_norm = str(Path(project).resolve())
        all_sessions = [s for s in all_sessions if s.project and proj_norm in str(s.project)]
    return sorted(all_sessions, key=lambda s: s.last_ts or "", reverse=True)


def dump_cursor_session(session_id: str, output_path: Path | None = None) -> list[PromptEntry]:
    """Dump full conversation from a Cursor transcript. Returns entries; optionally writes to file."""
    entries: list[PromptEntry] = []
    if not CURSOR_PROJECTS or not CURSOR_PROJECTS.exists():
        return entries
    for proj_dir in CURSOR_PROJECTS.iterdir():
        if not proj_dir.is_dir():
            continue
        agent_dir = proj_dir / "agent-transcripts"
        if not agent_dir.exists():
            continue
        jsonl = agent_dir / f"{session_id}.jsonl"
        if not jsonl.exists():
            continue
        project_path = _cursor_project_path(proj_dir.name)
        with open(jsonl) as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                obj = _parse_line(line)
                if not obj:
                    continue
                role = obj.get("role", "unknown")
                text = ""
                msg = obj.get("message") or {}
                content = msg.get("content") or []
                for c in content:
                    if isinstance(c, dict) and c.get("type") == "text":
                        text += c.get("text", "")
                    elif isinstance(c, str):
                        text += c
                if not text:
                    continue
                entries.append(
                    PromptEntry(
                        source="cursor",
                        role=role,
                        text=text,
                        timestamp=None,
                        session_id=session_id,
                        project=project_path,
                        line_num=line_num,
                    )
                )
        break
    if output_path and entries:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        lines: list[str] = [
            f"# Cursor session dump: {session_id}",
            f"# Project: {entries[0].project or 'unknown'}",
            "# Source: cursor agent-transcript",
            "",
        ]
        for e in entries:
            lines.append(f"## {e.role.upper()}")
            lines.append("")
            lines.append(e.text[:2000] + ("..." if len(e.text) > 2000 else ""))
            lines.append("")
        output_path.write_text("\n".join(lines), encoding="utf-8")
    return entries


def _extract_seed(f: Path) -> dict[str, Any] | None:
    """Extract metadata and preview from an idea seed file."""
    try:
        content = f.read_text(encoding="utf-8")
        front = {}
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                for line in parts[1].strip().split("\n"):
                    if ":" in line:
                        k, v = line.split(":", 1)
                        front[k.strip()] = v.strip()
        return {
            "path": str(f),
            "source": front.get("source", "unknown"),
            "project": front.get("project"),
            "session_id": front.get("session_id"),
            "saved_at": front.get("saved_at"),
            "preview": content.split("\n\n", 1)[-1][:200] if "\n\n" in content else content[:200],
        }
    except Exception:
        return None


def list_idea_seeds(project_root: Path | None = None) -> list[dict[str, Any]]:
    """List harvested idea seeds. If project_root given, filter to that project."""
    seeds: list[dict[str, Any]] = []
    search_dirs: list[Path] = []
    if project_root:
        seeds_dir = project_root / "docs" / "research" / "idea-seeds"
        if seeds_dir.exists():
            search_dirs.append(seeds_dir)
    else:
        fallback = Path.home() / ".claude" / "idea-seeds"
        if fallback.exists():
            search_dirs.append(fallback)
        # Also scan known project idea-seeds from Cursor projects
        if CURSOR_PROJECTS and CURSOR_PROJECTS.exists():
            for proj_dir in CURSOR_PROJECTS.iterdir():
                if proj_dir.is_dir():
                    pp = _cursor_project_path(proj_dir.name)
                    if pp:
                        sd = Path(pp) / "docs" / "research" / "idea-seeds"
                        if sd.exists() and sd not in search_dirs:
                            search_dirs.append(sd)
    for d in search_dirs:
        for f in d.glob("seed_*.md"):
            seed = _extract_seed(f)
            if seed:
                seeds.append(seed)
    return seeds


# --- Generic explore (no $idea/$defer/$pending) ---


def _explore_claude_prompts(
    session_id: str | None = None,
    project: str | None = None,
    limit: int = 500,
    since_hours: float | None = None,
) -> list[PromptEntry]:
    """All prompts from Claude history (no flag filter)."""
    entries: list[PromptEntry] = []
    if not CLAUDE_HISTORY.exists():
        return entries
    cutoff = time.time() - (since_hours * 3600) if since_hours else 0
    with open(CLAUDE_HISTORY) as f:
        for line_num, line in enumerate(f, 1):
            if len(entries) >= limit:
                break
            line = line.strip()
            if not line:
                continue
            obj = _parse_line(line)
            if not obj:
                continue
            display = obj.get("display") or ""
            if not display:
                continue
            ts = obj.get("timestamp")
            if since_hours and ts:
                if (ts / 1000) < cutoff:
                    continue
            sid = obj.get("sessionId") or f"claude-{line_num}"
            if session_id and sid != session_id:
                continue
            proj = obj.get("project")
            if project and proj and project not in str(proj):
                continue
            ts_str = datetime.fromtimestamp(ts / 1000, tz=timezone.utc).isoformat() + "Z" if ts else None
            entries.append(
                PromptEntry(
                    source="claude",
                    role="user",
                    text=display,
                    timestamp=ts_str,
                    session_id=sid,
                    project=proj,
                    line_num=line_num,
                )
            )
    return entries


def _explore_codex_prompts(
    session_id: str | None = None,
    project: str | None = None,
    limit: int = 500,
    since_hours: float | None = None,
) -> list[PromptEntry]:
    """All prompts from Codex history (no flag filter)."""
    entries: list[PromptEntry] = []
    if not CODEX_HISTORY.exists():
        return entries
    cutoff = time.time() - (since_hours * 3600) if since_hours else 0
    cwd_map: dict[str, str] = {}
    if CODEX_STATE_DB.exists():
        try:
            conn = sqlite3.connect(str(CODEX_STATE_DB))
            cur = conn.execute("SELECT id, cwd FROM threads")
            for row in cur:
                cwd_map[str(row[0])] = str(row[1]) if row[1] else ""
            conn.close()
        except Exception:
            pass
    with open(CODEX_HISTORY) as f:
        for line_num, line in enumerate(f, 1):
            if len(entries) >= limit:
                break
            line = line.strip()
            if not line:
                continue
            obj = _parse_line(line)
            if not obj:
                continue
            text = obj.get("text") or ""
            if not text:
                continue
            ts = obj.get("ts")
            if since_hours and ts:
                if ts < cutoff:
                    continue
            sid = obj.get("session_id") or f"codex-{line_num}"
            if session_id and sid != session_id:
                continue
            cwd = cwd_map.get(sid, "")
            if project and cwd and project not in cwd:
                continue
            ts_str = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat() + "Z" if ts else None
            entries.append(
                PromptEntry(
                    source="codex",
                    role="user",
                    text=text,
                    timestamp=ts_str,
                    session_id=sid,
                    project=cwd or None,
                    line_num=line_num,
                )
            )
    return entries


def _explore_cursor_prompts(
    session_id: str | None = None,
    project: str | None = None,
    limit: int = 500,
    since_hours: float | None = None,
) -> list[PromptEntry]:
    """All prompts and responses from Cursor transcripts (no flag filter)."""
    entries: list[PromptEntry] = []
    if not CURSOR_PROJECTS or not CURSOR_PROJECTS.exists():
        return entries
    cutoff = time.time() - (since_hours * 3600) if since_hours else 0
    for proj_dir in sorted(CURSOR_PROJECTS.iterdir()):
        if not proj_dir.is_dir():
            continue
        agent_dir = proj_dir / "agent-transcripts"
        if not agent_dir.exists():
            continue
        project_path = _cursor_project_path(proj_dir.name)
        if project and project_path and project not in str(project_path):
            continue
        for jsonl in agent_dir.glob("*.jsonl"):
            if since_hours and jsonl.stat().st_mtime < cutoff:
                continue
            sid = jsonl.stem
            if session_id and sid != session_id:
                continue
            with open(jsonl) as f:
                for line_num, line in enumerate(f, 1):
                    if len(entries) >= limit:
                        break
                    line = line.strip()
                    if not line:
                        continue
                    obj = _parse_line(line)
                    if not obj:
                        continue
                    role = obj.get("role", "unknown")
                    text = ""
                    msg = obj.get("message") or {}
                    content = msg.get("content") or []
                    for c in content:
                        if isinstance(c, dict) and c.get("type") == "text":
                            text += c.get("text", "")
                        elif isinstance(c, str):
                            text += c
                    if not text:
                        continue
                    entries.append(
                        PromptEntry(
                            source="cursor",
                            role=role,
                            text=text,
                            timestamp=None,
                            session_id=sid,
                            project=project_path,
                            line_num=line_num,
                        )
                    )
    return entries


def explore_prompts(
    source: str | None = None,
    session_id: str | None = None,
    project: str | None = None,
    limit: int = 200,
    since_hours: float | None = None,
) -> list[PromptEntry]:
    """Discover/explore all prompts across sources. No $idea/$defer filter."""
    all_entries: list[PromptEntry] = []
    if source in (None, "claude"):
        all_entries.extend(_explore_claude_prompts(session_id, project, limit, since_hours))
    if source in (None, "codex"):
        all_entries.extend(_explore_codex_prompts(session_id, project, limit, since_hours))
    if source in (None, "cursor"):
        all_entries.extend(_explore_cursor_prompts(session_id, project, limit, since_hours))

    # Sort by timestamp desc (entries with ts first, then by source)
    def _sort_key(e: PromptEntry) -> tuple:
        ts = e.timestamp or ""
        return (ts, e.source, e.session_id or "")

    all_entries.sort(key=_sort_key, reverse=True)
    return all_entries[:limit]


def explore_session(session_id: str, source: str | None = None) -> tuple[SessionInfo, list[PromptEntry]] | None:
    """Explore a session by ID: metadata + all prompts/responses."""
    sessions = list_sessions(source=source)
    session = next((s for s in sessions if s.session_id == session_id), None)
    if not session:
        return None
    entries = explore_prompts(source=session.source, session_id=session_id, limit=2000)
    return session, entries


def explore_chat(session_id: str, output_path: Path | None = None) -> list[PromptEntry]:
    """Full chat exploration: dump conversation (user + assistant) for a session.
    Cursor: full transcript. Claude/Codex: prompts only (no responses in history).
    """
    entries = dump_cursor_session(session_id, output_path)
    if entries:
        return entries
    # Claude/Codex: prompts only
    entries = explore_prompts(session_id=session_id, limit=2000)
    if output_path and entries:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            f"# Session: {session_id}",
            f"# Source: {entries[0].source} (prompts only, no responses in history)",
            "",
        ]
        for e in entries:
            lines.append(f"## {e.role.upper()}")
            lines.append("")
            lines.append(e.text[:2000] + ("..." if len(e.text) > 2000 else ""))
            lines.append("")
        output_path.write_text("\n".join(lines), encoding="utf-8")
    return entries


def run_harvest(script_dir: Path | None = None) -> tuple[int, str]:
    """Run harvest-idea-seeds.sh. Returns (returncode, output)."""
    base = script_dir or Path(__file__).resolve().parent.parent.parent
    script = base / "scripts" / "harvest-idea-seeds.sh"
    if not script.exists():
        return 1, f"Harvest script not found: {script}"
    result = shim_run(
        [str(script)],
        capture_output=True,
        text=True,
        cwd=str(base),
        timeout=120,
        check=False,
    )
    out = (result.stdout or "") + (result.stderr or "")
    return result.returncode, out
