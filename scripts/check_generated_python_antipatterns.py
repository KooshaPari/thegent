#!/usr/bin/env python3
"""Detect generated-code anti-patterns in Python sources."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Rule:
    rule_id: str
    severity: str
    pattern: re.Pattern[str]
    message: str


RULES: list[Rule] = [
    Rule("GENPY001", "error", re.compile(r"\beval\s*\("), "Use of eval()"),
    Rule("GENPY002", "error", re.compile(r"\bexec\s*\("), "Use of exec()"),
    Rule("GENPY003", "warning", re.compile(r"^\s*except\s*:\s*$"), "Bare except clause"),
    Rule(
        "GENPY004",
        "error",
        re.compile(r"subprocess\.(run|Popen|call|check_output|check_call)\(.*shell\s*=\s*True"),
        "subprocess call with shell=True",
    ),
    Rule(
        "GENPY005",
        "warning",
        re.compile(r"requests\.(get|post|put|patch|delete|request)\("),
        "requests call without explicit timeout",
    ),
    Rule(
        "GENPY006",
        "warning",
        re.compile(r"(?i)TODO:\s*(implement|placeholder|stub|fixme)"),
        "Placeholder TODO marker",
    ),
]


SEVERITY_RANK = {"info": 0, "warning": 1, "error": 2, "critical": 3}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="Files/directories to scan")
    parser.add_argument("--json-out", required=True, help="JSON report output path")
    parser.add_argument("--sarif-out", help="Optional SARIF output path")
    parser.add_argument(
        "--fail-on",
        choices=["info", "warning", "error", "critical"],
        default="error",
        help="Fail if any finding is at/above this severity",
    )
    parser.add_argument("--max-findings", type=int, default=-1, help="Fail if exceeded (> -1)")
    parser.add_argument(
        "--exclude",
        action="append",
        default=[".venv", "node_modules", "__pycache__", ".git", "dist", "build"],
        help="Path segment to exclude (repeatable)",
    )
    return parser.parse_args()


def iter_python_files(paths: list[str], excludes: list[str]) -> list[Path]:
    out: list[Path] = []
    for raw in paths:
        p = Path(raw)
        if not p.exists():
            continue
        if p.is_file() and p.suffix == ".py":
            out.append(p)
            continue
        if p.is_dir():
            for child in p.rglob("*.py"):
                if any(seg in excludes for seg in child.parts):
                    continue
                out.append(child)
    return out


def scan_file(path: Path) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return findings

    for idx, line in enumerate(lines, start=1):
        for rule in RULES:
            if rule.rule_id == "GENPY005":
                if rule.pattern.search(line) and "timeout=" not in line:
                    findings.append(
                        {
                            "rule_id": rule.rule_id,
                            "severity": rule.severity,
                            "message": rule.message,
                            "path": str(path),
                            "line": idx,
                        }
                    )
                continue
            if rule.pattern.search(line):
                findings.append(
                    {
                        "rule_id": rule.rule_id,
                        "severity": rule.severity,
                        "message": rule.message,
                        "path": str(path),
                        "line": idx,
                    }
                )
    return findings


def to_sarif(findings: list[dict[str, Any]]) -> dict[str, Any]:
    rules: dict[str, dict[str, Any]] = {}
    results: list[dict[str, Any]] = []
    rule_lookup = {rule.rule_id: rule for rule in RULES}
    for finding in findings:
        rule_id = str(finding["rule_id"])
        rule = rule_lookup.get(rule_id)
        rules.setdefault(
            rule_id,
            {
                "id": rule_id,
                "name": rule_id,
                "shortDescription": {"text": rule.message if rule else rule_id},
                "help": {"text": "generated Python anti-pattern"},
            },
        )
        level = "error" if finding["severity"] in {"error", "critical"} else "warning"
        results.append(
            {
                "ruleId": rule_id,
                "level": level,
                "message": {"text": str(finding["message"])},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": str(finding["path"])},
                            "region": {"startLine": int(finding["line"])},
                        }
                    }
                ],
            }
        )

    return {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {"driver": {"name": "generated-python-antipatterns", "rules": sorted(rules.values(), key=lambda r: r["id"])}},
                "results": results,
            }
        ],
    }


def main() -> int:
    args = parse_args()
    files = iter_python_files(args.paths, args.exclude)
    findings: list[dict[str, Any]] = []
    for path in files:
        findings.extend(scan_file(path))

    by_severity: dict[str, int] = {"info": 0, "warning": 0, "error": 0, "critical": 0}
    for finding in findings:
        by_severity[str(finding["severity"])] += 1

    report = {
        "schema_version": "generated-python-checker/v1",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "checker": "generated-python-antipatterns",
        "summary": {
            "scanned_files": len(files),
            "total_findings": len(findings),
            "by_severity": by_severity,
        },
        "findings": findings,
    }
    json_out = Path(args.json_out)
    json_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.sarif_out:
        sarif = to_sarif(findings)
        sarif_out = Path(args.sarif_out)
        sarif_out.parent.mkdir(parents=True, exist_ok=True)
        sarif_out.write_text(json.dumps(sarif, indent=2) + "\n", encoding="utf-8")

    threshold = SEVERITY_RANK[args.fail_on]
    has_blocking = any(SEVERITY_RANK[str(f["severity"])] >= threshold for f in findings)
    too_many = args.max_findings >= 0 and len(findings) > args.max_findings
    return 1 if (has_blocking or too_many) else 0


if __name__ == "__main__":
    raise SystemExit(main())
