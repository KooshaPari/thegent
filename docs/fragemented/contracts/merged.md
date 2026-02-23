# Merged Fragmented Markdown

## Source: contracts/ATOMS_CLEAN_DEPLOY_KNOWLEDGE_BASE.md

# Atoms Clean/Deploy Knowledge Base

## Purpose

This document is the cross-repo baseline for `atoms` clean/deploy behavior and environment discovery.
It codifies the canonical path and operational defaults used by this repo's automation and docs.

## 81) Cross-Repo Clean/Deploy Inventory

### `../atoms-mcp-prod`

| Surface | Source | Status |
|---|---|---|
| Clean entrypoint | `Taskfile.yml` -> `clean` target | Canonical |
| Clean CLI command | `cli.py` -> `clean()` (`atoms clean`) | Canonical |
| Vercel deployment config | `vercel.json` | Canonical |
| Deployment guide | `docs/DEPLOYMENT_GUIDE.md` | Canonical |
| Cloud Run helper | `scripts/deploy_gcp.sh` | Non-canonical (legacy helper)

### `../agentapi/atomsAgent`

| Surface | Source | Status |
|---|---|---|
| Cloud Run command surface | `src/atomsAgent/cli/commands/cloud_run.py` | Canonical |
| Cloud Run deploy docs | `docs/guides/deployment.md` | Canonical |
| Infrastructure target | `infrastructure/README.md` (IAC: SST Ion for Cloud Run) | Canonical |
| Legacy deploy path | Pulumi references removed from current flow | Deprecated |

## 82) Canonical Clean/Deploy Path (as used by thegent)

### Canonical path recommendation

For shared operations documented in thegent, **prefer Vercel-first clean/deploy for `atoms-mcp-prod` and SST/Cloud Run for `atomsAgent`**.

- Canonical for MCP server: `../atoms-mcp-prod`
  - Clean via `atoms clean` (`../atoms-mcp-prod/cli.py` / `Taskfile.yml`).
  - Deploy via Vercel (`vercel.json` + `docs/DEPLOYMENT_GUIDE.md`).
- Canonical for Agent API service: `../agentapi/atomsAgent`
  - Deploy via `atoms-agent cloud-run deploy` (`src/atomsAgent/cli/commands/cloud_run.py`).
  - IAC is driven by SST (`infrastructure/README.md`).

### Deprecated/legacy paths

- Legacy Pulumi flows and older Cloud Run wrappers are explicitly treated as non-canonical and should not be used for standard delivery paths.

## 83) Env-Discovery Contract (Institutionalized)

### Contract objective

Any tooling that needs Atoms deployment secrets/environment values MUST resolve them through an explicit, ordered search order before failing. This prevents implicit environment drift and makes local/CI behavior deterministic.

### Canonical discovery order (hard requirement)

1. In-process explicit environment variables.
2. Workspace-specific overrides in the current repo (`.env`, `.env.local`).
3. Canonical project-level `atoms.tech` env files in the sibling `clean/deploy/atoms.tech` workspace:
   - `../clean/deploy/atoms.tech/.env.local`
   - `../clean/deploy/atoms.tech/.env`
4. Upward workspace fallback `atoms.tech/.env` siblings when present in parent locations.
5. `config/secrets.yml` (repo-level secret file when allowed by deployment mode).

### Hard-fail check definition

The contract is now executable and SHALL fail hard when required variables are missing.

- Required for `atoms-mcp-prod` canonical deploy:
  - `SUPABASE_URL`
  - `SUPABASE_KEY`
  - `FASTMCP_SERVER_AUTH_AUTHKITPROVIDER_AUTHKIT_DOMAIN`
  - `FASTMCP_SERVER_AUTH_AUTHKITPROVIDER_BASE_URL`
  - `WORKOS_API_KEY`
  - `WORKOS_CLIENT_ID`
  - `CRON_SECRET`
- Required for `atomsAgent` canonical deploy:
  - `ATOMS_SECRET_AUTHKIT_JWKS_URL`
  - `ATOMS_SECRET_SUPABASE_URL`
  - `ATOMS_SECRET_SUPABASE_KEY`
  - `ATOMS_SECRET_VERTEX_PROJECT_ID`
  - `ATOMS_SECRET_VERTEX_LOCATION`

Legacy or optional variables (for debug/local workflows only) must never be treated as canonical gates.

Operational check command:

```bash
uv run python scripts/validate_atoms_env_discovery.py --repo atoms-mcp-prod
uv run python scripts/validate_atoms_env_discovery.py --repo atomsagent
```

Contract checks fail with non-zero exit codes and emit strict error details for the missing variable and the expected source path.

### Contract implementation notes

- `agentapi/atomsAgent/scripts/generate_supabase_models.py` follows this ordered fallback for env and secret lookup and remains the operational reference for DB model tooling.
- `thegent/scripts/validate_atoms_env_discovery.py` is the canonical hard-fail checker used by the gent for pre-deploy/CI validation.
- CI/ops tasks should treat missing mandatory environment variables as hard failures once this contract scope is invoked.
- Future env loader changes in sibling repos must update this section and the checker together in the same task.

## Operational Check

Before any release-like cleanup/deploy operation:
1. Verify the target repo path matches the canonical entry above.
2. Verify the command matches canonical clean/deploy operation.
3. Verify env inputs are present in at least one allowed source from the contract.
4. If env resolution requires additional sources, update this contract and source code together in the same task.

---

## Source: contracts/CONTRACT_AUTHORITY.md

# Contract Authority

**Status:** Authoritative
**Date:** 2026-02-14
**Scope:** Structured output contracts for thegent orchestration

---

## 1. Purpose

This document is the **single source of truth** for structured output contracts used by thegent. All agent outputs, XML protocols, and provider-specific formats normalize to the canonical schema defined here.

---

## 2. Contract Registry

| Contract ID | Version | Description | Compatibility |
|-------------|---------|-------------|---------------|
| csm | csm-v1 | Canonical Structured Message: unified schema | task-tool-18, zen-rich-v1 |
| task-tool | task-tool-18 | Task-tool 18-tag XML (snake_case) | csm-v1 |
| zen | zen-rich-v1 | Zen rich protocol (status, progress, actions, files) | csm-v1 |

---

## 3. Canonical Schema (CSM v1)

All agent outputs normalize to `CanonicalStructuredMessage`:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| task_id | str | No | Task identifier |
| run_id | str | No | Run correlation ID |
| chunk_id | str | No | Chunk identifier |
| status | enum | Yes | pending, in_progress, completed, failed, blocked, cancelled |
| phase | enum | No | planner, operator, reviewer, unknown |
| progress | float | No | 0.0–1.0 |
| objective | str | No | Task objective |
| summary | str | No | Condensed summary |
| actions_completed | list[str] | No | Completed action list |
| issues | list[str] | No | Issues encountered |
| next_steps | list[str] | No | Recommended next steps |
| evidence_set_hash | str | No | Governance evidence hash |
| policy_gate_id | str | No | Policy gate identifier |
| decision_reason_code | str | No | Decision rationale code |
| schema_version | str | Yes | Always "csm-v1" |
| source_contract | str | No | Original contract (task-tool-18, zen-rich-v1, etc.) |

---

## 4. Versioning Policy

- **contract_id**: Logical contract (csm, task-tool, zen).
- **version**: Semantic version string (e.g. csm-v1, task-tool-18).
- **compatible_with**: Versions that can be normalized to this contract.
- **deprecated**: If true, do not use for new integrations.

Migration: Use dual-read/dual-write windows when upgrading. Never remove a version without a deprecation period. See `docs/contracts/UPGRADE_PLAYBOOK.md` for upgrade, canary, and rollback procedures.

---

## 5. Adapter Contract

Provider adapters implement `OutputAdapter`:

- `provider`: Provider identifier (copilot, gemini, codex, claude, etc.)
- `normalize(raw, context) -> AdapterResult`: Convert raw output to CSM

Adapters must:
- Return `AdapterResult` with `csm` and `confidence` (0.0–1.0).
- Populate `parse_errors` on partial failure.
- Set `source_contract` when known.

---

## 6. Implementation Location

- **Registry**: `src/thegent/contracts/registry.py`
- **CSM schema**: `src/thegent/contracts/csm.py`
- **Adapters**: `src/thegent/contracts/adapters.py`
- **Provider contracts**: `docs/contracts/PROVIDER_ADAPTER_CONTRACTS.md`
- **Usage**: `from thegent.contracts import get_registry, CanonicalStructuredMessage, normalize_output`

---

## 7. Legacy Adapter (G-KD-01)

Legacy or non-XML outputs are handled via:

- **GenericOutputAdapter**: Uses `extract_condensed` for plain text; sets `source_contract=plain`, confidence 0.7.
- **Fallback path**: When XML adapter fails or no tags, `normalize_output` returns CSM with `source_contract=fallback-plain`, confidence 0.3–0.5.
- **Contract negotiation**: `source_contract` in CSM identifies origin (xml-tags, plain, fallback-plain). Policy gates may reject fallback-plain for critical lanes.

All adapters produce CSM with `schema_version="csm-v1"`. Legacy outputs are never rejected at parse time; they are normalized and tagged for policy decisions.

---

## 8. Fallback Control Plane

See **FALLBACK_POLICY.md** for normalization fallback policy, observability, and guardrails.

---

## 9. References

- Research validation: `docs/docset/thegent-research-validation-2026-02-14.md`
- Cross-analysis: `docs/docset/thegent-cross-analysis-matrix-2026-02-14.md`
- Kush docs: `docs/docset/thegent-kush-docs-deep-dive-2026-02-14.md`
- Gap analysis: `docs/docset/thegent-gaps-and-discovery-2026-02-14.md`
- **Task-tool XML contract (authoritative):** `../task-tool/docs/xml_contract.md` — aligned with implementation (task_graph root, snake_case tags)

---

## Source: contracts/FALLBACK_POLICY.md

# Fallback Control Plane

**Status:** Authoritative
**Date:** 2026-02-14
**Scope:** Normalization fallback policy for MCP and CLI

---

## 1. Purpose

When agent output cannot be normalized via a provider adapter (XML, JSON, etc.), thegent falls back to plain-text extraction. This document defines the **fallback control plane**: policy, observability, and guardrails that govern when fallback is acceptable.

---

## 2. Policy Configuration

| Config | Default | Description |
|--------|---------|--------------|
| `THGENT_NORMALIZATION_POLICY_ALLOW_FALLBACK` | true | Allow plain-text fallback when adapter fails |
| `THGENT_NORMALIZATION_POLICY_MIN_CONFIDENCE` | 0.4 | Minimum confidence threshold; below triggers policy violation |
| `THGENT_NORMALIZATION_POLICY_MAX_FALLBACK_RATE` | 0.3 | Max global fallback rate (30%); above triggers policy violation |
| `THGENT_NORMALIZATION_POLICY_STRICT_PROVIDERS` | "" | Comma-separated providers that must never use fallback |

---

## 3. Fallback Flow

1. **Adapter attempt:** Provider adapter (e.g. XMLOutputAdapter for gemini) normalizes raw output.
2. **On failure:** If adapter throws or returns parse_errors, fallback is considered.
3. **Fallback:** `extract_condensed()` produces a minimal CSM with `source_contract="fallback-plain"`, confidence 0.3–0.5.
4. **Policy evaluation:** `evaluate_fallback()` checks strict providers, confidence, global fallback rate.
5. **Telemetry:** `ContractTelemetry.record_normalization()` records fallback events for observability.

---

## 4. MCP and CLI Parity

Both MCP `thegent_run` and CLI `thegent run` use the same `run_with_failover` path, which:

- Calls `normalize_output(agent, raw)` after each run
- Evaluates `evaluate_fallback()` with config-driven `FallbackPolicy`
- Records to `ContractTelemetry` for drift detection

**MCP fallback policy** = same as CLI; no separate MCP-specific policy.

---

## 5. Observability

- **ContractTelemetry:** Tracks fallback rate per provider and globally.
- **Drift detection:** `detect_drift()` flags significant fallback rate increases.
- **Fallback KPIs (G-CA-02 B3):** `get_fallback_kpis()` returns structured metrics; `thegent observe kpis` for dashboard/alerting.
- **Parser-quality routing (G-CA-02 B2):** `rank_providers_by_parser_quality()` orders providers by confidence/fallback; enabled via `THGENT_ROUTING_PARSER_QUALITY_ENABLED`.
- **Session dir:** Telemetry stored under `THGENT_SESSION_DIR` (default `.thegent/sessions`).

---

## 6. Guardrails

| Guardrail | Behavior |
|-----------|----------|
| Critical lane (G-CA-03 C3) | `--lane critical` rejects runs with `source_contract` fallback-plain or unknown; run fails with error_class unknown_contract. |
| Strict provider | If provider in `strict_providers`, fallback is blocked; `SemanticValidationError` raised when `allow_fallback=False`. |
| Confidence threshold | Below `min_confidence_threshold` → policy violation logged. |
| Max fallback rate | Global rate > `max_fallback_rate` → policy violation logged. |
| Parse error class | `parse_truncated` from `extract_condensed_validated` → adapter result returned (no fallback to COMPLETED). |

---

## 7. Implementation

- **Policy:** `src/thegent/contracts/policy.py` — `FallbackPolicy`, `evaluate_fallback`
- **Config:** `src/thegent/config.py` — `normalization_policy_*`
- **Telemetry:** `src/thegent/contracts/telemetry.py` — `ContractTelemetry`
- **Usage:** `src/thegent/cli_impl.py` — `run_with_failover`

---

## See also

- [WORK_STREAM.md](../reference/WORK_STREAM.md) — canonical backlog
- [00-MASTER-INDEX.md](../plans/00-MASTER-INDEX.md) — plan index
- [PROVIDER_ADAPTER_CONTRACTS.md](./PROVIDER_ADAPTER_CONTRACTS.md) — adapter contracts

---

## Source: contracts/PROVIDER_ADAPTER_CONTRACTS.md

# Provider Adapter Contracts (G-RV-05)

**Purpose:** Document output contracts for copilot, gemini, codex, and claude adapters.
**Date:** 2026-02-14
**Scope:** WBS-X5 Provider Adapter Layer

---

## 1. Overview

Provider adapters normalize raw agent output into `CanonicalStructuredMessage` (CSM). All four primary providers (copilot, gemini, codex, claude) use the same XML-based contract. Adapters are implemented in `src/thegent/contracts/adapters.py`.

| Provider | Adapter | Source Contract | Notes |
|----------|---------|-----------------|-------|
| copilot | XMLOutputAdapter | task-tool-18 / xml-tags | GitHub Copilot CLI |
| gemini | XMLOutputAdapter | task-tool-18 / xml-tags | Google Gemini CLI |
| codex | XMLOutputAdapter | task-tool-18 / xml-tags | Codex proxy / cursor |
| claude | XMLOutputAdapter | task-tool-18 / xml-tags | Anthropic Claude CLI |
| cursor-agent | XMLOutputAdapter | task-tool-18 / xml-tags | Cursor agent |
| antigravity | XMLOutputAdapter | task-tool-18 / xml-tags | Proxy backend |

---

## 2. Shared XML Protocol

All providers emit XML tags in stdout. The parser extracts balanced tags `<TAG>content</TAG>` (case-insensitive).

### 2.1 Supported Tags → CSM Mapping

| XML Tag | CSM Field | Notes |
|---------|-----------|-------|
| STATUS, TASK_STATUS | status | pending, in_progress, completed, failed, blocked, cancelled, done→completed, skipped→cancelled |
| PROGRESS, TASK_PROGRESS, PERCENT_COMPLETE | progress | 0–100 or 0.0–1.0; normalized to 0.0–1.0 |
| TASK_ID, TASKID | task_id | |
| OBJECTIVE, TASK_OBJECTIVE | objective | |
| SUMMARY, TASK_SUMMARY, TASK_UPDATE, TASKUPDATE | summary | |
| ACTIONS_COMPLETED | actions_completed | Newline-separated list |
| ISSUES, TASK_ISSUES | issues | Newline-separated list |
| NEXT_STEPS, TASK_NEXT_STEPS | next_steps | Newline-separated list |

### 2.2 Status Normalization

```
pending, in_progress, completed, failed, blocked, cancelled
done → completed
skipped → cancelled
```

---

## 3. Per-Provider Contract Notes

### 3.1 Copilot

- **CLI:** `copilot` (GitHub Copilot CLI)
- **Output:** Stdout with XML tags; same tag set as task-tool-18
- **Fallback:** If no XML tags, `GenericOutputAdapter` or `extract_condensed` yields `source_contract=plain` with confidence 0.7

### 3.2 Gemini

- **CLI:** `gemini` (Google Gemini CLI)
- **Output:** Stdout with XML tags; supports task-tool-18 and zen-rich-v1
- **Fallback:** Same as copilot

### 3.3 Codex

- **CLI:** `cursor agent` or codex proxy
- **Output:** Stdout with XML tags; cursor-agent format compatible with task-tool-18
- **Fallback:** Same as copilot

### 3.4 Claude

- **CLI:** `claude` (Anthropic Claude CLI)
- **Output:** Stdout with XML tags; same tag set as task-tool-18
- **Fallback:** Same as copilot

---

## 4. Adapter Result Contract

Every adapter returns `AdapterResult`:

| Field | Type | Description |
|-------|------|--------------|
| csm | CanonicalStructuredMessage | Normalized output |
| confidence | float | 0.0–1.0; 1.0 = full parse, 0.7 = validation issues, 0.3–0.5 = fallback |
| parse_errors | list[str] | parse_truncated, no_xml_tags_detected, or validation issues |
| source_provider | str | Provider identifier |

---

## 5. Fallback Behavior

When `normalize_output(..., allow_fallback=True)`:

1. Try registered adapter (XMLOutputAdapter for primary providers)
2. If parse_truncated → return adapter result (do not fall back)
3. If adapter fails or no tags → fallback to `extract_condensed` with `source_contract=fallback-plain`, confidence 0.3–0.5
4. If `allow_fallback=False` → raise `SemanticValidationError`

---

## 6. Implementation Reference

- **Adapters:** `src/thegent/contracts/adapters.py`
- **Registry:** `ADAPTER_REGISTRY`, `get_adapter`, `register_adapter`
- **Normalization:** `normalize_output(provider, raw, context, allow_fallback)`
- **CSM schema:** `src/thegent/contracts/csm.py`
- **Parser:** `src/thegent/contracts/parser.py` (IncrementalXMLParser)

---

## 7. Conformance

- Run `thegent govern conformance` for adapter conformance suite
- Run `thegent govern conformance --check-drift` for drift alarms
- See `docs/contracts/FALLBACK_POLICY.md` for policy and observability

---

## See also

- [WORK_STREAM.md](../reference/WORK_STREAM.md) — canonical backlog
- [00-MASTER-INDEX.md](../plans/00-MASTER-INDEX.md) — plan index
- [FALLBACK_POLICY.md](./FALLBACK_POLICY.md) — fallback policy

---

## Source: contracts/TEST_HEALTH_DASHBOARD.md

# Pytest Health Dashboard and Alert Contract

## Scope

This document defines the pytest CI health signal contract used by `Taskfile` + GitHub Actions.

## 84) Observability Plumbing

### Source artifacts

The following files are produced by `task test:pr-gate`:

- `artifacts/pytest/collect/pr-collect.json`
- `artifacts/pytest/requirements/requirements-gate.json`
- `artifacts/pytest/pr/run.json`
- `artifacts/pytest/traceability/requirements-map.json`

### Health aggregation

`task test:health` aggregates the above into:

- `artifacts/pytest/health/pr-gate.json`
- `artifacts/pytest/health/pr-gate.md`

Command reference:

```bash
uv run python scripts/test_pytest_wave_artifacts.py health \
  --collect-artifact artifacts/pytest/collect/pr-collect.json \
  --requirements-gate-artifact artifacts/pytest/requirements/requirements-gate.json \
  --pr-run-artifact artifacts/pytest/pr/run.json \
  --requirements-map-artifact artifacts/pytest/traceability/requirements-map.json \
  --output artifacts/pytest/health/pr-gate.json \
  --summary artifacts/pytest/health/pr-gate.md \
  --strict \
  --fail-on-warning \
  --min-health-score 90
```

### Output contract (`artifacts/pytest/health/pr-gate.json`)

- `overall_status`: `passed` / `warn` / `failed`
- `overall_health_score`: integer 0-100
- `alerts`: array with `severity`, `code`, `title`, `details`, `artifact`, `recommended_action`
- `collect`, `requirements_gate`, `pr_run`, `requirements_map` sections preserve source artifact payloads for drill-down.
- `runbook`: contract thresholds used for this gate evaluation.

### Health scoring

- `error`: `-30`
- `warning`: `-10`
- `info`: `-3`

Default score range is `0..100` after penalty application.

## 85) CI Dashboard / Alert Surface

### CI behavior

In PR mode, CI runs `task test:pr-gate`, which now includes `health` aggregation.

- Workflow step prints alert summaries in logs for immediate visibility.
- Health alert artifact is uploaded via dedicated artifact upload name:
  - `pytest-health-${{ matrix.os }}-${{ matrix.python-version }}`

### Alert thresholds and severity mapping

- **Error**
  - Missing/invalid health input artifacts used in aggregation.
  - Pytest collect non-zero return code.
  - Collection errors > 0.
  - Mapped run failure (`status=failed` or non-zero return code).
- **Warning**
  - Collection budget exceeded.
  - Requirements gate blocked.
  - Uncovered low coverage ratio (< 0.95) in requirement map.
- **Info**
  - PR run fallback to fast lane.

### Runbook thresholds

- `requirements_map.requirement_coverage.coverage_ratio < 0.95` emits `warning`.
- `requirements.gate.blocked_count > 0` emits `warning`.
- `collect.over_budget == true` emits `warning`.
- Health score fail policy:
  - `>= 90`: pass
  - `80-89`: warn
  - `< 80`: fail

### CI gate command

- CI should call health aggregation with:
  - `--strict` (error alerts fail gate)
  - `--fail-on-warning` (warning alerts fail gate)
  - `--min-health-score 90` (hard minimum score)

### Alert handling

- Error alerts should be treated as gate-stopping defects.
- Warning alerts are required backlog items with owners and must be included in release notes if they indicate repeated failures.
- Info alerts should be reviewed before merge but can be tolerated when justified in PR context.

## 96) Requirements Extractor CLI Contract

`requirements-map` payload contract is considered a hard stability boundary.

Output contract (`artifacts/pytest/traceability/requirements-map.json`) must include:

- `schema_version` equals `requirements-map/v1`
- `generated_at`
- `record_count`
- `requirement_to_tests`
- `test_to_requirements`
- `trace_to_tests`
- `test_to_trace_requirements`
- `requirement_coverage`
- `secondary_evidence_coverage`

Command sample:

```bash
uv run python scripts/test_pytest_wave_artifacts.py requirements-map \
  --input-dir tests \
  --fr-tracker docs/reference/FR_TRACKER.md \
  --output artifacts/pytest/traceability/requirements-map.json \
  --csv-output artifacts/pytest/traceability/requirements-map.csv \
  --summary artifacts/pytest/traceability/requirements-map.md \
  --diagram-output artifacts/pytest/traceability/requirements-map.mdown \
  --diagram-max-nodes 100
```

## 97) Optional Lane Promotion Criteria Contract

`requirements-promotion-criteria` and `lane-promotion` are the promotion contracts for making optional lanes required.

Schema versions are:
- `lane-promotion-criteria/v1` for criteria payload
- `lane-promotion/v1` for lane-specific decision payload
Automation must emit:
- `criteria.required_stability_ratio`
- `criteria.required_stable_runs_required`
- `criteria.max_flake_ratio`
- `criteria.acceptable_fail_budget`
- `actual.run_count_threshold_met`
- `actual.health_score_threshold_met`
- `actual.stability_ratio`
- `actual.observed_flake_ratio`
Decision fields are:
- `recommendation.ready_for_lane_promotion`
- `recommendation.make_optional_lanes_required`
- `recommendation.reasons`
- `recommendation.ready_to_require_optional_lanes` from lane payload
- `promotion_plan`

## 98) One-Page FR Mapping Diagram Contract

`requirements-map` can emit a one-page Mermaid diagram and `requirements-diagram` can render directly from an artifact.

Diagram schema marker:
- `requirements-map-diagram/v1`
Generated artifacts:
- `artifacts/pytest/traceability/requirements-map.mdown`
- `artifacts/pytest/traceability/requirements-map.diagram.md`
Truncation behavior is controlled by `--diagram-max-nodes` on map and `--max-nodes` on diagram rendering; truncation is explicit with the warning line in output.

## 99) Quarterly Traceability Cleanup Routine

Quarterly cleanup uses `traceability-cleanup` and emits both debt and issue artifacts:

`artifacts/pytest/traceability/requirements-cleanup.json` uses schema `traceability-cleanup/v1`.
`artifacts/pytest/traceability/requirements-cleanup-issue.json` uses schema `traceability-cleanup-issue/v1`.

`test:traceability:quarterly-cleanup` is the Taskfile entrypoint for the routine and sets:

- stale window: `90` days
- issue threshold: `0` (open if any stale debt exists)
- issue contract output path (`--issue-output`)

---

## Source: contracts/UPGRADE_PLAYBOOK.md

# Contract Upgrade Playbook

**Status:** Authoritative
**Date:** 2026-02-14
**Scope:** Contract version upgrades, canary rollout, dual mode, rollback (G-RV-08)

---

## 1. Purpose

This playbook defines the operational process for upgrading contract versions (e.g., task-tool-18 → task-tool-20, csm-v1 → csm-v2). It covers dual-read/dual-write migration, canary rollout, and rollback steps.

---

## 2. Prerequisites

- **Contract registry** updated with new version and compatibility matrix (`src/thegent/contracts/registry.py`)
- **MigrationController** evaluates version status (`thegent govern migration <contract_id> <version>`)
- **Telemetry** in place for drift detection (`thegent observe drift`)
- **Fallback policy** configured per `docs/contracts/FALLBACK_POLICY.md`

---

## 3. Dual-Read / Dual-Write Migration

Use this pattern when introducing a new contract version that coexists with the old one.

### 3.1 Phases

| Phase | Read | Write | Duration |
|-------|------|-------|----------|
| **Dual-read** | Accept old + new formats | Emit old only | Until adapters support new |
| **Dual-write** | Accept old + new | Emit both old and new | Adoption ramp |
| **Cutover** | Accept new only | Emit new only | After adoption threshold |
| **Deprecation** | Reject old | Emit new only | After migration window |

### 3.2 Implementation

1. **Register new version** in `ContractRegistry` with `compatible_with` including the old version.
2. **Add adapter** that normalizes both old and new to canonical schema.
3. **Set `migration_window_end`** on the old version (ISO date) when it will be rejected.
4. **Run `thegent govern migration <contract_id> <version>`** to verify status.

### 3.3 Example

```python
# In registry: add task-tool-20, deprecate task-tool-18 with window
ContractVersion(
    contract_id="task-tool",
    version="task-tool-20",
    description="Task-tool 20-tag XML (extended)",
    compatible_with=("task-tool-18", "csm-v1"),
)
ContractVersion(
    contract_id="task-tool",
    version="task-tool-18",
    deprecated=True,
    migration_window_end="2026-04-01",  # After this, old version rejected
)
```

---

## 4. Canary Rollout

Progressive traffic ramp for new contract versions.

### 4.1 Stages

| Stage | Traffic % | Observation | Promotion Criteria |
|-------|-----------|-------------|--------------------|
| **Shadow** | 0% (log only) | Compare old vs new output | No errors in shadow |
| **Canary 1** | 1–5% | Monitor drift, fallback rate | Drift within budget |
| **Canary 2** | 10–25% | Same | No regression |
| **Canary 3** | 50% | Same | SLO met |
| **Full** | 100% | Same | — |

### 4.2 Configuration

Use environment or config to control canary percentage:

- `THGENT_CONTRACT_CANARY_PERCENT` (0–100): Percentage of runs using new version.
- `THGENT_CONTRACT_CANARY_PROVIDERS`: Comma-separated providers in canary (empty = all).

### 4.3 Checks Before Promotion

1. `thegent observe drift --structural-budget 5 --semantic-budget 10` — within budget.
2. `thegent govern conformance` — all adapters pass.
3. `thegent govern migration <contract_id> <version>` — allowed, status active.

---

## 5. Rollback Steps

### 5.1 Rollback Triggers

| Trigger | Action |
|---------|--------|
| Structural drift rate > budget | Pause canary, revert to old version |
| Semantic drift rate > budget | Pause canary, investigate |
| Fallback rate spike | Revert, check adapter |
| Conformance suite failure | Block promotion, fix adapter |
| Migration window expired | Old version rejected; ensure cutover complete |

### 5.2 Rollback Procedure

1. **Stop canary:** Set `THGENT_CONTRACT_CANARY_PERCENT=0` or disable canary in config.
2. **Revert registry:** If new version was promoted, mark deprecated and extend `migration_window_end` on old version.
3. **Restart services:** Ensure all processes pick up reverted config.
4. **Verify:** `thegent govern migration <contract_id> <old_version>` shows allowed.
5. **Post-mortem:** Capture drift events, adapter logs, and root cause.

### 5.3 Emergency Rollback

If production is impacted:

1. Set `THGENT_NORMALIZATION_POLICY_ALLOW_FALLBACK=true` (if not already) to allow plain-text fallback.
2. Disable canary immediately.
3. Notify on-call; follow incident playbook.
4. After stability, perform full rollback procedure above.

---

## 6. CLI Reference

| Command | Purpose |
|---------|---------|
| `thegent govern migration <contract_id> <version>` | Evaluate migration status for a version |
| `thegent govern migration --format json` | JSON output for automation |
| `thegent govern contracts` | List all contract versions |
| `thegent observe drift` | Check drift and alert budgets |
| `thegent govern conformance` | Run adapter conformance suite |

---

## 7. Checklist: New Contract Version

- [ ] Register new version in `ContractRegistry` with compatibility.
- [ ] Add or update adapter in `contracts/adapters.py`.
- [ ] Set `migration_window_end` on deprecated version.
- [ ] Run conformance: `thegent govern conformance`
- [ ] Enable shadow/canary with low percentage.
- [ ] Monitor `thegent observe drift` during ramp.
- [ ] Document rollback steps for this version.
- [ ] After cutover, remove old version from active use.

---

## 8. Related Documents

- `docs/contracts/CONTRACT_AUTHORITY.md` — Contract registry and schema
- `docs/contracts/FALLBACK_POLICY.md` — Fallback control plane
- `docs/VERIFICATION_RUNBOOK.md` — General verification checklist

---
