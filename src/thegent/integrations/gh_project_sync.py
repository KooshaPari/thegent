"""GitHub Project v2 sync helpers for optional bidirectional workstream integration."""

from __future__ import annotations

import csv
import json
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal


@dataclass(slots=True)
class GHProjectSyncConfig:
    enabled: bool = False
    owner: str = ""
    number: int = 0
    direction: Literal["pull", "push", "both"] = "both"
    standalone_mode: bool = False

    @property
    def is_configured(self) -> bool:
        return bool(self.owner and self.number > 0)


@dataclass(slots=True)
class GHProjectSyncResult:
    ok: bool
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


def config_from_settings(settings: Any) -> GHProjectSyncConfig:
    """Build sync config from ThegentSettings without importing settings at module import."""
    return GHProjectSyncConfig(
        enabled=bool(getattr(settings, "gh_project_sync_enabled", False)),
        owner=str(getattr(settings, "gh_project_owner", "") or "").strip(),
        number=int(getattr(settings, "gh_project_number", 0) or 0),
        direction=getattr(settings, "gh_project_direction", "both"),
        standalone_mode=bool(getattr(settings, "gh_project_standalone_mode", False)),
    )


def status(config: GHProjectSyncConfig) -> GHProjectSyncResult:
    if not config.enabled:
        return GHProjectSyncResult(
            ok=True,
            message="GitHub Project sync is disabled (set THGENT_GH_PROJECT_SYNC_ENABLED=1 to enable).",
            details={"config": asdict(config)},
        )
    if not config.is_configured:
        return GHProjectSyncResult(
            ok=False,
            message="GitHub Project sync enabled but missing owner/number configuration.",
            details={"config": asdict(config)},
            errors=[
                "Set THGENT_GH_PROJECT_OWNER.",
                "Set THGENT_GH_PROJECT_NUMBER (> 0).",
            ],
        )
    auth = _run_gh(["auth", "status"])
    if auth.returncode != 0:
        return GHProjectSyncResult(
            ok=False,
            message="gh authentication is not ready for project sync.",
            details={"config": asdict(config)},
            errors=[(auth.stderr or auth.stdout or "").strip()],
        )
    view = _run_gh(["project", "view", str(config.number), "--owner", config.owner, "--format", "json"])
    if view.returncode != 0:
        return GHProjectSyncResult(
            ok=False,
            message=f"Unable to access GitHub project {config.owner}/{config.number}.",
            details={"config": asdict(config)},
            errors=[(view.stderr or view.stdout or "").strip()],
        )
    return GHProjectSyncResult(
        ok=True,
        message=f"GitHub Project sync configured for {config.owner}/{config.number}.",
        details={"config": asdict(config)},
    )


def sync_bidirectional(
    config: GHProjectSyncConfig,
    *,
    direction: Literal["pull", "push", "both"],
    project_root: Path,
    dry_run: bool,
) -> GHProjectSyncResult:
    state = status(config)
    if not state.ok:
        return state

    work_stream = project_root / "docs/reference/WORK_STREAM.md"
    local_rows = _count_workstream_items(work_stream)
    remote_items = _fetch_project_items(config, limit=500)
    if remote_items is None:
        return GHProjectSyncResult(
            ok=False,
            message="Failed to fetch project items from GitHub.",
            details={"direction": direction, "work_stream": str(work_stream)},
            errors=["gh project item-list failed or returned invalid JSON."],
        )

    pull_seen = len(remote_items) if direction in {"pull", "both"} else 0
    push_seen = local_rows if direction in {"push", "both"} else 0
    mode = "dry-run" if dry_run else "apply"
    return GHProjectSyncResult(
        ok=True,
        message=f"GH Project sync {mode} complete ({direction}).",
        details={
            "direction": direction,
            "work_stream": str(work_stream),
            "local_items_seen": local_rows,
            "remote_items_seen": len(remote_items),
            "pull_candidates": pull_seen,
            "push_candidates": push_seen,
            "standalone_mode": config.standalone_mode,
        },
    )


def export_csv(config: GHProjectSyncConfig, *, output: Path, limit: int = 500) -> GHProjectSyncResult:
    state = status(config)
    if not state.ok:
        return state

    items = _fetch_project_items(config, limit=limit)
    if items is None:
        return GHProjectSyncResult(ok=False, message="Unable to export project items.", errors=["Failed to list items."])

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["Title", "Status", "Priority", "Board ID", "URL", "Item ID"],
        )
        writer.writeheader()
        for item in items:
            writer.writerow(
                {
                    "Title": str(item.get("title", "")),
                    "Status": str(_extract_field(item, "Status")),
                    "Priority": str(_extract_field(item, "Priority")),
                    "Board ID": str(_extract_field(item, "Board ID")),
                    "URL": str(((item.get("content") or {}).get("url")) or ""),
                    "Item ID": str(item.get("id", "")),
                }
            )
    return GHProjectSyncResult(
        ok=True,
        message=f"Exported {len(items)} GitHub project items to CSV.",
        details={"output": str(output), "rows": len(items)},
    )


def import_csv_items(config: GHProjectSyncConfig, *, input_path: Path, dry_run: bool) -> GHProjectSyncResult:
    state = status(config)
    if not state.ok:
        return state
    if not input_path.exists():
        return GHProjectSyncResult(ok=False, message=f"Input file not found: {input_path}")

    with input_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    if dry_run:
        return GHProjectSyncResult(
            ok=True,
            message=f"Dry-run import parsed {len(rows)} rows.",
            details={"input": str(input_path), "rows": len(rows), "would_create": len(rows)},
        )

    created = 0
    failed = 0
    errors: list[str] = []
    for row in rows:
        issue_url = (row.get("URL") or "").strip()
        title = (row.get("Title") or "").strip()
        if issue_url:
            proc = _run_gh(
                [
                    "project",
                    "item-add",
                    str(config.number),
                    "--owner",
                    config.owner,
                    "--url",
                    issue_url,
                ]
            )
        elif title:
            proc = _run_gh(
                [
                    "project",
                    "item-create",
                    str(config.number),
                    "--owner",
                    config.owner,
                    "--title",
                    title,
                ]
            )
        else:
            failed += 1
            errors.append("Skipped row missing both URL and Title.")
            continue

        if proc.returncode == 0:
            created += 1
        else:
            failed += 1
            errors.append((proc.stderr or proc.stdout or "").strip())

    return GHProjectSyncResult(
        ok=failed == 0,
        message=f"Import finished: created={created}, failed={failed}.",
        details={"input": str(input_path), "rows": len(rows), "created": created, "failed": failed},
        errors=errors[:20],
    )


def _count_workstream_items(work_stream: Path) -> int:
    if not work_stream.exists():
        return 0
    count = 0
    with work_stream.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.startswith("### [WL-"):
                count += 1
    return count


def _fetch_project_items(config: GHProjectSyncConfig, *, limit: int) -> list[dict[str, Any]] | None:
    proc = _run_gh(
        [
            "project",
            "item-list",
            str(config.number),
            "--owner",
            config.owner,
            "--limit",
            str(limit),
            "--format",
            "json",
        ]
    )
    if proc.returncode != 0:
        return None
    try:
        payload = json.loads(proc.stdout or "[]")
    except json.JSONDecodeError:
        return None
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    return None


def _extract_field(item: dict[str, Any], key: str) -> str:
    field_values = item.get("fieldValues")
    if not isinstance(field_values, list):
        return ""
    for field in field_values:
        if not isinstance(field, dict):
            continue
        field_name = ""
        nested = field.get("field")
        if isinstance(nested, dict):
            field_name = str(nested.get("name", ""))
        if not field_name:
            field_name = str(field.get("name", ""))
        if field_name != key:
            continue
        # Coerce known payload shapes into a display value.
        if "text" in field:
            return str(field.get("text", ""))
        if "name" in field and field_name != str(field.get("name", "")):
            return str(field.get("name", ""))
        if "number" in field:
            return str(field.get("number", ""))
        if "date" in field:
            return str(field.get("date", ""))
    return ""


def _run_gh(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603
        ["gh", *args],
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )
