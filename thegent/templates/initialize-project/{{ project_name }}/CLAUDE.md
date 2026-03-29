# {{project_name}}

{{project_description}}

---

## Questionnaire Snapshot

| Field | Selected |
|---|---|
| `project_type` | `{{project_type}}` |
| `runtime_profile` | `{{runtime_profile}}` |
| `governance_mode` | `{{governance_mode}}` |
| `observability_stack` | `{{observability_stack}}` |
| `deployment_target` | `{{deployment_target}}` |
| `quality_profile` | `{{quality_profile}}` |

Interfaces:
{% for interface in interfaces -%}
- `{{interface}}`
{% endfor -%}

Summary hints:
{% for hint in questionnaire_summary_hints -%}
- `{{hint}}`
{% endfor -%}

---

## Project-Type Operating Model

{% if project_type == "cli_tool" -%}
- Build a command surface that is stable, scriptable, and fast under repeated local use.
- Prioritize deterministic output, explicit exit codes, and practical `--help` examples.
{% elif project_type == "service_api" -%}
- Optimize for predictable API contracts, safe change rollout, and operational clarity.
- Prioritize idempotency, schema stability, and measurable SLO behavior.
{% elif project_type == "event_worker" -%}
- Optimize for safe queue consumption, replayability, and backpressure handling.
- Prioritize idempotent handlers, dead-letter strategy, and runbook-grade diagnostics.
{% elif project_type == "web_app" -%}
- Optimize for user-visible responsiveness and resilient end-to-end flows.
- Prioritize first meaningful render, clear failure states, and release safety.
{% elif project_type == "library_sdk" -%}
- Optimize for consumer trust: predictable versioning, docs, and upgrade path.
- Prioritize API compatibility, typed examples, and migration notes.
{% endif -%}

---

## DX Contract

- Keep local iteration under 60 seconds for common edits.
- Expose one canonical command path for lint, test, and build.
- No silent fallback behavior; failures must be explicit and actionable.

### DX Profile Rules

{% if quality_profile == "fast_iterate" -%}
- Run lint + unit tests per commit; run broader suites on pull requests.
{% elif quality_profile == "strict" -%}
- Require lint, type checks, unit tests, and integration checks on pull requests.
{% elif quality_profile == "critical" -%}
- Require full test suite, security checks, and release-readiness gates before merge.
{% endif -%}

{% if runtime_profile == "low_latency" -%}
- Add p95/p99 performance checks to CI and block regressions.
{% elif runtime_profile == "throughput" -%}
- Add queue/load tests to verify saturation and drain behavior.
{% elif runtime_profile == "balanced" -%}
- Balance latency and resource consumption with baseline load tests.
{% elif runtime_profile == "cost_optimized" -%}
- Add cost-per-request or cost-per-job checks in CI reporting.
{% elif runtime_profile == "offline_first" -%}
- Verify disconnected workflows with deterministic fixtures and sync recovery tests.
{% endif -%}

---

## AX Contract

- Agents own implementation, validation, and evidence capture.
- Keep patches small, reversible, and grounded in file-level verification.
- Prefer explicit plans for risky or cross-module changes.

### Governance Rules

{% if governance_mode == "solo" -%}
- Move fast but keep checks mandatory; no unchecked merges.
{% elif governance_mode == "standard" -%}
- Require review notes for architectural or risk-bearing changes.
{% elif governance_mode == "strict" -%}
- Require explicit risk log, traceability, and rollback plan before release.
{% endif -%}

### Observability Rules

{% if observability_stack == "minimal_logs" -%}
- Structured logs are mandatory and include correlation IDs.
{% elif observability_stack == "otel_prometheus" -%}
- Emit metrics, traces, and logs with consistent service/env labels.
{% elif observability_stack == "datadog" -%}
- Standardize `service`, `env`, `version`, and `team` tags on all telemetry.
{% elif observability_stack == "sentry_first" -%}
- Treat release health and grouped error quality as first-class signals.
{% endif -%}

---

## UX Contract

- Every interface must define success, loading, and failure behavior.
- Error output must include context and a concrete next action.
- Docs are part of UX; keep setup and first-value path explicit.

### Interface Requirements

{% if "cli" in interfaces -%}
- CLI: guarantee deterministic output modes and stable exit codes.
{% endif -%}
{% if "http_api" in interfaces -%}
- HTTP API: publish error schema, idempotency rules, and timeout expectations.
{% endif -%}
{% if "web_ui" in interfaces -%}
- Web UI: define empty/loading/error states for all primary routes.
{% endif -%}
{% if "events" in interfaces -%}
- Events: document contract versions, replay policy, and dead-letter behavior.
{% endif -%}
{% if "sdk" in interfaces -%}
- SDK: ship copy-paste quickstarts plus typed examples for critical paths.
{% endif -%}
{% if "docs" in interfaces -%}
- Docs: maintain a zero-to-first-success quickstart path.
{% endif -%}

### Deployment Expectations

{% if deployment_target == "local_only" -%}
- Optimize one-command bootstrap and reset for local environments.
{% elif deployment_target == "container_platform" -%}
- Require health probes, graceful shutdown, and resource limits.
{% elif deployment_target == "serverless" -%}
- Optimize cold starts and enforce stateless retry-safe handlers.
{% elif deployment_target == "edge" -%}
- Keep runtime assumptions minimal and latency budget explicit.
{% elif deployment_target == "package_registry" -%}
- Ship semantic versioning discipline, changelog hygiene, and upgrade notes.
{% elif deployment_target == "on_prem" -%}
- Document upgrade, rollback, and compatibility checks in operator runbooks.
{% endif -%}

---

## Questionnaire Summary Prompts

{% if "primary_user_flow" in questionnaire_summary_hints -%}
- Primary user flow: write the shortest path from setup to first production value.
{% endif -%}
{% if "biggest_risk" in questionnaire_summary_hints -%}
- Biggest risk: identify one failure mode and its leading indicator.
{% endif -%}
{% if "rollback_plan" in questionnaire_summary_hints -%}
- Rollback plan: define trigger, command path, and verification signal.
{% endif -%}
{% if "cost_guardrails" in questionnaire_summary_hints -%}
- Cost guardrails: define budget cap, alert threshold, and owner action.
{% endif -%}
{% if "onboarding" in questionnaire_summary_hints -%}
- Onboarding: keep first contribution setup under 15 minutes.
{% endif -%}

---

## Quick Start

```bash
# Install dependencies
{% if language == "python" -%}
uv sync
{% elif language == "typescript" -%}
pnpm install
{% elif language == "go" -%}
go mod download
{% elif language == "bash" -%}
# bash projects usually only require toolchain checks
bash --version
{% endif -%}

# Validate baseline
task lint
task test
{% if include_docs -%}
task docs:build
{% endif -%}
```

---

## Project Structure

```
{{project_name}}/
├── src/                    # Source code
├── tests/                  # Test files
{% if include_docs -%}
├── docs/                   # Documentation
│   └── .vitepress/         # VitePress docsite
{% endif -%}
├── hooks/                  # Pre-commit hooks
{% if include_act -%}
├── scripts/                # CI simulation and local utility scripts
│   └── ci_local_gha.sh     # Local `act` runner
{% endif -%}
{% if include_pm_tools -%}
├── docs/reference/         # Work stream and PM-oriented operations docs
│   └── WORK_STREAM.md
{% endif -%}
├── Taskfile.yml            # Build automation
├── CLAUDE.md               # This file
{% if include_ci -%}
└── .github/workflows/      # CI workflows
{% endif -%}
```
