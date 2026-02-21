"""Logical stream: Benchmark suites and result persistence."""

from collections import OrderedDict
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

console = Console()
app = typer.Typer(help="Run benchmark suites and persist result rows.")


def _normalize_output_format(raw: str) -> str:
    normalized = raw.strip().lower()
    if normalized in {"json", "rich", "table"}:
        return "rich" if normalized == "table" else normalized
    raise ValueError(f"Unsupported output format '{raw}'. Use one of: rich, json.")


def _normalize_harness_key(raw: str) -> str:
    return raw.strip().lower()


@app.command("run", help="Run one benchmark suite and append one result row.")
def bench_run(
    suite: str = typer.Option("smoke", "--suite", help="Benchmark suite ID (smoke, code-gen, file-ops, multi-step, tool-use)"),
    harness: str = typer.Option("codex", "--harness", help="Harness/provider label for the recorded row"),
    test_id: str | None = typer.Option(None, "--test", help="Optional benchmark test ID for the run"),
    run_id: str | None = typer.Option(None, "--run-id", help="Optional explicit run ID for persisted row"),
    results_path: Path | None = typer.Option(None, "--results-path", help="Override path for benchmark JSONL output"),
    output_format: str = typer.Option("rich", "--output-format", "-o", help="Output format: rich|json"),
) -> None:
    from thegent.bench import append_bench_record, run_suite

    try:
        normalized_output = _normalize_output_format(output_format)
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc

    try:
        record = run_suite(suite=suite, harness=harness, run_id=run_id, test_id=test_id)
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc

    persisted = append_bench_record(record, path=results_path)
    payload = record.to_dict()
    payload["results_path"] = str(persisted)

    if normalized_output == "json":
        console.print_json(data=payload)
        return

    console.print(
        f"[green]Persisted benchmark row[/green] suite={payload['suite']} test={payload['test_id']} "
        f"run_id={payload['run_id']} path={persisted}"
    )


@app.command("compare", help="Compare latest persisted benchmark rows for two harnesses.")
def bench_compare(
    suite: str = typer.Option("smoke", "--suite", help="Benchmark suite ID"),
    test_id: str | None = typer.Option(None, "--test-id", help="Optional benchmark test ID filter"),
    baseline_harness: str | None = typer.Option(None, "--baseline-harness", help="Baseline harness label"),
    candidate_harness: str | None = typer.Option(None, "--candidate-harness", help="Candidate harness label"),
    results_path: Path | None = typer.Option(None, "--results-path", help="Override path for benchmark JSONL output"),
    output_format: str = typer.Option("rich", "--output-format", "-o", help="Output format: rich|json"),
) -> None:
    from thegent.bench import load_bench_records

    try:
        normalized_output = _normalize_output_format(output_format)
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc

    records = load_bench_records(path=results_path)
    normalized_suite = (suite or "").strip().lower()
    filtered = [row for row in records if row.suite == normalized_suite]
    if test_id:
        filtered = [row for row in filtered if row.test_id == test_id]

    latest_by_harness: dict[str, Any] = OrderedDict()
    for row in reversed(filtered):
        harness_key = _normalize_harness_key(row.harness)
        if harness_key and harness_key not in latest_by_harness:
            latest_by_harness[harness_key] = row

    normalized_baseline = _normalize_harness_key(baseline_harness) if baseline_harness else None
    normalized_candidate = _normalize_harness_key(candidate_harness) if candidate_harness else None
    if (normalized_baseline and not normalized_candidate) or (normalized_candidate and not normalized_baseline):
        console.print("[red]Provide both --baseline-harness and --candidate-harness together.[/red]")
        raise typer.Exit(1)
    if normalized_baseline and normalized_candidate:
        if normalized_baseline == normalized_candidate:
            console.print("[red]Baseline and candidate harness must be different.[/red]")
            raise typer.Exit(1)
        baseline_harness_key = normalized_baseline
        candidate_harness_key = normalized_candidate
    else:
        # Auto-detect if not specified
        harnesses_keys = list(latest_by_harness.keys())
        if len(harnesses_keys) < 2:
            console.print("[red]Need at least two harness results to compare.[/red]")
            raise typer.Exit(1)
        baseline_harness_key = harnesses_keys[1]
        candidate_harness_key = harnesses_keys[0]

    baseline = latest_by_harness.get(baseline_harness_key)
    candidate = latest_by_harness.get(candidate_harness_key)
    if baseline is None or candidate is None:
        missing = baseline_harness_key if baseline is None else candidate_harness_key
        console.print(f"[red]No persisted benchmark row for harness '{missing}' in selected filter.[/red]")
        raise typer.Exit(1)

    delta_sec = candidate.latency_sec - baseline.latency_sec
    pct_delta = (delta_sec / baseline.latency_sec) * 100.0 if baseline.latency_sec > 0 else 0.0
    if delta_sec < 0:
        winner_harness = candidate.harness
        winner_reason = "lower_latency"
    elif delta_sec > 0:
        winner_harness = baseline.harness
        winner_reason = "lower_latency"
    else:
        winner_harness = "tie"
        winner_reason = "equal_latency"
    payload = {
        "suite": normalized_suite,
        "test_id": test_id or candidate.test_id,
        "baseline_harness": baseline.harness,
        "candidate_harness": candidate.harness,
        "baseline_latency_sec": round(baseline.latency_sec, 6),
        "candidate_latency_sec": round(candidate.latency_sec, 6),
        "latency_delta_sec": round(delta_sec, 6),
        "latency_delta_pct": round(pct_delta, 2),
        "baseline_tokens_input": baseline.tokens_input,
        "candidate_tokens_input": candidate.tokens_input,
        "baseline_tokens_output": baseline.tokens_output,
        "candidate_tokens_output": candidate.tokens_output,
        "baseline_tool_calls": baseline.tool_calls,
        "candidate_tool_calls": candidate.tool_calls,
        "baseline_success": baseline.success,
        "candidate_success": candidate.success,
        "baseline_run_id": baseline.run_id,
        "candidate_run_id": candidate.run_id,
        "winner_harness": winner_harness,
        "winner_reason": winner_reason,
        "winner_margin_sec": round(abs(delta_sec), 6),
        "winner_margin_pct": round(abs(pct_delta), 2),
    }

    if normalized_output == "json":
        console.print_json(data=payload)
        return

    table = Table(title="Benchmark Compare")
    table.add_column("Metric", style="cyan")
    table.add_column(payload["baseline_harness"], justify="right")
    table.add_column(payload["candidate_harness"], justify="right")
    table.add_column("Delta", justify="right")
    table.add_row(
        "Latency (sec)",
        f"{payload['baseline_latency_sec']:.6f}",
        f"{payload['candidate_latency_sec']:.6f}",
        f"{payload['latency_delta_sec']:+.6f} ({payload['latency_delta_pct']:+.2f}%)",
    )
    table.add_row("Tokens Input", str(payload["baseline_tokens_input"]), str(payload["candidate_tokens_input"]), "n/a")
    table.add_row("Tokens Output", str(payload["baseline_tokens_output"]), str(payload["candidate_tokens_output"]), "n/a")
    table.add_row("Tool Calls", str(payload["baseline_tool_calls"]), str(payload["candidate_tool_calls"]), "n/a")
    table.add_row("Success", str(payload["baseline_success"]), str(payload["candidate_success"]), "n/a")
    table.add_row("Run ID", payload["baseline_run_id"], payload["candidate_run_id"], "n/a")
    table.add_row("Winner", payload["winner_harness"], "", payload["winner_reason"])
    table.add_row(
        "Winner Margin",
        "",
        "",
        f"{payload['winner_margin_sec']:.6f} sec ({payload['winner_margin_pct']:.2f}%)",
    )
    console.print(table)
