# state_machine API Reference

> **Source**: `src/thegent/agents/state_machine.py`

Fallback State Machine for agent orchestration.

Manages the lifecycle of a task run across multiple providers and retry attempts,
enforcing fallback policies and semantic validation gates.

---

## FallbackStateMachine

State machine for managing orchestration fallbacks.

### Methods

#### FallbackStateMachine.__init__

```python
__init__(self, providers, run_id, policy, telemetry, max_retries_per_provider, retry_delay_base)
```

#### FallbackStateMachine.run

Execute the orchestration loop.

```python
run(self, runner_factory, prompt, model)
```

#### FallbackStateMachine.suggest_fallbacks

Suggest safe fallback options for the current failed/blocked state (WP-4003).

```python
suggest_fallbacks(self)
```

#### FallbackStateMachine.validate_transition

Validate if a state transition is allowed (WP-1004).

```python
validate_transition(self, from_state, to_state)
```

---

## OrchestrationState

State of an orchestration attempt.

---

## PromotionGate

WP-1005: Evidence capture and validation before state promotion.

### Methods

#### PromotionGate.__init__

```python
__init__(self, session_dir)
```

#### PromotionGate.capture_evidence

Capture and hash CSM state as evidence.

```python
capture_evidence(self, run_id, csm)
```

#### PromotionGate.validate_promotion

Validate if CSM is ready for promotion based on policy.

```python
validate_promotion(self, csm, policy)
```

---

## capture_evidence

Capture and hash CSM state as evidence.

```python
capture_evidence(self, run_id, csm)
```

---

## run

Execute the orchestration loop.

```python
run(self, runner_factory, prompt, model)
```

---

## suggest_fallbacks

Suggest safe fallback options for the current failed/blocked state (WP-4003).

```python
suggest_fallbacks(self)
```

---

## validate_promotion

Validate if CSM is ready for promotion based on policy.

```python
validate_promotion(self, csm, policy)
```

---

## validate_transition

Validate if a state transition is allowed (WP-1004).

```python
validate_transition(self, from_state, to_state)
```

---

