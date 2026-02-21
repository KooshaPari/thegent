"""Writers for health report/gate export payloads."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Callable

import typer

from . import health_serializers

_VALID_FORMATS = {"json", "md", "csv", "jsonl"}


def _normalize_format(export_format: str) -> str:
    normalized = export_format.lower().strip()
    if normalized not in _VALID_FORMATS:
        raise typer.BadParameter(f"Unsupported --export-format '{export_format}'. Choose one of: json, md, csv, jsonl.")
    return normalized


def _prepare_output_path(output: Path, overwrite: bool) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and output.is_dir():
        raise typer.BadParameter(f"Output path is a directory: {output}")
    if output.exists() and not overwrite:
        raise typer.BadParameter(f"Output path already exists: {output} (use --overwrite to replace it)")


def _atomic_write(output: Path, payload: str) -> None:
    tmp_path = output.parent / f".{output.name}.{os.getpid()}.{int(time.time() * 1e6)}.tmp"
    try:
        tmp_path.write_text(payload, encoding="utf-8")
        tmp_path.replace(output)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


def write_report_export(
    output: Path,
    report: dict[str, Any],
    export_format: str,
    overwrite: bool = False,
) -> str:
    fmt = _normalize_format(export_format)
    _prepare_output_path(output, overwrite=overwrite)
    if fmt == "md":
        payload = health_serializers.serialize_health_report_md(report)
    elif fmt == "csv":
        payload = health_serializers.serialize_health_report_csv(report)
    elif fmt == "jsonl":
        payload = health_serializers.serialize_health_report_jsonl(report)
    else:
        payload = json.dumps(report, indent=2, sort_keys=True)
    _atomic_write(output, payload)
    return fmt


def write_health_gate_export(
    output: Path,
    report: dict[str, Any],
    export_format: str,
    overwrite: bool = False,
) -> str:
    fmt = _normalize_format(export_format)
    _prepare_output_path(output, overwrite=overwrite)
    if fmt == "md":
        payload = health_serializers.serialize_health_gate_md(report)
    elif fmt == "csv":
        payload = health_serializers.serialize_health_gate_csv(report)
    elif fmt == "jsonl":
        payload = health_serializers.serialize_health_gate_jsonl(report)
    else:
        payload = json.dumps(report, indent=2, sort_keys=True)
    _atomic_write(output, payload)
    return fmt


def write_health_trend_export(
    output: Path,
    result: dict[str, Any],
    export_format: str,
    overwrite: bool = False,
    print_error: Callable[[str], None] | None = None,
) -> str:
    normalized = export_format.lower().strip()
    if normalized not in _VALID_FORMATS:
        if print_error is not None:
            print_error(
                f"[red]Unsupported --export-format '{export_format}'. Choose one of: json, md, csv, jsonl.[/red]"
            )
        raise typer.Exit(1)

    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and output.is_dir():
        if print_error is not None:
            print_error(f"[red]Output path is a directory: {output}[/red]")
        raise typer.Exit(1)
    if output.exists() and not overwrite:
        if print_error is not None:
            print_error(f"[red]Output path already exists: {output} (use --overwrite to replace it)[/red]")
        raise typer.Exit(1)

    if normalized == "md":
        payload = health_serializers.serialize_health_trend_md(result)
    elif normalized == "csv":
        payload = health_serializers.serialize_health_trend_csv(result)
    elif normalized == "jsonl":
        payload = health_serializers.serialize_health_trend_jsonl(result)
    else:
        payload = json.dumps(result, indent=2, sort_keys=True)
    _atomic_write(output, payload)
    return normalized
