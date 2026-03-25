#!/usr/bin/env bash
set -euo pipefail

REPOS_ROOT="/Users/kooshapari/CodeProjects/Phenotype/repos"
MANIFEST="/Users/kooshapari/CodeProjects/Phenotype/repos/thegent/docs/reports/reusable-tooling-audit/phase1_tooling_split_plan.json"
DRY_RUN=${DRY_RUN:-1}

python - <<'PY'
import json, os, pathlib, shutil, argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--manifest", default="/Users/kooshapari/CodeProjects/Phenotype/repos/thegent/docs/reports/reusable-tooling-audit/phase1_tooling_split_plan.json")
parser.add_argument("--apply", action="store_true")
parser.add_argument("--repo-root", default="/Users/kooshapari/CodeProjects/Phenotype/repos")
args = parser.parse_args()

payload = json.loads(Path(args.manifest).read_text())
modules = payload["modules"]
repo_root = Path(args.repo_root)
do_apply = bool(args.apply)

for mod in modules:
    src = Path(mod["source"]["abs_path"])
    for target in mod["targets"]:
        dst = repo_root / target["repo"] / mod["path"]
        if not src.exists():
            raise FileNotFoundError(f"source missing: {src}")
        if not dst.parent.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
        if do_apply:
            shutil.copy2(src, dst)
            print(f"UPDATED {dst}")
        else:
            print(f"DRY RUN: {dst} <= {src}")
PY

echo "Dry run finished. Set DRY_RUN=0 and add --apply to write files."
