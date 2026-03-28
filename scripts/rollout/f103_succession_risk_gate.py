#!/usr/bin/env python3
import argparse
import csv
import json
import pathlib
import sys


def fail(msg: str) -> None:
    print(f'F103 succession risk gate failed: {msg}', file=sys.stderr)
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
        fail(f'invalid succession risk csv header: {list(rows[0].keys())}')
    for row in rows:
        row['days_open'] = to_int(row.get('days_open'), 'days_open')
    return sorted(rows, key=lambda row: [row.get(c, '') for c in expected])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--succession', required=True)
    parser.add_argument('--risk-csv', required=True)
    parser.add_argument('--max-open-high-risk-ratio', type=float, default=0.0)
    parser.add_argument('--max-unmapped-roles', type=int, default=0)
    parser.add_argument('--max-high-risk-days', type=int, default=30)
    args = parser.parse_args()

    try:
        config = json.loads(pathlib.Path(args.succession).read_text())
    except Exception:
        fail('invalid succession json')
    if not isinstance(config, dict) or bool(config.get('risk_tracking_enabled', True)) is not True:
        fail('risk_tracking_enabled != true')

    rows = normalized_csv_rows(
        pathlib.Path(args.risk_csv),
        ['role_id', 'risk_level', 'owner', 'status', 'days_open'],
    )
    open_roles = [r for r in rows if (r.get('status') or '').strip().lower() not in {'mitigated', 'closed'}]
    high_risk_open = [r for r in open_roles if (r.get('risk_level') or '').strip().lower() == 'high']
    stale_high_risk = [r for r in high_risk_open if r['days_open'] > args.max_high_risk_days]
    unmapped_roles = [r for r in rows if not (r.get('role_id') or '').strip()]

    ratio = (len(high_risk_open) / len(open_roles)) if open_roles else 0.0
    if ratio > args.max_open_high_risk_ratio or len(stale_high_risk) > 0 or len(unmapped_roles) > args.max_unmapped_roles:
        fail(
            f'open_roles={len(open_roles)} high_risk_open_roles={len(high_risk_open)} '
            f'high_risk_open_ratio={ratio:.6f} max_open_high_risk_ratio={args.max_open_high_risk_ratio} '
            f'stale_high_risk_roles={len(stale_high_risk)} max_high_risk_days={args.max_high_risk_days} '
            f'unmapped_roles={len(unmapped_roles)} max_unmapped_roles={args.max_unmapped_roles}'
        )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
