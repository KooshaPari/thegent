"""Linting accelerator for thegent (oxlint / ESLint / ruff wrapper)."""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path


@dataclass
class LintResult:
    """A single lint diagnostic."""

    file: str
    line: int
    column: int
    severity: str
    rule: str
    message: str
    source: str = "unknown"

    def __str__(self) -> str:
        return f"{self.file}:{self.line}:{self.column} [{self.severity}] {self.rule}: {self.message}"


def _severity_str(code: int) -> str:
    """Convert numeric severity to string."""
    if code >= 2:
        return "error"
    return "warning"


def _parse_json_array(raw: str, source: str) -> list[dict[str, Any]]:
    """Parse JSON output, raising ValueError on invalid or non-array JSON."""
    if not raw.strip():
        return []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{source}: invalid JSON output") from exc
    if not isinstance(data, list):
        raise ValueError(f"Expected JSON array from {source}")
    return data


class LintingAccelerator:
    """Unified linting interface for oxlint, ESLint, and ruff."""

    def is_oxlint_available(self) -> bool:
        return shutil.which("oxlint") is not None

    def is_eslint_available(self) -> bool:
        return shutil.which("eslint") is not None

    def is_ruff_available(self) -> bool:
        return shutil.which("ruff") is not None

    def run_oxlint(self, paths: list[Path], config: Path | None = None) -> list[LintResult]:
        """Run oxlint and return parsed results."""
        if not self.is_oxlint_available():
            raise FileNotFoundError("oxlint not found on PATH")

        cmd = ["oxlint", "--format", "json"]
        if config:
            cmd.extend(["--config", str(config)])
        cmd.extend(str(p) for p in paths)

        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120, check=False)
        items = _parse_json_array(proc.stdout, "oxlint")

        results: list[LintResult] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            if "messages" in item and "filePath" in item:
                for msg in item["messages"]:
                    if not isinstance(msg, dict):
                        continue
                    results.append(
                        LintResult(
                            file=item["filePath"],
                            line=msg.get("line", 0),
                            column=msg.get("column", 0),
                            severity=_severity_str(msg.get("severity", 2)),
                            rule=msg.get("ruleId") or "unknown",
                            message=msg.get("message", ""),
                            source="oxlint",
                        )
                    )
            elif "filename" in item:
                results.append(
                    LintResult(
                        file=item["filename"],
                        line=item.get("line", 0),
                        column=item.get("column", 0),
                        severity=_severity_str(item.get("severity", 2)),
                        rule=item.get("rule") or item.get("ruleId") or "unknown",
                        message=item.get("message", ""),
                        source="oxlint",
                    )
                )
        return results

    def run_eslint(self, paths: list[Path], config: Path | None = None) -> list[LintResult]:
        """Run eslint and return parsed results."""
        if not self.is_eslint_available():
            raise FileNotFoundError("eslint not found on PATH")

        cmd = ["eslint", "--format", "json"]
        if config:
            cmd.extend(["--config", str(config)])
        cmd.extend(str(p) for p in paths)

        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120, check=False)
        items = _parse_json_array(proc.stdout, "eslint")

        results: list[LintResult] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            for msg in item.get("messages", []):
                if not isinstance(msg, dict):
                    continue
                results.append(
                    LintResult(
                        file=item.get("filePath", ""),
                        line=msg.get("line", 0),
                        column=msg.get("column", 0),
                        severity=_severity_str(msg.get("severity", 2)),
                        rule=msg.get("ruleId") or "unknown",
                        message=msg.get("message", ""),
                        source="eslint",
                    )
                )
        return results

    def run_ruff(self, paths: list[Path], config: Path | None = None) -> list[LintResult]:
        """Run ruff and return parsed results."""
        if not self.is_ruff_available():
            raise FileNotFoundError("ruff not found on PATH")

        cmd = ["ruff", "check", "--output-format", "json"]
        if config:
            cmd.extend(["--config", str(config)])
        cmd.extend(str(p) for p in paths)

        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120, check=False)
        items = _parse_json_array(proc.stdout, "ruff")

        results: list[LintResult] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            loc = item.get("location", {})
            has_fix = item.get("fix") is not None
            results.append(
                LintResult(
                    file=item.get("filename", ""),
                    line=loc.get("row", 0),
                    column=loc.get("column", 0),
                    severity="warning" if has_fix else "error",
                    rule=item.get("code") or "unknown",
                    message=item.get("message", ""),
                    source="ruff",
                )
            )
        return results

    def lint(
        self,
        paths: list[Path],
        fast: bool = True,
        oxlint_config: Path | None = None,
        eslint_config: Path | None = None,
        include_status: bool = False,
    ) -> list[LintResult] | dict[str, Any]:
        """Unified lint entry point."""
        if fast:
            if self.is_oxlint_available():
                results = self.run_oxlint(paths, config=oxlint_config)
                if include_status:
                    return {
                        "status": "ok",
                        "engine": "oxlint",
                        "results": results,
                    }
                return results
            if self.is_eslint_available():
                results = self.run_eslint(paths, config=eslint_config)
                if include_status:
                    return {
                        "status": "ok",
                        "engine": "eslint",
                        "results": results,
                    }
                return results
            if include_status:
                return {
                    "status": "unavailable",
                    "engine": None,
                    "results": [],
                    "reason": "no_fast_linter_available",
                }
            return []
        if self.is_eslint_available():
            results = self.run_eslint(paths, config=eslint_config)
            if include_status:
                return {
                    "status": "ok",
                    "engine": "eslint",
                    "results": results,
                }
            return results
        if include_status:
            return {
                "status": "unavailable",
                "engine": None,
                "results": [],
                "reason": "eslint_not_available",
            }
        return []
