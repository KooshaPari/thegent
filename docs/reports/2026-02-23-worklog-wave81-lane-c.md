# Worklog Wave 81 - Lane C

Date: 2026-02-23

## WL-325 — Connector reconciliation initiative

### Status
- Still `BACKLOG` (P1) with no blocking dependencies; primary goal remains advancing connector reliability + retry/resume traceability before moving into execution.

### Gaps
- We have no dedicated reconciliation guardrail yet, so connectors that hit repeated retries or diverging remote state keep looping without deterministic recovery or clear operator signals (`thegent autosync` diagnostics highlight repeated retries and stale state as root causes).
- Connector health scoreboard and trend reporting are not wired into this initiative, so operators cannot prove that reconciliation runs are trending toward convergence before GA readiness is declared.

### Patch plan
1. Extend the mapping cache path that already lives under `src/thegent/integrations/connector_mapping_cache.py` so it records per-cycle reconciliation fingerprints and exposes a deterministic `last_applied` digest that can be replayed against the conflict queue (`docs/reference/WORK_STREAM.md:3720`).
2. Hook the reconciliation tracker into the existing reflection event log so every decision that replays or merges connector outputs gets a before/after snapshot, linking back to connector provenance and the circuit-breaker/timer metadata that already exists in `connector_timeout.py` and `connector_circuit_breaker.py` (`docs/reference/WORK_STREAM.md:3753`, `docs/reference/WORK_STREAM.md:3766`, `docs/reference/WORK_STREAM.md:3772`).
3. Surface that data through the autosync status artifacts so the connector health scoreboard and trend reporting gate referenced in the GA readiness criteria is satisfied (`docs/reference/AUTOSYNC_GA_READINESS_CRITERIA.md:18`).

### Validation
- Run the standard diagnostic sequence (`thegent sync work-stream`, `thegent sync autopilot --once`, `thegent sync autopilot-status`, inspect cycle artifacts) after injecting a controlled failure to confirm the reconciliation tracker emits the expected deterministic digest and clears the conflict queue per the troubleshooting matrix guidance (`docs/reference/AUTOSYNC_TROUBLESHOOTING_MATRIX.md:20`).
- Verify that repeated retries are now capped with a clear reconciliation outcome (pause/hard stop) so the same failure mode referenced in the matrix disappears (`docs/reference/AUTOSYNC_TROUBLESHOOTING_MATRIX.md:13`).

### Close criteria
- Reconciliation digests can be replayed deterministically without manual adjustments.
- Connector health scoreboard/trend artifact shows steady convergence after reconciliation runs, fulfilling the GA readiness checklist for this gate (`docs/reference/AUTOSYNC_GA_READINESS_CRITERIA.md:18`).

## WL-326 — Connector integrity initiative

### Status
- Still `BACKLOG` (P1) alongside WL-325; focus is ensuring connectors do not silently corrupt or lose state when retry/resume cycles execute.

### Gaps
- Integrity gaps remain because repeated retries currently hide whether local and remote items are consistent; the troubleshooting matrix recommends reconciling manifests against transition history, but we have neither the replay data nor the comparator in place yet (items stuck in conflict queue and divergence still observed) (`docs/reference/AUTOSYNC_TROUBLESHOOTING_MATRIX.md:14`).
- Operator-facing documentation does not yet explain how to verify that connector integrity holds after a checkpoint restore, which makes the GA readiness criteria (clear scoreboard/trend) unreachable without this initiative (`docs/reference/AUTOSYNC_GA_READINESS_CRITERIA.md:18`).

### Patch plan
1. Add an integrity guard within the mapping cache/circuit-braking stack so we capture the last good checkpoint for each connector and can verify that replayed artifacts match the stored digest before marking a cycle `PASS` (`docs/reference/WORK_STREAM.md:3727`, `docs/reference/WORK_STREAM.md:3766`).
2. Feed these integrity checkpoints into the reflection event log so each reconciliation decision carries the before/after and connector provenance needed for forensic review (`docs/reference/WORK_STREAM.md:3772`).
3. Publish the integrity verdicts to the autosync status artifacts so the readiness dashboard sees the trend (scoreboard gate) and we can prove the connector is not silently mutating local items (`docs/reference/AUTOSYNC_GA_READINESS_CRITERIA.md:18`).

### Validation
- Re-run the `thegent sync autopilot --once` sequence with injected divergence, then confirm the new integrity guard will either auto-reconcile or fail the cycle with a recorded mismatch before the conflict queue grows beyond one cycle (`docs/reference/AUTOSYNC_TROUBLESHOOTING_MATRIX.md:20`).
- Cross-check cycle manifests/manual transition logs to ensure no remote changes slip through without aligning with the checkpoint digest stored for that connector (`docs/reference/AUTOSYNC_TROUBLESHOOTING_MATRIX.md:14`).

### Close criteria
- Integrity guards block the run or reconcile automatically before downstream systems see divergent state.
- The connector health scoreboard/trend grab sees the failure/recovery pattern, satisfying the GA readiness gate and giving ops a reliable signal that integrity is enforced (`docs/reference/AUTOSYNC_GA_READINESS_CRITERIA.md:18`).
