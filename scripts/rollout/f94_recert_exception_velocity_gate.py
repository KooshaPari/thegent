#!/usr/bin/env python3
import argparse, csv, json, pathlib, sys


def fail(msg: str) -> None:
    print(f'F94 recert exception velocity gate failed: {msg}', file=sys.stderr)
    raise SystemExit(2)


def to_int(value: str, field: str) -> int:
    try:
        return int((value or '').strip())
    except ValueError:
        fail(f'invalid integer in {field}: {value!r}')


def boolish(value: str) -> bool:
    return (value or '').strip().lower() in {'true', '1', 'yes'}


def normalized_csv_rows(path: pathlib.Path, expected: list[str]) -> list[dict]:
    rows = list(csv.DictReader(path.read_text().splitlines()))
    if not rows:
        return []
    if list(rows[0].keys()) != expected:
        fail(f'invalid exceptions csv header: {list(rows[0].keys())}')
    for row in rows:
        row['days_open'] = to_int(row.get('days_open'), 'days_open')
    return sorted(rows, key=lambda row: [row.get(c, '') for c in expected])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--recert', required=True)
    parser.add_argument('--exceptions-csv', required=True)
    parser.add_argument('--max-weekly-velocity', type=int, default=0)
    parser.add_argument('--max-overdue-open-days', type=int, default=14)
    args = parser.parse_args()

    try:
        config = json.loads(pathlib.Path(args.recert).read_text())
    except Exception:
        fail('invalid recert json')
    if not isinstance(config, dict) or bool(config.get('exception_velocity_tracking_enabled', True)) is not True:
        fail('exception_velocity_tracking_enabled != true')

    rows = normalized_csv_rows(
        pathlib.Path(args.exceptions_csv),
        ['exception_id', 'status', 'is_new', 'days_open', 'owner'],
    )
    new_open = [
        r for r in rows
        if boolish(r.get('is_new')) and (r.get('status') or '').strip().lower() != 'resolved'
    ]
    overdue = [r for r in rows if (r.get('status') or '').strip().lower() != 'resolved' and r['days_open'] > args.max_overdue_open_days]
    if len(new_open) > args.max_weekly_velocity or overdue:
        fail(
            f'new_open_exceptions={len(new_open)} overdue_open_exceptions={len(overdue)} '
            f'max_weekly_velocity={args.max_weekly_velocity} max_overdue_open_days={args.max_overdue_open_days}'
        )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
