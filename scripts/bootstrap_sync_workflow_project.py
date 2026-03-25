#!/usr/bin/env python3
from __future__ import annotations

import argparse
import orjson as json
import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class IssueSpec:
    title: str
    body: str


ISSUES: tuple[IssueSpec, ...] = (
    IssueSpec(
        title="Sync: Implement real GitHub Project write path in autosync",
        body="Replace `_sync_to_github` stub in `src/thegent/integrations/workstream_autosync.py` with real GitHub Project item create/update operations tied to WORK_STREAM status.",
    ),
    IssueSpec(
        title="Sync: Implement GitHub -> WORK_STREAM status reflection",
        body="Replace `_sync_from_github` stub with real Project readback and markdown status updates in `docs/reference/WORK_STREAM.md`.",
    ),
    IssueSpec(
        title="Sync: Implement real Linear write path in autosync",
        body="Replace `_sync_to_linear` stub in `src/thegent/integrations/workstream_autosync.py` with Linear issue create/update operations mapped from WORK_STREAM items.",
    ),
    IssueSpec(
        title="Sync: Implement Linear -> WORK_STREAM status reflection",
        body="Replace `_sync_from_linear` stub with real Linear readback and status reconciliation into `docs/reference/WORK_STREAM.md`.",
    ),
    IssueSpec(
        title="Sync: Replace board sync stub with GitHub/Linear API adapters",
        body="Replace `_perform_board_sync` placeholder in `src/thegent/commands/sync.py` with provider-backed board sync logic and deterministic dry-run output.",
    ),
    IssueSpec(
        title="Sync: Add idempotent dedupe keyed by WL-ID in plan incorporate",
        body="Strengthen `thegent sync work-stream` ingestion in `src/thegent/commands/sync.py` to dedupe by WL-ID and keep dependency metadata stable.",
    ),
    IssueSpec(
        title="Sync: Enforce dependency-aware claim gating in agent workflow",
        body="Enhance claim/do-next orchestration (`src/thegent/planning/work_stream.py`, `src/thegent/cli/services/work_stream_orchestration.py`) so blocked items cannot be claimed.",
    ),
    IssueSpec(
        title="Sync: Persist autopilot status and health contract",
        body="Finalize status contract and tests for `docs/reference/autosync_status.json` and make `thegent sync autopilot-status` consume the configured status path.",
    ),
    IssueSpec(
        title="Sync: Add MCP tool coverage for workstream claim/complete loop",
        body="Expand MCP workflow integration around workstream tools so agent sessions can claim/complete/sync reliably from MCP without local CLI fallbacks.",
    ),
    IssueSpec(
        title="Sync: Add end-to-end tests for sync board and autopilot workflows",
        body="Add focused e2e + integration tests covering `thegent sync board`, `thegent sync autopilot`, and `thegent sync autopilot-status` against mocked remote adapters.",
    ),
)


def _run(cmd: list[str], *, dry_run: bool) -> str:
    rendered = " ".join(cmd)
    print(f"$ {rendered}")
    if dry_run:
        return ""
    try:
        result = subprocess.run(cmd, text=True, capture_output=True, check=True)
    except subprocess.CalledProcessError as exc:
        if exc.stdout:
            print(exc.stdout.strip())
        if exc.stderr:
            print(exc.stderr.strip())
        raise
    output = (result.stdout or "").strip()
    if output:
        print(output)
    if result.stderr:
        print(result.stderr.strip())
    return output


def _run_json(cmd: list[str], *, dry_run: bool) -> list[dict[str, object]]:
    output = _run(cmd, dry_run=dry_run)
    if dry_run or not output:
        return []
    loaded = json.loads(output)
    if isinstance(loaded, list):
        return loaded
    if isinstance(loaded, dict):
        for key in ("projects", "items", "data"):
            value = loaded.get(key)
            if isinstance(value, list):
                return value
    return []


def _ensure_labels(repo: str, dry_run: bool) -> None:
    labels = {"sync-system": "0052CC", "agent-workflow": "5319E7"}
    existing = {
        row.get("name")
        for row in _run_json(
            ["gh", "label", "list", "--repo", repo, "--limit", "200", "--json", "name"], dry_run=dry_run
        )
    }
    for label, color in labels.items():
        if label in existing:
            continue
        _run(
            [
                "gh",
                "label",
                "create",
                label,
                "--repo",
                repo,
                "--color",
                color,
                "--description",
                "Sync workflow execution track",
            ],
            dry_run=dry_run,
        )


def _ensure_project(owner: str, title: str, dry_run: bool) -> int:
    projects = _run_json(
        ["gh", "project", "list", "--owner", owner, "--limit", "200", "--format", "json"], dry_run=dry_run
    )
    for project in projects:
        if project.get("title") == title:
            number = int(project["number"])
            print(f"Using existing project #{number}: {title}")
            return number
    output = ""
    if dry_run:
        _run(["gh", "project", "create", "--owner", owner, "--title", title], dry_run=True)
        return 0
    try:
        output = _run(
            ["gh", "project", "create", "--owner", owner, "--title", title, "--format", "json"], dry_run=False
        )
        data = json.loads(output)
        number = int(data["number"])
        print(f"Created project #{number}: {title}")
        return number
    except subprocess.CalledProcessError, json.JSONDecodeError, KeyError, ValueError:
        pass
    owner_data = json.loads(
        _run(
            [
                "gh",
                "api",
                "graphql",
                "-f",
                "query=query($login:String!){user(login:$login){id}}",
                "-F",
                f"login={owner}",
            ],
            dry_run=False,
        )
    )
    owner_id = owner_data["data"]["user"]["id"]
    if dry_run:
        return 0
    created = json.loads(
        _run(
            [
                "gh",
                "api",
                "graphql",
                "-f",
                "query=mutation($ownerId:ID!,$title:String!){createProjectV2(input:{ownerId:$ownerId,title:$title}){projectV2{number title}}}",
                "-F",
                f"ownerId={owner_id}",
                "-F",
                f"title={title}",
            ],
            dry_run=False,
        )
    )
    number = int(created["data"]["createProjectV2"]["projectV2"]["number"])
    print(f"Created project #{number}: {title}")
    return number


def _existing_issues(repo: str, dry_run: bool) -> dict[str, str]:
    issues = _run_json(
        ["gh", "issue", "list", "--repo", repo, "--state", "all", "--limit", "200", "--json", "title,url"],
        dry_run=dry_run,
    )
    return {str(row["title"]): str(row["url"]) for row in issues if row.get("title") and row.get("url")}


def _ensure_issues(repo: str, dry_run: bool) -> list[str]:
    existing = _existing_issues(repo, dry_run=dry_run)
    urls: list[str] = []
    for spec in ISSUES:
        if spec.title in existing:
            urls.append(existing[spec.title])
            continue
        output = _run(
            [
                "gh",
                "issue",
                "create",
                "--repo",
                repo,
                "--title",
                spec.title,
                "--body",
                spec.body,
                "--label",
                "sync-system,agent-workflow",
            ],
            dry_run=dry_run,
        )
        if not dry_run:
            urls.append(output.splitlines()[-1].strip())
    return urls


def _ensure_project_items(owner: str, project_number: int, issue_urls: list[str], dry_run: bool) -> None:
    if project_number <= 0:
        return
    rows = _run_json(
        ["gh", "project", "item-list", str(project_number), "--owner", owner, "--limit", "500", "--format", "json"],
        dry_run=dry_run,
    )
    existing_urls = {
        str(content["url"])
        for row in rows
        for content in [row.get("content")]
        if isinstance(content, dict) and content.get("url")
    }
    for url in issue_urls:
        if url in existing_urls:
            continue
        _run(["gh", "project", "item-add", str(project_number), "--owner", owner, "--url", url], dry_run=dry_run)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create/seed sync-system GH issues and project board.")
    parser.add_argument("--owner", required=True, help="GitHub owner or org (e.g. KooshaPari)")
    parser.add_argument("--repo", required=True, help="Repository slug (e.g. KooshaPari/thegent)")
    parser.add_argument(
        "--project-title", default="thegent Sync System Deep Integration", help="Project title to create/reuse"
    )
    parser.add_argument("--dry-run", action="store_true", help="Print commands without writing")
    args = parser.parse_args()

    summary = bootstrap_sync_workflow_project(
        owner=args.owner,
        repo=args.repo,
        project_title=args.project_title,
        dry_run=args.dry_run,
    )
    print(f"Prepared {summary['prepared_count']} sync workflow issues")
    if summary["project_number"]:
        print(f"Project number: {summary['project_number']}")
    return 0


def bootstrap_sync_workflow_project(
    *,
    owner: str,
    repo: str,
    project_title: str,
    dry_run: bool,
) -> dict[str, object]:
    """Bootstrap/sync the sync workflow GH project idempotently.

    Returns a compact summary of the operations performed.
    """
    _ensure_labels(repo=repo, dry_run=dry_run)
    project_number = _ensure_project(owner=owner, title=project_title, dry_run=dry_run)
    issue_urls = _ensure_issues(repo=repo, dry_run=dry_run)
    _ensure_project_items(owner=owner, project_number=project_number, issue_urls=issue_urls, dry_run=dry_run)
    return {
        "prepared_count": len(issue_urls),
        "project_number": project_number,
        "issue_urls": issue_urls,
    }


if __name__ == "__main__":
    raise SystemExit(main())
