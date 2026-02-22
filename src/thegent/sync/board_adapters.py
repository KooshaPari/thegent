"""Board sync adapter implementations for `thegent sync board`."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from thegent.resilience import transient_retry


class BoardSyncAdapter(Protocol):
    """Protocol for board sync adapters."""

    source: str

    def sync(self, board_id: str, work_stream_items: list[dict[str, str]]) -> dict[str, Any]:
        """Sync local work-stream items to a remote board."""

    def fetch_remote_status(
        self,
        board_id: str,
        work_stream_items: list[dict[str, str]],
    ) -> dict[str, str]:
        """Fetch remote status mapping for local work-stream item ids."""


@dataclass(slots=True)
class GitHubBoardAdapter:
    """GitHub Projects adapter backed by existing WL-157 integration."""

    source: str = "github"

    def sync(self, board_id: str, work_stream_items: list[dict[str, str]]) -> dict[str, Any]:
        from thegent.integrations.gh_project_sync import GHProjectConfig, sync_to_github

        owner, number = self._parse_board_locator(board_id)
        config = GHProjectConfig(
            enabled=True,
            owner=owner,
            number=number,
            direction="write_only",
            standalone_mode=False,
        )
        payload = [
            {
                "item_id": item["id"],
                "id": item["id"],
                "title": f"[{item['id']}] {item['title']}",
                "status": item["status"],
            }
            for item in work_stream_items
        ]

        upstream = sync_to_github(config, payload)
        errors = [str(err) for err in upstream.get("errors", [])]
        successful = max(len(work_stream_items) - len(errors), 0)

        return {
            "synced": successful,
            "failed": len(errors),
            "updated_items": work_stream_items[:successful],
            "errors": errors,
        }

    @transient_retry(max_attempts=3, min_wait=0.0, max_wait=0.0)
    def fetch_remote_status(
        self,
        board_id: str,
        work_stream_items: list[dict[str, str]],
    ) -> dict[str, str]:
        from thegent.integrations.gh_project_sync import GHProjectConfig, sync_from_github

        owner, number = self._parse_board_locator(board_id)
        config = GHProjectConfig(
            enabled=True,
            owner=owner,
            number=number,
            direction="read_only",
            standalone_mode=False,
        )

        payload = sync_from_github(config)
        requested_ids = {item.get("id", "").upper() for item in work_stream_items}
        raw_items = payload.get("items", [])

        statuses: dict[str, str] = {}
        for entry in raw_items:
            item_id = str(entry.get("item_id") or "").upper()
            if not item_id or (requested_ids and item_id not in requested_ids):
                continue
            statuses[item_id] = str(entry.get("status") or "BACKLOG")
        return statuses

    def _parse_board_locator(self, board_id: str) -> tuple[str, int]:
        raw = (board_id or "").strip()
        if not raw:
            raise ValueError("GitHub board ID is required.")

        if ":" in raw:
            owner, number = raw.split(":", 1)
            if owner and number.isdigit():
                return owner, int(number)

        if "/" in raw:
            owner, number = raw.split("/", 1)
            if owner and number.isdigit():
                return owner, int(number)

        if raw.isdigit():
            owner = os.getenv("THGENT_GITHUB_OWNER") or self._owner_from_repository_env()
            if not owner:
                raise ValueError(
                    "GitHub board ID must be 'owner:number' or set THGENT_GITHUB_OWNER/GITHUB_REPOSITORY for numeric IDs."
                )
            return owner, int(raw)

        raise ValueError("Invalid GitHub board ID format. Use owner:number, owner/number, or numeric project number.")

    @staticmethod
    def _owner_from_repository_env() -> str | None:
        repo = os.getenv("GITHUB_REPOSITORY", "")
        if "/" not in repo:
            return None
        return repo.split("/", 1)[0] or None


@dataclass(slots=True)
class LinearBoardAdapter:
    """Linear adapter using GraphQL API (issue upsert by WL-tagged title)."""

    source: str = "linear"
    endpoint: str = "https://api.linear.app/graphql"

    def sync(self, board_id: str, work_stream_items: list[dict[str, str]]) -> dict[str, Any]:
        token = os.getenv("THGENT_LINEAR_API_KEY") or os.getenv("LINEAR_API_KEY")
        if not token:
            raise RuntimeError("Linear sync requires THGENT_LINEAR_API_KEY or LINEAR_API_KEY.")

        team_key = (board_id or "").strip() or os.getenv("THGENT_LINEAR_TEAM_KEY", "").strip()
        if not team_key:
            raise RuntimeError("Linear sync requires board_id as team key or THGENT_LINEAR_TEAM_KEY.")

        team_id = self._resolve_team_id(token, team_key)

        synced = 0
        failed = 0
        updated_items: list[dict[str, str]] = []
        errors: list[str] = []
        for item in work_stream_items:
            try:
                title = f"[{item['id']}] {item['title']}"
                description = f"Synced from WORK_STREAM.md\n\nWL: {item['id']}\nStatus: {item['status']}\n"
                issue_id = self._find_issue_id(token, team_key, title)
                if issue_id:
                    self._update_issue(token, issue_id, title, description)
                else:
                    self._create_issue(token, team_id, title, description)
                synced += 1
                updated_items.append(item)
            except Exception as exc:
                failed += 1
                errors.append(f"{item.get('id', '<unknown>')}: {exc}")

        return {
            "synced": synced,
            "failed": failed,
            "updated_items": updated_items,
            "errors": errors,
        }

    @transient_retry(max_attempts=3, min_wait=0.0, max_wait=0.0)
    def fetch_remote_status(
        self,
        board_id: str,
        work_stream_items: list[dict[str, str]],
    ) -> dict[str, str]:
        from thegent.integrations.linear_graphql import LinearGraphQLConfig, sync_from_linear

        if not board_id:
            raise RuntimeError("Linear board ID is required for remote status reconciliation.")

        token = os.getenv("THGENT_LINEAR_API_KEY") or os.getenv("LINEAR_API_KEY")
        if not token:
            raise RuntimeError("Linear sync requires THGENT_LINEAR_API_KEY or LINEAR_API_KEY.")

        team_key = board_id.strip() or os.getenv("THGENT_LINEAR_TEAM_KEY", "").strip()
        if not team_key:
            raise RuntimeError("Linear sync requires board_id as team key or THGENT_LINEAR_TEAM_KEY.")

        payload = sync_from_linear(LinearGraphQLConfig(api_key=token, team_key=team_key))
        requested_ids = {item.get("id", "").upper() for item in work_stream_items}
        raw_items = payload.get("items", [])
        if not isinstance(raw_items, list):
            return {}

        statuses: dict[str, str] = {}
        for entry in raw_items:
            item_id = str(entry.get("item_id") or "").upper()
            if not item_id or (requested_ids and item_id not in requested_ids):
                continue
            status = entry.get("status")
            if status is not None:
                statuses[item_id] = str(status)
        return statuses

    def _resolve_team_id(self, token: str, team_key: str) -> str:
        query = """
        query TeamByKey($teamKey: String!) {
          teams(filter: { key: { eq: $teamKey } }, first: 1) {
            nodes {
              id
            }
          }
        }
        """
        data = self._graphql(token, query, {"teamKey": team_key})
        nodes = data.get("teams", {}).get("nodes", [])
        if not nodes:
            raise RuntimeError(f"Linear team not found for key '{team_key}'.")
        team_id = nodes[0].get("id")
        if not team_id:
            raise RuntimeError("Linear team lookup returned an item without id.")
        return str(team_id)

    def _find_issue_id(self, token: str, team_key: str, title: str) -> str | None:
        query = """
        query FindIssue($teamKey: String!, $title: String!) {
          issues(
            first: 1
            filter: {
              team: { key: { eq: $teamKey } }
              title: { eq: $title }
            }
          ) {
            nodes {
              id
            }
          }
        }
        """
        data = self._graphql(token, query, {"teamKey": team_key, "title": title})
        nodes = data.get("issues", {}).get("nodes", [])
        if not nodes:
            return None
        issue_id = nodes[0].get("id")
        return str(issue_id) if issue_id else None

    def _create_issue(self, token: str, team_id: str, title: str, description: str) -> None:
        mutation = """
        mutation CreateIssue($teamId: String!, $title: String!, $description: String!) {
          issueCreate(
            input: {
              teamId: $teamId
              title: $title
              description: $description
            }
          ) {
            success
          }
        }
        """
        data = self._graphql(token, mutation, {"teamId": team_id, "title": title, "description": description})
        if not data.get("issueCreate", {}).get("success", False):
            raise RuntimeError("Linear issueCreate returned success=false.")

    def _update_issue(self, token: str, issue_id: str, title: str, description: str) -> None:
        mutation = """
        mutation UpdateIssue($issueId: String!, $title: String!, $description: String!) {
          issueUpdate(
            id: $issueId
            input: {
              title: $title
              description: $description
            }
          ) {
            success
          }
        }
        """
        data = self._graphql(
            token,
            mutation,
            {"issueId": issue_id, "title": title, "description": description},
        )
        if not data.get("issueUpdate", {}).get("success", False):
            raise RuntimeError("Linear issueUpdate returned success=false.")

    def _graphql(self, token: str, query: str, variables: dict[str, Any]) -> dict[str, Any]:
        payload = json.dumps({"query": query, "variables": variables}).encode("utf-8")
        request = Request(
            self.endpoint,
            data=payload,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": token,
            },
        )
        try:
            with urlopen(request, timeout=20) as response:  # noqa: S310
                body = response.read().decode("utf-8")
        except (HTTPError, URLError) as exc:
            raise RuntimeError(f"Linear GraphQL request failed: {exc}") from exc

        parsed = json.loads(body)
        if parsed.get("errors"):
            first = parsed["errors"][0]
            if isinstance(first, dict) and "message" in first:
                raise RuntimeError(str(first["message"]))
            raise RuntimeError(f"Linear GraphQL error: {first}")

        data = parsed.get("data")
        if not isinstance(data, dict):
            raise RuntimeError("Linear GraphQL response missing data object.")
        return data


def resolve_board_adapter(source: str) -> BoardSyncAdapter:
    """Resolve adapter implementation for board source."""
    normalized = (source or "").strip().lower()
    if normalized == "github":
        return GitHubBoardAdapter()
    if normalized == "linear":
        return LinearBoardAdapter()
    raise ValueError(f"Unsupported board source '{source}'. Expected one of: github, linear.")
