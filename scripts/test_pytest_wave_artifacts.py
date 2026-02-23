#!/usr/bin/env python3
"""Pytest wave artifacts helpers.

Commands:
- collect: run `pytest --collect-only` and emit timing/selection artifacts.
- trace-scan: scan for marker and requirement coverage hints.
- heavy-untagged: identify likely untagged heavy tests.
- requirements-map: emit requirement-to-test and test-to-requirement links.
- requirements-gate: enforce PR change test coverage of requirement markers.
- pr-targets: compute PR-targeted tests from changed files.
- run-pr-lane: execute PR-targeted or fallback PR lane profile.
    - requirements-map-diagram: emit one-page requirement FR->test mermaid map.
    - lane-promotion-criteria: emit promotion policy contract for a lane.
    - lane-promotion: evaluate lane stability against promotion policy and run-history evidence.
    - traceability-cleanup: identify stale deprecated markers and traceability debt.
"""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import tomllib
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from datetime import timedelta
from pathlib import Path
from typing import Iterable, Sequence

from pytest_wave_health_helpers import _derive_pr_targets
from pytest_wave_health_helpers import _discover_changed_files
from pytest_wave_health_helpers import run_health

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_DIR = ROOT / "tests"
DEFAULT_COLLECT_PATH = (str(DEFAULT_INPUT_DIR),)

HEAVY_MARKERS = {"slow", "integration", "e2e", "load", "deep", "chaos", "a11y"}
TRACE_EVIDENCE_COMMENT_CONFIDENCE = 0.95
TRACE_EVIDENCE_DOCSTRING_CONFIDENCE = 0.8
TRACE_EVIDENCE_DECORATOR_CONTEXT_CONFIDENCE = 0.85
TRACE_EVIDENCE_FALLBACK_CONFIDENCE = 0.65
REQUIREMENT_ID_RE = re.compile(r"[A-Z]{2,}(?:-[A-Z0-9]+)*(?:-[0-9]+|-[A-Z0-9]+)")
EXEMPT_COMMENT_RE = re.compile(r"^\s*#\s*requirement-gate-exempt(?:\s*:\s*(?P<reason>.+))?\s*$")
TRACE_COMMENT_RE = re.compile(r"@?trace\s*[:=]?\s*(?P<refs>.+)", re.IGNORECASE)
FR_TRACKER_ID_RE = re.compile(r"\|\s*(FR-[A-Z0-9-]+)\s*\|")

REQUIREMENTS_MAP_SCHEMA_VERSION = "requirements-map/v1"
REQUIREMENTS_MAP_DIAGRAM_SCHEMA_VERSION = "requirements-map-diagram/v1"
REQUIREMENTS_DEBT_SCHEMA_VERSION = "requirements-debt/v1"
PROMOTION_CRITERIA_SCHEMA_VERSION = "lane-promotion-criteria/v1"
LANE_PROMOTION_SUMMARY_SCHEMA_VERSION = "lane-promotion/v1"
RUN_SUMMARY_SCHEMA_VERSION = "pytest-run/v1"
TRACE_CLEANUP_SCHEMA_VERSION = "traceability-cleanup/v1"
TRACE_CLEANUP_ISSUE_SCHEMA_VERSION = "traceability-cleanup-issue/v1"
TRACE_SCAN_SCHEMA_VERSION = "traceability-links/v1"
TRACE_CLEANUP_BREACH_BUDGET = 0

REQUIREMENTS_MAP_DIAGRAM_MAX_REQUIREMENTS = 100
REQUIREMENTS_MAP_DIAGRAM_MAX_TESTS_PER_REQUIREMENT = 30

KNOWN_PYTEST_MARKERS = {
    "unit",
    "integration",
    "e2e",
    "slow",
    "asyncio",
    "load",
    "chaos",
    "a11y",
    "requirement",
    "fast",
    "deep",
    "skip",
    "skipif",
    "xfail",
    "parametrize",
    "usesfixtures",
    "usefixtures",
    "filterwarnings",
}

DEPRECATED_MARKER_HINTS = {"legacy", "wip", "todo", "legacy_marker", "flake"}

LANE_MARKER_MAP = {
    "fast": "fast_lane_marker",
    "ci-fast": "fast_lane_marker",
    "pr": "pr_lane_marker",
    "ci-pr": "pr_lane_marker",
    "nightly": "nightly_lane_marker",
    "ci-nightly": "nightly_lane_marker",
    "flake": "flake_lane_marker",
    "ci-flake": "flake_lane_marker",
}

PARSER_PARITY_TARGET_NAMES = {
    "test_wl131_parser_parity.py",
    "test_wl131_rust_python_parity.py",
}

PARSER_TOUCHING_PATH_PREFIXES = (
    "crates/thegent-parser",
    "src/thegent/contracts/parser",
    "src/thegent/output_parser",
    "src/thegent/execution_jsonl_parsers",
    "src/thegent/routing",
)

# Quarterly cleanup cadence and debt windows are intentionally explicit for deterministic governance.
TRACEABILITY_STALE_WINDOW_DAYS = 90


def _iso_to_datetime(value: str | None) -> datetime:
    if not value:
        return datetime.fromtimestamp(0, tz=timezone.utc)
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return datetime.fromtimestamp(0, tz=timezone.utc)


def _mermaid_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", value)[:90]


@dataclass(frozen=True)
class LanePromotionConfig:
    output: Path
    lane: str
    requirements_map_artifact: Path | None
    requirements_gate_artifact: Path | None
    health_artifact: Path | None
    run_artifacts: list[Path]
    min_runs: int
    min_coverage_ratio: float
    max_flake_ratio: float
    acceptable_fail_budget: int


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _command_hash(command: list[str]) -> str:
    return hashlib.sha1(" ".join(command).encode("utf-8")).hexdigest()


def _load_pytest_lanes(pyproject_path: Path) -> dict[str, str]:
    if not pyproject_path.exists():
        return {}

    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    return data.get("tool", {}).get("thegent", {}).get("pytest_lanes", {})


def _build_marker_expression(
    marker_expr: str | None,
    lane: str | None,
    marker_fallback: str | None,
) -> str | None:
    if marker_expr:
        return marker_expr

    if not lane:
        return marker_fallback

    marker_key = LANE_MARKER_MAP.get(lane)
    if not marker_key:
        return marker_fallback

    configured = _load_pytest_lanes(ROOT / "pyproject.toml").get(marker_key)
    if configured:
        return configured

    return marker_fallback


def _parse_collect_metrics(output: str, stderr: str) -> tuple[int | None, int | None]:
    text = "\n".join([output, stderr])
    collected = None
    errors = None

    collect_match = re.search(r"\b(\d+)/\d+\s+tests?\s+collected\b", text)
    if not collect_match:
        collect_match = re.search(r"\b(\d+)\s+tests?\s+collected\b", text)
    if not collect_match:
        collect_match = re.search(r"collected\s+(\d+)\s+items?", text)
    if not collect_match and "no tests collected" in text:
        collected = 0

    if collect_match:
        collected = int(collect_match.group(1))

    errors_match = re.search(r"(\d+)\s+errors?", text)
    if errors_match:
        errors = int(errors_match.group(1))

    return collected, errors


def _parse_run_metrics(output: str, returncode: int) -> dict[str, int]:
    text = "\n".join([output, ""])
    failures = 0
    passed = 0
    total = 0

    match = re.search(r"(\d+)\s+failed", text)
    if match:
        failures = int(match.group(1))

    match = re.search(r"(\d+)\s+passed", text)
    if match:
        passed = int(match.group(1))

    match = re.search(r"collected\s+(\d+)\s+items?", text)
    if match:
        total = int(match.group(1))

    if total == 0 and (passed or failures):
        total = passed + failures

    return {
        "returncode": returncode,
        "failed": failures,
        "passed": passed,
        "collected": total,
    }


def _parse_collect_items(output: str) -> list[str]:
    items: list[str] = []
    for line in output.splitlines():
        node = line.strip()
        if not node:
            continue
        if node.startswith("="):
            continue
        if node.startswith("collected "):
            continue
        if node.startswith("ERROR"):
            continue
        if "::" not in node:
            continue
        items.append(node)
    return list(dict.fromkeys(items))


def _extract_string_values(node: ast.AST) -> list[str]:
    values: list[str] = []

    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        values.append(node.value)
        return values

    if isinstance(node, ast.List | ast.Tuple | ast.Set):
        for item in node.elts:
            values.extend(_extract_string_values(item))

    return values


def _attribute_name(expr: ast.AST) -> str | None:
    if isinstance(expr, ast.Attribute) and isinstance(expr.value, ast.Name):
        if expr.value.id == "pytest":
            return expr.attr
        if expr.value.id == "mark":
            return expr.attr

    if (
        isinstance(expr, ast.Attribute)
        and isinstance(expr.value, ast.Attribute)
        and isinstance(expr.value.value, ast.Name)
        and expr.value.value.id == "pytest"
        and expr.value.attr == "mark"
    ):
        return expr.attr

    if (
        isinstance(expr, ast.Attribute)
        and isinstance(expr.value, ast.Attribute)
        and isinstance(expr.value.value, ast.Attribute)
        and isinstance(expr.value.value.value, ast.Name)
        and expr.value.value.value.id == "pytest"
        and expr.value.value.attr == "mark"
    ):
        return expr.attr

    return None


def _iter_markers_and_requirements(decorators: Iterable[ast.AST]) -> tuple[list[str], list[str]]:
    markers: list[str] = []
    requirements: list[str] = []

    for decorator in decorators:
        name: str | None = None
        args: Sequence[ast.AST] = []

        if isinstance(decorator, ast.Call):
            name = _attribute_name(decorator.func)
            args = decorator.args
            args = (*args, *(kw.value for kw in decorator.keywords if kw.value is not None))
        elif isinstance(decorator, ast.Attribute):
            name = _attribute_name(decorator)

        if not name:
            continue

        markers.append(name)

        if name != "requirement":
            continue

        for value in args:
            requirements.extend(_extract_string_values(value))

    return sorted(set(markers)), sorted(set(requirements))


def _find_exemption_comment(lines: list[str], line_number: int) -> str | None:
    for offset in range(1, 6):
        index = line_number - offset - 1
        if index < 0:
            break
        match = EXEMPT_COMMENT_RE.search(lines[index])
        if match:
            return (match.group("reason") or "legacy_exemption").strip()

    return None


def _is_comment_line(line: str) -> bool:
    return line.lstrip().startswith("#")


def _is_likely_docstring_line(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith(("'''", '"""')) or stripped.endswith(("'''", '"""'))


def _parse_trace_references(text: str, confidence: float, refs: dict[str, float]) -> None:
    for raw in TRACE_COMMENT_RE.finditer(text):
        value = raw.group("refs")
        for raw_ref in value.split(","):
            value_ref = raw_ref.strip()
            if not value_ref:
                continue
            normalized = _normalize_requirement_id(value_ref)
            if not normalized:
                continue
            refs[normalized] = max(confidence, refs.get(normalized, 0.0))


def _find_trace_references(
    lines: list[str],
    line_number: int,
    end_line: int | None = None,
) -> list[tuple[str, float]]:
    refs: dict[str, float] = {}
    if not lines:
        return []

    start = max(0, line_number - 1 - 12)
    for index in range(start, line_number - 1):
        if index >= len(lines):
            break
        if _is_comment_line(lines[index]):
            _parse_trace_references(
                lines[index],
                TRACE_EVIDENCE_COMMENT_CONFIDENCE,
                refs,
            )
        else:
            _parse_trace_references(
                lines[index],
                TRACE_EVIDENCE_DECORATOR_CONTEXT_CONFIDENCE,
                refs,
            )

    if end_line is None:
        end_line = line_number
    node_end = min(max(end_line, line_number), len(lines))
    body_end = min(node_end + 10, len(lines))
    for index in range(line_number, body_end):
        if _is_comment_line(lines[index]):
            _parse_trace_references(
                lines[index],
                TRACE_EVIDENCE_COMMENT_CONFIDENCE,
                refs,
            )
        elif _is_likely_docstring_line(lines[index]):
            _parse_trace_references(
                lines[index],
                TRACE_EVIDENCE_DOCSTRING_CONFIDENCE,
                refs,
            )

    return [(key, value) for key, value in sorted(refs.items(), key=lambda item: item[0])]


def _source_lines(node: ast.AST) -> int:
    end_line = getattr(node, "end_lineno", None)
    start_line = getattr(node, "lineno", 1)
    if end_line is None:
        return 0
    return max(0, end_line - start_line)


def _node_id(file_path: Path, stack: tuple[str, ...]) -> str:
    return f"{file_path}::{'::'.join(stack)}"


@dataclass(frozen=True)
class TestRecord:
    file: str
    kind: str
    nodeid: str
    line: int
    markers: list[str]
    requirements: list[str]
    trace_references: list[tuple[str, float]]
    exemption_reason: str | None
    source_loc: int


@dataclass(frozen=True)
class RequirementGateConfig:
    changed_files: list[str] | None
    input_dir: Path
    output: Path
    strict: bool
    changed_file_list: Path | None = None
    exceptions_path: Path | None = None
    summary: Path | None = None


@dataclass(frozen=True)
class PrTargetConfig:
    changed_files: list[str]
    output: Path
    changed_file_list: Path | None = None
    include_untestable: bool = False


@dataclass(frozen=True)
class RunPrLaneConfig:
    changed_files: list[str]
    changed_file_list: Path | None
    config: str
    output: Path
    summary: Path | None
    maxfail: int
    strict: bool
    lane: str | None
    include_untestable: bool = False


def _gather_test_nodes(
    *,
    parent_stack: tuple[str, ...],
    lines: list[str],
    file_path: Path,
    node: ast.AST,
    inherited_markers: list[str],
    inherited_requirements: list[str],
    inherited_exemption: str | None,
) -> list[TestRecord]:
    records: list[TestRecord] = []

    if isinstance(node, ast.ClassDef):
        node_markers, node_requirements = _iter_markers_and_requirements(node.decorator_list)
        markers = sorted(set(inherited_markers + node_markers))
        requirements = sorted(set(inherited_requirements + node_requirements))
        exemption = inherited_exemption or _find_exemption_comment(lines, getattr(node, "lineno", 1))
        trace_refs = _find_trace_references(
            lines,
            getattr(node, "lineno", 1),
            getattr(node, "end_lineno", getattr(node, "lineno", 1)),
        )

        if node.name.startswith("Test"):
            records.append(
                TestRecord(
                    file=_rel_path_string(file_path),
                    kind="ClassDef",
                    nodeid=_node_id(file_path, parent_stack + (node.name,)),
                    line=getattr(node, "lineno", 1),
                    markers=markers,
                    requirements=requirements,
                    trace_references=trace_refs,
                    exemption_reason=exemption,
                    source_loc=_source_lines(node),
                )
            )

        for child in node.body:
            records.extend(
                _gather_test_nodes(
                    parent_stack=parent_stack + (node.name,),
                    lines=lines,
                    file_path=file_path,
                    node=child,
                    inherited_markers=markers,
                    inherited_requirements=requirements,
                    inherited_exemption=exemption,
                )
            )
        return records

    if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
        node_markers, node_requirements = _iter_markers_and_requirements(node.decorator_list)
        markers = sorted(set(inherited_markers + node_markers))
        requirements = sorted(set(inherited_requirements + node_requirements))
        exemption = inherited_exemption or _find_exemption_comment(lines, getattr(node, "lineno", 1))
        trace_refs = _find_trace_references(
            lines,
            getattr(node, "lineno", 1),
            getattr(node, "end_lineno", getattr(node, "lineno", 1)),
        )

        if node.name.startswith("test"):
            records.append(
                TestRecord(
                    file=_rel_path_string(file_path),
                    kind=type(node).__name__,
                    nodeid=_node_id(file_path, parent_stack + (node.name,)),
                    line=getattr(node, "lineno", 1),
                    markers=markers,
                    requirements=requirements,
                    trace_references=trace_refs,
                    exemption_reason=exemption,
                    source_loc=_source_lines(node),
                )
            )

    return records


def _rel_path_string(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _load_changed_file_list(changed_file_list: Path | None) -> list[Path]:
    if changed_file_list is None:
        return []

    if not changed_file_list.exists() or not changed_file_list.is_file():
        return []

    if not str(changed_file_list).strip():
        return []

    return _load_changed_paths(changed_file_list)


def scan_tests(input_dir: Path, include_files: set[Path] | None = None) -> list[TestRecord]:
    records: list[TestRecord] = []

    for path in sorted(input_dir.rglob("test_*.py")):
        if include_files is not None and path not in include_files:
            continue

        if "venv" in path.parts or "__pycache__" in path.parts:
            continue

        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except SyntaxError as exc:
            raise RuntimeError(f"failed to parse {path}") from exc

        lines = source.splitlines()
        for node in tree.body:
            records.extend(
                _gather_test_nodes(
                    parent_stack=(),
                    lines=lines,
                    file_path=path,
                    node=node,
                    inherited_markers=[],
                    inherited_requirements=[],
                    inherited_exemption=None,
                )
            )

    return records


def parse_fr_tracker(path: Path | None) -> list[str]:
    if path is None or not path.exists():
        return []

    ids: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = FR_TRACKER_ID_RE.search(line)
        if match:
            ids.append(match.group(1))

    return sorted(set(ids))


def run_collect(
    *,
    marker_expr: str | None,
    output: Path,
    strict: bool,
    marker_label: str,
    budget: int | None,
    summary_output: Path | None,
    lane: str | None = None,
    marker: str | None = None,
    marker_fallback: str | None = None,
    test_paths: list[str] | None = None,
) -> dict[str, object]:
    command = [sys.executable, "-m", "pytest", "--collect-only", "-q"]

    expression = _build_marker_expression(
        marker_expr=marker_expr,
        lane=lane,
        marker_fallback=marker_fallback if marker_fallback is not None else marker,
    )
    if expression:
        command.extend(["-m", expression])

    command.append("--strict-markers")
    command.extend(test_paths or list(DEFAULT_COLLECT_PATH))

    # Collection should stay lightweight and deterministic; opt out of plugin
    # auto-discovery by default unless caller explicitly overrides.
    collect_env = os.environ.copy()
    collect_env.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")

    started = datetime.now().timestamp()
    proc = subprocess.run(command, capture_output=True, text=True, env=collect_env)
    ended = datetime.now().timestamp()

    collected, errors = _parse_collect_metrics(proc.stdout, proc.stderr)
    items = _parse_collect_items(f"{proc.stdout}\n{proc.stderr}")
    over_budget = budget is not None and collected is not None and collected > budget

    payload: dict[str, object] = {
        "schema_version": "collect/v1",
        "timestamp": _now_iso(),
        "command": command,
        "command_hash": _command_hash(command),
        "label": marker_label,
        "lane": lane,
        "marker": marker,
        "marker_expr": expression,
        "returncode": proc.returncode,
        "collected": collected,
        "errors": errors,
        "items": items,
        "duration_ms": int((ended - started) * 1000),
        "budget": budget,
        "over_budget": over_budget,
        "test_paths": test_paths or list(DEFAULT_COLLECT_PATH),
        "stderr_tail": proc.stderr.splitlines()[-8:],
        "stdout_tail": proc.stdout.splitlines()[-8:],
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    if summary_output:
        _write_collect_summary(marker_label, payload, summary_output)

    if strict and (proc.returncode != 0 or bool(errors)):
        raise SystemExit(proc.returncode if proc.returncode else 2)

    if strict and over_budget:
        raise SystemExit(2)

    return payload


def _write_collect_summary(label: str, payload: dict[str, object], path: Path) -> None:
    status = "pass"
    if payload["returncode"] != 0 or payload["errors"] not in (None, 0) or payload["over_budget"]:
        status = "fail"

    lines = [
        "# Pytest Lane Metrics",
        "",
        f"- Lane: `{label}`",
        f"- Marker: `{payload['marker_expr'] or payload['marker']}`",
        f"- Command: `{' '.join(shlex.quote(item) for item in payload['command'])}`",
        f"- Command hash: `{payload['command_hash']}`",
        f"- Duration (ms): `{payload['duration_ms']}`",
        f"- Collected nodes: `{payload['collected']}`",
        f"- Item nodes: `{len(payload['items'])}`",
        f"- Errors: `{payload['errors']}`",
        f"- Budget: `{payload['budget']}`",
        f"- Over budget: `{payload['over_budget']}`",
        f"- Status: `{status}`",
    ]

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_trace_scan(records: list[TestRecord], output: Path) -> None:
    test_to_requirements: dict[str, list[str]] = {}
    test_to_trace: dict[str, list[str]] = {}
    trace_links: list[dict[str, object]] = []
    trace_only_rows: list[dict[str, object]] = []

    for row in records:
        requirements = sorted(row.requirements)
        trace_references = sorted(row.trace_references, key=lambda item: item[0])

        test_to_requirements[row.nodeid] = requirements
        if row.trace_references:
            test_to_trace[row.nodeid] = [req for req, _ in trace_references]
        else:
            test_to_trace[row.nodeid] = []

        for req_id in requirements:
            trace_links.append(
                {
                    "source": row.nodeid,
                    "target": req_id,
                    "relation": "requirement_marker",
                    "confidence": 1.0,
                }
            )

        for req_id, confidence in trace_references:
            trace_links.append(
                {
                    "source": row.nodeid,
                    "target": req_id,
                    "relation": "trace_comment",
                    "confidence": confidence,
                }
            )

        if "requirement" not in row.markers and row.trace_references:
            trace_only_rows.append(
                {
                    "file": row.file,
                    "nodeid": row.nodeid,
                    "line": row.line,
                    "markers": row.markers,
                    "trace_requirements": [req for req, _ in trace_references],
                    "trace_confidence": dict(trace_references),
                    "message": "trace evidence present but no @pytest.mark.requirement marker",
                }
            )

    row_count = len(records)
    with_requirements = sum(1 for row in records if row.requirements)
    with_trace = sum(1 for row in records if row.trace_references)
    payload = {
        "schema_version": TRACE_SCAN_SCHEMA_VERSION,
        "timestamp": _now_iso(),
        "total_tests": row_count,
        "trace_reference_stats": {
            "tests_with_requirement_marker": with_requirements,
            "tests_with_trace_references": with_trace,
            "trace_reference_only_tests": len(trace_only_rows),
        },
        "test_to_requirements": dict(sorted(test_to_requirements.items())),
        "test_to_trace_references": dict(sorted(test_to_trace.items())),
        "trace_links": trace_links,
        "missing_requirement": [
            {
                "file": row.file,
                "nodeid": row.nodeid,
                "line": row.line,
                "markers": row.markers,
                "requirements": row.requirements,
                "trace_requirements": [req for req, _ in row.trace_references],
                "trace_confidence": dict(row.trace_references),
                "source_loc": row.source_loc,
                "trace_evidence_confidence": max((confidence for _, confidence in row.trace_references), default=0.0),
                "evidence": [
                    {
                        "type": "requirement_marker",
                        "source": "decorator",
                        "id": req_id,
                        "confidence": 1.0,
                    }
                    for req_id in row.requirements
                ]
                + [
                    {
                        "type": "trace_reference",
                        "source": "comment",
                        "id": req_id,
                        "confidence": confidence,
                    }
                    for req_id, confidence in row.trace_references
                ],
            }
            for row in records
            if "requirement" not in row.markers
        ],
        "trace_only_warnings": trace_only_rows,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def run_heavy_untagged(records: list[TestRecord], output: Path, min_loc: int) -> None:
    heavy = [
        record
        for record in records
        if not record.requirements and (set(record.markers).intersection(HEAVY_MARKERS) or record.source_loc >= min_loc)
    ]

    payload = {
        "timestamp": _now_iso(),
        "min_loc": min_loc,
        "count": len(heavy),
        "tests": [
            {
                "file": record.file,
                "nodeid": record.nodeid,
                "line": record.line,
                "markers": record.markers,
                "source_loc": record.source_loc,
            }
            for record in heavy
        ],
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _normalize_requirement_id(value: str) -> str:
    match = REQUIREMENT_ID_RE.search(value)
    if not match:
        return value
    return match.group(0)


def run_requirements_map(
    records: list[TestRecord],
    output: Path,
    fr_tracker: list[str],
    csv_output: Path | None,
    summary: Path | None = None,
    diagram_output: Path | None = None,
    diagram_max_nodes: int = REQUIREMENTS_MAP_DIAGRAM_MAX_REQUIREMENTS,
) -> dict[str, object]:
    req_to_tests: dict[str, list[str]] = defaultdict(list)
    test_to_requirements: dict[str, list[str]] = {}
    trace_to_tests: dict[str, list[str]] = defaultdict(list)
    test_to_trace_requirements: dict[str, list[str]] = {}

    for record in records:
        normalized_requirements = [_normalize_requirement_id(req_id) for req_id in record.requirements]
        normalized_requirements = sorted(set(normalized_requirements))
        test_to_requirements[record.nodeid] = normalized_requirements

        normalized_trace_references = [
            req_id for req_id, _ in sorted(record.trace_references, key=lambda item: item[0])
        ]
        test_to_trace_requirements[record.nodeid] = normalized_trace_references

        for req_id in normalized_requirements:
            req_to_tests[req_id].append(record.nodeid)

        for req_id in normalized_trace_references:
            if req_id in normalized_requirements:
                continue
            trace_to_tests[req_id].append(record.nodeid)

    for values in req_to_tests.values():
        values.sort()
    for values in trace_to_tests.values():
        values.sort()

    requirement_ids = sorted(req_to_tests)
    uncovered = [req_id for req_id in fr_tracker if req_id not in req_to_tests]
    secondary_uncovered = [
        req_id for req_id in fr_tracker if req_id not in req_to_tests and req_id not in trace_to_tests
    ]
    mapped_count = len(requirement_ids)
    secondary_mapped_count = len(trace_to_tests)
    trace_only_tests = sum(1 for row in records if row.trace_references and not row.requirements)

    payload: dict[str, object] = {
        "schema_version": REQUIREMENTS_MAP_SCHEMA_VERSION,
        "generated_at": _now_iso(),
        "input_dir": str(records[0].file).rsplit("/", 1)[0] if records else str(DEFAULT_INPUT_DIR),
        "record_count": len(records),
        "requirement_to_tests": {req_id: req_to_tests[req_id] for req_id in requirement_ids},
        "test_to_requirements": dict(sorted(test_to_requirements.items())),
        "trace_to_tests": {req_id: trace_to_tests[req_id] for req_id in sorted(trace_to_tests)},
        "test_to_trace_requirements": dict(sorted(test_to_trace_requirements.items())),
        "requirement_coverage": {
            "tracked_requirements": len(fr_tracker),
            "mapped_requirements": mapped_count,
            "coverage_ratio": round(mapped_count / len(fr_tracker), 4) if fr_tracker else None,
            "uncovered_requirements": uncovered,
        },
        "secondary_evidence_coverage": {
            "mapped_requirements": secondary_mapped_count,
            "uncovered_requirements": secondary_uncovered,
            "trace_only_tests": trace_only_tests,
            "trace_requirements": {req_id: trace_to_tests[req_id] for req_id in sorted(trace_to_tests)},
        },
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    if csv_output is not None:
        csv_output.parent.mkdir(parents=True, exist_ok=True)
        with csv_output.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["requirement", "test_count", "tests"])
            for req_id in requirement_ids:
                writer.writerow([req_id, len(req_to_tests[req_id]), ",".join(req_to_tests[req_id])])

    if summary is not None:
        summary.parent.mkdir(parents=True, exist_ok=True)
        summary.write_text(
            "\n".join(
                [
                    "# Requirement Traceability Map",
                    "",
                    f"- Tracked requirements: `{len(fr_tracker)}`",
                    f"- Mapped requirements: `{mapped_count}`",
                    f"- Uncovered requirements: `{len(uncovered)}`",
                    "",
                    "## Coverage ratio",
                    f"- `coverage_ratio`: `{payload['requirement_coverage']['coverage_ratio']}`",
                    "",
                ]
                + (
                    [f"- Uncovered: `{req}`" for req in uncovered]
                    if uncovered
                    else ["No uncovered requirements found."]
                )
            )
            + "\n",
            encoding="utf-8",
        )

    if diagram_output is not None:
        run_requirements_diagram(
            payload=payload,
            output=diagram_output,
            max_nodes=diagram_max_nodes,
        )

    return payload


def run_requirements_diagram(payload: dict[str, object], output: Path, max_nodes: int = 100) -> None:
    requirement_to_tests = payload.get("requirement_to_tests", {})
    if not isinstance(requirement_to_tests, dict):
        raise RuntimeError("requirements-map payload missing requirement_to_tests")

    requirements: list[tuple[str, list[str]]] = sorted(
        [
            (req_id, sorted(tests))
            for req_id, tests in requirement_to_tests.items()
            if isinstance(req_id, str) and isinstance(tests, list)
        ]
    )
    max_nodes = max_nodes if max_nodes > 0 else len(requirements)
    visible_requirements = requirements[:max_nodes]

    coverage = payload.get("requirement_coverage", {})
    coverage_ratio = None
    if isinstance(coverage, dict):
        coverage_ratio = coverage.get("coverage_ratio")

    if visible_requirements:
        req_lines = [f'    req_{_mermaid_id(req_id)}["{req_id}"]' for req_id, _ in visible_requirements]
    else:
        req_lines = []

    edges: list[str] = []
    node_refs: list[str] = []
    node_count = 0
    truncated_edges = False
    for req_id, tests in visible_requirements:
        req_node = f"req_{_mermaid_id(req_id)}"
        for test_node in tests[:REQUIREMENTS_MAP_DIAGRAM_MAX_TESTS_PER_REQUIREMENT]:
            if len(tests) > REQUIREMENTS_MAP_DIAGRAM_MAX_TESTS_PER_REQUIREMENT:
                truncated_edges = True
            if not test_node:
                continue
            safe_test = _mermaid_id(test_node)
            test_ref = f"t_{safe_test}"
            node_count += 1
            node_refs.append(f'    {test_ref}["{test_node}"]')
            edges.append(f"    {req_node} --> {test_ref}")

    if not node_refs:
        for uncovered in payload.get("requirement_coverage", {}).get("uncovered_requirements", []):
            req_node = f"req_{_mermaid_id(uncovered)}"
            req_lines.append(f'    {req_node}["{uncovered} (uncovered)"]')

    truncated_requirements = len(requirement_to_tests) > len(visible_requirements)
    truncated = truncated_requirements or truncated_edges

    lines = [
        "# Requirement DAG",
        "",
        f"- Schema version: `{REQUIREMENTS_MAP_DIAGRAM_SCHEMA_VERSION}`",
        f"- Source coverage ratio: `{coverage_ratio}`",
        f"- Visible requirements: `{len(visible_requirements)}`",
        f"- Visible test edges: `{len(edges)}`",
        f"- Truncated requirements: `{truncated_requirements}`",
        f"- Truncated edges: `{truncated_edges}`",
        "",
        "```mermaid",
        "flowchart TD",
    ]

    if req_lines:
        lines.append("    subgraph FRs")
        lines.extend(req_lines)
        lines.append("    end")
        lines.append("    subgraph Tests")
        lines.extend(node_refs)
        lines.append("    end")
    else:
        lines.append("    classDef warn fill:#fee,stroke:#900,color:#900")
        lines.append('    warn("No mapped requirements detected"):::warn')

    if edges:
        lines.extend(edges)

    lines.extend(["```", ""])

    if truncated:
        lines.append("This diagram is truncated for readability. Regenerate with larger limits to view full edges.")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_trace_cleanup(
    records: list[TestRecord],
    output: Path,
    summary: Path | None = None,
    stale_window_days: int = TRACEABILITY_STALE_WINDOW_DAYS,
    issue_output: Path | None = None,
    issue_threshold: int = TRACE_CLEANUP_BREACH_BUDGET,
) -> None:
    now = datetime.now(timezone.utc).timestamp()
    stale_threshold_seconds = stale_window_days * 24 * 60 * 60
    stale_items: list[dict[str, object]] = []
    deprecated_marker_items: list[dict[str, object]] = []

    for row in records:
        if row.requirements:
            continue

        absolute_file = ROOT / row.file
        age_seconds = 0.0
        if absolute_file.exists():
            age_seconds = now - absolute_file.stat().st_mtime

        age_days = round(age_seconds / 86400, 2)

        if row.trace_references and age_seconds > stale_threshold_seconds:
            stale_items.append(
                {
                    "file": row.file,
                    "nodeid": row.nodeid,
                    "line": row.line,
                    "markers": row.markers,
                    "trace_references": [req for req, _ in row.trace_references],
                    "age_days": age_days,
                    "debt_type": "stale_trace_only_test",
                    "required_action": "Add @pytest.mark.requirement or drop stale trace reference with migration comment.",
                    "evidence": [
                        {
                            "type": "trace_reference",
                            "id": req_id,
                            "confidence": confidence,
                        }
                        for req_id, confidence in row.trace_references
                    ],
                }
            )

        if any(marker in DEPRECATED_MARKER_HINTS for marker in row.markers):
            deprecated_marker_items.append(
                {
                    "file": row.file,
                    "nodeid": row.nodeid,
                    "line": row.line,
                    "markers": row.markers,
                    "debt_type": "deprecated_marker",
                    "required_action": "Replace deprecated marker usage before next release window.",
                    "age_days": age_days,
                }
            )

    payload: dict[str, object] = {
        "schema_version": TRACE_CLEANUP_SCHEMA_VERSION,
        "timestamp": _now_iso(),
        "cleanup_cadence_days": 90,
        "stale_window_days": stale_window_days,
        "total_traced_tests_without_marker": sum(1 for row in records if not row.requirements and row.trace_references),
        "deprecated_marker_debt_count": len(deprecated_marker_items),
        "deprecated_marker_debt": sorted(
            deprecated_marker_items,
            key=lambda item: (str(item.get("file", "")), str(item.get("nodeid", ""))),
        ),
        "stale_debt_count": len(stale_items),
        "stale_debt": sorted(
            stale_items,
            key=lambda item: (str(item.get("file", "")), str(item.get("nodeid", ""))),
        ),
        "stale_window_breach": len(stale_items) > issue_threshold,
        "deprecated_marker_breach": len(deprecated_marker_items) > issue_threshold,
        "quarterly_cleanup_issue": (
            "open"
            if (len(stale_items) > issue_threshold or len(deprecated_marker_items) > issue_threshold)
            else "closed"
        ),
        "stale_debt_candidates": sorted(
            stale_items + deprecated_marker_items,
            key=lambda item: (str(item.get("file", "")), str(item.get("nodeid", ""))),
        ),
    }

    issue_open = payload["quarterly_cleanup_issue"] == "open"

    if issue_output is not None:
        issue_payload = {
            "schema_version": TRACE_CLEANUP_ISSUE_SCHEMA_VERSION,
            "issued_at": _now_iso(),
            "status": payload["quarterly_cleanup_issue"],
            "artifact": str(output),
            "cleanup_cadence_days": payload.get("cleanup_cadence_days"),
            "stale_window_days": stale_window_days,
            "stale_window_breach": payload["stale_window_breach"],
            "deprecated_marker_breach": payload["deprecated_marker_breach"],
            "stale_debt_count": payload["stale_debt_count"],
            "deprecated_marker_debt_count": payload["deprecated_marker_debt_count"],
            "recommended_action": ("open" if issue_open else "monitor"),
            "cleanup_plan": {
                "run_cleanup": "task test:traceability:quarterly-cleanup",
                "fallback_action": "open cleanup tracker ticket and schedule next release slice",
            },
        }
        issue_output.parent.mkdir(parents=True, exist_ok=True)
        issue_output.write_text(
            json.dumps(issue_payload, indent=2) + "\n",
            encoding="utf-8",
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    if summary is None:
        return

    summary.parent.mkdir(parents=True, exist_ok=True)
    summary.write_text(
        "\n".join(
            [
                "# Traceability Cleanup Summary",
                "",
                f"- stale_window_days: `{stale_window_days}`",
                f"- stale_window_breach: `{payload['stale_window_breach']}`",
                f"- deprecated_marker_breach: `{payload['deprecated_marker_breach']}`",
                f"- stale_debt_count: `{payload['stale_debt_count']}`",
                f"- deprecated_marker_debt_count: `{payload['deprecated_marker_debt_count']}`",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def _coerce_artifact_status(payload: dict[str, object]) -> str:
    status = payload.get("status")
    if status in {"passed", "failed", "skipped", "error", "blocked", "timeout"}:
        return str(status)

    return "passed" if _int_or_zero(payload.get("returncode")) == 0 else "failed"


def _collect_run_metrics(run_artifacts: list[Path] | None) -> dict[str, object]:
    artifacts = run_artifacts or []
    entries = [_safe_load_artifact(path) for path in artifacts]

    run_payloads = [payload for payload in entries if isinstance(payload, dict)]
    if not run_payloads:
        return {
            "run_count": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "unknown": 0,
            "run_artifacts": [str(path) for path in artifacts],
            "observed_flake_ratio": 0.0,
            "stability_ratio": 0.0,
            "run_artifact_statuses": [],
        }

    passed = 0
    failed = 0
    skipped = 0
    unknown = 0
    statuses: list[str] = []
    for payload in run_payloads:
        status = _coerce_artifact_status(payload)
        statuses.append(status)
        if status == "passed":
            passed += 1
        elif status == "failed":
            failed += 1
        elif status == "skipped":
            skipped += 1
        else:
            unknown += 1
    run_count = len(statuses)
    return {
        "run_count": run_count,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "unknown": unknown,
        "run_artifacts": [str(path) for path in artifacts],
        "observed_flake_ratio": round(failed / run_count, 4) if run_count else 0.0,
        "stability_ratio": round(passed / run_count, 4) if run_count else 0.0,
        "run_artifact_statuses": statuses,
    }


def _requirements_promotion_payload(
    *,
    requirements_map_artifact: Path | None,
    requirements_gate_artifact: Path | None,
    health_artifact: Path | None,
    run_artifacts: list[Path] | None,
    min_coverage_ratio: float,
    min_runs: int,
    max_flake_ratio: float,
    acceptable_fail_budget: int,
) -> tuple[dict[str, object], list[str], bool]:
    map_payload = _safe_load_artifact(requirements_map_artifact) if requirements_map_artifact else {}
    if not isinstance(map_payload, dict):
        map_payload = {}

    gate_payload = _safe_load_artifact(requirements_gate_artifact) if requirements_gate_artifact else {}
    if not isinstance(gate_payload, dict):
        gate_payload = {}

    health_payload = _safe_load_artifact(health_artifact) if health_artifact else {}
    if not isinstance(health_payload, dict):
        health_payload = {}

    coverage_ratio = None
    coverage_data = map_payload.get("requirement_coverage", {})
    if isinstance(coverage_data, dict):
        raw_ratio = coverage_data.get("coverage_ratio")
        if isinstance(raw_ratio, int | float):
            coverage_ratio = float(raw_ratio)

    blocked_count = gate_payload.get("blocked_count", 0)
    if isinstance(blocked_count, str) and blocked_count.isdigit():
        blocked_count = int(blocked_count)
    blocked_count = _int_or_zero(blocked_count)

    health_score = health_payload.get("overall_health_score")
    if isinstance(health_score, str) and health_score.isdigit():
        health_score = int(health_score)
    if not isinstance(health_score, int | float):
        health_score = None

    has_map = (
        isinstance(map_payload.get("schema_version"), str)
        and map_payload.get("schema_version") == REQUIREMENTS_MAP_SCHEMA_VERSION
    )

    run_metrics = _collect_run_metrics(run_artifacts)
    run_count = run_metrics["run_count"]
    failed_runs = run_metrics["failed"]
    passed_runs = run_metrics["passed"]
    observed_flake_ratio = run_metrics["observed_flake_ratio"]
    stability_ratio = run_metrics["stability_ratio"]

    promote_coverage = coverage_ratio is not None and coverage_ratio >= min_coverage_ratio
    promote_blocked = blocked_count == 0
    promote_health = isinstance(health_score, int | float) and float(health_score) >= 90.0
    promote_min_runs = isinstance(run_count, int) and run_count >= min_runs
    promote_stability = isinstance(stability_ratio, float) and stability_ratio >= (1.0 - max_flake_ratio)
    promote_flake = isinstance(observed_flake_ratio, float) and observed_flake_ratio <= max_flake_ratio
    promote_fail_budget = isinstance(failed_runs, int) and failed_runs <= acceptable_fail_budget

    ready = bool(
        promote_coverage
        and promote_blocked
        and promote_health
        and promote_min_runs
        and promote_stability
        and promote_flake
        and promote_fail_budget
    )

    required_stability_ratio = 1.0 - max_flake_ratio

    reasons: list[str] = [
        "coverage_below_threshold" if not promote_coverage else None,
        "blocked_requirements_detected" if not promote_blocked else None,
        "low_health_score" if not promote_health else None,
        "insufficient_run_history" if not promote_min_runs else None,
        "stability_threshold_not_met" if not promote_stability else None,
        "observed_flake_ratio_too_high" if not promote_flake else None,
        "acceptable_fail_budget_exceeded" if not promote_fail_budget else None,
    ]
    reasons = [item for item in reasons if item]

    payload: dict[str, object] = {
        "schema_version": PROMOTION_CRITERIA_SCHEMA_VERSION,
        "timestamp": _now_iso(),
        "criteria": {
            "min_requirement_coverage_ratio": min_coverage_ratio,
            "min_runs": min_runs,
            "required_stability_ratio": required_stability_ratio,
            "max_flake_ratio": max_flake_ratio,
            "acceptable_fail_budget": acceptable_fail_budget,
            "run_artifacts": run_metrics["run_artifacts"],
            "health_gate_min_score": 90,
            "required_stable_runs_required": min_runs,
        },
        "actual": {
            "requirement_coverage_ratio": coverage_ratio,
            "requirements_map_available": has_map,
            "requirements_gate_blocked_count": blocked_count,
            "health_score": health_score,
            "run_count": run_count,
            "passed_runs": passed_runs,
            "failed_runs": failed_runs,
            "skipped_runs": run_metrics["skipped"],
            "run_artifact_statuses": run_metrics["run_artifact_statuses"],
            "run_artifacts": run_metrics["run_artifacts"],
            "observed_flake_ratio": observed_flake_ratio,
            "required_stability_ratio": required_stability_ratio,
            "stability_ratio": stability_ratio,
            "coverage_threshold_met": promote_coverage,
            "requirements_gate_blocked": promote_blocked,
            "health_score_threshold_met": promote_health,
            "run_count_threshold_met": promote_min_runs,
            "flake_ratio_threshold_met": promote_flake,
            "fail_budget_threshold_met": promote_fail_budget,
            "run_history_threshold_met": promote_min_runs,
        },
        "recommendation": {
            "ready_for_lane_promotion": ready,
            "make_optional_lanes_required": ready,
            "reasons": reasons,
        },
        "flake_gate": {
            "max_flake_ratio": max_flake_ratio,
            "observed_flake_ratio": observed_flake_ratio,
            "required_stability_ratio": required_stability_ratio,
            "max_stable_runs_required": min_runs,
            "observed_stable_ratio": stability_ratio,
            "required_optional_run_count": min_runs,
            "failure_budget_remaining": max(acceptable_fail_budget - failed_runs, 0),
        },
    }
    return payload, reasons, ready


def run_requirements_promotion_criteria(
    *,
    requirements_map_artifact: Path | None,
    requirements_gate_artifact: Path | None,
    health_artifact: Path | None,
    output: Path,
    min_coverage_ratio: float,
    min_runs: int,
    max_flake_ratio: float,
    acceptable_fail_budget: int,
    run_artifacts: list[Path] | None = None,
) -> None:
    payload, _, _ = _requirements_promotion_payload(
        requirements_map_artifact=requirements_map_artifact,
        requirements_gate_artifact=requirements_gate_artifact,
        health_artifact=health_artifact,
        run_artifacts=run_artifacts,
        min_coverage_ratio=min_coverage_ratio,
        min_runs=min_runs,
        max_flake_ratio=max_flake_ratio,
        acceptable_fail_budget=acceptable_fail_budget,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def run_lane_promotion(config: LanePromotionConfig) -> None:
    min_coverage_ratio = config.min_coverage_ratio
    payload, _, _ = _requirements_promotion_payload(
        requirements_map_artifact=config.requirements_map_artifact,
        requirements_gate_artifact=config.requirements_gate_artifact,
        health_artifact=config.health_artifact,
        run_artifacts=config.run_artifacts,
        min_coverage_ratio=min_coverage_ratio,
        min_runs=config.min_runs,
        max_flake_ratio=config.max_flake_ratio,
        acceptable_fail_budget=config.acceptable_fail_budget,
    )
    payload["schema_version"] = LANE_PROMOTION_SUMMARY_SCHEMA_VERSION
    payload["lane"] = config.lane
    payload["criteria"]["min_requirement_coverage_ratio"] = min_coverage_ratio
    payload["criteria"]["min_runs"] = config.min_runs
    payload["criteria"]["max_flake_ratio"] = config.max_flake_ratio
    payload["criteria"]["acceptable_fail_budget"] = config.acceptable_fail_budget

    payload["recommendation"] = {
        "ready_for_lane_promotion": bool(payload["recommendation"]["ready_for_lane_promotion"]),
        "reasons": payload["recommendation"]["reasons"],
        "ready_to_require_optional_lanes": bool(payload["recommendation"]["ready_for_lane_promotion"]),
    }
    payload["promotion_plan"] = {
        "lane": config.lane,
        "action": (
            "promote_optional_lane_to_required"
            if bool(payload["recommendation"]["ready_for_lane_promotion"])
            else "hold_optional_lane"
        ),
        "required": bool(payload["recommendation"]["ready_for_lane_promotion"]),
    }
    payload["actual"]["stable_runs_required"] = config.min_runs

    config.output.parent.mkdir(parents=True, exist_ok=True)
    config.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _load_changed_paths(changed_file: Path) -> list[Path]:
    paths: list[Path] = []
    for value in changed_file.read_text(encoding="utf-8").splitlines():
        value = value.strip()
        if not value or value.startswith("#"):
            continue
        paths.append(Path(value))
    return paths


def _load_exemptions(path: Path | None) -> list[dict[str, str]]:
    if path is None or not path.exists() or not path.is_file():
        return []

    raw = json.loads(path.read_text(encoding="utf-8"))
    items = raw.get("exemptions") if isinstance(raw, dict) else raw

    if not isinstance(items, list):
        raise RuntimeError("exceptions must be a list or include an 'exemptions' list")

    normalized = []
    for item in items:
        if not isinstance(item, dict):
            raise RuntimeError("exceptions entries must be objects")

        file_expr = str(item.get("file", "")).strip()
        test_expr = str(item.get("test", "")).strip()
        reason = str(item.get("reason", "explicit_exception")).strip()
        normalized.append({"file": file_expr, "test": test_expr, "reason": reason})

    return normalized


def _is_exempt(record: TestRecord, exemptions: list[dict[str, str]]) -> str | None:
    if record.exemption_reason:
        return record.exemption_reason

    for exemption in exemptions:
        file_expr = exemption["file"]
        if not file_expr:
            continue

        file_matches = record.file == file_expr or record.file.endswith(file_expr)
        if not file_matches:
            continue

        if not exemption["test"]:
            return exemption["reason"]

        test_suffix = f"::{exemption['test']}"
        legacy_test_suffix = f":{exemption['test']}"
        if record.nodeid.endswith(test_suffix) or record.nodeid.endswith(legacy_test_suffix):
            return exemption["reason"]

    return None


def run_requirements_gate(
    *,
    config: RequirementGateConfig,
    fr_tracker: list[str] | None = None,
) -> int:
    changed: list[Path] = []
    if config.changed_files:
        changed.extend(Path(path) for path in config.changed_files)
    changed.extend(_load_changed_file_list(config.changed_file_list))

    targets, untestable_files, has_unknown = _derive_pr_targets(changed, config.input_dir)

    if not targets:
        payload: dict[str, object] = {
            "timestamp": _now_iso(),
            "status": "skipped",
            "reason": "No test targets discovered from changed files",
            "fallback_to_fast_lane": has_unknown,
            "blocked": [],
            "blocked_count": 0,
            "total_checked": 0,
            "changed_files": [str(item) for item in changed],
            "untestable_files": [str(item) for item in untestable_files],
        }
        config.output.parent.mkdir(parents=True, exist_ok=True)
        config.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        if config.summary:
            config.summary.write_text(
                "# PR Requirement Mapping Gate\n\nNo test targets discovered from changed files.\n",
                encoding="utf-8",
            )
        return 0

    records = scan_tests(config.input_dir, include_files={item.resolve() for item in targets})
    if not records:
        payload = {
            "timestamp": _now_iso(),
            "status": "skipped",
            "reason": "Discovered targets could not be parsed as tests",
            "fallback_to_fast_lane": has_unknown,
            "blocked": [],
            "blocked_count": 0,
            "total_checked": 0,
            "changed_files": [str(item) for item in changed],
            "untestable_files": [str(item) for item in untestable_files],
        }
        config.output.parent.mkdir(parents=True, exist_ok=True)
        config.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        if config.summary:
            config.summary.write_text(
                "# PR Requirement Mapping Gate\n\nNo parsable tests found for discovered targets.\n",
                encoding="utf-8",
            )
        return 0

    exemptions = _load_exemptions(config.exceptions_path)
    blocked: list[dict[str, object]] = []

    for record in records:
        if record.requirements:
            continue
        reason = _is_exempt(record, exemptions)
        if reason is not None:
            continue

        blocked.append(
            {
                "file": record.file,
                "nodeid": record.nodeid,
                "line": record.line,
                "reason": "missing_requirement_marker",
                "requirement_exemption_available": False,
            }
        )

    payload = {
        "timestamp": _now_iso(),
        "status": "blocked" if blocked else "passed",
        "fallback_to_fast_lane": has_unknown,
        "total_checked": len(records),
        "blocked_count": len(blocked),
        "blocked": blocked,
        "requirements_catalog_size": len(fr_tracker or []),
        "changed_files": [str(item) for item in changed],
        "untestable_files": [str(item) for item in untestable_files],
    }

    config.output.parent.mkdir(parents=True, exist_ok=True)
    config.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    if config.summary:
        lines = [
            "# PR Requirement Mapping Gate",
            "",
            f"- Blocked: {len(blocked)}",
            f"- Total checked: {len(records)}",
            f"- Fallback to fast lane: {payload['fallback_to_fast_lane']}",
            "",
        ]
        if blocked:
            lines.append("## Blocked tests")
            for item in blocked:
                lines.append(f"- `{item['nodeid']}` ({item['file']}:{item['line']})")

        config.summary.write_text("\n".join(lines) + "\n", encoding="utf-8")

    if blocked and config.strict:
        return 1
    return 0


def run_pr_targets(config: PrTargetConfig) -> dict[str, object]:
    changed = [Path(item) for item in config.changed_files]
    changed.extend(_load_changed_file_list(config.changed_file_list))

    targets, untestable_files, has_unknown = _derive_pr_targets(changed, DEFAULT_INPUT_DIR)
    resolved_targets = list(targets)
    if config.include_untestable:
        resolved_targets.extend(untestable_files)
        resolved_targets = sorted(set(resolved_targets))

    payload = {
        "timestamp": _now_iso(),
        "status": "mapped" if resolved_targets else "unmapped",
        "fallback_to_fast_lane": has_unknown,
        "changed_files": config.changed_files,
        "target_count": len(resolved_targets),
        "targets": [str(path) for path in resolved_targets],
        "mapped_targets": [str(path) for path in targets],
        "untestable_files": [str(path) for path in untestable_files],
    }

    config.output.parent.mkdir(parents=True, exist_ok=True)
    config.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    return payload


def _normalize_changed_path_for_parser(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return path.as_posix()


def _targets_require_parser_parity(changed: Sequence[Path], targets: Sequence[Path]) -> bool:
    if any(target.name in PARSER_PARITY_TARGET_NAMES for target in targets):
        return True

    for changed_path in changed:
        normalized = _normalize_changed_path_for_parser(changed_path)
        if normalized in PARSER_PARITY_TARGET_NAMES:
            return True
        for prefix in PARSER_TOUCHING_PATH_PREFIXES:
            if normalized.startswith(prefix):
                return True

    return False


def run_pr_lane(config: RunPrLaneConfig) -> int:
    changed: list[Path] = []
    if config.changed_files:
        changed.extend(Path(path) for path in config.changed_files)
    changed.extend(_load_changed_file_list(config.changed_file_list))

    targets, untestable_files, has_unknown = _derive_pr_targets(changed, DEFAULT_INPUT_DIR)
    resolved_targets = list(targets)
    if config.include_untestable:
        resolved_targets.extend(untestable_files)
    resolved_targets = sorted(set(resolved_targets))
    lane_expr = _build_marker_expression(
        marker_expr=None,
        lane=config.lane,
        marker_fallback=config.lane,
    )

    command = [sys.executable, "-m", "pytest", f"--maxfail={config.maxfail}", "-q", "--no-header", "--no-summary"]
    if config.config:
        command.extend(["-c", config.config])
    if resolved_targets:
        command.extend(str(target) for target in resolved_targets)
    elif lane_expr:
        command.extend(["-m", lane_expr])
    command.append("--strict-markers")

    env = os.environ.copy()
    if _targets_require_parser_parity(changed, resolved_targets):
        env["THEGENT_PARSER_PARITY_REQUIRED"] = "1"

    started = datetime.now().timestamp()
    proc = subprocess.run(command, env=env, capture_output=True, text=True)
    ended = datetime.now().timestamp()

    payload = {
        "timestamp": _now_iso(),
        "status": "failed" if proc.returncode else "passed",
        "returncode": proc.returncode,
        "command": command,
        "command_hash": _command_hash(command),
        "duration_ms": int((ended - started) * 1000),
        "changed_files": [str(path) for path in changed],
        "targets": [str(path) for path in resolved_targets],
        "mapped_targets": [str(path) for path in targets],
        "untestable_files": [str(path) for path in untestable_files],
        "fallback_to_fast_lane": (has_unknown and not config.include_untestable)
        or (not bool(resolved_targets) and bool(lane_expr)),
        "stdout_tail": proc.stdout.splitlines()[-8:],
        "stderr_tail": proc.stderr.splitlines()[-8:],
    }

    config.output.parent.mkdir(parents=True, exist_ok=True)
    config.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    if config.summary:
        config.summary.write_text(
            f"# PR lane run\n\n- status: {payload['status']}\n- returncode: {proc.returncode}\n- fallback_to_fast_lane: {payload['fallback_to_fast_lane']}\n",
            encoding="utf-8",
        )

    if config.strict and proc.returncode != 0:
        raise SystemExit(proc.returncode)
    return proc.returncode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    collect = sub.add_parser("collect", help="collect-only baseline command")
    collect.add_argument("--marker", default=None, help="pytest -m selector")
    collect.add_argument("--marker-expr", default=None, help="raw pytest marker expression")
    collect.add_argument("--lane", default=None, help="lookup marker expression from [tool.thegent.pytest_lanes]")
    collect.add_argument("--output", required=True)
    collect.add_argument("--summary", default=None)
    collect.add_argument("--strict", action="store_true")
    collect.add_argument("--label", default="collect")
    collect.add_argument("--budget", type=int)
    collect.add_argument("--test-path", nargs="*", default=list(DEFAULT_COLLECT_PATH))

    trace = sub.add_parser("trace-scan", help="scan for marker and requirement coverage hints")
    trace.add_argument("--input-dir", default=str(DEFAULT_INPUT_DIR))
    trace.add_argument("--output", required=True)

    heavy = sub.add_parser("heavy-untagged", help="find potentially untagged heavy tests")
    heavy.add_argument("--input-dir", default=str(DEFAULT_INPUT_DIR))
    heavy.add_argument("--output", required=True)
    heavy.add_argument("--min-loc", default=80, type=int)

    reqmap = sub.add_parser("requirements-map", help="build test↔requirement mapping")
    reqmap.add_argument("--input-dir", default=str(DEFAULT_INPUT_DIR))
    reqmap.add_argument("--fr-tracker")
    reqmap.add_argument("--output", required=True)
    reqmap.add_argument("--csv-output")
    reqmap.add_argument("--summary")
    reqmap.add_argument("--diagram-output", help="optional requirements DAG markdown output")
    reqmap.add_argument("--diagram-max-nodes", type=int, default=REQUIREMENTS_MAP_DIAGRAM_MAX_REQUIREMENTS)

    diag = sub.add_parser("requirements-diagram", help="render requirement DAG from traceability map")
    diag.add_argument("--requirements-map", required=True)
    diag.add_argument("--output", required=True)
    diag.add_argument("--max-nodes", type=int, default=REQUIREMENTS_MAP_DIAGRAM_MAX_REQUIREMENTS)

    for _alias_name in ("requirements-map-diagram",):
        _p = sub.add_parser(_alias_name, help="alias for requirements-diagram")
        _p.add_argument("--requirements-map", required=True)
        _p.add_argument("--output", required=True)
        _p.add_argument("--max-nodes", type=int, default=REQUIREMENTS_MAP_DIAGRAM_MAX_REQUIREMENTS)

    def _add_trace_cleanup_args(p: argparse.ArgumentParser) -> None:
        p.add_argument("--input-dir", default=str(DEFAULT_INPUT_DIR))
        p.add_argument("--output", required=True)
        p.add_argument("--summary", default=None)
        p.add_argument("--stale-window-days", type=int, default=TRACEABILITY_STALE_WINDOW_DAYS)
        p.add_argument("--issue-output", default=None)
        p.add_argument("--issue-threshold", type=int, default=TRACE_CLEANUP_BREACH_BUDGET)

    trace_cleanup = sub.add_parser("trace-cleanup", help="report stale traceability debt candidates")
    _add_trace_cleanup_args(trace_cleanup)
    trace_cleanup_alias = sub.add_parser(
        "traceability-cleanup", help="alias for trace-cleanup with quarter cadence intent"
    )
    _add_trace_cleanup_args(trace_cleanup_alias)

    promote = sub.add_parser("requirements-promotion-criteria", help="compute lane promotion signal")
    promote.add_argument("--requirements-map")
    promote.add_argument("--requirements-gate")
    promote.add_argument("--health")
    promote.add_argument("--output", required=True)
    promote.add_argument("--min-runs", type=int, default=3)
    promote.add_argument("--min-coverage-ratio", type=float, default=0.95)
    promote.add_argument("--max-flake-ratio", type=float, default=0.05)
    promote.add_argument("--acceptable-fail-budget", type=int, default=1)
    promote.add_argument("--run-artifact", action="append", default=[])

    lane_promotion = sub.add_parser(
        "lane-promotion",
        help="compute lane promotion readiness from artifact inputs",
    )
    lane_promotion.add_argument("--lane", required=True)
    lane_promotion.add_argument("--requirements-map")
    lane_promotion.add_argument("--requirements-gate")
    lane_promotion.add_argument("--health")
    lane_promotion.add_argument("--output", required=True)
    lane_promotion.add_argument("--min-runs", type=int, default=3)
    lane_promotion.add_argument("--min-coverage-ratio", type=float, default=0.95)
    lane_promotion.add_argument("--max-flake-ratio", type=float, default=0.05)
    lane_promotion.add_argument("--acceptable-fail-budget", type=int, default=1)
    lane_promotion.add_argument("--run-artifact", action="append", default=[])

    gate = sub.add_parser("requirements-gate", help="validate PR changed tests carry requirement markers")
    gate.add_argument("--input-dir", default=str(DEFAULT_INPUT_DIR))
    gate.add_argument("--changed-files", action="append", default=[])
    gate.add_argument("--changed-file-list")
    gate.add_argument("--exceptions")
    gate.add_argument("--fr-tracker")
    gate.add_argument("--output", required=True)
    gate.add_argument("--summary")
    gate.add_argument("--strict", action="store_true")

    pr_targets = sub.add_parser("pr-targets", help="derive PR-targeted test nodes from changed files")
    pr_targets.add_argument("--changed-file", action="append", default=[])
    pr_targets.add_argument("--changed-file-list")
    pr_targets.add_argument("--include-untestable", action="store_true")
    pr_targets.add_argument("--base", default=None, help="base ref for changelist diff")
    pr_targets.add_argument("--head", default="HEAD", help="head ref for changelist diff")
    pr_targets.add_argument("--output", required=True)

    run_pr = sub.add_parser("run-pr-lane", help="execute PR-targeted lane")
    run_pr.add_argument("--changed-file", action="append", default=[])
    run_pr.add_argument("--changed-file-list")
    run_pr.add_argument("--base", default=None, help="base ref for changelist diff")
    run_pr.add_argument("--head", default="HEAD", help="head ref for changelist diff")
    run_pr.add_argument("--lane", default="pr")
    run_pr.add_argument("--config", default="pytest-pr.ini")
    run_pr.add_argument("--output", required=True)
    run_pr.add_argument("--summary")
    run_pr.add_argument("--include-untestable", action="store_true")
    run_pr.add_argument("--maxfail", type=int, default=1)
    run_pr.add_argument("--strict", action="store_true")

    health = sub.add_parser("health", help="aggregate pytest artifacts into health summary")
    health.add_argument("--collect-artifact", required=False, default="artifacts/pytest/collect/pr-collect.json")
    health.add_argument(
        "--requirements-gate-artifact", required=False, default="artifacts/pytest/requirements/requirements-gate.json"
    )
    health.add_argument("--pr-run-artifact", required=False, default="artifacts/pytest/pr/run.json")
    health.add_argument(
        "--requirements-map-artifact", required=False, default="artifacts/pytest/traceability/requirements-map.json"
    )
    health.add_argument("--output", required=True)
    health.add_argument("--summary")
    health.add_argument("--strict", action="store_true")
    health.add_argument(
        "--fail-on-warning", action="store_true", help="exit non-zero when any warning alerts are present"
    )
    health.add_argument(
        "--min-health-score",
        type=int,
        default=None,
        help="exit non-zero when overall_health_score is below this threshold",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "collect":
        run_collect(
            marker_expr=args.marker_expr or args.marker,
            marker=args.marker,
            lane=args.lane,
            output=Path(args.output),
            strict=args.strict,
            marker_label=args.label,
            budget=args.budget,
            test_paths=args.test_path,
            summary_output=Path(args.summary) if args.summary else None,
        )
        return 0

    input_dir = Path(args.input_dir).resolve() if hasattr(args, "input_dir") else DEFAULT_INPUT_DIR
    records = scan_tests(input_dir)

    if args.command == "trace-scan":
        run_trace_scan(records, Path(args.output))
        return 0

    if args.command == "heavy-untagged":
        run_heavy_untagged(records, Path(args.output), args.min_loc)
        return 0

    if args.command == "requirements-map":
        req_ids = parse_fr_tracker(Path(args.fr_tracker) if args.fr_tracker else ROOT / "docs/reference/FR_TRACKER.md")
        run_requirements_map(
            records,
            Path(args.output),
            req_ids,
            Path(args.csv_output) if args.csv_output else None,
            summary=Path(args.summary) if args.summary else None,
            diagram_output=Path(args.diagram_output) if args.diagram_output else None,
            diagram_max_nodes=args.diagram_max_nodes,
        )
        return 0

    if args.command in ("requirements-diagram", "requirements-map-diagram"):
        payload = _safe_load_artifact(Path(args.requirements_map))
        if not isinstance(payload, dict):
            raise SystemExit(1)
        run_requirements_diagram(payload=payload, output=Path(args.output), max_nodes=args.max_nodes)
        return 0

    if args.command in ("trace-cleanup", "traceability-cleanup"):
        run_trace_cleanup(
            records=records,
            output=Path(args.output),
            summary=Path(args.summary) if args.summary else None,
            stale_window_days=args.stale_window_days,
            issue_output=Path(args.issue_output) if args.issue_output else None,
            issue_threshold=args.issue_threshold,
        )
        return 0

    if args.command == "requirements-promotion-criteria":
        run_requirements_promotion_criteria(
            requirements_map_artifact=Path(args.requirements_map) if args.requirements_map else None,
            requirements_gate_artifact=Path(args.requirements_gate) if args.requirements_gate else None,
            health_artifact=Path(args.health) if args.health else None,
            output=Path(args.output),
            min_runs=args.min_runs,
            min_coverage_ratio=args.min_coverage_ratio,
            max_flake_ratio=args.max_flake_ratio,
            acceptable_fail_budget=args.acceptable_fail_budget,
            run_artifacts=[Path(item) for item in args.run_artifact],
        )
        return 0

    if args.command == "lane-promotion":
        run_lane_promotion(
            LanePromotionConfig(
                output=Path(args.output),
                lane=args.lane,
                requirements_map_artifact=Path(args.requirements_map) if args.requirements_map else None,
                requirements_gate_artifact=Path(args.requirements_gate) if args.requirements_gate else None,
                health_artifact=Path(args.health) if args.health else None,
                run_artifacts=[Path(item) for item in args.run_artifact],
                min_runs=args.min_runs,
                min_coverage_ratio=args.min_coverage_ratio,
                max_flake_ratio=args.max_flake_ratio,
                acceptable_fail_budget=args.acceptable_fail_budget,
            )
        )
        return 0

    if args.command == "requirements-gate":
        fr_tracker = parse_fr_tracker(
            Path(args.fr_tracker) if args.fr_tracker else ROOT / "docs/reference/FR_TRACKER.md"
        )
        changed_list = Path(args.changed_file_list) if args.changed_file_list else None
        return run_requirements_gate(
            config=RequirementGateConfig(
                changed_files=args.changed_files,
                changed_file_list=changed_list,
                exceptions_path=Path(args.exceptions) if args.exceptions else None,
                input_dir=input_dir,
                output=Path(args.output),
                summary=Path(args.summary) if args.summary else None,
                strict=args.strict,
            ),
            fr_tracker=fr_tracker,
        )

    if args.command == "pr-targets":
        changed_files = args.changed_file
        changed_file_list = Path(args.changed_file_list) if args.changed_file_list else None
        if not changed_files:
            if changed_file_list is None:
                changed_files = [str(path) for path in _discover_changed_files(base_ref=args.base, head_ref=args.head)]
            else:
                changed_files = []

        payload = run_pr_targets(
            PrTargetConfig(
                changed_files=changed_files,
                changed_file_list=changed_file_list,
                output=Path(args.output),
                include_untestable=args.include_untestable,
            )
        )
        return 0 if payload else 1

    if args.command == "run-pr-lane":
        changed_files = args.changed_file
        if not changed_files:
            changed_files = [str(path) for path in _discover_changed_files(base_ref=args.base, head_ref=args.head)]

        return run_pr_lane(
            RunPrLaneConfig(
                changed_files=changed_files,
                changed_file_list=Path(args.changed_file_list) if args.changed_file_list else None,
                config=args.config,
                output=Path(args.output),
                summary=Path(args.summary) if args.summary else None,
                maxfail=args.maxfail,
                strict=args.strict,
                lane=args.lane,
                include_untestable=args.include_untestable,
            )
        )

    if args.command == "health":
        requirements_map_path = Path(args.requirements_map_artifact) if args.requirements_map_artifact else None
        return run_health(
            collect_artifact=Path(args.collect_artifact),
            requirements_gate_artifact=Path(args.requirements_gate_artifact),
            pr_run_artifact=Path(args.pr_run_artifact),
            requirements_map_artifact=requirements_map_path,
            output=Path(args.output),
            summary=Path(args.summary) if args.summary else None,
            strict=args.strict,
            fail_on_warning=args.fail_on_warning,
            min_health_score=args.min_health_score,
        )

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
