# turn_submit_boundaries API Reference

> **Source**: `src/thegent/protocols/turn_submit_boundaries.py`

Typed phase boundaries for turn/submit orchestration helpers.

---

## CliCommandParsePhase

**Inherits from**: `TypedDict`

---

## CliDispatchPhase

**Inherits from**: `TypedDict`

---

## CommitPhase

**Inherits from**: `TypedDict`

---

## HookInvocationPhase

**Inherits from**: `TypedDict`

---

## HookRegistrationPhase

**Inherits from**: `TypedDict`

---

## ObservabilityEventPhase

**Inherits from**: `TypedDict`

---

## ParsePhase

**Inherits from**: `TypedDict`

---

## PolicyMatchPhase

**Inherits from**: `TypedDict`

---

## ProviderRuleEvaluationPhase

**Inherits from**: `TypedDict`

---

## ProviderSelectionPhase

**Inherits from**: `TypedDict`

---

## QueuePriorityPhase

**Inherits from**: `TypedDict`

---

## QueueSchedulingPhase

**Inherits from**: `TypedDict`

---

## ResponsePhase

**Inherits from**: `TypedDict`

---

## RetryLoopPhase

**Inherits from**: `TypedDict`

---

## SessionStateUpdatePhase

**Inherits from**: `TypedDict`

---

## SideEffectsPhase

**Inherits from**: `TypedDict`

---

## SyncCommitPhase

**Inherits from**: `TypedDict`

---

## SyncDiffPhase

**Inherits from**: `TypedDict`

---

## WorkflowGuardPhase

**Inherits from**: `TypedDict`

---

## build_cli_command_parse_phase

```python
build_cli_command_parse_phase(raw_command: str, parsed_tokens: list[str], selected_handler: str) -> CliCommandParsePhase
```

---

## build_cli_dispatch_phase

```python
build_cli_dispatch_phase(parsed_command: str, command_args: dict[(str, Any)], selected_handler: str) -> CliDispatchPhase
```

---

## build_commit_phase

```python
build_commit_phase(session_id: str, session: dict[(str, Any)], turn_id: str, turn: dict[(str, Any)]) -> CommitPhase
```

---

## build_hook_invocation_phase

```python
build_hook_invocation_phase(hook_name: str, registration_id: str, payload: dict[(str, Any)]) -> HookInvocationPhase
```

---

## build_hook_registration_phase

```python
build_hook_registration_phase(hook_name: str, registration_options: dict[(str, Any)], invocation_payload: dict[(str, Any)]) -> HookRegistrationPhase
```

---

## build_observability_event_phase

```python
build_observability_event_phase(event_name: str, event_payload: dict[(str, Any)], serialization_format: str) -> ObservabilityEventPhase
```

---

## build_parse_phase

```python
build_parse_phase(session_id: str, user_input: str) -> ParsePhase
```

---

## build_policy_match_phase

```python
build_policy_match_phase(policy_id: str, matched_rules: list[str], enforcement_action: str) -> PolicyMatchPhase
```

---

## build_provider_rule_evaluation_phase

```python
build_provider_rule_evaluation_phase(candidate_scores: dict[(str, int)], selection_strategy: str, selected_provider: str) -> ProviderRuleEvaluationPhase
```

---

## build_provider_selection_phase

```python
build_provider_selection_phase(candidate_providers: list[str], selected_provider: str, selection_reason: str) -> ProviderSelectionPhase
```

---

## build_queue_priority_phase

```python
build_queue_priority_phase(priority_bucket: str, queued_turn_ids: list[str], dispatch_window: int) -> QueuePriorityPhase
```

---

## build_queue_scheduling_phase

```python
build_queue_scheduling_phase(prioritized_turn_ids: list[str], scheduler_epoch: int, batch_size: int) -> QueueSchedulingPhase
```

---

## build_response_phase

```python
build_response_phase(request_has_id: bool, request_id: Any, turn: dict[(str, Any)], approval_payload: Any) -> ResponsePhase
```

---

## build_retry_loop_phase

```python
build_retry_loop_phase(attempt_count: int, max_attempts: int, terminal_outcome: str) -> RetryLoopPhase
```

---

## build_session_state_update_phase

```python
build_session_state_update_phase(session_id: str, state_changes: dict[(str, Any)], persistence_revision: int) -> SessionStateUpdatePhase
```

---

## build_side_effects_phase

```python
build_side_effects_phase(session_id: str, turn_id: str, turn: dict[(str, Any)], user_input: str, requires_approval: bool, approval_diff: Any) -> SideEffectsPhase
```

---

## build_sync_commit_phase

```python
build_sync_commit_phase(diff_records: list[dict[(str, Any)]], commit_id: str, dry_run: bool) -> SyncCommitPhase
```

---

## build_sync_diff_phase

```python
build_sync_diff_phase(diff_records: list[dict[(str, Any)]], commit_message: str, commit_author: str) -> SyncDiffPhase
```

---

## build_workflow_guard_phase

```python
build_workflow_guard_phase(workflow_id: str, guard_results: dict[(str, bool)], execution_step: str) -> WorkflowGuardPhase
```

---

## resolve_cli_handler_selection_target

```python
resolve_cli_handler_selection_target(phase: CliCommandParsePhase) -> tuple[(str, list[str], str)]
```

---

## resolve_commit_target

```python
resolve_commit_target(phase: CommitPhase) -> tuple[(str, dict[(str, Any)], str, dict[(str, Any)])]
```

---

## resolve_hook_invocation_target

```python
resolve_hook_invocation_target(phase: HookRegistrationPhase) -> tuple[(str, dict[(str, Any)], dict[(str, Any)])]
```

---

## resolve_observability_serialization_target

```python
resolve_observability_serialization_target(phase: ObservabilityEventPhase) -> tuple[(str, dict[(str, Any)], str)]
```

---

## resolve_observability_target

```python
resolve_observability_target(phase: SyncCommitPhase) -> tuple[(list[dict[(str, Any)]], str, bool)]
```

---

## resolve_parse_target

```python
resolve_parse_target(phase: ParsePhase) -> tuple[(str, str, Any, bool)]
```

---

## resolve_policy_enforcement_plan_target

```python
resolve_policy_enforcement_plan_target(phase: PolicyMatchPhase) -> tuple[(str, list[str], str)]
```

---

## resolve_policy_enforcement_target

```python
resolve_policy_enforcement_target(phase: HookInvocationPhase) -> tuple[(str, str, dict[(str, Any)])]
```

---

## resolve_provider_final_selection_target

```python
resolve_provider_final_selection_target(phase: ProviderRuleEvaluationPhase) -> tuple[(dict[(str, int)], str, str)]
```

---

## resolve_queue_execution_target

```python
resolve_queue_execution_target(phase: QueuePriorityPhase) -> tuple[(str, list[str], int)]
```

---

## resolve_response_target

```python
resolve_response_target(phase: ResponsePhase) -> tuple[(bool, Any, dict[(str, Any)], Any)]
```

---

## resolve_retry_outcome_target

```python
resolve_retry_outcome_target(phase: CliDispatchPhase) -> tuple[(str, dict[(str, Any)], str)]
```

---

## resolve_session_persistence_plan_target

```python
resolve_session_persistence_plan_target(phase: SessionStateUpdatePhase) -> tuple[(str, dict[(str, Any)], int)]
```

---

## resolve_session_persistence_target

```python
resolve_session_persistence_target(phase: QueueSchedulingPhase) -> tuple[(list[str], int, int)]
```

---

## resolve_side_effects_target

```python
resolve_side_effects_target(phase: SideEffectsPhase) -> tuple[(str, str, dict[(str, Any)], str, bool, Any)]
```

---

## resolve_sync_commit_plan_target

```python
resolve_sync_commit_plan_target(phase: SyncDiffPhase) -> tuple[(list[dict[(str, Any)]], str, str)]
```

---

## resolve_terminal_outcome_target

```python
resolve_terminal_outcome_target(phase: RetryLoopPhase) -> tuple[(int, int, str)]
```

---

## resolve_workflow_execution_target

```python
resolve_workflow_execution_target(phase: WorkflowGuardPhase) -> tuple[(str, dict[(str, bool)], str)]
```

---

## resolve_workflow_guard_target

```python
resolve_workflow_guard_target(phase: ProviderSelectionPhase) -> tuple[(list[str], str, str)]
```

---

