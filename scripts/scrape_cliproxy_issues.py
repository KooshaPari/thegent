#!/usr/bin/env python3
"""Scrape GitHub issues from CLIProxyAPI and CLIProxyAPIPlus repos."""

import orjson as json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx


REPOS = [
    ("router-for-me", "CLIProxyAPI"),
    ("router-for-me", "CLIProxyAPIPlus"),
]

OUTPUT_DIR = Path(__file__).parent.parent / "docs" / "docset"
OUTPUT_FILE = OUTPUT_DIR / "cliproxy-github-issues.json"


def fetch_github_issues(owner: str, repo: str, state: str = "all", per_page: int = 100) -> list[dict[str, Any]]:
    """Fetch all issues from a GitHub repository."""
    issues = []
    page = 1

    headers = {
        "Accept": "application/vnd.github.v3+json",
    }
    if token := os.getenv("GITHUB_TOKEN"):
        headers["Authorization"] = f"token {token}"

    client = httpx.Client(timeout=30.0)

    while True:
        url = f"https://api.github.com/repos/{owner}/{repo}/issues"
        params = {
            "state": state,
            "per_page": per_page,
            "page": page,
            "sort": "created",
            "direction": "desc",
        }

        resp = client.get(url, headers=headers, params=params)

        if resp.status_code == 403:
            reset_time = int(resp.headers.get("X-RateLimit-Reset", 0))
            wait_time = max(reset_time - time.time(), 0) + 1
            print(f"Rate limited. Waiting {wait_time:.0f}s...")
            time.sleep(wait_time)
            continue

        if resp.status_code != 200:
            print(f"Error fetching {owner}/{repo}: {resp.status_code}")
            break

        data = resp.json()
        if not data:
            break

        issues.extend(data)
        print(f"Page {page}: {len(data)} issues (total: {len(issues)})")

        page += 1
        time.sleep(1)

    client.close()
    return issues


def categorize_issue(issue: dict) -> str:
    """Categorize an issue based on labels and title."""
    title = issue.get("title", "").lower()
    labels = [l["name"].lower() for l in issue.get("labels", [])]

    for label in labels:
        if "bug" in label or "error" in label or "fail" in label:
            return "bug"
        if "feat" in label or "feature" in label or "request" in label:
            return "feature"
        if "enhancement" in label or "improv" in label:
            return "enhancement"
        if "qol" in label or "ux" in label or "docs" in label:
            return "qol"
        if "perf" in label or "optim" in label:
            return "performance"
        if "security" in label or "auth" in label:
            return "security"

    if any(kw in title for kw in ["bug", "error", "fail", "crash", "broken"]):
        return "bug"
    if any(kw in title for kw in ["support", "add", "enable", "implement"]):
        return "feature"
    if any(kw in title for kw in ["improv", "enhance", "better", "optimize"]):
        return "enhancement"

    return "other"


def process_issues(issues: list[dict], source_repo: str) -> list[dict]:
    """Process and categorize issues."""
    processed = []

    for issue in issues:
        if "pull_request" in issue:
            continue

        processed.append(
            {
                "id": issue["id"],
                "number": issue["number"],
                "title": issue["title"],
                "body": issue.get("body", "")[:500] if issue.get("body") else "",
                "state": issue["state"],
                "html_url": issue["html_url"],
                "source_repo": source_repo,
                "author": issue.get("user", {}).get("login", "unknown"),
                "labels": [l["name"] for l in issue.get("labels", [])],
                "created_at": issue["created_at"],
                "updated_at": issue["updated_at"],
                "comments": issue.get("comments", 0),
                "category": categorize_issue(issue),
                "thegent_status": "pending",
            }
        )

    return processed


def main():
    """Main function to scrape all issues."""
    print("GitHub Issue Scraper for CLIProxyAPI Board")
    print("=" * 50)

    all_issues = []

    for owner, repo in REPOS:
        print(f"\nFetching {owner}/{repo}...")

        for state in ["open", "closed"]:
            print(f"  - {state} issues...")
            issues = fetch_github_issues(owner, repo, state=state)
            processed = process_issues(issues, f"{owner}/{repo}")
            all_issues.extend(processed)
            print(f"    Total from {state}: {len(processed)}")

    all_issues.sort(key=lambda x: x["created_at"], reverse=True)

    for i, issue in enumerate(all_issues, 1):
        issue["board_id"] = i

    output = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_count": len(all_issues),
            "sources": [f"{o}/{r}" for o, r in REPOS],
            "categories": {
                "bug": len([i for i in all_issues if i["category"] == "bug"]),
                "feature": len([i for i in all_issues if i["category"] == "feature"]),
                "enhancement": len([i for i in all_issues if i["category"] == "enhancement"]),
                "qol": len([i for i in all_issues if i["category"] == "qol"]),
                "other": len([i for i in all_issues if i["category"] == "other"]),
            },
        },
        "issues": all_issues,
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nTotal: {len(all_issues)}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
