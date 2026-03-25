#!/usr/bin/env bash
set -euo pipefail

MANIFEST="/Users/kooshapari/CodeProjects/Phenotype/repos/thegent/docs/reports/reusable-tooling-audit/phase2_expand_tooling_split.json"
REPO_ROOT="/Users/kooshapari/CodeProjects/Phenotype/repos"
APPLY=${APPLY:-1}
DRY=${DRY:-}

if [ -n "$DRY" ]; then
  APPLY=0
fi

MANIFEST_PATH="$MANIFEST" REPO_ROOT_PATH="$REPO_ROOT" APPLY="$APPLY" python - <<'PY'
import json
import os
from pathlib import Path

manifest = Path(os.environ['MANIFEST_PATH'])
payload = json.loads(manifest.read_text())
repo_root = Path(os.environ['REPO_ROOT_PATH'])
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
