"""Automatic bidirectional synchronization for local workstream + external trackers."""

from __future__ import annotations

import json
import re
import subprocess
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

BOARD_ID_RE = re.compile(r"\b(WL-\d+)\b")


@dataclass(slots=True)
class LocalWorkItem:
    board_id: str
    title: str
    status: str
    priority: str


@dataclass(slots=True)
class SyncCycleReport:
    timestamp: str
    local_items: int
    github_created: int
    linear_created: int
    status_reflections_applied: int
    notes: list[str]


def run_autosync_loop(
    *,
    settings: Any,
    project_root: Path,
    once: bool,
    interval_sec: int,
) -> None:
    if not settings.workstream_autosync_enabled:
        raise RuntimeError(
            "Autopilot is disabled. Set THGENT_WORKSTREAM_AUTOSYNC_ENABLED=1 to enable automatic synchronization."
        )

    work_stream = (project_root / "docs/reference/WORK_STREAM.md").resolve()
    reports_dir = (project_root / "docs/reports").resolve()
    reports_dir.mkdir(parents=True, exist_ok=True)

    while True:
        report = _run_cycle(settings=settings, work_stream=work_stream)
        report_payload = {
            "timestamp": report.timestamp,
            "local_items": report.local_items,
            "github_created": report.github_created,
            "linear_created": report.linear_created,
            "status_reflections_applied": report.status_reflections_applied,
            "notes": report.notes,
        }
        latest_path = reports_dir / "workstream_autosync_latest.json"
        latest_path.write_text(json.dumps(report_payload, indent=2), encoding="utf-8")
        stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        (reports_dir / f"workstream_autosync_{stamp}.json").write_text(
            json.dumps(report_payload, indent=2), encoding="utf-8"
        )

        if once:
            return
        time.sleep(interval_sec)


def _run_cycle(*, settings: Any, work_stream: Path) -> SyncCycleReport:
    local_items = _parse_local_work_items(work_stream)
    status_updates: dict[str, str] = {}
    notes: list[str] = []

    github_created = 0
    if settings.gh_project_sync_enabled:
        github_created, gh_status_map = _sync_github(settings=settings, local_items=local_items)
        status_updates.update(gh_status_map)
        notes.append(f"github: created={github_created}, reflected={len(gh_status_map)}")

    linear_created = 0
    if settings.linear_sync_enabled:
        linear_created, lin_status_map = _sync_linear(settings=settings, local_items=local_items)
        # Do not overwrite explicit GitHub reflections for same item in same cycle.
        for board_id, status in lin_status_map.items():
            status_updates.setdefault(board_id, status)
        notes.append(f"linear: created={linear_created}, reflected={len(lin_status_map)}")

    applied = _apply_status_reflections(work_stream=work_stream, status_updates=status_updates)
    return SyncCycleReport(
        timestamp=datetime.now(UTC).isoformat(),
        local_items=len(local_items),
        github_created=github_created,
        linear_created=linear_created,
        status_reflections_applied=applied,
        notes=notes,
    )


def _parse_local_work_items(work_stream: Path) -> list[LocalWorkItem]:
    if not work_stream.exists():
        raise FileNotFoundError(f"WORK_STREAM.md not found: {work_stream}")

    lines = work_stream.read_text(encoding="utf-8").splitlines()
    items: list[LocalWorkItem] = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line.startswith("### [WL-"):
            i += 1
            continue
        m = re.match(r"^### \[(WL-\d+)\]\s+(.+)$", line)
        if not m:
            i += 1
            continue
        board_id, title = m.group(1), m.group(2).strip()
        status = "BACKLOG"
        priority = "P2"
        j = i + 1
        while j < len(lines):
            cur = lines[j].strip()
            if cur.startswith("### [WL-"):
                break
            if cur.startswith("**Status:**"):
                status = cur.replace("**Status:**", "").strip()
            elif cur.startswith("**Priority:**"):
                priority = cur.replace("**Priority:**", "").strip()
            j += 1
        items.append(LocalWorkItem(board_id=board_id, title=title, status=status, priority=priority))
        i = j
    return items


def _sync_github(*, settings: Any, local_items: list[LocalWorkItem]) -> tuple[int, dict[str, str]]:
    owner = str(settings.gh_project_owner or "").strip()
    number = int(settings.gh_project_number or 0)
    if not owner or number <= 0:
        raise RuntimeError(
            "GitHub sync enabled but not configured. Set THGENT_GH_PROJECT_OWNER and THGENT_GH_PROJECT_NUMBER."
        )
    if _run_gh(["auth", "status"]).returncode != 0:
        raise RuntimeError("GitHub sync enabled but gh auth is not ready. Run `gh auth status` and add project scope.")

    remote_items = _gh_fetch_items(owner=owner, number=number)
    existing_board_ids = {bid for bid in (_gh_board_id(it) for it in remote_items) if bid}
    existing_titles = {str(it.get("title", "")).strip() for it in remote_items}

    created = 0
    for item in local_items:
        if item.board_id in existing_board_ids or item.title in existing_titles:
            continue
        body = (
            f"Board ID: {item.board_id}\n"
            f"Status: {item.status}\n"
            f"Priority: {item.priority}\n"
            "Synced from docs/reference/WORK_STREAM.md"
        )
        proc = _run_gh(
            [
                "project",
                "item-create",
                str(number),
                "--owner",
                owner,
                "--title",
                item.title,
                "--body",
                body,
            ]
        )
        if proc.returncode == 0:
            created += 1

    status_reflections: dict[str, str] = {}
    for remote in _gh_fetch_items(owner=owner, number=number):
        board_id = _gh_board_id(remote)
        if not board_id:
            continue
        remote_status = _gh_status(remote)
        if remote_status:
            status_reflections[board_id] = remote_status
    return created, status_reflections


def _sync_linear(*, settings: Any, local_items: list[LocalWorkItem]) -> tuple[int, dict[str, str]]:
    api_key = str(settings.linear_api_key or "").strip()
    team_id = str(settings.linear_team_id or "").strip()
    if not api_key or not team_id:
        raise RuntimeError(
            "Linear sync enabled but missing configuration. Set THGENT_LINEAR_API_KEY and THGENT_LINEAR_TEAM_ID."
        )

    issues = _linear_fetch_issues(api_url=settings.linear_api_url, api_key=api_key, team_id=team_id)
    by_board_id = {_linear_board_id(issue): issue for issue in issues if _linear_board_id(issue)}
    by_title = {str(issue.get("title", "")).strip(): issue for issue in issues}

    created = 0
    for item in local_items:
        existing = by_board_id.get(item.board_id) or by_title.get(item.title)
        if existing:
            issue_id = str(existing.get("id", "")).strip()
            if issue_id:
                _linear_update_issue(
                    api_url=settings.linear_api_url,
                    api_key=api_key,
                    issue_id=issue_id,
                    title=item.title,
                    description=_linear_description(item),
                    priority=_linear_priority(item.priority),
                )
            continue
        ok = _linear_create_issue(
            api_url=settings.linear_api_url,
            api_key=api_key,
            team_id=team_id,
            title=item.title,
            description=_linear_description(item),
            priority=_linear_priority(item.priority),
            project_id=str(settings.linear_project_id or "").strip() or None,
        )
        if ok:
            created += 1

    status_reflections: dict[str, str] = {}
    for issue in _linear_fetch_issues(api_url=settings.linear_api_url, api_key=api_key, team_id=team_id):
        board_id = _linear_board_id(issue)
        if not board_id:
            continue
        state = (((issue.get("state") or {})).get("name") or "").strip()
        if state:
            status_reflections[board_id] = _normalize_remote_status(state)
    return created, status_reflections


def _apply_status_reflections(*, work_stream: Path, status_updates: dict[str, str]) -> int:
    if not status_updates:
        return 0
    lines = work_stream.read_text(encoding="utf-8").splitlines()
    applied = 0
    current_board_id: str | None = None
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("### [WL-"):
            match = re.match(r"^### \[(WL-\d+)\]\s+(.+)$", stripped)
            current_board_id = match.group(1) if match else None
            continue
        if not current_board_id or not stripped.startswith("**Status:**"):
            continue
        new_status = status_updates.get(current_board_id)
        if not new_status:
            continue
        current_status = stripped.replace("**Status:**", "").strip()
        if current_status == new_status:
            continue
        lines[idx] = f"**Status:** {new_status}"
        applied += 1
    if applied:
        work_stream.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return applied


def _gh_fetch_items(*, owner: str, number: int) -> list[dict[str, Any]]:
    proc = _run_gh(["project", "item-list", str(number), "--owner", owner, "--limit", "500", "--format", "json"])
    if proc.returncode != 0:
        raise RuntimeError(f"gh project item-list failed: {(proc.stderr or proc.stdout).strip()}")
    payload = json.loads(proc.stdout or "[]")
    if not isinstance(payload, list):
        return []
    return [item for item in payload if isinstance(item, dict)]


def _gh_board_id(item: dict[str, Any]) -> str:
    title = str(item.get("title", ""))
    title_id = BOARD_ID_RE.search(title)
    if title_id:
        return title_id.group(1)
    content = item.get("content") or {}
    if isinstance(content, dict):
        body = str(content.get("body", ""))
        m = re.search(r"Board ID:\s*(WL-\d+)", body)
        if m:
            return m.group(1)
    return ""


def _gh_status(item: dict[str, Any]) -> str:
    field_values = item.get("fieldValues")
    if not isinstance(field_values, list):
        return ""
    for field in field_values:
        if not isinstance(field, dict):
            continue
        field_name = str(((field.get("field") or {}).get("name")) or field.get("name") or "")
        if field_name != "Status":
            continue
        raw = str(field.get("name") or field.get("text") or field.get("value") or "")
        if raw:
            return _normalize_remote_status(raw)
    return ""


def _normalize_remote_status(raw: str) -> str:
    value = raw.strip().lower()
    if any(token in value for token in ("done", "complete", "closed", "cancelled", "canceled")):
        return "COMPLETED"
    if any(token in value for token in ("progress", "doing", "active", "started", "in progress")):
        return "IN PROGRESS"
    if any(token in value for token in ("backlog", "todo", "to do", "planned", "open")):
        return "BACKLOG"
    return raw.strip().upper()


def _run_gh(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603
        ["gh", *args],
        check=False,
        capture_output=True,
        text=True,
        timeout=90,
    )


def _linear_fetch_issues(*, api_url: str, api_key: str, team_id: str) -> list[dict[str, Any]]:
    query = """
    query TeamIssues($teamId: String!) {
      issues(
        filter: { team: { id: { eq: $teamId } } }
        first: 250
      ) {
        nodes {
          id
          identifier
          title
          description
          priority
          state { name }
          updatedAt
          url
        }
      }
    }
    """
    data = _linear_graphql(api_url=api_url, api_key=api_key, query=query, variables={"teamId": team_id})
    nodes = (((data.get("issues") or {}).get("nodes")) or [])
    return [node for node in nodes if isinstance(node, dict)]


def _linear_create_issue(
    *,
    api_url: str,
    api_key: str,
    team_id: str,
    title: str,
    description: str,
    priority: int,
    project_id: str | None,
) -> bool:
    mutation = """
    mutation IssueCreate($input: IssueCreateInput!) {
      issueCreate(input: $input) {
        success
      }
    }
    """
    payload: dict[str, Any] = {
        "teamId": team_id,
        "title": title,
        "description": description,
        "priority": priority,
    }
    if project_id:
        payload["projectId"] = project_id
    data = _linear_graphql(api_url=api_url, api_key=api_key, query=mutation, variables={"input": payload})
    return bool(((data.get("issueCreate") or {}).get("success")))


def _linear_update_issue(
    *,
    api_url: str,
    api_key: str,
    issue_id: str,
    title: str,
    description: str,
    priority: int,
) -> bool:
    mutation = """
    mutation IssueUpdate($id: String!, $input: IssueUpdateInput!) {
      issueUpdate(id: $id, input: $input) {
        success
      }
    }
    """
    data = _linear_graphql(
        api_url=api_url,
        api_key=api_key,
        query=mutation,
        variables={"id": issue_id, "input": {"title": title, "description": description, "priority": priority}},
    )
    return bool(((data.get("issueUpdate") or {}).get("success")))


def _linear_graphql(*, api_url: str, api_key: str, query: str, variables: dict[str, Any]) -> dict[str, Any]:
    with httpx.Client(timeout=30.0) as client:
        response = client.post(
            api_url,
            headers={"Authorization": api_key, "Content-Type": "application/json"},
            json={"query": query, "variables": variables},
        )
    response.raise_for_status()
    payload = response.json()
    if payload.get("errors"):
        raise RuntimeError(f"Linear GraphQL error: {payload['errors']}")
    data = payload.get("data")
    if not isinstance(data, dict):
        raise RuntimeError("Linear GraphQL did not return a data object.")
    return data


def _linear_board_id(issue: dict[str, Any]) -> str:
    desc = str(issue.get("description", "") or "")
    m = re.search(r"Board ID:\s*(WL-\d+)", desc)
    if m:
        return m.group(1)
    title = str(issue.get("title", "") or "")
    t = BOARD_ID_RE.search(title)
    return t.group(1) if t else ""


def _linear_description(item: LocalWorkItem) -> str:
    return (
        f"Board ID: {item.board_id}\n"
        f"Status: {item.status}\n"
        f"Priority: {item.priority}\n"
        "Source: docs/reference/WORK_STREAM.md"
    )


def _linear_priority(priority: str) -> int:
    mapping = {"P0": 1, "P1": 1, "P2": 2, "P3": 3, "P4": 4}
    return mapping.get(priority.strip().upper(), 2)
