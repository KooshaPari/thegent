#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

if [ -z "${UV_CACHE_DIR:-}" ]; then
  UV_CACHE_DIR="$REPO_ROOT/.cache/uv"
fi
mkdir -p "$UV_CACHE_DIR"
export UV_CACHE_DIR

ACT_EVENT="${THGENT_ACT_EVENT:-${ACT_EVENT:-push}}"
ACT_WORKFLOW="${THGENT_ACT_WORKFLOW:-${ACT_WORKFLOW:-.github/workflows/ci.yml}}"
ACT_JOB="${THGENT_ACT_JOB:-${ACT_JOB:-}}"
ACT_BRANCH="${THGENT_GH_BRANCH:-${GH_BRANCH:-main}}"
ARTIFACT_DIR="${THGENT_ACT_ARTIFACT_DIR:-artifacts/act}"
ACT_DOCKERLESS="${THGENT_ACT_DOCKERLESS:-${ACT_DOCKERLESS:-0}}"
DRY_RUN="${THGENT_ACT_DRY_RUN:-${ACT_DRY_RUN:-0}}"
FORCE_REUSE="${THGENT_ACT_REUSE:-${ACT_REUSE:-1}}"
VERBOSE="${THGENT_ACT_VERBOSE:-${ACT_VERBOSE:-0}}"
KEEP_EVENT_FILE="${THGENT_ACT_KEEP_EVENT:-${ACT_KEEP_EVENT:-0}}"
GH_REPOSITORY="${GITHUB_REPOSITORY:-local/repo}"
GH_BRANCH_DEFAULT="${ACT_BRANCH}"

if [[ "$ACT_EVENT" != "pull_request" && "$ACT_EVENT" != "push" ]]; then
  echo "Unsupported event '$ACT_EVENT'. Supported: pull_request, push." >&2
  exit 1
fi

if [[ ! -f "$ACT_WORKFLOW" ]]; then
  echo "Workflow not found: $ACT_WORKFLOW" >&2
  exit 1
fi

mkdir -p "$ARTIFACT_DIR"
RUN_TOKEN="$(date -u +%Y%m%dT%H%M%S)-$(git rev-parse --short HEAD 2>/dev/null || echo no-git)"
RUN_ARTIFACT_DIR="$ARTIFACT_DIR/$RUN_TOKEN"
mkdir -p "$RUN_ARTIFACT_DIR"

event_dir="${THGENT_ACT_EVENT_DIR:-$REPO_ROOT/.github/act-events}"
mkdir -p "$event_dir"

event_file=""
cleanup_event_file=""

cleanup_eventfile() {
  if [[ "$KEEP_EVENT_FILE" == "1" ]]; then
    if [[ -n "$cleanup_event_file" ]]; then
      echo "Kept event file for inspection: $cleanup_event_file"
    fi
    return 0
  fi

  if [[ -n "$cleanup_event_file" && -f "$cleanup_event_file" ]]; then
    rm -f "$cleanup_event_file"
  fi
}

trap cleanup_eventfile EXIT

run_dockerless_ci_job() {
  case "$1" in
    preflight)
      task ci:preflight
      ;;
    test)
      if [ "$ACT_EVENT" = "pull_request" ]; then
        task test:pr-gate
      else
        task test:collect:fast-gate
        task test:fast-lane
      fi
      ;;
    quality)
      task quality
      ;;
    quality-unified|quality_unified)
      task quality:ci:unified
      ;;
    coverage)
      task coverage:ci
      ;;
    template-collect-nightly|template_collect_nightly|template-collect)
      task test:collect:templates
      ;;
    leak-detection|leak_detection|leak)
      uv run pytest tests/test_resource_leaks.py -v
      uv run pytest tests/test_resource_leaks.py -v -m slow || true
      ;;
    integration)
      task test:nightly-lane
      ;;
    zig-readiness|zig_readiness)
      task quality:runtime-contracts:zig-abi
      ;;
    pre-commit)
      task ci:local:pre-commit
      ;;
    pre-push)
      task ci:local:pre-push
      ;;
    *)
      echo "Unsupported job '$1' for dockerless local emulation." >&2
      echo "Supported jobs: preflight, test, quality, quality-unified, coverage, template-collect-nightly, leak-detection, zig-readiness, integration, pre-commit, pre-push."
      echo "Use ACT_DOCKERLESS=1 with a supported job, or run without ACT_JOB for full local ci lane."
      return 1
      ;;
  esac
}

run_dockerless_event_lane() {
  if [ "$ACT_EVENT" = "pull_request" ]; then
    task ci:local
  else
    task ci:local
  fi
}

if [[ -n "${THGENT_ACT_EVENT_FILE:-}" ]]; then
  event_file="${THGENT_ACT_EVENT_FILE}"
elif [[ "$ACT_EVENT" == "pull_request" ]]; then
  base_ref="${THGENT_GH_BASE_REF:-${BASE_REF:-$GH_BRANCH_DEFAULT}}"
  base_sha="${THGENT_GH_BASE_SHA:-}"
  head_ref="${THGENT_GH_HEAD_REF:-$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo HEAD)}"
  head_sha="${THGENT_GH_HEAD_SHA:-$(git rev-parse HEAD)}"
  repo_full_name="$GH_REPOSITORY"
  repo_name="${repo_full_name##*/}"

  if [[ -z "$base_sha" ]]; then
    if base_sha_resolved="$(git rev-parse "origin/${base_ref}^{commit}" 2>/dev/null)"; then
      base_sha="$base_sha_resolved"
    elif base_sha_resolved="$(git rev-parse "${base_ref}^{commit}" 2>/dev/null)"; then
      base_sha="$base_sha_resolved"
    else
      base_sha="$head_sha"
    fi
  fi

  event_file="$event_dir/pull_request-${RUN_TOKEN}.json"
  cleanup_event_file="$event_file"

  cat > "$event_file" <<EOF_EVENT
{
  "action": "opened",
  "pull_request": {
    "number": 1,
    "head": {
      "ref": "${head_ref}",
      "sha": "${head_sha}"
    },
    "base": {
      "ref": "${base_ref}",
      "sha": "${base_sha}"
    }
  },
  "repository": {
    "name": "${repo_name}",
    "full_name": "${repo_full_name}",
    "default_branch": "${base_ref}"
  },
  "sender": {
    "login": "thegent-local"
  }
}
EOF_EVENT
else
  event_file="$event_dir/push-${RUN_TOKEN}.json"
  cleanup_event_file="$event_file"
  push_ref="${THGENT_GH_HEAD_REF:-${ACT_BRANCH}}"
  repo_full_name="$GH_REPOSITORY"
  repo_name="${repo_full_name##*/}"

  head_sha="${THGENT_GH_HEAD_SHA:-$(git rev-parse HEAD)}"

  cat > "$event_file" <<EOF_EVENT
{
  "ref": "refs/heads/${push_ref}",
  "before": "0000000000000000000000000000000000000000",
  "after": "${head_sha}",
  "repository": {
    "name": "${repo_name}",
    "full_name": "${repo_full_name}",
    "default_branch": "main"
  },
  "head_commit": {
    "id": "${head_sha}",
    "message": "Local GH action simulation",
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "author": {"name": "thegent-local"},
    "committer": {"name": "thegent-local"}
  }
}
EOF_EVENT
fi

act_args=(
  "act"
  "$ACT_EVENT"
  "-W"
  "$ACT_WORKFLOW"
  "--artifact-server-path"
  "$RUN_ARTIFACT_DIR"
  "--container-architecture"
  "linux/amd64"
)

if [[ "$FORCE_REUSE" == "1" ]]; then
  act_args+=("--reuse")
fi

if [[ -n "$ACT_JOB" ]]; then
  act_args+=("--job" "$ACT_JOB")
fi

if [[ -n "$event_file" ]]; then
  act_args+=("--eventpath" "$event_file")
fi

if [[ "$VERBOSE" == "1" ]]; then
  act_args+=("--verbose")
fi

if ! command -v act >/dev/null 2>&1; then
  echo "act is required for GH Actions emulation." >&2
  echo "Install with: brew install act" >&2
  echo "Install with: go install github.com/nektos/act@latest" >&2
  exit 1
fi

if [[ "$ACT_DOCKERLESS" == "1" ]]; then
  if [[ "$DRY_RUN" == "1" ]]; then
    if [ -n "$ACT_JOB" ]; then
      echo "dockerless-ci job simulation:"
      echo "  event=${ACT_EVENT}"
      echo "  job=${ACT_JOB}"
      exit 0
    fi

    echo "dockerless-ci full-lane simulation:"
    echo "  event=${ACT_EVENT}"
    exit 0
  fi

  if [ -n "$ACT_JOB" ]; then
    echo "Running dockerless local emulation for job '${ACT_JOB}' (event=${ACT_EVENT})."
    run_dockerless_ci_job "$ACT_JOB"
    exit $?
  fi

  echo "Running dockerless local emulation for full ${ACT_EVENT} lane."
  run_dockerless_event_lane
  exit $?
fi

if [[ "$DRY_RUN" == "1" ]]; then
  printf 'act dry-run command:\n'
  printf '  %q ' "${act_args[@]}"
  printf '\n'
  printf 'Generated event file: %s\n' "$event_file"
  exit 0
fi

if ! command -v docker >/dev/null 2>&1 && ! command -v podman >/dev/null 2>&1; then
  echo "act requires Docker; please install/start Docker Desktop or Podman and retry." >&2
  echo "Install with: brew install --cask docker"
  exit 1
fi

if command -v docker >/dev/null 2>&1; then
  if ! docker ps >/dev/null 2>&1; then
    echo "Docker is unavailable or not running. Start Docker and retry local GH Actions emulation." >&2
    exit 1
  fi
elif ! podman info >/dev/null 2>&1; then
  echo "Docker is unavailable or not running. Start Docker and retry local GH Actions emulation." >&2
  echo "Start Podman and ensure podman socket is available." >&2
  exit 1
fi

export THEGENT_LOCAL_ACT="1"
export GITHUB_EVENT_NAME="$ACT_EVENT"
if [[ "$ACT_EVENT" == "pull_request" ]]; then
  export GITHUB_BASE_REF="${THGENT_GH_BASE_REF:-main}"
fi

echo "Running: ${act_args[*]}"
"${act_args[@]}"

exit $?
