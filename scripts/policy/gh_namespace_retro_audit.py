#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from typing import Any


@dataclass
class Finding:
    kind: str
    number: int
    repo: str
    title: str
    url: str
    author: str
    updated_at: str


def run_json(cmd: list[str]) -> Any:
    proc = subprocess.run(cmd, text=True, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(f"command failed: {' '.join(cmd)}\n{proc.stderr.strip()}")
    out = proc.stdout.strip()
    if not out:
        return []
    return json.loads(out)


def get_default_logins() -> list[str]:
    status = subprocess.run(["gh", "auth", "status"], text=True, capture_output=True)
    if status.returncode != 0:
        return []
    logins: list[str] = []
    for line in status.stdout.splitlines():
        line = line.strip()
        if "Logged in to github.com account" in line:
            parts = line.split("account", 1)
            if len(parts) == 2:
                login = parts[1].split("(", 1)[0].strip()
                if login and login not in logins:
                    logins.append(login)
    return logins


def collect(kind: str, author: str, allowed_owner: str, limit: int) -> list[Finding]:
    cmd = [
        "gh",
        "search",
        "prs" if kind == "pr" else "issues",
        "--author",
        author,
        "--state",
        "open",
        "--limit",
        str(limit),
        "--json",
        "number,title,url,updatedAt,repository,author",
    ]
    items = run_json(cmd)

    findings: list[Finding] = []
    for item in items:
        repo = item["repository"]["nameWithOwner"]
        owner = repo.split("/", 1)[0]
        if owner == allowed_owner:
            continue
        findings.append(
            Finding(
                kind=kind,
                number=item["number"],
                repo=repo,
                title=item["title"],
                url=item["url"],
                author=item["author"]["login"],
                updated_at=item["updatedAt"],
            )
        )
    return findings


def print_table(findings: list[Finding]) -> None:
    if not findings:
        print("No out-of-namespace open PRs/issues found.")
        return

    print("Out-of-namespace open PRs/issues:")
    for f in findings:
        print(f"- [{f.kind}] {f.repo}#{f.number} | {f.title}")
        print(f"  author={f.author} updated={f.updated_at}")
        print(f"  url={f.url}")
        target_repo = f"KooshaPari/{f.repo.split('/', 1)[1]}"
        print(f"  recreate-target={target_repo}")
        print("  closure-note=Close stale lane; reopen under KooshaPari namespace.")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit open PRs/issues authored by selected users outside allowed owner namespace."
    )
    parser.add_argument("--allowed-owner", default="KooshaPari")
    parser.add_argument(
        "--authors",
        default="",
        help="Comma-separated GitHub logins to audit (defaults to all logged-in accounts from gh auth status)",
    )
    parser.add_argument("--limit", type=int, default=200)
    args = parser.parse_args()

    authors = [x.strip() for x in args.authors.split(",") if x.strip()]
    if not authors:
        authors = get_default_logins()

    if not authors:
        print("No authors to audit. Log in with gh or pass --authors.", file=sys.stderr)
        return 2

    all_findings: list[Finding] = []
    for author in authors:
        for kind in ("pr", "issue"):
            try:
                all_findings.extend(collect(kind, author, args.allowed_owner, args.limit))
            except RuntimeError as exc:
                print(f"warning: {exc}", file=sys.stderr)

    # Stable output for automation and replay.
    all_findings.sort(key=lambda x: (x.repo, x.kind, x.number))
    print_table(all_findings)
    return 1 if all_findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
