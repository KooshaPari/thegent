#!/usr/bin/env python3
import argparse
import csv
import json
import pathlib
import sys


def fail(msg: str) -> None:
    print(f'F102 board review staleness gate failed: {msg}', file=sys.stderr)
    raise SystemExit(2)


def to_int(value: str, field: str) -> int:
    try:
        return int((value or '').strip())
    except ValueError:
        fail(f'invalid integer in {field}: {value!r}')


def normalized_csv_rows(path: pathlib.Path, expected: list[str]) -> list[dict]:
    rows = list(csv.DictReader(path.read_text().splitlines()))
    if not rows:
        return []
    if list(rows[0].keys()) != expected:
        fail(f'invalid board reviews csv header: {list(rows[0].keys())}')
    for row in rows:
        row['days_stale'] = to_int(row.get('days_stale'), 'days_stale')
    return sorted(rows, key=lambda row: [row.get(c, '') for c in expected])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--board', required=True)
    parser.add_argument('--reviews-csv', required=True)
    parser.add_argument('--max-stale-reviews', type=int, default=0)
    parser.add_argument('--max-stale-ratio', type=float, default=0.0)
    parser.add_argument('--max-stale-days', type=int, default=21)
    args = parser.parse_args()

    try:
        config = json.loads(pathlib.Path(args.board).read_text())
    except Exception:
        fail('invalid board json')
    if not isinstance(config, dict) or bool(config.get('board_review_staleness_tracking_enabled', True)) is not True:
        fail('board_review_staleness_tracking_enabled != true')

    rows = normalized_csv_rows(
        pathlib.Path(args.reviews_csv),
        ['review_id', 'status', 'days_stale', 'reviewer', 'maturity_level'],
    )
    stale = [
        r for r in rows
        if (r.get('status') or '').strip().lower() not in {'complete', 'completed'} and r['days_stale'] > args.max_stale_days
    ]
    total_open = [r for r in rows if (r.get('status') or '').strip().lower() not in {'complete', 'completed'}]
    ratio = (len(stale) / len(total_open)) if total_open else 0.0

    if len(stale) > args.max_stale_reviews or ratio > args.max_stale_ratio:
        fail(
            f'open_reviews={len(total_open)} stale_reviews={len(stale)} stale_ratio={ratio:.6f} '
            f'max_stale_reviews={args.max_stale_reviews} max_stale_ratio={args.max_stale_ratio} '
            f'max_stale_days={args.max_stale_days}'
        )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
