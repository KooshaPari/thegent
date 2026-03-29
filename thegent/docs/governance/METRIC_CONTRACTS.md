# Metric Contracts

Hard governance contracts for:

- quality
- security
- reliability
- extensibility
- other code hygiene metrics

---

## Contract Files

- Active contract: `contracts/metric-contracts.json`
- Schema: `schemas/metric-contracts.schema.json`
- Reusable template: `templates/quality/metric-contracts.json`

---

## Gate

`hooks/governance-gates.sh` now includes `gate_metric_contracts` (fail-closed capable).

Gate report output:

- `.claude/verification/metric-contracts-gate.json`

Metrics report input (configurable in contract):

- default: `.claude/verification/quality-metrics.json`

---

## Enablement

`thegent setup` bootstraps both:

- `contracts/metric-contracts.json`
- `.claude/quality.json` with `governance.metric_contracts.enforce_gate=true`

Set in project `quality.json`:

```json
{
  "governance": {
    "metric_contracts": {
      "enforce_gate": true
    }
  }
}
```

On `critical` tier, this gate is also forced on by policy.

---

## Minimal Metrics Payload

```json
{
  "generated_at": "2026-02-20T00:00:00Z",
  "quality": { "lint_errors": 0, "type_errors": 0, "test_pass_rate": 1.0 },
  "security": { "critical_vulns": 0, "high_vulns": 0, "secrets_detected": 0 },
  "reliability": { "flake_rate": 0.0, "pass_rate": 1.0 },
  "extensibility": { "max_file_lines": 420, "max_function_lines": 45 },
  "other": { "todo_markers": 0 }
}
```
