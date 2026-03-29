# ADR-017: Unified Quality Control Plane

- Status: Accepted
- Date: 2026-02-22
- Owner: quality-platform

## Context

`thegent` now has a growing set of quality signals:

- hook result envelopes (`quality-gate`, `security-pipeline`)
- SARIF export bridge
- generated-code anti-pattern checker
- mutation/perf pilot artifacts

Without one control-plane decision, policy behavior drifts between local lanes and CI.

## Decision

Use **GitHub+SARIF-native** as the default control plane for unified quality in 2026.

- Canonical transport: SARIF + JSON side artifacts
- Canonical policy input: contract-backed artifacts under `artifacts/quality` and `artifacts/hooks`
- Sonar remains optional as a downstream adapter, not source-of-truth

## Rationale

- Lowest integration friction with existing GitHub checks and code-scanning workflows.
- Works with multi-tool and custom checker outputs uniformly.
- Keeps internal contracts explicit and portable, independent of vendor lock-in.

## Consequences

- Every new checker must define:
  - JSON artifact contract
  - optional SARIF adapter
  - deterministic task entry in `Taskfile.yml`
- CI promotion gates will consume contract-validated artifacts.
- Future Sonar integration should ingest from these artifacts, not bypass them.

## Rollout

1. Enforce control-plane policy contract in quality lanes.
2. Aggregate hook/checker artifacts into one quality summary artifact.
3. Promote non-blocking pilots to required checks after stability windows.
