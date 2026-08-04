"""Durable local JSONL persistence for validated ForgeEval results."""

from __future__ import annotations

import json
import os
from pathlib import Path

from pydantic import ValidationError

from thegent.forge_eval.contracts import ForgeEvalResult


class ResultStoreError(ValueError):
    """Raised when persisted ForgeEval result evidence is invalid or ambiguous."""


class ForgeEvalResultStore:
    """Append and read newline-delimited, validated evaluation observations."""

    def __init__(self, path: Path) -> None:
        self._path = path

    @property
    def path(self) -> Path:
        """Return the local JSONL evidence path."""
        return self._path

    def append(self, result: ForgeEvalResult) -> None:
        """Durably append one non-duplicate result after validating stored history."""
        if any(existing.run_id == result.run_id for existing in self.read_all()):
            raise ResultStoreError(f"run_id {result.run_id!r} already exists in {self._path}")
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = result.model_dump_json() + "\n"
        with self._path.open("a", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())

    def read_all(self) -> tuple[ForgeEvalResult, ...]:
        """Read and validate every persisted local result in deterministic order."""
        if not self._path.exists():
            return ()
        records: list[ForgeEvalResult] = []
        for line_number, line in enumerate(self._path.read_text(encoding="utf-8").splitlines(), start=1):
            if line.strip():
                records.append(self._parse_line(line, line_number))
        return tuple(records)

    def _parse_line(self, line: str, line_number: int) -> ForgeEvalResult:
        try:
            return ForgeEvalResult.model_validate(json.loads(line))
        except (json.JSONDecodeError, ValidationError) as exc:
            raise ResultStoreError(f"invalid result at {self._path}:{line_number}: {exc}") from exc
