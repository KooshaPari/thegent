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
        return [], f"E77 invalid input: {exc}"

    if isinstance(data, list):
        return data, None
    if isinstance(data, dict):
        for key in ("attestations", "events", "rows", "items"):
            rows = data.get(key)
            if isinstance(rows, list):
                return rows, None
    return [], "E77 invalid input: expected list or dict with attestations/events/rows/items"


def _pick(row: dict, keys: tuple[str, ...]) -> str:
    for key in keys:
        value = row.get(key)
        if value is None or str(value).strip() == "":
            continue
        return str(value).strip()
    return ""


def _bool(v: object) -> bool:
    if isinstance(v, bool):
        return v
    return str(v).strip().lower() in {"1", "true", "yes", "on", "y"}


def _is_inconsistent(row: dict) -> bool:
    if _bool(
        row.get("replay_inconsistent")
        or row.get("replay_inconsistency")
        or row.get("consistency_broken")
    ):
        return True

    replayed = _bool(row.get("replay") or row.get("is_replay") or row.get("replayed"))
    if replayed and not _pick(row, ("replay_reference", "replay_reference_id", "replayed_from")):
        return True

    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attestations", required=True)
    parser.add_argument("--max-inconsistencies", type=int, default=0)
    parser.add_argument("--max-replays", type=int, default=0)
    args = parser.parse_args()

    rows, err = _load_rows(pathlib.Path(args.attestations))
    if err:
        print(err, file=sys.stderr)
        return 2

    seen: dict[str, tuple[str, str]] = {}
    bad = set()

    for row in rows:
        if _is_inconsistent(row):
            bad.add(_pick(row, ("attestation_id", "id", "event_id", "name")))
            continue

        key = _pick(row, ("attestation_id", "id", "event_id"))
        if not key:
            continue

        fingerprint = (
            _pick(row, ("signature", "attestation_signature", "digest", "hash")),
            _pick(row, ("replay_nonce", "replay_reference", "replay_sequence")),
        )

        previous = seen.get(key)
        if previous is None:
            seen[key] = fingerprint
        elif previous != fingerprint:
            bad.add(key)

    replays = [s for s in seen if _bool(next((r for r in rows if _pick(r, ("attestation_id", "id", "event_id")) == s), {}).get("replay"))]
    if len(replays) > args.max_replays:
        print(f"E77 attestation replay inconsistency breach (replays): {len(replays)}", file=sys.stderr)
        return 2

    if len(bad) > args.max_inconsistencies:
        offenders = sorted(bad)
        print(f"E77 attestation replay consistency breach: {len(offenders)}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
