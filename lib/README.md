# kush/lib — Shared scripts for kush projects

Shared bash/Python utilities used across sharecli, thegent, trace, job-hunter, and other kush projects.

## Layout

```
lib/
├── README.md
└── quality-agent-common.sh   # Copilot/thegent agent logic for quality scripts
```

## quality-agent-common.sh

Provides `_run_copilot` and `_do_agent` for quality-fix-agent and quality-agent scripts.

**Usage:** Source from project scripts. Requires `ROOT_DIR` and `HEADLESS` (0/1) to be set.

**Discovery:** Projects under `kush/<project>/scripts/` auto-resolve `KUSH_LIB` to `kush/lib`. For projects outside kush (e.g. `~/Dev/job-hunter`):

```bash
export KUSH_LIB=~/path/to/kush/lib
# or
export KUSH_LIB=~/temp-PRODVERCEL/485/kush/lib
```

**Override:** `THGENT_HEADLESS_CMD` — custom headless command (e.g. `thegent run`).

## Adding to a new project

1. Add `scripts/quality-fix-agent.sh` (or `quality-agent.sh`) that sources the lib.
2. Ensure project is under `kush/` or set `KUSH_LIB`.
3. Copy the wrapper pattern from sharecli/thegent.

Example minimal wrapper for trace or job-hunter:

```bash
#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
KUSH_LIB="${KUSH_LIB:-$(cd "$ROOT_DIR/../.." 2>/dev/null && pwd)/lib}"
[[ -f "$KUSH_LIB/quality-agent-common.sh" ]] && source "$KUSH_LIB/quality-agent-common.sh"
# ... project-specific _run_fix or quality command ...
```
