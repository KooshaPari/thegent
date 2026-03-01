"""WL-115 benchmark record model."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from thegent.integrations.base import SerializableMixin


@dataclass(frozen=True)
class BenchRecord(SerializableMixin):
    """Canonical JSONL row for benchmark runs."""

    suite: str
    harness: str
    test_id: str
    latency_sec: float
    tokens_input: int
    tokens_output: int
    tool_calls: int
    success: bool
    error_recovery_attempts: int
    run_id: str
    ts_utc: str

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> BenchRecord:
        """Hydrate a benchmark row from a JSON payload."""
        required = {
            "suite",
            "harness",
            "test_id",
            "latency_sec",
            "tokens_input",
            "tokens_output",
            "tool_calls",
            "success",
            "error_recovery_attempts",
            "run_id",
            "ts_utc",
        }
        missing = sorted(required.difference(payload))
        if missing:
            raise ValueError(f"Missing benchmark fields: {', '.join(missing)}")
        return cls(
            suite=str(payload["suite"]),
            harness=str(payload["harness"]),
            test_id=str(payload["test_id"]),
            latency_sec=float(payload["latency_sec"]),
            tokens_input=int(payload["tokens_input"]),
            tokens_output=int(payload["tokens_output"]),
            tool_calls=int(payload["tool_calls"]),
            success=bool(payload["success"]),
            error_recovery_attempts=int(payload["error_recovery_attempts"]),
            run_id=str(payload["run_id"]),
            ts_utc=str(payload["ts_utc"]),
        )

    @classmethod
    def new(
        cls,
        *,
        suite: str,
        harness: str,
        test_id: str,
        latency_sec: float,
        tokens_input: int,
        tokens_output: int,
        tool_calls: int,
        success: bool,
        error_recovery_attempts: int,
        run_id: str,
        ts_utc: str | None = None,
    ) -> BenchRecord:
        """Construct a record, stamping timestamp when absent."""
        stamp = ts_utc or datetime.now(UTC).isoformat()
        return cls(
            suite=suite,
            harness=harness,
            test_id=test_id,
            latency_sec=latency_sec,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            tool_calls=tool_calls,
            success=success,
            error_recovery_attempts=error_recovery_attempts,
            run_id=run_id,
            ts_utc=stamp,
        )
