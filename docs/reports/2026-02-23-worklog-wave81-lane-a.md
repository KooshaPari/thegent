# Worklog Wave 81 Lane A report (2026-02-23)

## WL-321 Connector baseline initiative 321
**Status** ─ `docs/reference/WORK_STREAM.md:26755` still marks WL-321 as BACKLOG, so there is no dedicated lane implementation yet and the workstream entry remains the only record of the P1 connector-reliability goal.

**Gap list**
- Autosync can still spin a cycle against degraded connectors before giving up; the Wave 70 master triage explicitly called out a missing pre-apply probe that hard-fails on degraded endpoints (`docs/reports/2026-02-22-worklog-wave70-master.md:104`).
- The same packet also highlighted the lack of deterministic run telemetry/correlation IDs for connector traceability (`docs/reports/2026-02-22-worklog-wave70-master.md:294`), which blocks establishing a baseline before retry/resume behavior is exercised.

**Minimal patch plan**
1. Normalize `_probe_connectors` and the surrounding health-gate logic (`src/thegent/integrations/workstream_autosync.py:851` and `:1086`) so it returns immutable connector-status snapshots and feeds them into the cycle manifest/incident snapshot outputs defined around `_append_cycle_manifest` (`src/thegent/integrations/workstream_autosync.py:352`) and `_build_incident_snapshot_bundle` (`src/thegent/integrations/workstream_autosync.py:879`).
2. Extend the cycle manifest output schema (see `SyncCycleManifest` at `src/thegent/integrations/workstream_autosync_shared.py:534`) and the incident snapshot bundle so every completed cycle records connector health, the baseline signature (hash) of the last probe, and a resume token that callers can mirror into `autosync_status.json` or the failure queue.
3. Add/expand unit coverage in `tests/test_wl160_workstream_autosync.py:1248` to assert the new connector-baseline metadata lands in the manifest and incident snapshot artifacts before a cycle is marked success or failure.

**Validation commands**
- `python -m pytest tests/test_wl160_workstream_autosync.py -k "probe" -q` (covers the maintenance/probe scenarios at `tests/test_wl160_workstream_autosync.py:582`).
- `python -m pytest tests/test_wl201_sync_provenance.py -q` (validates the underlying provenance/stamp helpers referenced at `tests/test_wl201_sync_provenance.py:1`).

**Close criteria**
- The cycle manifest and incident snapshot artifacts no longer omit connector health/resume tokens (the log produced by `_append_cycle_manifest` and `_build_incident_snapshot_bundle` should include the new fields).
- A baseline failure now surfaces a deterministic `ConnectorHealthProbeResult` hash and resume token so autosync can either back off or replay from a known state.
- Once the new plumbing is wired, update `docs/reference/WORK_STREAM.md` to move WL-321 out of BACKLOG so the new implementation is traceable.

## WL-322 Connector validation initiative 322
**Status** ─ `docs/reference/WORK_STREAM.md:26766` keeps WL-322 in BACKLOG and no other file currently references the validation-and-traceable-outputs subplot, so the initiative still needs an actionable branch.

**Gap list**
- There is no consolidated provenance record for connector writes, which is why Wave 70 captured the missing run correlation IDs and the resulting traceability gaps (`docs/reports/2026-02-22-worklog-wave70-master.md:294`).
- The code already has a provenance helper (`src/thegent/integrations/sync_provenance.py:1`) but it is not yet wired to autosync outputs, so validation information remains fragmented and not machine-readable.

**Minimal patch plan**
1. Materialize a deterministic run/provenance stamp for every cycle using the structures in `src/thegent/integrations/sync_provenance.py:1-140`, populate it with the cycle UUID, operator name, `correlation_id`, and the computed BLAKE-resume hash (the helper already tracks `prev_hash`/`signature` fields).
2. Surface that stamp in `SyncCycleManifest.inputs`/`outputs` (via `_append_cycle_manifest` at `src/thegent/integrations/workstream_autosync.py:352`) and in the incident snapshot bundle (`src/thegent/integrations/workstream_autosync.py:879`), so downstream automation/validation actors can read a single `sync_id`/`cycle_number` combination when they retry or audit.
3. Expose the last stamp in `autosync_status.json` or manifest readers so CLI tooling and human operators can validate connector outputs against the recorded stamp before retrying; tests such as `tests/test_wl160_workstream_autosync.py:1248` already assert correlation IDs survive manifest writes, and `tests/test_wl201_sync_provenance.py:1` proves the stamp schema.

**Validation commands**
- `python -m pytest tests/test_wl201_sync_provenance.py -q` (ensures the stamp helpers stay deterministic and signature-friendly as shown at `tests/test_wl201_sync_provenance.py:1`).
- `python -m pytest tests/test_wl160_workstream_autosync.py -k "correlation" -q` (covers the manifest/incident snapshot assertions around lines `1248` and following).

**Close criteria**
- Every autosync cycle manifest/incident snapshot contains the new provenance stamp/validation payload and the CLI/documentation surfaces (`autosync_status.json`, cycle manifest reader) can resolve the same `sync_id`/`prev_hash` pair.
- Automation tests that rely on `SyncCycleManifest` inputs/outputs or `SyncProvenanceStamp` fields pass without workaround; the wall of traceable outputs described in the worklog entry is now reproducible from the artifacts.
- Update `docs/reference/WORK_STREAM.md` to reflect that WL-322 has moved into the implementation phase once these outputs are live.
