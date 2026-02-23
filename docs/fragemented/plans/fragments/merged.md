# Merged Fragmented Markdown

## Source: plans/fragments/LANE_STRATEGY_MATRIX.md

# Lane Strategy Matrix for Hybrid Hook Runtime

## 1) Purpose and Scope
This matrix operationalizes `docs/plans/HOOK_POINT_HYBRID_LATENCY_MASTER_PLAN.md` into deterministic routing behavior for all supported hook points.

Goals:
- keep interactive latency bounded,
- preserve critical governance coverage,
- remove ambiguous fallback behavior,
- make lane selection and degradation operator-visible.

## 2) Lane Model: Options and Sub-Modes

### 2.1 Lane A: `instant`
Primary use: high-frequency, user-facing hooks where responsiveness dominates.

Sub-modes:
| Sub-mode | Intent | Allowed Work | Disallowed Work | Max Sync Budget |
|---|---|---|---|---|
| `A0-guard-only` | Pure local guardrail check | in-memory policy checks, cached metadata checks | spawn, shell, network, deep file parse | 40ms |
| `A1-guard-plus-enqueue` | Guard + full async deferral | `A0` + enqueue lane-C job | any unbounded sync task | 60ms |
| `A2-instant-reconcile` | Lightweight debt/reconcile pass | `A1` + bounded stale-state reconcile | tree scans, dependency audit, test execution | 100ms hard |

### 2.2 Lane B: `fast-safe`
Primary use: write/control surfaces that may block action.

Sub-modes:
| Sub-mode | Intent | Allowed Work | Disallowed Work | Max Sync Budget |
|---|---|---|---|---|
| `B0-changed-scope` | Narrow sync safety on changed artifacts | bounded shell/native checks on changed files only | repo-wide scans without cached index | 800ms |
| `B1-critical-write` | Stronger pre-write protections | `B0` + suppression/security write guards | full quality/security pipelines | 1500ms p99 |
| `B2-strong-gate` | temporary strict sync gate | `B1` + selected high-risk checks | non-essential advisory checks | 5000ms hard |

### 2.3 Lane C: `full`
Primary use: exhaustive correctness and compliance checks.

Sub-modes:
| Sub-mode | Intent | Execution | Typical Work | Budget Model |
|---|---|---|---|---|
| `C0-async-standard` | default exhaustive validation | async | quality gate, security pipeline, spec verifier, complexity, maturity | queue/SLO based |
| `C1-async-priority` | accelerated critical validation | async P1 queue | security-critical checks first | queue/SLO based |
| `C2-blocking-release` | hard enforcement path | blocking | full release/merge gate set | policy-defined, no interactive SLA |

## 3) Latency Budgets and Deadline Checkpoints

### 3.1 Sync checkpoint contract
| Lane | Soft Checkpoint 1 | Soft Checkpoint 2 | Hard Stop | Action at Hard Stop |
|---|---|---|---|---|
| `instant` | 60ms | 85ms | 100ms | stop sync checks, emit degrade artifact, enqueue full |
| `fast-safe` | 700ms | 1200ms | 5000ms | stop non-critical checks, keep mandatory guard set |
| `full` blocking | policy-specific | policy-specific | policy-specific | fail-closed on mandatory checks |

### 3.2 SLO targets
| Lane | p95 Target | p99 Target | Max |
|---|---|---|---|
| `instant` | <=80ms | <=100ms | 100ms |
| `fast-safe` | <=1200ms | <=1500ms | 5000ms |
| `full` async | n/a | n/a | governed by queue SLO |
| `full` blocking | profile-specific | profile-specific | policy cap only |

## 4) Routing Heuristics

### 4.1 Baseline hook defaults
| Hook Point | Default Lane | Default Sub-mode |
|---|---|---|
| `SessionStart` | `instant` | `A1-guard-plus-enqueue` |
| `UserPromptSubmit` / `PromptSubmit` | `instant` | `A1-guard-plus-enqueue` |
| `PreToolUse:Write/Edit` | `fast-safe` | `B1-critical-write` |
| `PreToolUse:Read/Exec/Non-write` | `instant` | `A0-guard-only` |
| `PostToolUse` | `instant` | `A0-guard-only` |
| `TaskCompleted` | `instant` | `A2-instant-reconcile` |
| `SubagentStop` | `instant` | `A2-instant-reconcile` |
| `Stop` | `fast-safe` | `B0-changed-scope` + `C0-async-standard` always enqueued |

### 4.2 Escalation and de-escalation heuristics
| Condition | Lane Change |
|---|---|
| security-sensitive file touched | escalate to `B2` or `C2` (profile-dependent) |
| dependency/infra manifest changed | escalate sync lane one level and force `C1` |
| repeated async critical findings in last N runs | force `B2` for next risky hook points |
| queue backlog above threshold and pending P1 findings | force strict mode for write/stop paths |
| low risk + warm cache + no debt | allow downgrade from `B1` to `A2` on explicitly safe hooks |

## 5) Risk Signals (Input Features for Router)

### 5.1 Content and artifact risk signals
| Signal ID | Signal | Weight | Typical Source |
|---|---|---|---|
| `R1` | touches security/auth/secret files | high | path classifier |
| `R2` | modifies dependency or lock manifests | high | diff classifier |
| `R3` | introduces suppression directives | high | write-time guard |
| `R4` | changes policy/config/hook dispatch files | high | path classifier |
| `R5` | high churn in critical files in short window | medium | rolling diff stats |
| `R6` | test or lint debt already outstanding | medium | async artifact ledger |
| `R7` | prior critical async finding unresolved | high | enforcement ledger |
| `R8` | only docs/comments touched | low | content classifier |

### 5.2 Runtime health risk signals
| Signal ID | Signal | Weight | Typical Source |
|---|---|---|---|
| `H1` | queue depth P1 above budget | high | queue telemetry |
| `H2` | cache cold/miss ratio high | medium | cache metrics |
| `H3` | hook timeout rate elevated | high | hook telemetry |
| `H4` | recent false negative / escaped defect | high | incident feed |
| `H5` | worker pool saturation | medium | runtime telemetry |

### 5.3 Risk tiering
| Score Band | Tier | Default Action |
|---|---|---|
| 0-19 | `T0-low` | keep default lane |
| 20-49 | `T1-elevated` | escalate sub-mode within same lane |
| 50-79 | `T2-high` | escalate to `fast-safe`/`B2` |
| 80+ | `T3-critical` | force `full` priority or blocking per profile |

## 6) Override Rules and Precedence

### 6.1 Precedence order (highest to lowest)
1. hard policy overrides (`release`, `strict`, explicit block states)
2. unresolved critical finding enforcement state
3. operator explicit override for current session
4. hook default route
5. adaptive optimization heuristics

### 6.2 Override catalog
| Override | Scope | Effect | Expiry |
|---|---|---|---|
| `profile=release` | session/workflow | force `C2` on required hooks | explicit reset |
| `profile=strict` | session | force `B1/B2`, disallow `A0` on write paths | explicit reset |
| `override:lane=instant` | single hook or session | pin to `A*` where policy allows | timed or manual clear |
| `override:lane=fast-safe` | single hook or session | pin to `B*` | timed or manual clear |
| `override:ack-token` | action-level | allows continuation after acknowledged async finding | one-time |
| `enforcement:block-next-risky-action` | session | blocks risky write/stop until condition clears | auto-clear on remediation |

### 6.3 Non-bypassable rules
| Rule | Behavior |
|---|---|
| unresolved critical security finding | cannot route risky hooks to `A*` |
| release/merge guarded path | cannot skip `C2` |
| hard budget breach in sync lane | must degrade deterministically and emit artifact |
| missing required policy artifact | fail closed for gated hook points |

## 7) Degrade Semantics

### 7.1 Degrade stages
| Stage | Trigger | Behavior | Operator Visibility |
|---|---|---|---|
| `D0-none` | within budget and healthy state | full planned sync checks run | normal summary |
| `D1-trim-advisory` | soft checkpoint 1 reached | drop advisory sync checks, keep mandatory | summary marks `degraded=advisory_trimmed` |
| `D2-trim-noncritical` | soft checkpoint 2 reached | run mandatory-only sync set, enqueue rest | summary marks `degraded=mandatory_only` |
| `D3-fail-closed-or-defer` | hard stop reached | fail/hold if mandatory incomplete; otherwise defer to async with enforcement | explicit warning + queue id + enforcement state |

### 7.2 Degrade invariants
- no silent skip of mandatory checks,
- every skipped/deferred check emits artifact with reason,
- every degrade event includes lane, sub-mode, deadline checkpoint, and replay token,
- degraded sync behavior always pairs with lane-C enqueue unless policy blocks continuation.

## 8) Decision Tables by Hook Point

## 8.1 `SessionStart`
| Input Condition | Route | Budget | Degrade Rule | Enforcement Result |
|---|---|---|---|---|
| clean state, warm cache | `A1` | 60ms | `D1` at 40ms | enqueue `C0` baseline health checks |
| stale queue debt present | `A2` | 100ms | `D2` at 85ms | enqueue `C1` debt reconciliation |
| unresolved critical finding | `B0` | 800ms | `D2` at 700ms | require acknowledgment token before risky hooks |

## 8.2 `UserPromptSubmit` / `PromptSubmit`
| Input Condition | Route | Budget | Degrade Rule | Enforcement Result |
|---|---|---|---|---|
| normal prompt, no sensitive triggers | `A1` | 60ms | `D1` at 40ms | async full scan queued |
| sensitive pattern or policy trigger | `B0` | 800ms | `D2` at 700ms | prompt may be blocked/rewritten per policy |
| repeated sensitive triggers + unresolved findings | `B2` | 5000ms | `D3` at hard stop | block until explicit acknowledgment/remediation |

## 8.3 `PreToolUse:Write/Edit`
| Input Condition | Route | Budget | Degrade Rule | Enforcement Result |
|---|---|---|---|---|
| low-risk write, docs-only, no suppression | `B0` | 800ms | `D1` at 700ms | allow + enqueue `C0` |
| code/config write with medium risk | `B1` | 1500ms p99 | `D2` at 1200ms | allow if mandatory set passes |
| security/policy/manifest write or unresolved critical debt | `B2` | 5000ms | `D3` at hard stop | block on mandatory failure; force `C1`/`C2` |

## 8.4 `PreToolUse:Non-write`
| Input Condition | Route | Budget | Degrade Rule | Enforcement Result |
|---|---|---|---|---|
| read/list/search operations | `A0` | 40ms | `D1` at 30ms | continue |
| non-write touching sensitive path metadata | `A2` | 100ms | `D2` at 85ms | enqueue targeted async review |
| strict/release profile active | `B0` | 800ms | `D2` at 700ms | continue with stronger checks |

## 8.5 `PostToolUse`
| Input Condition | Route | Budget | Degrade Rule | Enforcement Result |
|---|---|---|---|---|
| tool succeeded, low-risk output | `A0` | 40ms | `D1` at 30ms | continue |
| tool failed or suspicious output markers | `A2` | 100ms | `D2` at 85ms | enqueue `C1` follow-up |
| high-risk write just completed | `B0` | 800ms | `D2` at 700ms | force artifact and next-hook escalation |

## 8.6 `TaskCompleted`
| Input Condition | Route | Budget | Degrade Rule | Enforcement Result |
|---|---|---|---|---|
| no pending debt | `A2` | 100ms | `D2` at 85ms | emit completion summary |
| pending async critical checks | `B0` | 800ms | `D2` at 700ms | gate completion or require ack |
| strict/release profile | `B1` | 1500ms p99 | `D2` at 1200ms | completion blocked on mandatory outcomes |

## 8.7 `SubagentStop`
| Input Condition | Route | Budget | Degrade Rule | Enforcement Result |
|---|---|---|---|---|
| non-critical subagent task | `A2` | 100ms | `D2` at 85ms | async reconciliation queued |
| critical file paths touched | `B1` | 1500ms p99 | `D2` at 1200ms | escalate next parent hook lane |
| repeated subagent violations | `B2` | 5000ms | `D3` at hard stop | block propagation until reviewed |

## 8.8 `Stop`
| Input Condition | Route | Budget | Degrade Rule | Enforcement Result |
|---|---|---|---|---|
| normal interactive session end | `B0` + `C0` enqueue | 800ms sync | `D2` at 700ms | emit debt ledger + async job ids |
| elevated risk or unresolved critical findings | `B1` + `C1` enqueue | 1500ms p99 | `D2` at 1200ms | block risky continuation next session |
| release/merge/prod stop path | `C2` blocking | policy | fail closed | full gate required before success |

## 9) Operator UX and Observability

### 9.1 Per-hook UX payload (required)
| Field | Description |
|---|---|
| `hook_point` | event name |
| `lane` / `sub_mode` | selected route |
| `risk_tier` | `T0-T3` with numeric score |
| `budget_ms` / `elapsed_ms` | latency contract and measured runtime |
| `degrade_stage` | `D0-D3` |
| `checks_run` | mandatory/advisory check ids executed |
| `checks_deferred` | deferred check ids + reason |
| `async_queue_ids` | queued lane-C jobs |
| `enforcement_state` | none, ack-required, blocked-next, blocked-now |
| `override_source` | policy, operator, auto-escalation, none |

### 9.2 Operator-facing messages
| Scenario | UX Message Requirement |
|---|---|
| lane escalation | show trigger signal(s) and resulting lane shift |
| degrade occurred | show checkpoint reached and exact checks deferred |
| action blocked | show mandatory check that failed and remediation path |
| async critical finding | show finding id, impact, and next-hook enforcement |
| override applied | show who/what applied it and expiry |

### 9.3 Dashboards and alerts
| Metric | Alert Threshold | Action |
|---|---|---|
| `instant_p99_ms` | >100ms for 5m | investigate hot-path regression |
| `fastsafe_p99_ms` | >1500ms for 10m | inspect bounded checks and cache health |
| `queue_p1_oldest_age_s` | >60s | force strict escalation on risky hooks |
| `degrade_rate_by_hook` | sudden spike >2x baseline | inspect load/cold cache/loop hotspots |
| `blocked_actions_count` | trend up >30% day-over-day | tune policy or remediate recurring failures |

## 10) Implementation Notes for Router Consistency
- Use deterministic scoring for risk tier; avoid non-reproducible heuristics.
- Keep a versioned routing policy (`routing_policy_version`) in each hook artifact.
- Persist last enforcement state per session to avoid lost escalation on restart.
- Coalesce duplicate async jobs by `(hook_point, commit/config fingerprint, check set)`.
- If queue health violates SLO, auto-promote risky hooks one lane up until recovery.

## 11) Minimal Compliance Checklist
| Requirement | Pass Criterion |
|---|---|
| lane chosen for every hook point | no `unknown` lane events |
| hard budgets enforced | zero hard-stop overruns without `D3` record |
| no silent deferrals | every deferred check has reason + queue id |
| critical findings enforced | `critical finding -> enforcement action` always recorded |
| operator clarity | hook summary always includes lane + reason |

## 12) Change Control
This matrix is the executable policy reference for lane routing. Any change must update:
- lane/sub-mode definitions,
- risk signal catalog,
- hook-point decision tables,
- operator-visible semantics,
- latency SLO expectations.

---

## Source: plans/fragments/NO_REGRESSION_ENFORCEMENT.md

# No-Regression Enforcement for Hybrid Sync/Async Checks

## Scope and Intent
This fragment defines how hybrid lane execution preserves governance coverage when heavy checks move from sync to async. It operationalizes the master plan contract: no silent check drops, deterministic enforcement, and auditable policy actions.

Goals:
- preserve safety/quality/security outcomes while reducing sync latency,
- make async findings enforceable in near-real-time,
- provide explicit operator workflows for acknowledgment and exceptions,
- guarantee forensic traceability for every deferred/blocked/overridden decision.

## Definitions
- `sync lane`: `instant` or `fast-safe` execution during hook handling.
- `async lane`: `full` checks executed through durable queue workers.
- `artifact`: immutable record of a check result or deferral decision.
- `critical finding`: policy-mapped severity requiring immediate enforcement action.
- `block-next`: policy flag that prevents next risky mutation/release action until resolved.
- `ack token`: time-bound, actor-bound override grant tied to explicit finding IDs.

## Enforcement Invariants (No-Regression Contract)
1. Every deferred or skipped heavy check MUST emit an async artifact with queue/job identity.
2. Every async completion MUST emit a terminal artifact (`passed`, `failed`, `error`, `expired`).
3. Any `critical` or `high` finding in protected domains MUST trigger at least one enforcement action:
   - `block-next`, or
   - `strict-escalation`, or
   - `hard-block-now` (for release/prod profiles).
4. No enforcement action may be implicit; all transitions must be ledgered with actor, reason, and timestamps.
5. If async subsystem health is degraded beyond SLO, router MUST fail closed to stricter sync behavior per profile.

## Async Artifact Model

### Required Artifact Types
- `check.deferred`: sync lane deferred a heavy check to async.
- `check.started`: async worker picked job.
- `check.result`: normalized finding payload and verdict.
- `enforcement.applied`: block/escalation/action committed.
- `ack.issued`: acknowledgment token created.
- `ack.used`: token consumed to permit a guarded action.
- `exception.granted`: temporary policy exception approved.
- `exception.expired`: exception auto-expired.
- `system.degraded`: queue/worker/SLO degradation event.

### Artifact Data Contract (JSON example)
```json
{
  "artifact_id": "art_01JZ9YQ2A7E6M8",
  "artifact_type": "check.result",
  "created_at": "2026-02-18T02:15:21.943Z",
  "repo": "thegent",
  "commit": "a1b2c3d4",
  "hook_point": "Stop",
  "lane": "full",
  "trace_id": "tr_01JZ9YQ1ZZM5",
  "job": {
    "queue_id": "q_01JZ9YQ1V7",
    "job_id": "job_01JZ9YQ1X8",
    "priority": "P1",
    "attempt": 1
  },
  "check": {
    "check_id": "security-pipeline",
    "version": "2026.02.18",
    "scope": ["src/hooks/runtime/router.rs", "Cargo.lock"],
    "defer_reason": "lane_budget_exceeded"
  },
  "result": {
    "status": "failed",
    "severity_max": "critical",
    "finding_count": 2,
    "finding_ids": ["SEC-2026-441", "SEC-2026-445"]
  },
  "policy": {
    "decision": "block-next",
    "decision_reason": "critical finding in protected file class",
    "effective_until": "2026-02-18T03:15:21.943Z"
  },
  "actor": {
    "type": "system",
    "id": "hook-worker-3"
  },
  "signature": "sha256:..."
}
```

## Block-Next Policy

### What It Blocks
`block-next` is evaluated on the next risky action class:
- `write` to protected paths,
- `dependency` manifest updates,
- `release`/`merge` gates,
- `prod` deployment hooks.

Non-risky read-only actions remain permitted.

### Block-Next State Contract
```json
{
  "block_id": "blk_01JZ9Z5S4T",
  "repo": "thegent",
  "active": true,
  "trigger": {
    "finding_ids": ["SEC-2026-441"],
    "severity": "critical",
    "source_artifact_id": "art_01JZ9YQ2A7E6M8"
  },
  "scope": {
    "action_classes": ["write", "release"],
    "paths": ["src/**", "Cargo.lock"]
  },
  "created_at": "2026-02-18T02:15:22.101Z",
  "expires_at": null,
  "lift_condition": "finding_resolved_or_valid_ack",
  "status_reason": "pending remediation"
}
```

### Deterministic Evaluation Pseudocode
```text
onHookAction(action, context):
  active_blocks = ledger.getActiveBlocks(context.repo)
  matching = filter(active_blocks, b => action.class in b.scope.action_classes
                                 && pathMatches(action.paths, b.scope.paths))

  if matching is empty:
    allow()

  valid_ack = ackStore.findValidAck(
    repo=context.repo,
    actor=context.actor,
    action=action,
    finding_ids=union(matching.trigger.finding_ids)
  )

  if valid_ack exists:
    emit(ack.used, valid_ack, action)
    allow_with_audit("allowed_by_ack")

  deny("blocked_by_async_critical_finding", details=matching)
  emit(enforcement.applied, decision="block", details=matching)
```

## Acknowledgment Workflow

### When Ack Is Allowed
Ack is policy-controlled and allowed only when:
- finding severity is `high` or `critical` and profile permits human override,
- actor has required role/authority,
- ack includes ticket/reference and explicit reason,
- TTL is bounded and short (default 30 minutes),
- scope is minimal (specific findings + specific action class).

### Ack Token Contract
```json
{
  "ack_id": "ack_01JZ9ZCXRH",
  "repo": "thegent",
  "issued_by": "user:koosha",
  "issued_at": "2026-02-18T02:20:00.000Z",
  "expires_at": "2026-02-18T02:50:00.000Z",
  "finding_ids": ["SEC-2026-441"],
  "allow": {
    "action_classes": ["write"],
    "paths": ["src/hooks/runtime/**"]
  },
  "justification": "Hotfix required; follow-up remediation tracked as SEC-908",
  "external_ref": "SEC-908",
  "single_use": true,
  "signature": "sha256:..."
}
```

### Ack Guardrails
- Never reusable across repositories.
- Invalidated automatically on superseding critical findings.
- Auto-revoked if async recheck increases severity or scope.

## Exception Handling Policy

### Exception Types
- `timeboxed-exception`: temporary bypass for explicitly scoped operations.
- `environment-exception`: operational outage mode with fail-closed fallback requirements.
- `false-positive-exception`: requires evidence and check-rule reference.

### Mandatory Exception Fields
- exception ID, owner, approver, rationale, evidence links,
- exact scope (check IDs, paths, action classes),
- explicit expiration timestamp,
- rollback/remediation plan reference.

### Exception Enforcement Rules
- Default deny when exception record is missing required fields.
- Expired exceptions are not soft-failed; they are immediately non-effective.
- Exception usage emits `exception.used` audit artifacts per action.

## Auditability and Forensics

### Ledger Requirements
- Append-only artifact ledger (logical immutability).
- Monotonic sequence per repo + globally unique IDs.
- Tamper-evident hashing/signature chain.
- Query surfaces by `trace_id`, `finding_id`, `block_id`, `ack_id`, and `hook_point`.

### Minimum Audit Queries
- "Show all deferred checks without terminal results > X minutes."
- "Show all active blocks and their origin findings."
- "Show all actions allowed via ack in last 24h."
- "Show all exceptions expiring in next 60 minutes."

### Audit Event Example
```json
{
  "event": "enforcement.applied",
  "timestamp": "2026-02-18T02:15:22.101Z",
  "repo": "thegent",
  "trace_id": "tr_01JZ9YQ1ZZM5",
  "decision": "block",
  "action_attempted": "PreToolUse:Write",
  "reason": "critical finding SEC-2026-441",
  "operator_visible_message": "Write blocked: resolve SEC-2026-441 or provide valid ack token"
}
```

## Failure Modes and Required Behavior

| Failure Mode | Detection | Required Behavior | Operator Signal |
|---|---|---|---|
| Async queue backlog > SLO | queue depth + age thresholds | fail closed to stricter sync lane for protected actions | `system.degraded` + lane escalation notice |
| Worker crash loop | heartbeat + restart counter | pause low-priority jobs, preserve P1, apply conservative block-next for unresolved critical debt | active incident banner |
| Missing terminal artifacts | deferred-result timeout monitor | mark job `expired`, trigger requeue or strict fallback, emit audit event | explicit debt warning with IDs |
| Ledger unavailable | write-path health check | deny risky actions; allow read-only operations only | hard error with remediation instructions |
| Clock skew/token expiry inconsistency | monotonic check + signature time window | invalidate affected ack/exception tokens and require reissue | token invalid message |
| Duplicate/out-of-order artifacts | idempotency key + sequence validation | dedupe, preserve first valid terminal state, emit anomaly artifact | anomaly warning |
| Policy config corruption | checksum/signature validation | reject config and load last known good; strict mode for protected actions | config rollback alert |

## End-to-End Enforcement Pseudocode
```text
onSyncHook(hookPoint, action, context):
  lane = routeLane(hookPoint, action, context)
  syncResult = runSyncChecksWithBudget(lane, context)

  for each deferredCheck in syncResult.deferred:
    job = enqueueAsync(deferredCheck, context)
    emit(check.deferred, deferredCheck, job)

  decision = evaluateImmediatePolicy(syncResult, context)
  if decision == deny:
    emit(enforcement.applied, decision="deny", reason=decision.reason)
    return blocked

  return allowed

onAsyncResult(result, context):
  emit(check.result, result)

  enforcement = mapFindingsToPolicy(result.findings, context.profile)
  switch enforcement.type:
    case none:
      return
    case block_next:
      block = createOrUpdateBlock(context.repo, enforcement.scope, result.finding_ids)
      emit(enforcement.applied, decision="block-next", block_id=block.id)
    case escalate_strict:
      setRepoMode(context.repo, "strict", ttl=enforcement.ttl)
      emit(enforcement.applied, decision="strict-escalation")
    case hard_block_now:
      setRepoMode(context.repo, "release")
      emit(enforcement.applied, decision="hard-block-now")
```

## Operational Defaults (Recommended)
- `critical finding -> block-next` immediately.
- `>=2 critical findings in 60m -> strict escalation for 30m`.
- `async critical enforcement latency target <=60s`.
- `ack TTL 30m`, single-use for `critical` by default.
- `exception max TTL 24h`, requires approver different from requester.

## Acceptance Criteria
- 100% of deferred checks create artifacts and queue IDs.
- 100% of async jobs end in terminal artifact state.
- All critical findings in protected domains produce recorded enforcement action.
- Blocked actions return deterministic, user-actionable reasons.
- Audit queries can reconstruct complete decision chains from finding to action.

## Open Implementation Notes
- Keep enforcement mapping data-driven (policy table), not hard-coded per check.
- Use idempotency keys (`repo+commit+hook+check+scope-hash`) to avoid duplicate enforcement churn.
- Ensure compatibility with mode profiles from the master plan (`instant`, `interactive`, `strict`, `release`).

---

## Source: plans/fragments/PERF_OPTIMIZATION_PLAYBOOK.md

# Performance Optimization Playbook for Hybrid Hook Runtime

## Scope
This playbook defines concrete optimization tactics to keep the hybrid hook runtime within:
- `instant` lane: `<=100ms` end-to-end per hook point.
- `fast-safe` lane: `<=1.5s` p99 and `<=5s` hard cap.

It complements `docs/plans/HOOK_POINT_HYBRID_LATENCY_MASTER_PLAN.md` by detailing hot-path behavior, queueing design, contention control, and enforcement-grade regression gates.

## Performance Envelope Budgeting

### End-to-End Budget Split
Use explicit micro-budgets to prevent local regressions from consuming the entire envelope.

| Lane | Router + risk classify | Check execution | State/cache IO | Serialization + response | Guard band | Total |
|---|---:|---:|---:|---:|---:|---:|
| `instant` | 10ms | 45ms | 15ms | 10ms | 20ms | 100ms |
| `fast-safe` | 80ms | 900ms | 220ms | 120ms | 180ms | 1500ms |

Guard band is reserved for variance and must not be allocated to default workload.

### Deadline Checkpoints
- `instant` checkpoint 1 at `60ms`: stop non-critical advisory checks; emit deferral artifacts.
- `instant` checkpoint 2 at `85ms`: finalize only mandatory allow/block decision path.
- `fast-safe` checkpoint at `1200ms`: stop lower-priority bounded probes and flush result.
- Hard cutoff: deterministic decision at lane cap, never unbounded waiting.

## Hot-Path Micro-Optimizations

### Dispatcher and Routing
- Keep a single in-process dispatch path with no subprocess spawn in `instant`.
- Precompile rule tables at config-load time; avoid per-hook dynamic parsing.
- Use integer severity/risk enums and array-indexed jump tables instead of map-heavy dynamic branching.
- Normalize file/path metadata once per hook event; pass immutable references through all checks.

### Allocation and Data Movement
- Reuse per-thread/per-worker scratch buffers for path sets, finding lists, and JSON builders.
- Prefer borrowed slices/views over cloning full path collections.
- Cap synchronous artifact payload size; persist full detail async when needed.
- Avoid repeated hash recomputation by carrying precomputed event fingerprint.

### IO and Process Boundaries
- In `instant`, disallow filesystem tree walks and shell-outs entirely.
- In `fast-safe`, allow only bounded, whitelisted commands with strict per-command timeouts.
- Move expensive normalization (glob expansion, classification resolution) to precomputed indexes.

### Deterministic Degrade Rules
- Degrade order: advisory checks -> non-critical enrichments -> expensive formatting.
- Never degrade mandatory policy checks required for allow/block correctness.
- Every degradation emits `check.deferred` artifact with `defer_reason` and queue identity.

## Queue and Admission Design

### Queue Topology
Use a durable multi-priority queue for `full` lane jobs:
- `P1`: security-critical and release-impacting checks.
- `P2`: quality/spec/complexity checks.
- `P3`: advisory/reporting checks.

Each job key should include `(repo, branch, commit, hook_point, check_set_hash)` for dedupe/coalescing.

### Admission Control
- Global in-flight cap per repository to prevent one repo starving others.
- Per-priority token buckets to preserve `P1` latency under load.
- If backlog breaches threshold, shed `P3` first and preserve `P1`/`P2`.
- Promote repeated failing `P2` jobs touching protected domains to `P1`.

### Coalescing and Deduplication
- Coalesce superseded jobs for same `(repo, check_set_hash)` keeping latest commit only.
- Cancel stale jobs when newer equivalent context exists and no enforcement dependency remains.
- Keep enforcement-relevant terminal artifacts even when job execution is skipped due to coalescing.

### Backpressure and Fail-Closed Behavior
- If queue delay SLO for `P1` exceeds policy threshold, router escalates sync lane (`instant` -> `fast-safe` or `strict`).
- If async subsystem is unhealthy, fail closed for risky action classes using stricter sync checks.
- Expose backlog depth, oldest-age, and processing rate as first-class health signals.

## Cache Strategy

### Cache Layers
- `L1` in-memory cache per process for hot rule/config structures.
- `L2` shared local persistent cache for file classification and check metadata.
- `L3` artifact ledger/index for async enforcement and audit lookups.

### Cache Keys and Invalidation
Key by immutable fingerprints:
- code state: `head_commit` or equivalent snapshot ID,
- policy state: `config_fingerprint`,
- check behavior: `check_version`.

Invalidate on:
- policy/config change,
- dependency manifest class changes,
- protected-path classifier schema updates.

### Warmup and Precomputation
- Prewarm lane router, path classifiers, and hot regex/rule sets on `SessionStart`.
- Maintain incremental changed-file index updated per write/edit event.
- Build and refresh protected-path bloom/filter structures out-of-band.

### Cache Safety Rules
- Never serve stale cache entries across mismatched `config_fingerprint`.
- Stale-or-miss behavior must be deterministic and policy-safe (compute or defer, never guess).
- Cache read timeout in sync lanes must be bounded; fallback path must remain within lane budget.

## Lock and Contention Tactics

### Contention Model
Primary contention points:
- active block/ack state store,
- async artifact ledger append path,
- shared changed-file index updates,
- queue admission counters.

### Tactics
- Prefer immutable snapshots + atomic pointer swaps for read-heavy config/rule data.
- Use sharded locks by repository and data class (ledger, block state, index).
- Keep critical sections minimal: compute outside lock, commit state inside lock.
- Use lock-free read paths where correctness permits (epoch/version checks).
- Apply single-writer batching for artifact append to reduce lock churn.

### Anti-Patterns to Ban
- Global mutex around full hook evaluation.
- Holding locks across IO, serialization, or network waits.
- Nested lock ordering without a strict documented hierarchy.

### Lock SLOs
- p99 lock wait in `instant` critical path: `<=2ms` per acquisition.
- p99 total lock wait per `instant` hook: `<=8ms`.
- Alert when lock-wait share exceeds 15% of lane budget.

## Measurement and Experiment Plan

### Required Instrumentation
Emit per-hook structured timings with shared `trace_id`:
- route/classify,
- cache lookup,
- each check unit,
- artifact emit,
- queue enqueue/dequeue,
- enforcement evaluation.

Track distribution metrics: `p50`, `p95`, `p99`, `max`, plus error/timeout/defer counts.

### Benchmark Matrix
Run repeatable perf suites across:
- hook points: `PromptSubmit`, `PreToolUse:Write/Edit`, `PostToolUse`, `Stop`.
- repo sizes: small/medium/large changed-set scenarios.
- cache states: cold, warm, partially invalidated.
- load states: nominal, bursty, overload.

### Tail-Latency Investigation Protocol
- For any p99 breach, break down by segment share and isolate top contributors.
- Use variance-focused analysis (not only means): identify bimodal distributions and long-tail causes.
- Confirm no correctness regressions while applying micro-optimizations.

### Acceptance Criteria
- `instant`: p99 `<=100ms` with deterministic cap enforcement in certified scenarios.
- `fast-safe`: p99 `<=1.5s`, max `<=5s`.
- Async `P1` finding-to-enforcement latency meets configured threshold (default `<=60s`).

## CI Regression Gates

### Perf Gates (Required)
- Gate 1: `instant` p99 must not exceed baseline + 5ms and never exceed 100ms.
- Gate 2: `fast-safe` p99 must not exceed baseline + 100ms and never exceed 1.5s.
- Gate 3: max latency hard-cap violations (`instant >100ms`, `fast-safe >5s`) fail CI immediately.
- Gate 4: lock-wait share and queue backlog age must remain within policy bounds.

### Correctness + Coverage Gates
- Ensure deferred checks still produce terminal async artifacts.
- Ensure critical async findings trigger enforcement (`block-next`, escalation, or hard block) deterministically.
- Ensure no silent skip: every skipped/deferred check requires explicit artifact reason.

### Benchmark Governance in CI
- Use fixed benchmark fixtures and deterministic load profiles.
- Compare against rolling baseline from mainline with noise-aware tolerance bands.
- Run short PR perf suite on every change touching hook runtime; run full suite on nightly and release branches.

### Degradation and Rollback Triggers
- Automatic strict-mode escalation in staging when perf/correctness gates fail repeatedly.
- Auto-block rollout promotion when any critical gate fails.
- Require green perf + correctness trend over consecutive runs before re-enabling progressive rollout.

## Execution Roadmap (Phased WBS + DAG)

| Phase | Task ID | Description | Depends On |
|---|---|---|---|
| P1 | P1.1 | Define segment budgets and checkpoint rules per lane | - |
| P1 | P1.2 | Add fine-grained timing instrumentation and trace IDs | P1.1 |
| P2 | P2.1 | Apply hot-path allocation/dispatch optimizations | P1.2 |
| P2 | P2.2 | Implement deterministic degrade policy ordering | P2.1 |
| P3 | P3.1 | Implement queue admission, coalescing, and backpressure | P1.2 |
| P3 | P3.2 | Add fail-closed escalation on async health degradation | P3.1 |
| P4 | P4.1 | Implement multi-layer cache keying and invalidation | P2.1 |
| P4 | P4.2 | Add prewarm and incremental index refresh | P4.1 |
| P5 | P5.1 | Apply lock sharding/snapshot strategy and lock SLO telemetry | P2.1 |
| P5 | P5.2 | Remove lock anti-patterns and validate contention reduction | P5.1 |
| P6 | P6.1 | Build reproducible benchmark matrix and tail-latency diagnostics | P2.2, P3.2, P4.2, P5.2 |
| P6 | P6.2 | Wire CI perf/correctness regression gates | P6.1 |
| P7 | P7.1 | Shadow run and tune thresholds with production-like load | P6.2 |
| P7 | P7.2 | Promote to default interactive mode with enforced gates | P7.1 |

## Operational Checklist
- Lane budgets are explicitly configured and checkpointed.
- No subprocess/network/tree-scan behavior exists in `instant` lane.
- Async queue exposes backlog age and priority health signals.
- Cache keying includes code + policy fingerprints.
- Lock-wait metrics are tracked and gated.
- CI fails on latency-cap breaches and silent deferral gaps.

---

## Source: plans/fragments/ROLLOUT_AND_OPERATIONS.md

# Rollout and Operations Runbook for Hybrid Lane System

## Scope
This runbook defines how to safely roll out and operate the hybrid lane system (`instant`, `fast-safe`, `full`) from the current `fast` profile baseline.

It covers:
- phased rollout and promotion gates,
- kill-switches and rollback behavior,
- observability and SLO dashboards,
- incident response and on-call procedures,
- migration steps from current `fast` profile.

References:
- `docs/plans/HOOK_POINT_HYBRID_LATENCY_MASTER_PLAN.md`
- `docs/plans/fragments/LANE_STRATEGY_MATRIX.md`
- `docs/plans/fragments/NO_REGRESSION_ENFORCEMENT.md`
- `docs/plans/fragments/PERF_OPTIMIZATION_PLAYBOOK.md`

## Operational Objectives
- Maintain interactive responsiveness:
  - `instant` lane: p99 `<=100ms`, hard cap `100ms`.
  - `fast-safe` lane: p99 `<=1.5s`, hard cap `<=5s`.
- Preserve coverage and enforcement:
  - no silent check drops,
  - async critical findings enforce within `<=60s`,
  - block/ack/escalation states always auditable.
- Enable fast, low-risk fallback to known-safe behavior (`fast` profile equivalent).

## Preconditions and Readiness Checklist
- Lane router with deterministic policy precedence is enabled.
- Async queue supports `P1/P2/P3` priorities, dedupe, and backlog telemetry.
- Artifact ledger is available for defer/result/enforcement events.
- Kill-switch configuration is wired and testable in staging.
- Dashboards/alerts are provisioned before first production exposure.
- Runbook drill completed at least once in staging:
  - force backlog breach,
  - verify auto-escalation,
  - execute rollback.

## Phased Rollout Plan (WBS + DAG)

| Phase | Task ID | Description | Depends On |
|---|---|---|---|
| R0 | R0.1 | Baseline current `fast` profile metrics (latency, block rate, queue age=0 baseline) | - |
| R0 | R0.2 | Validate kill-switches and rollback path in staging | R0.1 |
| R1 | R1.1 | Shadow mode: route decisions computed, no enforcement changes | R0.2 |
| R1 | R1.2 | Compare shadow vs current outcomes (false positives/negatives, latency overhead) | R1.1 |
| R2 | R2.1 | Canary 5% sessions/repos with `interactive` profile (`A/B` sync + `C` async) | R1.2 |
| R2 | R2.2 | Enable block-next enforcement only for `P1 critical` findings in canary | R2.1 |
| R3 | R3.1 | Expand to 25% then 50% after stable SLO windows | R2.2 |
| R3 | R3.2 | Enable acknowledgment flow and strict escalation automation | R3.1 |
| R4 | R4.1 | Default-on `interactive` for all non-release paths | R3.2 |
| R4 | R4.2 | Keep `release` profile as blocking full checks (`C2`) | R4.1 |
| R5 | R5.1 | Post-rollout hardening: tune thresholds, reduce alert noise, finalize SOP | R4.2 |

Promotion gate for each phase:
- latency SLOs green for two consecutive windows,
- no increase in escaped critical defects,
- async `P1` enforcement latency within objective,
- rollback drill remains passing.

## Kill-Switches and Rollback Controls

### Kill-Switch Catalog
| Switch | Scope | Default | Effect |
|---|---|---|---|
| `HYBRID_ENABLED` | global | `true` (post-rollout) | master toggle for hybrid router |
| `LANE_INSTANT_ENABLED` | global/hook | `true` | disables `instant`; routes to `fast-safe` |
| `ASYNC_ENFORCEMENT_ENABLED` | global | `true` | disables block/ack from async findings; sync checks still run |
| `ENFORCEMENT_MODE` | session/profile | `normal` | `normal`/`strict`/`fail_closed` |
| `FORCE_PROFILE` | session/repo | unset | pins routing to `fast` or `release` behavior |
| `QUEUE_ADMISSION_LIMIT` | queue | tuned | throttles async intake under overload |

### Emergency Rollback Modes
1. `soft rollback`: disable `instant` lane only.
2. `policy rollback`: disable async enforcement, keep telemetry and async artifacts.
3. `full rollback`: disable hybrid and force current `fast` profile semantics.

Rollback target:
- rollback command/config takes effect in `<5 minutes`,
- routing summaries visibly show fallback profile and reason.

## Migration from Current `fast` Profile

### Baseline (Current State)
- `fast` profile governs interactive paths with bounded sync checks.
- limited/no lane-A path for ultra-low-latency hooks.
- full checks often tied to heavier stop/reconcile windows.

### Migration Steps
1. Capture `fast` baseline:
   - hook latency (`p50/p95/p99/max`) by hook point,
   - current block/allow rates,
   - defect escape and incident baseline.
2. Introduce hybrid in shadow mode:
   - compute lane decisions,
   - emit artifacts without changing allow/block behavior.
3. Enable `interactive` profile in canary:
   - `PromptSubmit`/high-frequency hooks use `instant`,
   - write-sensitive hooks stay `fast-safe`,
   - always enqueue `full` async.
4. Turn on async critical enforcement for canary:
   - begin with `P1 critical` only,
   - validate `block-next` and ack token behavior.
5. Progressively expand population:
   - 5% -> 25% -> 50% -> 100%,
   - hold or rollback on any gate violation.
6. Keep release path unchanged:
   - `release` profile remains blocking full checks (`C2`).
7. Decommission legacy-only `fast` routing once stability is sustained.

### Data and State Compatibility
- Preserve existing policy IDs and finding IDs.
- Map legacy block states into new enforcement ledger schema.
- Ensure historical trend continuity by tagging metrics with `profile` and `routing_policy_version`.

## Observability and Telemetry

### Required Metrics
| Domain | Metric | Target/Alert |
|---|---|---|
| latency | `instant_p99_ms` | alert if `>100ms` for 5m |
| latency | `fastsafe_p99_ms` | alert if `>1500ms` for 10m |
| cap breaches | `instant_hard_cap_violations` | page if `>0` sustained 5m |
| cap breaches | `fastsafe_hard_cap_violations` | page if sustained breach |
| async health | `queue_p1_oldest_age_s` | alert `>60s`, page `>180s` |
| async health | `queue_depth_by_priority` | alert on rapid growth + low drain |
| enforcement | `block_next_active_count` | trend, alert on spike >2x baseline |
| enforcement | `ack_issued_total` / `ack_used_total` | anomaly alert on sudden increase |
| quality | `deferred_without_terminal_result` | alert if non-zero over SLA |

### Required Structured Fields Per Hook Event
- `trace_id`
- `hook_point`
- `lane` and `sub_mode`
- `risk_tier` and route reason
- `elapsed_ms` and budget
- `degrade_stage`
- `checks_run` and `checks_deferred`
- `async_queue_ids`
- `enforcement_state`
- `routing_policy_version`

## SLO Dashboards

### Dashboard 1: Interactive Latency
- Charts:
  - `p50/p95/p99/max` by lane and hook point,
  - hard cap violations by minute,
  - degrade stage distribution (`D0-D3`).
- Primary question:
  - Are interactive hooks within lane contracts?

### Dashboard 2: Async Correctness and Throughput
- Charts:
  - queue depth and oldest age by priority,
  - job start-to-terminal latency,
  - deferred-to-terminal completion rate.
- Primary question:
  - Is async keeping up with required enforcement latency?

### Dashboard 3: Enforcement and Safety
- Charts:
  - active blocks over time,
  - blocked actions by action class,
  - ack issuance/use and expiration,
  - unresolved critical findings age.
- Primary question:
  - Are critical findings deterministically enforced without operator confusion?

### Dashboard 4: Rollout Health
- Charts:
  - adoption by phase/cohort,
  - rollback count and reason,
  - incident count by profile/version.
- Primary question:
  - Can rollout continue, or must promotion pause?

## Incident Response Runbook

### Severity Model
| Severity | Definition | Initial Action |
|---|---|---|
| SEV-1 | broad policy bypass risk or sustained critical enforcement failure | trigger rollback mode 2 or 3 immediately |
| SEV-2 | SLO breach with enforcement intact | disable `instant` lane and stabilize |
| SEV-3 | localized degradation or alert noise | keep rollout frozen, investigate and patch |

### Triage Decision Tree
1. Is enforcement correctness at risk?
   - Yes: rollback first, investigate second.
2. Is latency SLO breach isolated to `instant`?
   - Yes: disable `instant`, keep `fast-safe` + async.
3. Is async queue P1 backlog above threshold?
   - Yes: force strict for risky hooks and shed lower priorities.
4. Is ledger unavailable?
   - Yes: fail closed for risky actions; permit read-only operations.

### First 15 Minutes Checklist
1. Freeze rollout promotion.
2. Capture incident context:
   - active profile(s),
   - routing policy version,
   - failing metrics and earliest timestamp.
3. Execute relevant kill-switch mode.
4. Confirm fallback behavior in live hook summaries.
5. Open incident channel/ticket with trace IDs and affected cohorts.

### Recovery and Exit Criteria
- SLOs within target for two consecutive windows.
- No missing terminal artifacts.
- No unresolved critical findings aging beyond enforcement SLA.
- One staged canary verification pass after mitigation before re-expansion.

## On-Call Operations

### Daily Checks
- queue P1 oldest age and drain rate,
- active block count and oldest unresolved block age,
- hard cap violation count by lane,
- ack token usage trend and top issuers,
- rollback switch status.

### Weekly Reliability Review
- compare hybrid vs legacy `fast` defect/escape rates,
- tune risk routing thresholds,
- review top incident root causes,
- retire temporary overrides and stale exceptions.

## Change Management and Safe Deploy
- Deploy routing/enforcement changes behind versioned policy flags.
- Roll out policy versions progressively; never all-at-once.
- Require staging replay against recorded traces before production policy promotion.
- Keep last-known-good policy bundle available for immediate rollback.

## Validation Checklist Before Marking Rollout Complete
- `interactive` default-on for target scope.
- all four dashboards active with alert routing tested.
- rollback modes tested in staging within last 7 days.
- incident SOP exercised at least once with time-to-mitigate recorded.
- release profile still enforces blocking full checks.
- legacy `fast` fallback remains available and documented.

---
