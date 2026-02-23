from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _to_artifact_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _safe_load_artifact(path: Path) -> dict[str, object]:
    if not path.exists():
        return {
            "status": "missing",
            "path": str(path),
            "error": "artifact_not_found",
            "timestamp": _now_iso(),
        }

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {
            "status": "invalid",
            "path": str(path),
            "error": f"invalid_json:{exc}",
            "timestamp": _now_iso(),
        }

    if not isinstance(payload, dict):
        return {
            "status": "invalid",
            "path": str(path),
            "error": "artifact_payload_not_object",
            "timestamp": _now_iso(),
        }

    return payload


def _int_or_zero(value: object) -> int:
    if isinstance(value, bool):
        return 1 if value else 0
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return 0


def _bool_or_false(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return False


def _build_health_alert(
    *,
    severity: str,
    code: str,
    title: str,
    details: str,
    artifact: str,
    action: str,
) -> dict[str, str]:
    return {
        "severity": severity,
        "code": code,
        "title": title,
        "details": details,
        "artifact": artifact,
        "recommended_action": action,
    }


def _derive_pr_targets(changed_files: list[Path], tests_dir: Path) -> tuple[list[Path], list[Path], bool]:
    if not changed_files:
        return [], [], True

    targets: set[Path] = set()
    untestable: set[Path] = set()
    has_unknown = False

    for changed in changed_files:
        path = changed
        if not path.exists():
            candidate = ROOT / path
            if candidate.exists():
                path = candidate
            else:
                has_unknown = True
                untestable.add(path)
                continue

        if path.suffix != ".py":
            has_unknown = True
            untestable.add(path)
            continue

        if "tests" in path.parts:
            if path.exists() and path.is_file():
                targets.add(path)
            else:
                has_unknown = True
                untestable.add(path)
            continue

        stem = path.stem
        mapped_for_file = False

        for candidate in sorted(tests_dir.glob(f"test_{stem}.py")):
            targets.add(candidate)
            mapped_for_file = True

        for candidate in sorted(tests_dir.glob(f"**/*test_{stem}*.py")):
            if candidate.is_file() and candidate.name.startswith("test_"):
                targets.add(candidate)
                mapped_for_file = True

        for candidate in sorted(tests_dir.glob(f"*{stem}*.py")):
            if not candidate.name.startswith("test_"):
                continue
            if candidate not in targets:
                targets.add(candidate)
                mapped_for_file = True

        if path.parent.as_posix() != ".":
            relative_parent = path.relative_to(ROOT / "src/thegent") if "src/thegent" in path.parts else path.parent
            related_dir = tests_dir / relative_parent
            if related_dir.is_dir():
                for candidate in sorted(related_dir.glob("test_*.py")):
                    targets.add(candidate)
                    mapped_for_file = True

        if not mapped_for_file:
            has_unknown = True
            untestable.add(path)

    normalized = {_to_artifact_path(candidate) for candidate in targets}
    normalized_untestable = {_to_artifact_path(candidate) for candidate in untestable}
    return (
        [Path(item) for item in sorted(normalized)],
        [Path(item) for item in sorted(normalized_untestable)],
        has_unknown,
    )


def run_health(
    *,
    collect_artifact: Path,
    requirements_gate_artifact: Path,
    pr_run_artifact: Path,
    requirements_map_artifact: Path | None,
    output: Path,
    summary: Path | None,
    strict: bool,
    fail_on_warning: bool = False,
    min_health_score: int | None = None,
) -> int:
    collect_payload = _safe_load_artifact(collect_artifact)
    requirements_gate_payload = _safe_load_artifact(requirements_gate_artifact)
    run_payload = _safe_load_artifact(pr_run_artifact)

    requirements_map_payload = (
        _safe_load_artifact(requirements_map_artifact) if requirements_map_artifact is not None else None
    )

    alerts: list[dict[str, str]] = []

    collect_status = str(collect_payload.get("status", collect_payload.get("returncode", "passed")))
    if collect_status == "missing" or collect_payload.get("status") == "missing":
        alerts.append(
            _build_health_alert(
                severity="error",
                code="collect.artifact_missing",
                title="Collection artifact missing",
                details=f"Missing file: {collect_artifact}",
                artifact=str(collect_artifact),
                action=("Run `task test:collect:fast-gate` (or `task test:pr-gate`) to regenerate collection output."),
            )
        )
    elif collect_status == "invalid" or collect_payload.get("status") == "invalid":
        alerts.append(
            _build_health_alert(
                severity="error",
                code="collect.artifact_invalid",
                title="Collection artifact invalid",
                details=f"Could not parse collect artifact: {collect_artifact}",
                artifact=str(collect_artifact),
                action="Re-run collection with `task test:collect:fast-gate` and verify writable artifacts directory.",
            )
        )
    else:
        returncode = _int_or_zero(collect_payload.get("returncode"))
        errors = _int_or_zero(collect_payload.get("errors"))
        if returncode != 0:
            alerts.append(
                _build_health_alert(
                    severity="error",
                    code="collect.returncode_nonzero",
                    title="Collection returned non-zero",
                    details=f"collect returncode={returncode}",
                    artifact=str(collect_artifact),
                    action="Fix pytest collection errors before merging or gate on legacy-only exceptions.",
                )
            )
        elif errors > 0:
            alerts.append(
                _build_health_alert(
                    severity="error",
                    code="collect.errors_detected",
                    title="Collection errors detected",
                    details=f"collect errors={errors}",
                    artifact=str(collect_artifact),
                    action="Address or quarantine collection failures with explicit skip markers.",
                )
            )

        if _bool_or_false(collect_payload.get("over_budget")):
            alerts.append(
                _build_health_alert(
                    severity="warning",
                    code="collect.budget_exceeded",
                    title="Collection exceeded budget",
                    details=f"collected={collect_payload.get('collected')}, budget={collect_payload.get('budget')}",
                    artifact=str(collect_artifact),
                    action="Review marker boundaries in `pyproject.toml` lane definitions.",
                )
            )

    req_status = str(requirements_gate_payload.get("status", "unknown"))
    if req_status == "missing" or requirements_gate_payload.get("status") == "missing":
        alerts.append(
            _build_health_alert(
                severity="warning",
                code="requirements.gate_missing",
                title="Requirements gate artifact missing",
                details=f"Missing file: {requirements_gate_artifact}",
                artifact=str(requirements_gate_artifact),
                action="Run `task test:requirements:gate` when evaluating PR changes.",
            )
        )
    elif req_status == "invalid" or requirements_gate_payload.get("status") == "invalid":
        alerts.append(
            _build_health_alert(
                severity="error",
                code="requirements.gate_invalid",
                title="Requirements gate artifact invalid",
                details=f"Could not parse file: {requirements_gate_artifact}",
                artifact=str(requirements_gate_artifact),
                action="Re-run `task test:requirements:gate` and verify JSON output path.",
            )
        )
    else:
        blocked_count = _int_or_zero(requirements_gate_payload.get("blocked_count"))
        fallback = _bool_or_false(requirements_gate_payload.get("fallback_to_fast_lane"))
        total_checked = _int_or_zero(requirements_gate_payload.get("total_checked"))
        if blocked_count > 0:
            alerts.append(
                _build_health_alert(
                    severity="warning",
                    code="requirements.missing_marker",
                    title="Unmapped changed tests",
                    details=f"blocked={blocked_count} (checked {total_checked})",
                    artifact=str(requirements_gate_artifact),
                    action=('Add `@pytest.mark.requirement("FR-...")` annotations or add an explicit exemption entry.'),
                )
            )
        if fallback:
            alerts.append(
                _build_health_alert(
                    severity="warning",
                    code="requirements.fallback_to_fast_lane",
                    title="Fallback lane used",
                    details="No changelist mapping or non-test changes detected.",
                    artifact=str(requirements_gate_artifact),
                    action=(
                        "Review changed-file mapping; ensure changed files include test entry points or add mapping guidance."
                    ),
                )
            )

    run_status = str(run_payload.get("status", "unknown"))
    if run_status == "missing" or run_payload.get("status") == "missing":
        alerts.append(
            _build_health_alert(
                severity="warning",
                code="run.artifact_missing",
                title="PR run artifact missing",
                details=f"Missing file: {pr_run_artifact}",
                artifact=str(pr_run_artifact),
                action="Run `task test:pr` or `task test:pr-gate` to execute and write run summary.",
            )
        )
    elif run_status == "invalid" or run_payload.get("status") == "invalid":
        alerts.append(
            _build_health_alert(
                severity="error",
                code="run.artifact_invalid",
                title="PR run artifact invalid",
                details=f"Could not parse file: {pr_run_artifact}",
                artifact=str(pr_run_artifact),
                action="Re-run PR gate task with a writable artifacts path.",
            )
        )
    else:
        if run_payload.get("returncode", 0) not in (0, "0", None):
            alerts.append(
                _build_health_alert(
                    severity="error",
                    code="run.failed",
                    title="Mapped PR run failed",
                    details=f"status={run_status}, returncode={run_payload.get('returncode')}",
                    artifact=str(pr_run_artifact),
                    action="Re-run with `task test:pr`, fix failing tests, then rerun gate.",
                )
            )

        if _bool_or_false(run_payload.get("fallback_to_fast_lane")):
            alerts.append(
                _build_health_alert(
                    severity="info",
                    code="run.fallback_to_fast_lane",
                    title="Mapped run used fast-lane fallback",
                    details="No PR targets were resolvable for mapped execution.",
                    artifact=str(pr_run_artifact),
                    action=("Review file mapping and add stable test targets for changed paths under `tests/`."),
                )
            )

    if requirements_map_payload is None:
        alerts.append(
            _build_health_alert(
                severity="info",
                code="requirements_map.missing_input",
                title="Requirements map not included",
                details="No requirements map artifact supplied.",
                artifact="",
                action="Run `task test:requirements:map` to add coverage trend context.",
            )
        )
    elif requirements_map_payload.get("status") in {"missing", "invalid"}:
        alerts.append(
            _build_health_alert(
                severity="warning",
                code="requirements_map.invalid",
                title="Requirements coverage artifact invalid",
                details=f"Could not parse map file: {requirements_map_artifact}",
                artifact=str(requirements_map_artifact),
                action="Re-run `task test:requirements:map` and verify marker annotations in tests.",
            )
        )
    else:
        coverage = requirements_map_payload.get("requirement_coverage", {})
        coverage_ratio = coverage.get("coverage_ratio")
        if isinstance(coverage_ratio, int | float) and coverage_ratio < 0.95:
            alerts.append(
                _build_health_alert(
                    severity="warning",
                    code="requirements_map.low_coverage",
                    title="Requirement coverage below target",
                    details=f"coverage_ratio={coverage_ratio}",
                    artifact=str(requirements_map_artifact),
                    action=("Add missing `@pytest.mark.requirement(...)` markers or justify exclusions."),
                )
            )

    score = 100
    for alert in alerts:
        if alert["severity"] == "error":
            score -= 30
        elif alert["severity"] == "warning":
            score -= 10
        else:
            score -= 3
    score = max(0, min(100, score))

    has_error = any(alert["severity"] == "error" for alert in alerts)
    has_warning = any(alert["severity"] == "warning" for alert in alerts)
    overall_status = "failed" if has_error else "warn" if has_warning else "passed"

    payload = {
        "schema_version": "pytest-health/v1",
        "timestamp": _now_iso(),
        "overall_status": overall_status,
        "overall_health_score": score,
        "collect": collect_payload,
        "requirements_gate": requirements_gate_payload,
        "pr_run": run_payload,
        "requirements_map": requirements_map_payload,
        "alerts": alerts,
        "artifact_inputs": {
            "collect": str(collect_artifact),
            "requirements_gate": str(requirements_gate_artifact),
            "pr_run": str(pr_run_artifact),
            "requirements_map": str(requirements_map_artifact) if requirements_map_artifact is not None else None,
        },
        "runbook": {
            "collection_error_threshold": 0,
            "requirement_gate_blocked_error_threshold": 1,
            "requirement_map_coverage_target": 0.95,
            "status_threshold": {
                "passed": ">=90",
                "warn": "80-89",
                "failed": "<80",
            },
            "min_health_score": min_health_score,
            "fail_on_warning": fail_on_warning,
        },
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    if summary:
        lines = [
            "# Pytest Health Summary",
            "",
            f"- Overall status: `{overall_status}`",
            f"- Health score: `{score}`",
            f"- Alerts: `{len(alerts)}`",
            "",
            "## Alert surface",
        ]

        for alert in alerts:
            lines.extend(
                [
                    f"### {alert['severity'].upper()}: `{alert['code']}`",
                    f"- title: {alert['title']}",
                    f"- details: {alert['details']}",
                    f"- artifact: `{alert['artifact']}`",
                    f"- action: {alert['recommended_action']}",
                    "",
                ]
            )

        summary.write_text("\n".join(lines) + "\n", encoding="utf-8")

    if strict and has_error:
        return 1

    if fail_on_warning and has_warning:
        return 1

    if min_health_score is not None and score < min_health_score:
        return 1

    return 0


def _discover_changed_files(*, base_ref: str | None, head_ref: str = "HEAD") -> list[Path]:
    if base_ref is None:
        base_ref = os.environ.get("PR_BASE_REF") or os.environ.get("GITHUB_BASE_REF")

    if base_ref:
        try:
            merge_base = subprocess.check_output(
                ["git", "-C", str(ROOT), "merge-base", base_ref, head_ref],
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
        except subprocess.CalledProcessError:
            merge_base = f"{base_ref}...{head_ref}"

        try:
            raw_paths = subprocess.check_output(
                ["git", "-C", str(ROOT), "diff", "--name-only", merge_base, head_ref],
                text=True,
            ).splitlines()
            return [Path(path) for path in raw_paths if path.strip()]
        except subprocess.CalledProcessError:
            pass

    try:
        staged = subprocess.check_output(
            ["git", "-C", str(ROOT), "diff", "--name-only", "HEAD"],
            text=True,
        ).splitlines()
        if staged:
            return [Path(path) for path in staged if path.strip()]
    except subprocess.CalledProcessError:
        pass

    try:
        return [
            Path(path)
            for path in subprocess.check_output(
                ["git", "-C", str(ROOT), "ls-files", "--other", "--exclude-standard"],
                text=True,
            ).splitlines()
            if path.strip()
        ]
    except subprocess.CalledProcessError:
        return []
