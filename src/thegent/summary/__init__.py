"""Summary helpers and log parsing diagnostics."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import orjson


@dataclass
class GitCommit:
    sha: str
    message: str


@dataclass
class GitCommitPayload:
    status: str
    commits: list[GitCommit]
    error: dict[str, str] = field(default_factory=dict)


@dataclass
class LogParseStats:
    malformed_json: int = 0
    invalid_timestamp: int = 0
    out_of_window: int = 0
    unsupported_type: int = 0
    sampled_errors: list[str] = field(default_factory=list)

    def sample(self, kind: str, message: str) -> None:
        if len(self.sampled_errors) < 5:
            self.sampled_errors.append(f"{kind}: {message}")

    def as_dict(self) -> dict[str, Any]:
        return {
            "malformed_json": self.malformed_json,
            "invalid_timestamp": self.invalid_timestamp,
            "out_of_window": self.out_of_window,
            "unsupported_type": self.unsupported_type,
            "sampled_errors": self.sampled_errors,
        }


def get_git_commits(path: str | Path, start: datetime | None = None, end: datetime | None = None) -> GitCommitPayload:
    repo = Path(path)
    if not (repo / ".git").exists():
        return GitCommitPayload(status="not_repo", commits=[], error={"type": "not_repo"})
    args = ["git", "-C", str(repo), "log", "--pretty=%H%x00%s"]
    if start is not None:
        args.append(f"--since={start.isoformat()}")
    if end is not None:
        args.append(f"--until={end.isoformat()}")
    result = subprocess.run(args, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        return GitCommitPayload(status="error", commits=[], error={"type": "git_log_failed", "message": result.stderr})
    commits = []
    for line in result.stdout.splitlines():
        sha, _, message = line.partition("\0")
        if sha:
            commits.append(GitCommit(sha=sha, message=message))
    return GitCommitPayload(status="ok" if commits else "empty", commits=commits)


def _parse_log_entry(row: str, start: datetime, end: datetime, stats: LogParseStats) -> dict[str, Any] | None:
    try:
        payload = orjson.loads(row)
    except orjson.JSONDecodeError as exc:
        stats.malformed_json += 1
        stats.sample("malformed_json", str(exc))
        return None
    entry_type = payload.get("type")
    if entry_type not in {"assistant", "user"}:
        stats.unsupported_type += 1
        stats.sample("unsupported_type", str(entry_type))
        return None
    try:
        timestamp = datetime.fromisoformat(str(payload["timestamp"]))
    except Exception as exc:
        stats.invalid_timestamp += 1
        stats.sample("invalid_timestamp", str(exc))
        return None
    if not (start <= timestamp <= end):
        stats.out_of_window += 1
        return None
    return payload


def _read_log_file(path: Path, start: datetime, end: datetime, include_diagnostics: bool = False) -> dict[str, Any]:
    stats = LogParseStats()
    entries: list[dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                parsed = _parse_log_entry(line.strip(), start, end, stats)
                if parsed is not None:
                    entries.append(parsed)
    except FileNotFoundError as exc:
        return {"status": "missing", "entries": 0, "error": {"type": type(exc).__name__, "message": str(exc)}}
    except PermissionError as exc:
        return {"status": "permission_denied", "entries": 0, "error": {"type": type(exc).__name__, "message": str(exc)}}
    payload: dict[str, Any] = {"status": "ok", "entries": len(entries)}
    if include_diagnostics:
        payload["parse_counts"] = stats.as_dict()
    return payload


__all__ = ["GitCommit", "GitCommitPayload", "LogParseStats", "_parse_log_entry", "_read_log_file", "get_git_commits"]
