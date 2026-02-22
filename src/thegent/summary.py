"""Summary and audit log implementation for thegent."""

import json
import logging
import os
import subprocess
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from thegent.config import ThegentSettings
from thegent.execution import RunRegistry

_log = logging.getLogger(__name__)


@dataclass
class GitCommitsResult:
    commits: list[str]
    status: str
    error: dict[str, Any] | None = None


@dataclass
class LogParseStats:
    malformed_json: int = 0
    missing_required_key: int = 0
    invalid_shape: int = 0
    invalid_timestamp: int = 0
    out_of_window: int = 0
    unsupported_type: int = 0
    sampled_errors: list[str] = field(default_factory=list)
    sample_limit: int = 5

    def sample(self, kind: str, detail: str, line: str) -> None:
        if len(self.sampled_errors) >= self.sample_limit:
            return
        self.sampled_errors.append(f"{kind}: {detail[:100]} | line={line.strip()[:120]}")

    def as_dict(self) -> dict[str, Any]:
        return {
            "malformed_json": self.malformed_json,
            "missing_required_key": self.missing_required_key,
            "invalid_shape": self.invalid_shape,
            "invalid_timestamp": self.invalid_timestamp,
            "out_of_window": self.out_of_window,
            "unsupported_type": self.unsupported_type,
            "sampled_errors": self.sampled_errors,
        }


def get_project_key(project_path: Path) -> str:
    """Generate filesystem-safe key for project path (WP-3006)."""
    path_str = str(project_path.expanduser().resolve())
    return path_str.replace("/", "-")


def get_time_range(period: str) -> tuple[datetime, datetime]:
    """Resolve period string into start and end datetimes."""
    now = datetime.now(UTC)
    if period == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "yesterday":
        start = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        end = now.replace(hour=0, minute=0, second=0, microsecond=0)
        return start, end
    elif period == "week":
        # Start of current week (Monday)
        start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    elif period.endswith("d"):
        try:
            days = int(period[:-1])
            start = now - timedelta(days=days)
        except ValueError:
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period.endswith("h"):
        try:
            hours = int(period[:-1])
            start = now - timedelta(hours=hours)
        except ValueError:
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        # Default to today
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return start, now


def get_git_commits(project_path: Path, start_dt: datetime, end_dt: datetime) -> GitCommitsResult:
    """Fetch git commits within the time range."""
    if not (project_path / ".git").exists():
        error = {"type": "not_repo", "message": f"Missing .git in {project_path}"}
        _log.warning(
            "Git commit collection skipped: not a git repo (cwd=%s, cmd=%s)",
            str(project_path),
            " ".join(cmd for cmd in ("git", "log")),
        )
        return GitCommitsResult(commits=[], status="not_repo", error=error)

    since = start_dt.isoformat()
    until = end_dt.isoformat()
    cmd = ["git", "log", f"--since={since}", f"--until={until}", "--pretty=format:%h %ad %s", "--date=short"]
    try:
        res = subprocess.run(cmd, cwd=str(project_path), capture_output=True, text=True, check=False)
    except OSError as exc:
        error = {"type": type(exc).__name__, "message": str(exc)[:200]}
        _log.warning("Git commit collection failed: cwd=%s cmd=%s error=%s", str(project_path), " ".join(cmd), exc)
        return GitCommitsResult(commits=[], status="error", error=error)

    if res.returncode != 0:
        error = {
            "type": "git_log_failed",
            "message": (res.stderr.strip() or f"git log exited with status {res.returncode}")[:200],
            "returncode": res.returncode,
        }
        _log.warning(
            "Git commit collection failed: cwd=%s cmd=%s returncode=%s stderr=%s",
            str(project_path),
            " ".join(cmd),
            res.returncode,
            (res.stderr or "").strip()[:500],
        )
        return GitCommitsResult(commits=[], status="error", error=error)

    commits = [line.strip() for line in res.stdout.splitlines() if line.strip()]
    return GitCommitsResult(commits=commits, status="empty" if not commits else "ok")


def _parse_log_entry(
    line: str, start_dt: datetime, end_dt: datetime, diagnostics: LogParseStats | None = None
) -> dict[str, Any] | None:
    """Parse a single log entry, returning it if within time range."""
    try:
        data = json.loads(line)
    except json.JSONDecodeError as exc:
        if diagnostics is not None:
            diagnostics.malformed_json += 1
            diagnostics.sample("malformed_json", str(exc), line)
        return None

    if not isinstance(data, dict):
        if diagnostics is not None:
            diagnostics.invalid_shape += 1
            diagnostics.sample("invalid_shape", f"type={type(data).__name__}", line)
        return None

    try:
        if data["type"] in ("user", "assistant"):
            ts_str = data["timestamp"]
            # handle various timestamp formats
            ts = datetime.fromisoformat(ts_str)

            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=UTC)

            if start_dt <= ts <= end_dt:
                return data
            if diagnostics is not None:
                diagnostics.out_of_window += 1
        elif diagnostics is not None:
            diagnostics.unsupported_type += 1
    except KeyError:
        if diagnostics is not None:
            diagnostics.missing_required_key += 1
            diagnostics.sample("missing_required_key", "required key missing", line)
    except (TypeError, ValueError) as exc:
        if diagnostics is not None:
            diagnostics.invalid_timestamp += 1
            diagnostics.sample("invalid_timestamp", str(exc), line)
    return None


def _read_log_file(
    log_file: Path, start_dt: datetime, end_dt: datetime, *, include_diagnostics: bool = False
) -> list[dict[str, Any]] | dict[str, Any]:
    """Read a single log file and return entries within time range."""
    parse_stats = LogParseStats()
    diagnostics: dict[str, Any] = {
        "path": str(log_file),
        "status": "ok",
        "entries": 0,
        "logs": [],
        "parse_counts": parse_stats.as_dict(),
        "error": None,
    }
    logs = []
    try:
        with log_file.open("r", encoding="utf-8") as f:
            for line in f:
                entry = _parse_log_entry(line, start_dt, end_dt, parse_stats)
                if entry is not None:
                    logs.append(entry)
    except FileNotFoundError as exc:
        diagnostics["status"] = "missing"
        diagnostics["error"] = {"type": type(exc).__name__, "message": str(exc)}
        return diagnostics if include_diagnostics else logs
    except PermissionError as exc:
        diagnostics["status"] = "permission_denied"
        diagnostics["error"] = {"type": type(exc).__name__, "message": str(exc)}
        return diagnostics if include_diagnostics else logs
    except UnicodeDecodeError as exc:
        diagnostics["status"] = "decode_error"
        diagnostics["error"] = {"type": type(exc).__name__, "message": str(exc)}
        return diagnostics if include_diagnostics else logs
    except OSError as exc:
        diagnostics["status"] = "io_error"
        diagnostics["error"] = {"type": type(exc).__name__, "message": str(exc)}
        return diagnostics if include_diagnostics else logs

    diagnostics["entries"] = len(logs)
    diagnostics["logs"] = logs
    diagnostics["parse_counts"] = parse_stats.as_dict()
    return diagnostics if include_diagnostics else logs


def get_chat_logs(
    session_dir: Path, project_key: str, start_dt: datetime, end_dt: datetime, *, include_diagnostics: bool = False
) -> list[dict[str, Any]] | dict[str, Any]:
    """Fetch chat logs from project session directory."""
    project_logs_dir = session_dir / "claude-config" / "projects" / project_key
    payload: dict[str, Any] = {
        "logs": [],
        "status": "ok",
        "diagnostics": {
            "project_logs_dir": str(project_logs_dir),
            "files_seen": 0,
            "files_readable": 0,
            "files_unreadable": 0,
            "parse_counts": {
                "malformed_json": 0,
                "missing_required_key": 0,
                "invalid_shape": 0,
                "invalid_timestamp": 0,
                "out_of_window": 0,
                "unsupported_type": 0,
                "sampled_errors": [],
            },
            "file_errors": [],
        },
    }
    if not project_logs_dir.exists():
        payload["status"] = "missing_directory"
        return payload if include_diagnostics else []

    logs = []
    for log_file in project_logs_dir.glob("*.jsonl"):
        payload["diagnostics"]["files_seen"] += 1
        file_result = _read_log_file(log_file, start_dt, end_dt, include_diagnostics=True)
        if file_result["status"] == "ok":
            payload["diagnostics"]["files_readable"] += 1
        else:
            payload["diagnostics"]["files_unreadable"] += 1
            payload["diagnostics"]["file_errors"].append(
                {
                    "path": file_result["path"],
                    "status": file_result["status"],
                    "error": file_result["error"],
                }
            )

        parse_counts = payload["diagnostics"]["parse_counts"]
        for key, count in file_result["parse_counts"].items():
            if key == "sampled_errors":
                existing = parse_counts["sampled_errors"]
                for sample in count:
                    if len(existing) >= 5:
                        break
                    existing.append(sample)
            else:
                parse_counts[key] += count

        if file_result["status"] == "ok":
            logs.extend(file_result["logs"])

    payload["logs"] = sorted(logs, key=lambda x: x.get("timestamp", ""))
    if payload["diagnostics"]["files_seen"] == 0:
        payload["status"] = "empty"
    elif payload["diagnostics"]["files_unreadable"] > 0:
        payload["status"] = "partial" if logs else "error"
    return payload if include_diagnostics else payload["logs"]


def summary_impl(
    period: str = "today",
    project_path: Path | None = None,
    summarize: bool = True,
    agent: str = "claude",
) -> dict[str, Any]:
    """FR-X09: Unified summary and audit log across runs, chats, and commits."""
    from thegent.cli.commands.impl import _resolve_cwd, run_impl

    settings = ThegentSettings()
    resolved_path = _resolve_cwd(project_path) or Path.cwd()
    session_dir = Path(settings.session_dir).expanduser().resolve()

    start_dt, end_dt = get_time_range(period)

    # 1. Runs (Actions)
    registry = RunRegistry(session_dir)
    # Get a large enough history to cover the period
    all_runs = registry.list_runs(limit=2000)
    project_abs = str(resolved_path.resolve())

    filtered_runs = []
    for run in all_runs:
        started_str = run.get("started_at_utc")
        if started_str:
            try:
                started_dt = datetime.fromisoformat(started_str)
                if started_dt.tzinfo is None:
                    started_dt = started_dt.replace(tzinfo=UTC)

                if start_dt <= started_dt <= end_dt:
                    # Check if run belongs to project
                    run_cwd = run.get("cwd")
                    if run_cwd and (run_cwd == project_abs or run_cwd.startswith(project_abs + os.sep)):
                        filtered_runs.append(run)
            except Exception:
                continue

    # 2. Chat Logs
    project_key = get_project_key(resolved_path)
    chat_logs_result = get_chat_logs(session_dir, project_key, start_dt, end_dt, include_diagnostics=True)
    chat_logs = chat_logs_result["logs"]

    # 3. Git Commits
    commit_result = get_git_commits(resolved_path, start_dt, end_dt)
    commits = commit_result.commits

    # Format Audit Log
    audit_lines = [f"# Audit Log for {resolved_path}", f"Period: {period} ({start_dt.date()} to {end_dt.date()})", ""]

    if commits:
        audit_lines.append("## Git Commits")
        for c in commits:
            audit_lines.append(f"- {c}")
        audit_lines.append("")

    if filtered_runs:
        audit_lines.append("## Actions / Runs")
        # Sort runs by time ascending for audit log
        filtered_runs.sort(key=lambda x: x.get("started_at_utc", ""))
        for r in filtered_runs:
            ts_str = r.get("started_at_utc", "")
            ts = ts_str.split("T")[-1][:8] if "T" in ts_str else ts_str
            status = r.get("status", "started")
            agent_name = r.get("agent", "?")
            prompt = r.get("prompt", "")
            prompt_preview = (prompt[:100] + "...") if len(prompt) > 100 else prompt
            audit_lines.append(f"- **{ts}** [{agent_name}] {status}: {prompt_preview}")
        audit_lines.append("")

    if chat_logs:
        audit_lines.append("## Chat History")
        for log in chat_logs:
            ts_str = log.get("timestamp", "")
            ts = ts_str.split("T")[-1][:8] if "T" in ts_str else ts_str
            role = log.get("type", "")
            message_obj = log.get("message", {})
            msg = ""
            if isinstance(message_obj, dict):
                content = message_obj.get("content", "")
                if isinstance(content, list):
                    msg = " ".join(
                        [c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text"]
                    )
                else:
                    msg = str(content)

            msg_preview = (msg[:150] + "...") if len(msg) > 150 else msg
            audit_lines.append(f"- **{ts}** [{role}]: {msg_preview}")
        audit_lines.append("")

    audit_log = "\n".join(audit_lines)

    result = {
        "audit_log": audit_log,
        "project": str(resolved_path),
        "period": period,
        "start_dt": start_dt.isoformat(),
        "end_dt": end_dt.isoformat(),
        "counts": {
            "runs": len(filtered_runs),
            "chats": len(chat_logs),
            "commits": len(commits),
        },
        "diagnostics": {
            "git_commits": {
                "status": commit_result.status,
                "error": commit_result.error,
            },
            "chat_logs": {
                "status": chat_logs_result["status"],
                "files_seen": chat_logs_result["diagnostics"]["files_seen"],
                "files_unreadable": chat_logs_result["diagnostics"]["files_unreadable"],
                "parse_counts": chat_logs_result["diagnostics"]["parse_counts"],
                "file_errors": chat_logs_result["diagnostics"]["file_errors"],
            },
        },
    }

    if summarize and (commits or filtered_runs or chat_logs):
        summary_prompt = f"""You are thegent summary agent. I will provide you with an audit log of runs, chat messages, and git commits for a specific project and time period.
Your task is to summarize what was accomplished, what issues were encountered, and what the overall progress looks like.

Audit Log:
{audit_log}

Please provide a concise but comprehensive report in Markdown with these sections:
1. **High-level Summary** (1-2 paragraphs)
2. **Key Accomplishments** (bullet points)
3. **Issues Encountered** (if any)
4. **Next Steps** (if evident from logs)
"""
        # Call agent for summary
        summary_res = run_impl(agent=agent, prompt=summary_prompt, mode="write", timeout=120, full=True)
        if "stdout" in summary_res:
            result["summary"] = summary_res["stdout"]
        else:
            result["summary"] = "Error generating summary: " + summary_res.get("error", "Unknown error")
    elif summarize:
        result["summary"] = "No activity found for the specified period and project."

    return result
