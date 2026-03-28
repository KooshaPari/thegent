#!/usr/bin/env python3
import argparse, csv, json, pathlib, sys


def fail(msg: str) -> None:
    print(f'F95 succession risk distribution gate failed: {msg}', file=sys.stderr)
    raise SystemExit(2)


def normalized_csv_rows(path: pathlib.Path, expected: list[str]) -> list[dict]:
    rows = list(csv.DictReader(path.read_text().splitlines()))
    if not rows:
        return []
    if list(rows[0].keys()) != expected:
        fail(f'invalid succession risk csv header: {list(rows[0].keys())}')
    return sorted(rows, key=lambda row: [row.get(c, '') for c in expected])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--succession', required=True)
    parser.add_argument('--risk-csv', required=True)
    parser.add_argument('--max-high-risk-ratio', type=float, default=0.0)
    parser.add_argument('--max-unmapped-roles', type=int, default=0)
    args = parser.parse_args()

    try:
        config = json.loads(pathlib.Path(args.succession).read_text())
    except Exception:
        fail('invalid succession json')
    if not isinstance(config, dict) or bool(config.get('risk_distribution_tracking_enabled', True)) is not True:
        fail('risk_distribution_tracking_enabled != true')

    rows = normalized_csv_rows(
        pathlib.Path(args.risk_csv),
        ['role_id', 'risk_level', 'owner', 'status'],
    )
    high_risk = [r for r in rows if (r.get('risk_level') or '').strip().lower() == 'high']
    unresolved = [r for r in rows if (r.get('status') or '').strip().lower() != 'mitigated']
    unmapped = [r for r in rows if not (r.get('risk_level') or '').strip()]

    if rows:
        ratio = len(high_risk) / len(rows)
    else:
        ratio = 0.0
    if ratio > args.max_high_risk_ratio or len(unmapped) > args.max_unmapped_roles:
        fail(
            f'high_risk_roles={len(high_risk)} unresolved_roles={len(unresolved)} total_roles={len(rows)} '
            f'high_risk_ratio={ratio:.6f} max_high_risk_ratio={args.max_high_risk_ratio} '
            f'unmapped_roles={len(unmapped)} max_unmapped_roles={args.max_unmapped_roles}'
        )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
