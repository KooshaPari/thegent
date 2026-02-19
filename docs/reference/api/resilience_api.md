# resilience API Reference

> **Source**: `src/thegent/agents/resilience.py`

Retry and fallback logic for agent runs.

Distinguishes:
- rate_limit / transient: retry same provider (429, 502/503/504, etc.)
- usage_limit: subscription/quota exhausted; fallback to different provider.

---

## FailureKind

Classification of agent run failure.

**Inherits from**: `StrEnum`

---

## FailureTaxonomy

WP-2005: Granular taxonomy of failures for root cause analysis.

**Inherits from**: `StrEnum`

---

## RecoveryEngine

WP-2004: Automated recovery playbooks for known failure patterns.

### Methods

#### RecoveryEngine.suggest_playbook

Return a recovery playbook for the given failure type.

```python
suggest_playbook(self, failure_type)
```

---

## RetryBudget

WP-2002: SLO-aware retry budget.

---

## ToolCircuitBreaker

WP-2003: Circuit breaker for individual tools and models.

### Methods

#### ToolCircuitBreaker.__init__

```python
__init__(self, name, threshold, window_s)
```

#### ToolCircuitBreaker.is_open

True if the circuit is open (too many recent failures).

```python
is_open(self)
```

#### ToolCircuitBreaker.record_failure

Record a failure event.

```python
record_failure(self)
```

---

## ToolClass

WP-2002: Classification of tool calls for specialized retries.

**Inherits from**: `StrEnum`

---

## TransientAgentError

Raised when agent failed due to retryable condition (rate limit, 502, etc.).

**Inherits from**: `Exception`

### Methods

#### TransientAgentError.__init__

```python
__init__(self, result)
```

---

## UsageLimitError

Raised when provider hit usage/quota limit; caller should fallback to different provider.

**Inherits from**: `Exception`

### Methods

#### UsageLimitError.__init__

```python
__init__(self, result, agent)
```

---

## classify_failure

Classify failure as rate_limit (retry), usage_limit (fallback), or unknown.

```python
classify_failure(result)
```

---

## classify_to_taxonomy

Classify a raw error message into the failure taxonomy.

```python
classify_to_taxonomy(error_msg)
```

---

## decorator

```python
decorator(fn)
```

---

## is_open

True if the circuit is open (too many recent failures).

```python
is_open(self)
```

---

## is_retryable

Return True if failure is rate_limit or transient (retry same provider).

```python
is_retryable(result)
```

---

## is_usage_limit

Return True if failure indicates usage/quota limit (fallback to different provider).

```python
is_usage_limit(result)
```

---

## record_failure

Record a failure event.

```python
record_failure(self)
```

---

## suggest_playbook

Return a recovery playbook for the given failure type.

```python
suggest_playbook(self, failure_type)
```

---

## with_retry

Decorator that retries on TransientAgentError with exponential backoff.

```python
with_retry(max_attempts, min_wait, max_wait)
```

---

