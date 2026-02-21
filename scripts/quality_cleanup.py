#!/usr/bin/env python3
"""Cleanup helper for quality-run disk/IO control.

Removes stale `.shadow-*` directories and old `.quality/logs` files.
"""

from __future__ import annotations

import argparse
import shutil
import time
from pathlib import Path


def _is_older_than(path: Path, cutoff_ts: float) -> bool:
    try:
        return path.stat().st_mtime < cutoff_ts
    except OSError:
        return False


def _cleanup_shadow_dirs(root: Path, max_age_hours: int, dry_run: bool) -> tuple[int, int]:
    parent = root.parent
    cutoff = time.time() - (max_age_hours * 3600)
    removed = 0
    bytes_freed = 0

    for entry in parent.iterdir():
        if not entry.is_dir() or not entry.name.startswith(".shadow-"):
            continue
        if not _is_older_than(entry, cutoff):
            continue

        size = 0
        try:
            for p in entry.rglob("*"):
                if p.is_file():
                    size += p.stat().st_size
        except OSError:
            pass

        if dry_run:
            print(f"DRY-RUN shadow prune: {entry}")
        else:
            shutil.rmtree(entry)
            print(f"Removed shadow dir: {entry}")
        removed += 1
        bytes_freed += size

    return removed, bytes_freed


def _cleanup_quality_logs(root: Path, max_age_days: int, dry_run: bool) -> tuple[int, int]:
    logs_dir = root / ".quality" / "logs"
    if not logs_dir.exists():
        return 0, 0

    cutoff = time.time() - (max_age_days * 86400)
    removed = 0
    bytes_freed = 0

    for p in logs_dir.rglob("*"):
        if not p.is_file():
            continue
        if not _is_older_than(p, cutoff):
            continue
        try:
            size = p.stat().st_size
        except OSError:
            size = 0
        if dry_run:
            print(f"DRY-RUN log prune: {p}")
        else:
            p.unlink(missing_ok=True)
            print(f"Removed quality log: {p}")
        removed += 1
        bytes_freed += size

    if not dry_run:
        # Remove now-empty directories under .quality/logs
        for d in sorted(logs_dir.rglob("*"), reverse=True):
            if d.is_dir():
                try:
                    d.rmdir()
                except OSError:
                    pass

    return removed, bytes_freed


def main() -> int:
    parser = argparse.ArgumentParser(description="Cleanup stale shadow dirs and quality logs.")
    parser.add_argument("--root", default=".", help="Project root (default: current directory)")
    parser.add_argument(
        "--shadow-max-age-hours",
        type=int,
        default=24,
        help="Remove .shadow-* dirs older than this many hours (default: 24)",
    )
    parser.add_argument(
        "--log-max-age-days",
        type=int,
        default=7,
        help="Remove .quality/logs files older than this many days (default: 7)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show planned removals without deleting")
    args = parser.parse_args()

    if args.shadow_max_age_hours < 1:
        raise SystemExit("--shadow-max-age-hours must be >= 1")
    if args.log_max_age_days < 1:
        raise SystemExit("--log-max-age-days must be >= 1")

    root = Path(args.root).resolve()
    shadow_removed, shadow_bytes = _cleanup_shadow_dirs(root, args.shadow_max_age_hours, args.dry_run)
    log_removed, log_bytes = _cleanup_quality_logs(root, args.log_max_age_days, args.dry_run)

    total_bytes = shadow_bytes + log_bytes
    print(
        "quality-cleanup summary:"
        f" shadow_dirs_removed={shadow_removed}"
        f" logs_removed={log_removed}"
        f" bytes_reclaimed={total_bytes}"
        f" dry_run={args.dry_run}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
