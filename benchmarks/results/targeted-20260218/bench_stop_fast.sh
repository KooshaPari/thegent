#!/usr/bin/env bash
set -euo pipefail
export THGENT_STOP_PROFILE=fast
export THGENT_STOP_IDLE_TIMEOUT_SEC=10
export THGENT_STOP_MAX_TIMEOUT_SEC=15
printf '{"cwd":"/Users/kooshapari/temp-PRODVERCEL/485/kush/thegent","project_dir":"/Users/kooshapari/temp-PRODVERCEL/485/kush/thegent"}\n' | hooks/hook-dispatcher/target/release/hook-dispatcher stop >/dev/null 2>&1
