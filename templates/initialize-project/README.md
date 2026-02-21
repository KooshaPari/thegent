# Initialize-Project Template

Opinionated Copier template for bootstrapping projects with practical defaults for DX (developer experience), AX (agent experience), and UX (user experience).

## Usage

### Prerequisites

```bash
pip install copier
```

### Initialize a New Project

```bash
copier copy thegent/templates/initialize-project ./my-new-project
```

Use the interactive questionnaire and pick the profile that matches your actual runtime and delivery risk.

## Questionnaire Fields

| Field | Why it matters |
|---|---|
| `project_type` | Chooses the operating model for DX/AX/UX expectations |
| `runtime_profile` | Tunes latency/throughput/cost assumptions |
| `governance_mode` | Sets review and traceability strictness |
| `observability_stack` | Defines incident detection and debugging quality |
| `deployment_target` | Aligns build/release flow with runtime destination |
| `interfaces` | Declares external surfaces you must support |
| `quality_profile` | Sets the default test and gate intensity |
| `questionnaire_summary_hints` | Injects explicit planning prompts into `CLAUDE.md` |

## How To Answer: Project-Type Matrix

| Project type | Runtime profile | Governance | Observability | Deployment | Interfaces | Quality | Summary hints |
|---|---|---|---|---|---|---|---|
| `cli_tool` | `balanced` | `standard` | `minimal_logs` | `local_only` | `cli,docs` | `strict` | `primary_user_flow,biggest_risk` |
| `service_api` | `low_latency` | `standard` | `otel_prometheus` | `container_platform` | `http_api,docs` | `strict` | `primary_user_flow,biggest_risk,rollback_plan` |
| `event_worker` | `throughput` | `strict` | `otel_prometheus` | `serverless` | `events,docs` | `critical` | `biggest_risk,rollback_plan,cost_guardrails` |
| `web_app` | `low_latency` | `standard` | `sentry_first` | `edge` | `web_ui,http_api,docs` | `strict` | `primary_user_flow,biggest_risk,onboarding` |
| `library_sdk` | `cost_optimized` | `strict` | `minimal_logs` | `package_registry` | `sdk,docs` | `critical` | `primary_user_flow,onboarding,rollback_plan` |

Notes:
- If users wait on requests, bias toward `low_latency` plus `strict` or `critical` quality.
- If jobs queue and drain, bias toward `throughput` plus `critical` quality.
- If you choose `strict` governance, do not choose `fast_iterate` quality.

## What Gets Created

- `CLAUDE.md` - Project-specific instructions with DX/AX/UX contract
- `docs/governance/POLYGLOT_RUNTIME_DECISION_MATRIX.md` - Runtime and test governance baseline
- `Taskfile.yml` - Build automation with language-specific tasks
- `.gitignore` - Language-appropriate ignore file
- `.env.example` - Environment template
- `docs/` - VitePress docsite (if `include_docs=true`)
- `.github/workflows/ci.yml` - CI workflow (if `include_ci=true`)
- `hooks/` - Pre-commit hooks (if `include_hooks=true`)
- Docker files (if `include_docker=true`)

## Manual Template Selection

```bash
# CLAUDE.md template
cp thegent/templates/claude/CLAUDE.md.template ./CLAUDE.md

# Language-specific Taskfile
cp thegent/templates/python/Taskfile.python.yml ./Taskfile.yml

# Quality templates
cp thegent/templates/quality/ruff.toml ./ruff.toml
cp thegent/templates/quality/pyproject.template.toml ./pyproject.toml

# VitePress
cp -r thegent/templates/vitepress-full/* ./docs/.vitepress/
```
