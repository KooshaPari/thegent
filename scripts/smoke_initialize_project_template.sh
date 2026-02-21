#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: scripts/smoke_initialize_project_template.sh [--profile PROFILE]

Profiles:
  cli_tool
  service_api
  event_worker
  web_app
  library_sdk
  all

Default profile: service_api
USAGE
}

profile="service_api"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile)
      profile="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/.." && pwd)"
template_dir="$repo_root/templates/initialize-project"

if [[ ! -f "$template_dir/copier.yml" ]]; then
  echo "Template not found at $template_dir" >&2
  exit 1
fi

profiles=(cli_tool service_api event_worker web_app library_sdk)

validate_profile() {
  local selected="$1"
  if [[ "$selected" == "all" ]]; then
    return 0
  fi
  local p
  for p in "${profiles[@]}"; do
    if [[ "$selected" == "$p" ]]; then
      return 0
    fi
  done
  return 1
}

if ! validate_profile "$profile"; then
  echo "Invalid profile: $profile" >&2
  usage >&2
  exit 1
fi

write_profile_data() {
  local selected="$1"
  local data_file="$2"

  case "$selected" in
    cli_tool)
      cat >"$data_file" <<YAML
project_name: smoke-cli-tool
project_description: Smoke test for cli_tool profile
project_type: cli_tool
language: python
runtime_profile: balanced
governance_mode: standard
author: smoke-ci
observability_stack: minimal_logs
interfaces:
  - cli
  - docs
deployment_target: local_only
quality_profile: strict
questionnaire_summary_hints:
  - primary_user_flow
  - biggest_risk
include_docs: true
include_ci: true
include_hooks: true
YAML
      ;;
    service_api)
      cat >"$data_file" <<YAML
project_name: smoke-service-api
project_description: Smoke test for service_api profile
project_type: service_api
language: python
runtime_profile: low_latency
governance_mode: standard
author: smoke-ci
observability_stack: otel_prometheus
interfaces:
  - http_api
  - docs
deployment_target: container_platform
quality_profile: strict
questionnaire_summary_hints:
  - primary_user_flow
  - biggest_risk
  - rollback_plan
include_docs: true
include_ci: true
include_docker: true
include_hooks: true
YAML
      ;;
    event_worker)
      cat >"$data_file" <<YAML
project_name: smoke-event-worker
project_description: Smoke test for event_worker profile
project_type: event_worker
language: python
runtime_profile: throughput
governance_mode: strict
author: smoke-ci
observability_stack: otel_prometheus
interfaces:
  - events
  - docs
deployment_target: serverless
quality_profile: critical
questionnaire_summary_hints:
  - biggest_risk
  - rollback_plan
  - cost_guardrails
include_docs: true
include_ci: true
include_hooks: true
YAML
      ;;
    web_app)
      cat >"$data_file" <<YAML
project_name: smoke-web-app
project_description: Smoke test for web_app profile
project_type: web_app
language: typescript
runtime_profile: low_latency
governance_mode: standard
author: smoke-ci
observability_stack: sentry_first
interfaces:
  - web_ui
  - http_api
  - docs
deployment_target: edge
quality_profile: strict
questionnaire_summary_hints:
  - primary_user_flow
  - biggest_risk
  - onboarding
include_docs: true
include_ci: true
include_hooks: true
YAML
      ;;
    library_sdk)
      cat >"$data_file" <<YAML
project_name: smoke-library-sdk
project_description: Smoke test for library_sdk profile
project_type: library_sdk
language: python
runtime_profile: cost_optimized
governance_mode: strict
author: smoke-ci
observability_stack: minimal_logs
interfaces:
  - sdk
  - docs
deployment_target: package_registry
quality_profile: critical
questionnaire_summary_hints:
  - primary_user_flow
  - onboarding
  - rollback_plan
include_docs: true
include_ci: true
include_hooks: true
YAML
      ;;
    *)
      echo "Unsupported profile: $selected" >&2
      exit 1
      ;;
  esac
}

run_smoke_for_profile() {
  local selected="$1"
  local run_root="$2"
  local data_file="$run_root/profile.yml"

  mkdir -p "$run_root"
  write_profile_data "$selected" "$data_file"

  local project_name
  project_name="$(awk -F': ' '/^project_name:/{print $2}' "$data_file")"

  echo "[smoke] Rendering profile: $selected"
  uvx copier copy --defaults --data-file "$data_file" "$template_dir" "$run_root"

  local rendered_root="$run_root/$project_name"
  local claude_file="$rendered_root/CLAUDE.md"

  if [[ ! -f "$claude_file" ]]; then
    echo "[smoke] Missing rendered CLAUDE.md for profile $selected at $claude_file" >&2
    return 1
  fi

  if rg -n --glob '*.md' '\{\{|\{%' "$rendered_root" >/tmp/thegent-smoke-unresolved.log; then
    echo "[smoke] Unresolved template markers found in rendered markdown for profile $selected" >&2
    cat /tmp/thegent-smoke-unresolved.log >&2
    return 1
  fi

  if ! grep -Fq "| \`project_type\` | \`$selected\` |" "$claude_file"; then
    echo "[smoke] CLAUDE.md did not include expected project_type=$selected" >&2
    return 1
  fi

  echo "[smoke] Passed profile: $selected"
}

work_dir="$(mktemp -d "${TMPDIR:-/tmp}/thegent-copier-smoke.XXXXXX")"
cleanup() {
  rm -rf "$work_dir"
}
trap cleanup EXIT

if [[ "$profile" == "all" ]]; then
  for p in "${profiles[@]}"; do
    run_smoke_for_profile "$p" "$work_dir/$p"
  done
  echo "[smoke] All profiles passed"
else
  run_smoke_for_profile "$profile" "$work_dir/$profile"
fi
