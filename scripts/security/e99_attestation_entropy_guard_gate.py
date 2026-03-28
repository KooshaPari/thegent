#!/usr/bin/env python3
import argparse
import csv
import json
import pathlib
import sys


def _load_rows(path: pathlib.Path) -> tuple[list[dict], str | None]:
    try:
        if path.suffix.lower() == ".csv":
            return list(csv.DictReader(path.open())), None
        data = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        return [], f"E99 invalid input: {exc}"

    if isinstance(data, list):
        return data, None
    if isinstance(data, dict):
        for key in ("attestations", "entropy", "items", "reports", "records", "rows"):
            rows = data.get(key)
            if isinstance(rows, list):
                return rows, None
    return (
        [],
        "E99 invalid input: expected list or dict with "
        "attestations/entropy/items/reports/records/rows",
    )


def _pick(row: dict, keys: tuple[str, ...]) -> str:
    for key in keys:
        value = row.get(key)
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return ""


def _parse_float(value: object) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return float(text)
    except (TypeError, ValueError):
        return None


def _entropy_low(row: dict, min_entropy_bits: float) -> bool:
    status = str(row.get("status", "")).strip().lower()
    if status in {"failed", "invalid", "revoked", "expired", "breached"}:
        return True
    if bool(
        row.get("entropy_breach")
        or row.get("entropy_guard_trigger")
        or row.get("low_entropy")
        or row.get("entropy_anomaly")
    ):
        return True

    entropy = _parse_float(
        row.get("entropy_bits")
        or row.get("entropy")
        or row.get("confidence")
        or row.get("attestation_entropy")
    )
    return entropy is not None and entropy < min_entropy_bits


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attestations", required=True)
    parser.add_argument("--min-entropy-bits", type=float, default=3.5)
    parser.add_argument("--max-entropy-breaches", type=int, default=0)
    args = parser.parse_args()

    rows, err = _load_rows(pathlib.Path(args.attestations))
    if err:
        print(err, file=sys.stderr)
        return 2

    breaches = sorted(
        {
            _pick(r, ("id", "attestation_id", "name", "artifact_id"))
            for r in rows
            if _entropy_low(r, args.min_entropy_bits)
        }
    )
    if len(breaches) > args.max_entropy_breaches:
        print(
            f"E99 attestation entropy guard breach: count={len(breaches)} "
            f"max={args.max_entropy_breaches} min_entropy_bits={args.min_entropy_bits}",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
