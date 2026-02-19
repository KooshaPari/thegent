# execution API Reference

> **Source**: `src/thegent/execution.py`

Execution run metadata and registry for thegent orchestration.

---

## Auditor

Provides integrity verification for the run registry.

### Methods

#### Auditor.__init__

```python
__init__(self, registry_path)
```

#### Auditor.generate_maif_artifact

Generate a signed MAIF artifact for a run (WP-3002).

```python
generate_maif_artifact(self, run, output)
```

#### Auditor.persist_maif_artifact

Persist a MAIF artifact to the artifacts directory (WP-3002).

```python
persist_maif_artifact(self, session_dir, artifact)
```

#### Auditor.sign_run

Generate a cryptographic signature for a run record.

```python
sign_run(self, run)
```

#### Auditor.verify_registry

Verify the integrity of all records in the registry, including the hash chain.

```python
verify_registry(self)
```

---

## CalibrationRegistry

WP-4008: Persists calibration factors and curves for agents (G-GP-09).

### Methods

#### CalibrationRegistry.__init__

```python
__init__(self, session_dir)
```

#### CalibrationRegistry.get_factor

Return the persisted calibration factor for an agent.

```python
get_factor(self, agent)
```

#### CalibrationRegistry.update_agent

Persist a new calibration factor for an agent.

```python
update_agent(self, agent, factor, sample_size)
```

---

## CheckpointMeta

Metadata for a DAG/state checkpoint.

**Inherits from**: `BaseModel`

---

## CheckpointRegistry

Manages persistence and retrieval of state checkpoints.

### Methods

#### CheckpointRegistry.__init__

```python
__init__(self, session_dir)
```

#### CheckpointRegistry.create_checkpoint

Record a new checkpoint.

```python
create_checkpoint(self, reason, dag_content, owner)
```

#### CheckpointRegistry.get_checkpoint

Retrieve a specific checkpoint.

```python
get_checkpoint(self, checkpoint_id)
```

#### CheckpointRegistry.list_checkpoints

List recent checkpoints.

```python
list_checkpoints(self, limit)
```

---

## CircuitBreakerRegistry

Tracks failures and manages circuit states for models/agents.

### Methods

#### CircuitBreakerRegistry.__init__

```python
__init__(self, session_dir, threshold, window_s, recovery_s)
```

#### CircuitBreakerRegistry.is_open

Check if the circuit for a target in a category is open (blocked).

```python
is_open(self, target, category)
```

#### CircuitBreakerRegistry.record_failure

Record a failure for a target in a specific category.

```python
record_failure(self, target, category)
```

---

## ConcurrencyController

WP-5001: Adaptive concurrency controller with lane enforcement.

### Methods

#### ConcurrencyController.__init__

```python
__init__(self, session_dir, max_concurrency)
```

#### ConcurrencyController.acquire

Acquire a concurrency slot. Critical lane can bypass if under absolute limit.

```python
acquire(self, lane)
```

---

## ContinuityWatchdog

WP-5005: Background watchdog for stale ownership and automatic handoffs.

### Methods

#### ContinuityWatchdog.__init__

```python
__init__(self, session_dir)
```

#### ContinuityWatchdog.scan_stale_sessions

Scan for sessions with no activity for max_idle_s.

```python
scan_stale_sessions(self, max_idle_s)
```

#### ContinuityWatchdog.trigger_auto_handoff

Automatically trigger a handoff for a stale session (WP-5006).

```python
trigger_auto_handoff(self, session_id, _backup_owner)
```

---

## DLQManager

WP-Y2: Dead-Letter Queue (DLQ) for permanently failing items.

### Methods

#### DLQManager.__init__

```python
__init__(self, session_dir)
```

#### DLQManager.enqueue

Add a failing run to the DLQ.

```python
enqueue(self, run_meta, error)
```

#### DLQManager.list_items

List items in the DLQ with optional filtering.

```python
list_items(self, status, run_id)
```

#### DLQManager.resolve

Mark a DLQ item as resolved (e.g. replayed, fixed).

```python
resolve(self, run_id, resolution)
```

---

## DeferralQueue

WP-5004: Manages non-critical tasks deferred during burst load.

### Methods

#### DeferralQueue.__init__

```python
__init__(self, session_dir)
```

#### DeferralQueue.defer

Defer a task with an estimated time to resume.

```python
defer(self, run_id, reason, eta_s)
```

---

## EscalationQueue

WP-3008: Governance queue for blocked decisions with SLA tracking.

### Methods

#### EscalationQueue.__init__

```python
__init__(self, session_dir)
```

#### EscalationQueue.add

Add a blocked run to the escalation queue.

```python
add(self, run_id, reason, sla_minutes, owner, agent, lane, priority)
```

#### EscalationQueue.list_pending

List escalation items. If past_sla_only, return only items past escalate_by.

```python
list_pending(self, past_sla_only, limit)
```

#### EscalationQueue.resolve

Mark an escalation item as resolved. Returns True if found and updated.

```python
resolve(self, run_id, resolution)
```

---

## EvidenceLinter

WP-2007: Checks evidence struct completeness and consistency.

### Methods

#### EvidenceLinter.__init__

```python
__init__(self, session_dir)
```

#### EvidenceLinter.lint

Verify CSM evidence is complete based on phase.

```python
lint(self, csm)
```

---

## FreshnessValidator

WP-4005: Detects stale state and enforces refresh logic.

### Methods

#### FreshnessValidator.__init__

```python
__init__(self, session_dir)
```

#### FreshnessValidator.is_stale

Check if a file or registry is stale.

```python
is_stale(self, path, max_age_s)
```

#### FreshnessValidator.validate_action

Validate if the action is safe to perform based on context freshness.

```python
validate_action(self, run_id, context_files)
```

---

## HandoffManager

WP-4006/9004: Manages shift handoffs and continuity snapshots with enforcement.

### Methods

#### HandoffManager.__init__

```python
__init__(self, session_dir)
```

#### HandoffManager.confirm_handoff

WP-9004/12005: Incoming owner confirms handoff completeness with confidence.

```python
confirm_handoff(self, snapshot_id, incoming_owner, confidence)
```

#### HandoffManager.create_snapshot

Create a continuity snapshot for a handoff.

```python
create_snapshot(self, owner, run_ids)
```

#### HandoffManager.is_handoff_enforced

WP-9004: Check if a run is blocked by a pending handoff confirmation.

```python
is_handoff_enforced(self, run_id)
```

#### HandoffManager.verify_integrity

Verify the integrity of a handoff snapshot.

```python
verify_integrity(self, snapshot_id)
```

---

## IdempotencyManager

WP-1003: Ensures idempotent execution using 4-tuple keys.

### Methods

#### IdempotencyManager.__init__

```python
__init__(self, session_dir)
```

#### IdempotencyManager.check_and_record

Check if key exists in registry; return True if already executed.

```python
check_and_record(self, registry, key)
```

#### IdempotencyManager.generate_key

Generate a 4-tuple idempotency key (run_id, step, action, hash).

```python
generate_key(self, run_id, step_index, action_type, content)
```

---

## InterruptionTracker

WP-4004: Fatigue tracking and interruption controls.

### Methods

#### InterruptionTracker.__init__

```python
__init__(self, session_dir)
```

#### InterruptionTracker.get_fatigue_score

Calculate fatigue score based on recent interruptions (0.0-1.0).

```python
get_fatigue_score(self, window_s)
```

#### InterruptionTracker.record_interruption

Record an agent interruption event.

```python
record_interruption(self, run_id, severity)
```

---

## KPIManager

WP-Y7: TRAFFIC KPI framework (10-metric).

### Methods

#### KPIManager.__init__

```python
__init__(self, session_dir)
```

#### KPIManager.get_kpis

Calculate the 10 core KPIs for the dashboard.

```python
get_kpis(self)
```

---

## LaneController

WP-1002: Priority and urgency lane model for task management.

### Methods

#### LaneController.__init__

```python
__init__(self, session_dir, capacity)
```

#### LaneController.check_capacity

Check if a lane has capacity to run (starvation prevention).

```python
check_capacity(self, lane)
```

#### LaneController.get_lane_priority

Return numeric priority for a lane (lower is higher priority).

```python
get_lane_priority(self, lane)
```

#### LaneController.sort_tasks

Sort tasks by lane priority and then by creation time.

```python
sort_tasks(self, tasks)
```

---

## LoadClassifier

WP-5002: Classifies system load and detects burst conditions.

### Methods

#### LoadClassifier.__init__

```python
__init__(self, session_dir)
```

#### LoadClassifier.get_load_level

Return current load level: normal, high, burst.

```python
get_load_level(self)
```

---

## MAIFArtifact

WP-3002: Model AI Information Format (MAIF) for signed artifacts.

**Inherits from**: `BaseModel`

---

## OverrideRegistry

Stores policy overrides with TTL. WP-3003: revalidation on expiry.

### Methods

#### OverrideRegistry.__init__

```python
__init__(self, session_dir)
```

#### OverrideRegistry.has_unexpired

True if owner has an override that has not yet expired.

```python
has_unexpired(self, owner)
```

#### OverrideRegistry.record

Record an override; valid until now + ttl_seconds.

```python
record(self, owner, reason, ttl_seconds)
```

---

## PolicyEngine

Evaluates execution requests against governance policies.

### Methods

#### PolicyEngine.__init__

```python
__init__(self, settings)
```

#### PolicyEngine.evaluate

Evaluate a run against active policies.
Returns (result, reason) where result is 'allow', 'deny', or 'warn'.
G-GP-01: When THGENT_OPA_URL is set, delegates to OPA first; falls back to Python logic on failure.

```python
evaluate(self, run, registry)
```

---

## ProviderScorer

WP-Y8/11008: Continuous scoring and learning loop with policy guardrails.

### Methods

#### ProviderScorer.__init__

```python
__init__(self, session_dir)
```

#### ProviderScorer.get_scores

Return provider scores categorized by prompt characteristics.

```python
get_scores(self)
```

#### ProviderScorer.update_score

WP-11008: Update score with policy guardrails (e.g. requires approval for large changes).

```python
update_score(self, provider, characteristic, quality_score, approved)
```

---

## ReplayManager

WP-4007/9003/9006: Decision replay and rationale snapshots with sandbox and what-if support.

### Methods

#### ReplayManager.__init__

```python
__init__(self, session_dir)
```

#### ReplayManager.enable_sandbox

WP-9003: Enable read-only sandbox mode for replay.

```python
enable_sandbox(self)
```

#### ReplayManager.get_replay_chain

Fetch the sequence of events for a run from the registry.

```python
get_replay_chain(self, run_id)
```

#### ReplayManager.simulate_policy_change

WP-4007: Pre-flight simulation of a different policy.

```python
simulate_policy_change(self, run_meta, new_settings)
```

#### ReplayManager.what_if_branch

WP-9006/12004: Simulate an alternate outcome with branch governance.

```python
what_if_branch(self, run_id, branch_point_index, new_params, approved)
```

---

## RunMeta

Metadata for a single agent/droid execution run.

**Inherits from**: `BaseModel`

---

## RunRegistry

Manages persistence and retrieval of execution runs.

### Methods

#### RunRegistry.__init__

```python
__init__(self, session_dir)
```

#### RunRegistry.find_by_token

Find the most recent run with a given idempotency token.

```python
find_by_token(self, token)
```

#### RunRegistry.get_calibration_factor

Calculate calibration factor (avg feedback / avg confidence) for an agent.
G-GP-09: Checks CalibrationRegistry first for persisted factor.

```python
get_calibration_factor(self, agent)
```

#### RunRegistry.get_run_state

Return current run state from registry events (G-KD-03).

```python
get_run_state(self, run_id)
```

#### RunRegistry.list_runs

List recent runs by parsing the registry.

```python
list_runs(self, limit)
```

#### RunRegistry.purge_expired

WP-3006: Tiered retention purge (G-GP-07).
Removes records exceeding retention period. Returns counts of kept/purged.

```python
purge_expired(self, default_days, by_domain, dry_run)
```

#### RunRegistry.register_end

Update a run with completion metadata and hash chaining. G-GP-06: cost_usd optional.

```python
register_end(self, run_id, exit_code, status, ended_at_utc, duration_s, error_class, cost_usd)
```

#### RunRegistry.register_feedback

Record operator feedback for a run with hash chaining.

```python
register_feedback(self, run_id, score, note)
```

#### RunRegistry.register_pause

Record run pause for state-aware orchestration (G-KD-03).

```python
register_pause(self, run_id, reason, continuity_snapshot)
```

#### RunRegistry.register_resume

Record run resume for state-aware orchestration (G-KD-03).

```python
register_resume(self, run_id)
```

#### RunRegistry.register_start

Record the start of a run with hash chaining.

```python
register_start(self, run)
```

---

## RunState

Run lifecycle state for state-aware orchestration (G-KD-03).

**Inherits from**: `StrEnum`

---

## TrustBoundaryValidator

WP-3007: Validates environment transitions (e.g. staging→production).

### Methods

#### TrustBoundaryValidator.__init__

```python
__init__(self, session_dir)
```

#### TrustBoundaryValidator.get_last_environment

Return the last recorded environment from a run.

```python
get_last_environment(self)
```

#### TrustBoundaryValidator.record_environment

Record current environment after successful run.

```python
record_environment(self, env)
```

#### TrustBoundaryValidator.validate_transition

Validate transition from from_env to to_env.
Returns (allowed, reason). Promotions (dev→staging→prod) may require audit.

```python
validate_transition(self, from_env, to_env)
```

---

## acquire

Acquire a concurrency slot. Critical lane can bypass if under absolute limit.

```python
acquire(self, lane)
```

---

## add

Add a blocked run to the escalation queue.

```python
add(self, run_id, reason, sla_minutes, owner, agent, lane, priority)
```

---

## check_and_record

Check if key exists in registry; return True if already executed.

```python
check_and_record(self, registry, key)
```

---

## check_capacity

Check if a lane has capacity to run (starvation prevention).

```python
check_capacity(self, lane)
```

---

## confirm_handoff

WP-9004/12005: Incoming owner confirms handoff completeness with confidence.

```python
confirm_handoff(self, snapshot_id, incoming_owner, confidence)
```

---

## create_checkpoint

Record a new checkpoint.

```python
create_checkpoint(self, reason, dag_content, owner)
```

---

## create_snapshot

Create a continuity snapshot for a handoff.

```python
create_snapshot(self, owner, run_ids)
```

---

## defer

Defer a task with an estimated time to resume.

```python
defer(self, run_id, reason, eta_s)
```

---

## enable_sandbox

WP-9003: Enable read-only sandbox mode for replay.

```python
enable_sandbox(self)
```

---

## enqueue

Add a failing run to the DLQ.

```python
enqueue(self, run_meta, error)
```

---

## evaluate

Evaluate a run against active policies.
Returns (result, reason) where result is 'allow', 'deny', or 'warn'.
G-GP-01: When THGENT_OPA_URL is set, delegates to OPA first; falls back to Python logic on failure.

```python
evaluate(self, run, registry)
```

---

## find_by_token

Find the most recent run with a given idempotency token.

```python
find_by_token(self, token)
```

---

## generate_key

Generate a 4-tuple idempotency key (run_id, step, action, hash).

```python
generate_key(self, run_id, step_index, action_type, content)
```

---

## generate_maif_artifact

Generate a signed MAIF artifact for a run (WP-3002).

```python
generate_maif_artifact(self, run, output)
```

---

## get_calibration_factor

Calculate calibration factor (avg feedback / avg confidence) for an agent.
G-GP-09: Checks CalibrationRegistry first for persisted factor.

```python
get_calibration_factor(self, agent)
```

---

## get_checkpoint

Retrieve a specific checkpoint.

```python
get_checkpoint(self, checkpoint_id)
```

---

## get_factor

Return the persisted calibration factor for an agent.

```python
get_factor(self, agent)
```

---

## get_fatigue_score

Calculate fatigue score based on recent interruptions (0.0-1.0).

```python
get_fatigue_score(self, window_s)
```

---

## get_kpis

Calculate the 10 core KPIs for the dashboard.

```python
get_kpis(self)
```

---

## get_lane_priority

Return numeric priority for a lane (lower is higher priority).

```python
get_lane_priority(self, lane)
```

---

## get_last_environment

Return the last recorded environment from a run.

```python
get_last_environment(self)
```

---

## get_load_level

Return current load level: normal, high, burst.

```python
get_load_level(self)
```

---

## get_replay_chain

Fetch the sequence of events for a run from the registry.

```python
get_replay_chain(self, run_id)
```

---

## get_run_state

Return current run state from registry events (G-KD-03).

```python
get_run_state(self, run_id)
```

---

## get_scores

Return provider scores categorized by prompt characteristics.

```python
get_scores(self)
```

---

## has_unexpired

True if owner has an override that has not yet expired.

```python
has_unexpired(self, owner)
```

---

## is_handoff_enforced

WP-9004: Check if a run is blocked by a pending handoff confirmation.

```python
is_handoff_enforced(self, run_id)
```

---

## is_open

Check if the circuit for a target in a category is open (blocked).

```python
is_open(self, target, category)
```

---

## is_stale

Check if a file or registry is stale.

```python
is_stale(self, path, max_age_s)
```

---

## lint

Verify CSM evidence is complete based on phase.

```python
lint(self, csm)
```

---

## list_checkpoints

List recent checkpoints.

```python
list_checkpoints(self, limit)
```

---

## list_items

List items in the DLQ with optional filtering.

```python
list_items(self, status, run_id)
```

---

## list_pending

List escalation items. If past_sla_only, return only items past escalate_by.

```python
list_pending(self, past_sla_only, limit)
```

---

## list_runs

List recent runs by parsing the registry.

```python
list_runs(self, limit)
```

---

## persist_maif_artifact

Persist a MAIF artifact to the artifacts directory (WP-3002).

```python
persist_maif_artifact(self, session_dir, artifact)
```

---

## purge_expired

WP-3006: Tiered retention purge (G-GP-07).
Removes records exceeding retention period. Returns counts of kept/purged.

```python
purge_expired(self, default_days, by_domain, dry_run)
```

---

## record

Record an override; valid until now + ttl_seconds.

```python
record(self, owner, reason, ttl_seconds)
```

---

## record_environment

Record current environment after successful run.

```python
record_environment(self, env)
```

---

## record_failure

Record a failure for a target in a specific category.

```python
record_failure(self, target, category)
```

---

## record_interruption

Record an agent interruption event.

```python
record_interruption(self, run_id, severity)
```

---

## register_end

Update a run with completion metadata and hash chaining. G-GP-06: cost_usd optional.

```python
register_end(self, run_id, exit_code, status, ended_at_utc, duration_s, error_class, cost_usd)
```

---

## register_feedback

Record operator feedback for a run with hash chaining.

```python
register_feedback(self, run_id, score, note)
```

---

## register_pause

Record run pause for state-aware orchestration (G-KD-03).

```python
register_pause(self, run_id, reason, continuity_snapshot)
```

---

## register_resume

Record run resume for state-aware orchestration (G-KD-03).

```python
register_resume(self, run_id)
```

---

## register_start

Record the start of a run with hash chaining.

```python
register_start(self, run)
```

---

## resolve

Mark an escalation item as resolved. Returns True if found and updated.

```python
resolve(self, run_id, resolution)
```

---

## scan_stale_sessions

Scan for sessions with no activity for max_idle_s.

```python
scan_stale_sessions(self, max_idle_s)
```

---

## sign_run

Generate a cryptographic signature for a run record.

```python
sign_run(self, run)
```

---

## simulate_policy_change

WP-4007: Pre-flight simulation of a different policy.

```python
simulate_policy_change(self, run_meta, new_settings)
```

---

## sort_tasks

Sort tasks by lane priority and then by creation time.

```python
sort_tasks(self, tasks)
```

---

## trigger_auto_handoff

Automatically trigger a handoff for a stale session (WP-5006).

```python
trigger_auto_handoff(self, session_id, _backup_owner)
```

---

## update_agent

Persist a new calibration factor for an agent.

```python
update_agent(self, agent, factor, sample_size)
```

---

## update_score

WP-11008: Update score with policy guardrails (e.g. requires approval for large changes).

```python
update_score(self, provider, characteristic, quality_score, approved)
```

---

## validate_action

Validate if the action is safe to perform based on context freshness.

```python
validate_action(self, run_id, context_files)
```

---

## validate_transition

Validate transition from from_env to to_env.
Returns (allowed, reason). Promotions (dev→staging→prod) may require audit.

```python
validate_transition(self, from_env, to_env)
```

---

## verify_integrity

Verify the integrity of a handoff snapshot.

```python
verify_integrity(self, snapshot_id)
```

---

## verify_registry

Verify the integrity of all records in the registry, including the hash chain.

```python
verify_registry(self)
```

---

## what_if_branch

WP-9006/12004: Simulate an alternate outcome with branch governance.

```python
what_if_branch(self, run_id, branch_point_index, new_params, approved)
```

---

