"""Summary and audit log implementation for thegent."""

import json
import os
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from thegent.config import ThegentSettings
from thegent.execution import RunRegistry


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


def get_git_commits(project_path: Path, start_dt: datetime, end_dt: datetime) -> list[str]:
    """Fetch git commits within the time range."""
    if not (project_path / ".git").exists():
        return []
    try:
        since = start_dt.isoformat()
        until = end_dt.isoformat()
        cmd = ["git", "log", f"--since={since}", f"--until={until}", "--pretty=format:%h %ad %s", "--date=short"]
        res = subprocess.run(cmd, cwd=str(project_path), capture_output=True, text=True, check=True)
        return [line.strip() for line in res.stdout.splitlines() if line.strip()]
    except Exception:
        return []


def _parse_log_entry(line: str, start_dt: datetime, end_dt: datetime) -> dict[str, Any] | None:
    """Parse a single log entry, returning it if within time range."""
    try:
        data = json.loads(line)
        if data.get("type") in ("user", "assistant"):
            ts_str = data.get("timestamp")
            if ts_str:
                # handle various timestamp formats
                ts = datetime.fromisoformat(ts_str)

                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=UTC)

                if start_dt <= ts <= end_dt:
                    return data
    except Exception:
        pass
    return None


def _read_log_file(log_file: Path, start_dt: datetime, end_dt: datetime) -> list[dict[str, Any]]:
    """Read a single log file and return entries within time range."""
    logs = []
    try:
        with log_file.open("r", encoding="utf-8") as f:
            for line in f:
                entry = _parse_log_entry(line, start_dt, end_dt)
                if entry is not None:
                    logs.append(entry)
    except Exception:
        pass
    return logs


def get_chat_logs(session_dir: Path, project_key: str, start_dt: datetime, end_dt: datetime) -> list[dict[str, Any]]:
    """Fetch chat logs from project session directory."""
    project_logs_dir = session_dir / "claude-config" / "projects" / project_key
    if not project_logs_dir.exists():
        return []

    logs = []
    for log_file in project_logs_dir.glob("*.jsonl"):
        logs.extend(_read_log_file(log_file, start_dt, end_dt))
    return sorted(logs, key=lambda x: x.get("timestamp", ""))


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
    chat_logs = get_chat_logs(session_dir, project_key, start_dt, end_dt)

    # 3. Git Commits
    commits = get_git_commits(resolved_path, start_dt, end_dt)

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
