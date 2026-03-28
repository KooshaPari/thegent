#!/usr/bin/env python3
import argparse, csv, json, pathlib, sys


def fail(msg: str) -> None:
    print(f'F96 board review maturity gate failed: {msg}', file=sys.stderr)
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
        row['maturity_days'] = to_int(row.get('maturity_days'), 'maturity_days')
    return sorted(rows, key=lambda row: [row.get(c, '') for c in expected])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--board', required=True)
    parser.add_argument('--reviews-csv', required=True)
    parser.add_argument('--min-mature-review-ratio', type=float, default=0.9)
    parser.add_argument('--max-maturity-age-days', type=int, default=60)
    args = parser.parse_args()

    try:
        config = json.loads(pathlib.Path(args.board).read_text())
    except Exception:
        fail('invalid board json')
    if not isinstance(config, dict) or bool(config.get('board_review_maturity_tracking_enabled', True)) is not True:
        fail('board_review_maturity_tracking_enabled != true')

    rows = normalized_csv_rows(
        pathlib.Path(args.reviews_csv),
        ['review_id', 'status', 'maturity_level', 'maturity_days', 'reviewer'],
    )
    completed = [r for r in rows if (r.get('status') or '').strip().lower() in {'complete', 'completed'}]
    mature = [r for r in completed if (r.get('maturity_level') or '').strip().lower() == 'mature']
    stale = [r for r in completed if r['maturity_days'] > args.max_maturity_age_days]

    ratio = (len(mature) / len(completed)) if completed else 0.0
    if ratio < args.min_mature_review_ratio or stale:
        fail(
            f'mature_reviews={len(mature)} completed_reviews={len(completed)} '
            f'mature_review_ratio={ratio:.6f} min_mature_review_ratio={args.min_mature_review_ratio} '
            f'stale_mature_reviews={len(stale)} max_maturity_age_days={args.max_maturity_age_days}'
        )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
