#!/usr/bin/env bash
set -euo pipefail

MANIFEST="/Users/kooshapari/CodeProjects/Phenotype/repos/thegent/docs/reports/reusable-tooling-audit/phase1_minimal_tooling_split.json"
REPO_ROOT="/Users/kooshapari/CodeProjects/Phenotype/repos"
APPLY=${APPLY:-0}

MANIFEST=$MANIFEST REPO_ROOT=$REPO_ROOT python - <<'PY'
import json
import os
from pathlib import Path

manifest = Path(os.environ['MANIFEST'])
if not manifest.exists():
    raise SystemExit(f"manifest missing: {manifest}")

payload = json.loads(manifest.read_text())
repo_root = Path(os.environ['REPO_ROOT'])
apply = os.environ.get('APPLY', '0') == '1'

for mod in payload['modules']:
    src = Path(mod['source']['abs_path'])
    if not src.exists():
        raise SystemExit(f"source missing: {src}")

    for target in mod['targets']:
        dst = repo_root / target['repo'] / mod['path']
        dst.parent.mkdir(parents=True, exist_ok=True)
        if apply:
            dst.write_bytes(src.read_bytes())
            print(f"UPDATED {dst}")
        else:
            print(f"DRY RUN: {dst} <= {src}")
PY

if [ "$APPLY" != "1" ]; then
  echo "DRY RUN complete. Set APPLY=1 to apply."
fi
