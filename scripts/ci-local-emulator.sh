#!/usr/bin/env bash
# Local emulation helper for GitHub Actions CI workflows.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "$REPO_ROOT" ]]; then
  echo "ci-local-emulator: unable to locate git root from ${SCRIPT_DIR}" >&2
  exit 1
fi

cd "$REPO_ROOT"

EVENT_NAME="${THEGENT_CI_EVENT:-${GITHUB_EVENT_NAME:-push}}"
EMULATION_MODE="${THEGENT_CI_EMULATION_MODE:-full}"
BASE_REF="${GITHUB_BASE_REF:-${THEGENT_BASE_REF:-main}}"
BASE_REF="${BASE_REF#origin/}"
BASE_REF="${BASE_REF#refs/heads/}"
GITHUB_SHA="${GITHUB_SHA:-$(git rev-parse HEAD)}"
PR_CHANGED_FILE="${GITHUB_PR_CHANGED_FILE_LIST:-artifacts/pytest/requirements/changed-files.txt}"
PR_BASE_REF="${THEGENT_PR_BASE_REF:-}"
RUN_INTEGRATION="${THEGENT_CI_RUN_INTEGRATION:-0}"
RUN_ZIG="${THEGENT_CI_RUN_ZIG:-0}"
RUN_BENCHMARKS="${THEGENT_CI_RUN_BENCHMARKS:-0}"
RUN_BUILD_WHEELS="${THEGENT_CI_RUN_BUILD_WHEELS:-0}"
RUN_DOCS_BUILD="${THEGENT_CI_RUN_DOCS_BUILD:-0}"
RUN_RELEASE="${THEGENT_CI_RUN_RELEASE:-0}"
RUN_TEMPLATE_COLLECT="${THEGENT_CI_RUN_TEMPLATE_COLLECT:-0}"

export PYTHONPATH="${REPO_ROOT}"

log_section() {
  printf '\n===== %s =====\n' "$1"
}

is_pull_request_event() {
  [[ "$EVENT_NAME" == "pull_request" ]]
}

build_changed_file_list() {
  mkdir -p artifacts/pytest/requirements

  if is_pull_request_event; then
    log_section "Building PR changed-file list"
    local base_ref="origin/${BASE_REF}"
    local fallback_ref="${BASE_REF}"
    if ! git show-ref --verify --quiet "$base_ref" ; then
      if git remote get-url origin >/dev/null 2>&1; then
        git fetch --quiet origin "$BASE_REF" --depth=2 || true
      fi
    fi
    if ! git show-ref --verify --quiet "$base_ref" ; then
      base_ref="$fallback_ref"
    fi
    if ! git rev-parse --verify "$base_ref" >/dev/null 2>&1; then
      echo "ci-local-emulator: base ref ${base_ref} not available; falling back to HEAD~1" >&2
      base_ref="HEAD~1"
    fi
    if ! git rev-parse --verify "$GITHUB_SHA^{commit}" >/dev/null 2>&1; then
      echo "ci-local-emulator: GITHUB_SHA ${GITHUB_SHA} is not a commit; using HEAD" >&2
      GITHUB_SHA="$(git rev-parse HEAD)"
    fi
    git diff --name-only "${base_ref}...${GITHUB_SHA}" > "${PR_CHANGED_FILE}"
    export PR_BASE_REF="${BASE_REF}"
    export PYTEST_PR_CHANGED_FILE_LIST="${PR_CHANGED_FILE}"
    return 0
  fi

  : > "${PR_CHANGED_FILE}"
  export PR_BASE_REF="${PR_BASE_REF:-}"
  export PYTEST_PR_CHANGED_FILE_LIST="${PR_CHANGED_FILE}"
}

run_ci_preflight() {
  log_section "Preflight"
  task ci:preflight
}

run_ci_tests() {
  log_section "Tests ($EVENT_NAME)"
  if is_pull_request_event; then
    task test:pr-gate
  else
    task test:collect:fast-gate
    task test:fast-lane
  fi
}

run_ci_quality_gates() {
  log_section "CI-equivalent quality gates"
  uv run python scripts/check_wl122_max_lines_canonical_path.py --strict
  task quality:max-lines
  task quality:sitback-contracts
  task quality:harness-model-contracts
  task quality:providers:required-gate
  task quality:runtime-contracts
  task quality:security:sast
  task quality:chaos:smoke
  task quality:a11y:smoke
  task bench:smoke:ci
  task quality:perf:benchmark-gate
}

run_ci_build_wheels() {
  log_section "Build wheels"
  uv build
}

run_ci_docs() {
  log_section "Docs emulation"
  if [ -f docs/.vitepress/dist/index.html ]; then
    echo "[SKIP] docs prebuilt artifact exists."
    return 0
  fi
  task docs:build
}

run_ci_release() {
  log_section "Release emulation"
  python scripts/vitepress-agent-workflow.py --skip-demos
  task docs:build
  uv build
}

run_ci_hook_profile() {
  log_section "Hook-local CI profile"
  task hooks:run
  task test:collect:fast-gate
  task test:fast-lane
}

run_ci_leaks() {
  log_section "Leak detection"
  export CHECK_LEAKS=1
  uv run pytest tests/test_resource_leaks.py -v
}

run_ci_coverage() {
  log_section "Coverage"
  task coverage:ci
}

run_optional_jobs() {
  if [[ "$RUN_INTEGRATION" == "1" ]]; then
    log_section "Integration tests (optional)"
    uv run pytest tests/ -v -m "integration"
  fi

  if [[ "$RUN_ZIG" == "1" ]]; then
    log_section "Zig ABI readiness (optional)"
    (
      cd crates
      cargo build -p thegent-zmx-interop
      cargo test -p thegent-zmx-interop
    )
  fi

  if [[ "$RUN_BUILD_WHEELS" == "1" ]]; then
    run_ci_build_wheels
  fi

  if [[ "$RUN_DOCS_BUILD" == "1" ]]; then
    run_ci_docs
  fi

  if [[ "$RUN_TEMPLATE_COLLECT" == "1" ]]; then
    log_section "Template-path CI collect (optional)"
    task test:collect:templates
  fi

  if [[ "$RUN_RELEASE" == "1" ]]; then
    run_ci_release
  fi

  if [[ "$RUN_BENCHMARKS" == "1" ]]; then
    log_section "Benchmark suite (optional)"
    task bench:comprehensive
  fi
}

build_changed_file_list

case "$EMULATION_MODE" in
  quick)
    run_ci_hook_profile
    ;;
  hook)
    run_ci_hook_profile
    ;;
  full)
    run_ci_preflight
    run_ci_tests
    run_ci_leaks
    run_ci_quality_gates
    run_ci_coverage
    run_optional_jobs
    ;;
  *)
    echo "ci-local-emulator: unknown THEGENT_CI_EMULATION_MODE=$EMULATION_MODE" >&2
    exit 2
    ;;
esac

log_section "Local CI emulation complete"
echo "Local CI emulation completed successfully."
