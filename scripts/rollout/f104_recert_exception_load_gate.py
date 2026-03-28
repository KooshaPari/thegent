#!/usr/bin/env python3
import argparse
import csv
import json
import pathlib
import sys


def fail(msg: str) -> None:
    print(f'F104 recert exception load gate failed: {msg}', file=sys.stderr)
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
        fail(f'invalid recert exceptions csv header: {list(rows[0].keys())}')
    for row in rows:
        row['days_open'] = to_int(row.get('days_open'), 'days_open')
    return sorted(rows, key=lambda row: [row.get(c, '') for c in expected])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--recert', required=True)
    parser.add_argument('--exceptions-csv', required=True)
    parser.add_argument('--max-open-exceptions', type=int, default=0)
    parser.add_argument('--max-open-exceptions-per-owner', type=int, default=0)
    parser.add_argument('--max-high-priority-open', type=int, default=0)
    args = parser.parse_args()

    try:
        config = json.loads(pathlib.Path(args.recert).read_text())
    except Exception:
        fail('invalid recert json')
    if not isinstance(config, dict) or bool(config.get('exception_load_tracking_enabled', True)) is not True:
        fail('exception_load_tracking_enabled != true')

    rows = normalized_csv_rows(
        pathlib.Path(args.exceptions_csv),
        ['exception_id', 'status', 'owner', 'priority', 'days_open'],
    )
    open_exceptions = [
        r for r in rows
        if (r.get('status') or '').strip().lower() not in {'resolved', 'closed'}
    ]
    high_priority_open = [
        r for r in open_exceptions
        if (r.get('priority') or '').strip().lower() in {'high', 'critical'}
    ]
    owner_load = {}
    for row in open_exceptions:
        owner = (row.get('owner') or '').strip().lower() or 'unassigned'
        owner_load[owner] = owner_load.get(owner, 0) + 1
    max_owner_load = max(owner_load.values(), default=0)

    if len(open_exceptions) > args.max_open_exceptions or max_owner_load > args.max_open_exceptions_per_owner or len(high_priority_open) > args.max_high_priority_open:
        fail(
            f'open_exceptions={len(open_exceptions)} high_priority_open_exceptions={len(high_priority_open)} '
            f'max_owner_load={max_owner_load} max_open_exceptions={args.max_open_exceptions} '
            f'max_open_exceptions_per_owner={args.max_open_exceptions_per_owner} '
            f'max_high_priority_open={args.max_high_priority_open}'
        )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
