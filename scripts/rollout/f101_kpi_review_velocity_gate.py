#!/usr/bin/env python3
import argparse
import csv
import json
import pathlib
import sys


def fail(msg: str) -> None:
    print(f'F101 KPI review velocity gate failed: {msg}', file=sys.stderr)
    raise SystemExit(2)


def to_int(value: str, field: str) -> int:
    try:
        return int((value or '').strip())
    except ValueError:
        fail(f'invalid integer in {field}: {value!r}')


def boolish(value: str) -> bool:
    return (value or '').strip().lower() in {'1', 'true', 'yes', 'y'}


def normalized_csv_rows(path: pathlib.Path, expected: list[str]) -> list[dict]:
    rows = list(csv.DictReader(path.read_text().splitlines()))
    if not rows:
        return []
    if list(rows[0].keys()) != expected:
        fail(f'invalid KPI reviews csv header: {list(rows[0].keys())}')
    for row in rows:
        row['days_open'] = to_int(row.get('days_open'), 'days_open')
    return sorted(rows, key=lambda row: [row.get(c, '') for c in expected])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--kpi', required=True)
    parser.add_argument('--reviews-csv', required=True)
    parser.add_argument('--max-weekly-velocity', type=int, default=0)
    parser.add_argument('--max-open-review-ratio', type=float, default=0.0)
    parser.add_argument('--max-open-days', type=int, default=30)
    args = parser.parse_args()

    try:
        config = json.loads(pathlib.Path(args.kpi).read_text())
    except Exception:
        fail('invalid kpi json')
    if not isinstance(config, dict) or bool(config.get('review_velocity_tracking_enabled', True)) is not True:
        fail('review_velocity_tracking_enabled != true')

    rows = normalized_csv_rows(
        pathlib.Path(args.reviews_csv),
        ['kpi_id', 'review_id', 'is_new', 'status', 'days_open', 'owner'],
    )
    open_reviews = [
        r for r in rows
        if (r.get('status') or '').strip().lower() not in {'complete', 'completed'}
    ]
    open_new = [r for r in open_reviews if boolish(r.get('is_new'))]
    overdue = [r for r in open_reviews if r['days_open'] > args.max_open_days]

    total = len(rows)
    open_ratio = (len(open_reviews) / total) if total else 0.0

    if len(open_new) > args.max_weekly_velocity or len(overdue) > 0 or open_ratio > args.max_open_review_ratio:
        fail(
            f'kpi_reviews={total} open_reviews={len(open_reviews)} open_new_reviews={len(open_new)} '
            f'overdue_open_reviews={len(overdue)} open_review_ratio={open_ratio:.6f} '
            f'max_weekly_velocity={args.max_weekly_velocity} max_open_review_ratio={args.max_open_review_ratio} '
            f'max_open_days={args.max_open_days}'
        )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
