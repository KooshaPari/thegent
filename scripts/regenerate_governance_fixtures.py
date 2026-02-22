#!/usr/bin/env python3
"""Deterministically regenerate governance fixture metadata with version bump policy."""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
from pathlib import Path


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _append_bump_entry(doc: dict, note: str) -> dict:
    out = copy.deepcopy(doc)
    old_version = int(out["schema_version"])
    new_version = old_version + 1
    out["schema_version"] = new_version
    out.setdefault("changelog", [])
    out["changelog"].append(
        {
            "version": new_version,
            "date": dt.date.today().isoformat(),
            "note": note,
        }
    )
    return out


def _normalize_snapshot(snapshot: dict) -> dict:
    out = copy.deepcopy(snapshot)
    out["cases"] = sorted(out.get("cases", []), key=lambda c: c.get("input", ""))
    return out


def _normalize_manifest(manifest: dict) -> dict:
    out = copy.deepcopy(manifest)
    out["cases"] = sorted(out.get("cases", []), key=lambda c: c.get("file", ""))
    return out


def _compute_digest_manifest(root: Path, digests: dict) -> dict:
    out = copy.deepcopy(digests)
    files = sorted(
        [p.relative_to(root).as_posix() for p in (root / "replay").glob("*.jsonl")]
        + ["spiral_selector_contract_snapshot.json", "spiral_trend_replay_manifest.json"]
    )
    entries = [{"path": rel, "sha256": _sha256_file(root / rel)} for rel in files]
    out["files"] = entries
    lines = [f"{entry['path']}:{entry['sha256']}" for entry in entries]
    out["signed_digest"] = hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()
    return out


def _check_or_bump(
    old_doc: dict,
    new_doc: dict,
    *,
    allow_bump: bool,
    bump_note: str | None,
    label: str,
) -> tuple[dict, bool]:
    if old_doc == new_doc:
        return old_doc, False
    if not allow_bump:
        raise SystemExit(
            f"{label}: deterministic regeneration would change contents. "
            "Re-run with --bump-version and --note to record schema change."
        )
    if not bump_note:
        raise SystemExit(f"{label}: --bump-version requires --note")
    return _append_bump_entry(new_doc, bump_note), True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Regenerate governance fixtures deterministically.")
    parser.add_argument("--root", default="tests/fixtures/governance", help="Governance fixtures root")
    parser.add_argument("--check", action="store_true", help="Only verify; do not write")
    parser.add_argument("--bump-version", action="store_true", help="Allow schema/changelog bump when changes occur")
    parser.add_argument("--note", help="Changelog note to use when bumping schema version")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root)

    snapshot_path = root / "spiral_selector_contract_snapshot.json"
    manifest_path = root / "spiral_trend_replay_manifest.json"
    digests_path = root / "fixture_digests.json"

    snapshot_old = _read_json(snapshot_path)
    manifest_old = _read_json(manifest_path)
    digests_old = _read_json(digests_path)

    snapshot_new = _normalize_snapshot(snapshot_old)
    manifest_new = _normalize_manifest(manifest_old)

    snapshot_final, snapshot_changed = _check_or_bump(
        snapshot_old,
        snapshot_new,
        allow_bump=args.bump_version,
        bump_note=args.note,
        label=snapshot_path.name,
    )
    manifest_final, manifest_changed = _check_or_bump(
        manifest_old,
        manifest_new,
        allow_bump=args.bump_version,
        bump_note=args.note,
        label=manifest_path.name,
    )

    # Digests depend on snapshot/manifest bytes; compute after normalization/bump decisions.
    if not args.check:
        if snapshot_changed:
            _write_json(snapshot_path, snapshot_final)
        if manifest_changed:
            _write_json(manifest_path, manifest_final)
    else:
        # In check mode we still need to compare against hypothetical canonical forms.
        pass

    # Re-read persisted-or-original canonical docs when check mode is active.
    if args.check:
        snapshot_bytes_doc = snapshot_final
        manifest_bytes_doc = manifest_final
        # materialize to temp-hash inputs via JSON encoding parity
        temp_snapshot = root / ".tmp.snapshot.canonical.json"
        temp_manifest = root / ".tmp.manifest.canonical.json"
        try:
            _write_json(temp_snapshot, snapshot_bytes_doc)
            _write_json(temp_manifest, manifest_bytes_doc)
            snapshot_hash = _sha256_file(temp_snapshot)
            manifest_hash = _sha256_file(temp_manifest)
        finally:
            temp_snapshot.unlink(missing_ok=True)
            temp_manifest.unlink(missing_ok=True)
        digests_base = copy.deepcopy(digests_old)
        # inject canonical hashes for dependent files
        digest_map = {entry["path"]: entry["sha256"] for entry in digests_base.get("files", [])}
        digest_map["spiral_selector_contract_snapshot.json"] = snapshot_hash
        digest_map["spiral_trend_replay_manifest.json"] = manifest_hash
        # replace using live replay file hashes
        replay_entries = []
        for p in sorted((root / "replay").glob("*.jsonl")):
            replay_entries.append({"path": p.relative_to(root).as_posix(), "sha256": _sha256_file(p)})
        files = replay_entries + [
            {"path": "spiral_selector_contract_snapshot.json", "sha256": snapshot_hash},
            {"path": "spiral_trend_replay_manifest.json", "sha256": manifest_hash},
        ]
        digests_new = copy.deepcopy(digests_base)
        digests_new["files"] = files
        lines = [f"{entry['path']}:{entry['sha256']}" for entry in files]
        digests_new["signed_digest"] = hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()
    else:
        digests_new = _compute_digest_manifest(root, digests_old)

    digests_final, digests_changed = _check_or_bump(
        digests_old,
        digests_new,
        allow_bump=args.bump_version,
        bump_note=args.note,
        label=digests_path.name,
    )

    if args.check:
        if snapshot_changed or manifest_changed or digests_changed:
            raise SystemExit(
                "Governance fixture regeneration check failed: run "
                '`uv run python scripts/regenerate_governance_fixtures.py --bump-version --note "..."`'
            )
        print("governance fixtures are canonical")
        return 0

    if snapshot_changed:
        _write_json(snapshot_path, snapshot_final)
    if manifest_changed:
        _write_json(manifest_path, manifest_final)
    if digests_changed:
        _write_json(digests_path, digests_final)

    print(
        "governance fixtures regenerated "
        f"(snapshot_changed={snapshot_changed}, manifest_changed={manifest_changed}, digests_changed={digests_changed})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
