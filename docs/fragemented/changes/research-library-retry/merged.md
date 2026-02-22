# Merged Fragmented Markdown

## Source: changes/research-library-retry/design.md

# Retry Library Design Document

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  Application Code (HTTP client, DB, Agent Service)              │
│  @retry(strategy="http") or @retry_async(strategy="agent")      │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  Retry Decorator Layer (retry.py)                               │
│  - @retry(strategy, config)                                     │
│  - @retry_async(strategy, config)                               │
│  - retry_context(strategy, config)                              │
│  - Observability hooks (before_attempt, after_attempt)          │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  Strategy Layer (strategies.py)                                 │
│  - HTTPStrategy (4xx/5xx/timeout detection)                    │
│  - DatabaseStrategy (connection errors, transient locks)        │
│  - AgentStrategy (temporary unavailability, rate limits)        │
│  - CustomStrategy (user-defined exception matchers)            │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  Tenacity Layer (wrapped)                                        │
│  - tenacity.Retrying                                             │
│  - wait_random_exponential (base 2, max jitter)                │
│  - stop_after_attempt / stop_after_delay                        │
│  - Custom stop/wait strategies                                  │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  OpenTelemetry Layer (observability.py)                         │
│  - Span events for each retry attempt                           │
│  - Metrics: retry_attempts (counter), retry_latency (histogram)│
│  - Attributes: strategy, attempt #, error type, backoff delay   │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. RetryConfig (pydantic Settings)

```python
class RetryConfig(BaseSettings):
    """Configuration for retry behavior."""

    strategy: str = "default"  # "http", "db", "agent", "default"
    max_attempts: int = 5
    max_delay_seconds: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True

    # Timeout (for stop_after_delay)
    total_timeout_seconds: float | None = None

    # Observability
    emit_metrics: bool = True
    emit_traces: bool = True

    model_config = SettingsConfigDict(env_prefix="RETRY_")
```

### 2. RetryStrategy (Enum + Matcher)

```python
class RetryStrategy(str, Enum):
    DEFAULT = "default"      # Retry on any Exception
    HTTP = "http"            # HTTP 5xx, timeouts, connection errors
    DATABASE = "database"    # DB connection errors, transient locks
    AGENT = "agent"          # Agent service unavailability
    CUSTOM = "custom"        # User-provided exception matcher

def strategy_matcher(strategy: RetryStrategy) -> Callable[[Exception], bool]:
    """Returns a predicate: Exception -> bool (retry or not)."""
```

### 3. Core Decorators

#### Sync Version
```python
@retry(strategy="http", max_attempts=3, max_delay_seconds=10)
def fetch_data(url: str) -> dict:
    ...
```

#### Async Version
```python
@retry_async(strategy="agent", max_attempts=5)
async def call_agent(prompt: str) -> str:
    ...
```

#### Context Manager
```python
with retry_context(strategy="db", max_attempts=2):
    cursor.execute(query)
    result = cursor.fetchall()
```

### 4. Pre-Built Strategies

#### HTTPStrategy
- **Retryable errors**:
  - 5xx status codes (500, 502, 503, 504)
  - Connection errors (ConnectionError, TimeoutError)
  - Partial reads (httpx.ReadError)
- **Non-retryable**: 4xx (client fault), 3xx (redirect handled by httpx)
- **Default config**: max_attempts=5, exponential_base=2, max_delay=60s

#### DatabaseStrategy
- **Retryable errors**:
  - Database connection errors (psycopg2.OperationalError, etc.)
  - Transient locks (psycopg2.extensions.TransactionRollbackError)
  - Pool exhaustion (sqlalchemy.pool.NullPool errors)
- **Non-retryable**: Integrity violations, syntax errors
- **Default config**: max_attempts=3, exponential_base=2, max_delay=30s

#### AgentStrategy
- **Retryable errors**:
  - Service unavailability (503, 500)
  - Rate limit errors (429)
  - Timeout (agent taking too long)
- **Default config**: max_attempts=7, exponential_base=2, max_delay=120s

### 5. Observability Integration

#### Span Events
Each retry attempt emits a span event:
```json
{
  "name": "retry_attempt",
  "attributes": {
    "retry.strategy": "http",
    "retry.attempt": 2,
    "retry.max_attempts": 5,
    "retry.error_type": "ConnectionError",
    "retry.next_delay_seconds": 4.2,
    "retry.total_delay_seconds": 6.0
  },
  "timestamp": "2026-02-18T10:30:45Z"
}
```

#### Metrics
```python
# Counter: number of retry attempts
retry_attempts = Counter(
    name="retry_attempts_total",
    description="Total number of retry attempts",
    attributes=["strategy", "error_type", "outcome"],  # outcome: "success" | "exhausted" | "timeout"
)

# Histogram: latency of retried operation (including backoff)
retry_latency = Histogram(
    name="retry_latency_seconds",
    description="Latency of operations with retries",
    attributes=["strategy", "outcome"],
)
```

#### Attributes (in Span)
Every span created in a retried operation includes:
- `retry.strategy`: Strategy name
- `retry.enabled`: Boolean (true if retries active)
- `retry.attempt`: Current attempt number (0-indexed)
- `retry.max_attempts`: Max attempts configured

## Exception Hierarchy

```python
class RetryException(Exception):
    """Base exception for retry-specific errors."""
    pass

class RetryExhausted(RetryException):
    """Raised when max attempts reached."""
    last_exception: Exception
    attempts: int

class RetryTimeout(RetryException):
    """Raised when total_timeout_seconds exceeded."""
    last_exception: Exception
    elapsed_seconds: float
```

## Configuration

### Environment Variables (pydantic SettingsConfigDict)
```bash
RETRY_STRATEGY=http
RETRY_MAX_ATTEMPTS=5
RETRY_MAX_DELAY_SECONDS=60.0
RETRY_EXPONENTIAL_BASE=2.0
RETRY_JITTER=true
RETRY_EMIT_METRICS=true
RETRY_EMIT_TRACES=true
```

### Programmatic (Override in Code)
```python
retry_config = RetryConfig(
    strategy="agent",
    max_attempts=10,
    max_delay_seconds=120.0,
)

@retry(config=retry_config)
def call_agent(...):
    ...
```

## Integration Points

### With Agent Services
```python
# In agent runner
@retry_async(strategy="agent")
async def run_agent(agent_id: str, prompt: str) -> str:
    return await http_client.post(f"{AGENT_URL}/run", json={"prompt": prompt})
```

### With HTTP Client (httpx)
```python
# Wrap httpx.AsyncClient
class RetryableAsyncClient(httpx.AsyncClient):
    @retry_async(strategy="http")
    async def request(self, *args, **kwargs):
        return await super().request(*args, **kwargs)
```

### With Database (SQLAlchemy)
```python
# Wrap connection/transaction
@retry(strategy="database")
def execute_query(query):
    with engine.connect() as conn:
        return conn.execute(query)
```

## Error Handling & Backoff

### Backoff Strategy
- **Function**: `wait_random_exponential(multiplier=1, max=60)`
- **Formula**: `min(2^attempt + random(0, 1), 60)`
- **Example**:
  - Attempt 1: ~1s + jitter
  - Attempt 2: ~2s + jitter
  - Attempt 3: ~4s + jitter
  - Attempt 4: ~8s + jitter
  - Attempt 5: ~16s + jitter (capped at 60s)

### Stop Conditions
1. **Max Attempts**: Stop after N attempts (default 5)
2. **Total Timeout**: Stop if total_timeout_seconds exceeded
3. **Success**: Stop on first successful attempt

### Logging & Observability
- **Before attempt**: Log "Attempting [operation], attempt N/M"
- **After attempt (success)**: Log "Success after N attempts, total latency X.Xs"
- **After attempt (retry)**: Log "Retrying after error [type], waiting Ns before attempt N"
- **After attempt (exhausted)**: Log "Max attempts exhausted, last error: [...]"

## Test Strategy

### Unit Tests
- **Config validation**: Invalid retry configs raise errors
- **Strategy matching**: Each strategy correctly identifies retryable exceptions
- **Backoff calculation**: Exponential backoff is correct (no jitter variation)
- **Decorator behavior**: Retries work for sync/async/context manager
- **Observability**: Span events emitted, metrics recorded

### Integration Tests
- **HTTP strategy**: Mock HTTP service, test 5xx retry
- **Database strategy**: Mock DB, test connection error retry
- **Agent strategy**: Mock agent service, test timeout retry
- **End-to-end**: Full retry cycle (attempt 1 fails, attempt 2 succeeds)
- **Exhaustion**: Verify RetryExhausted raised after max attempts

### Performance Tests
- **Nominal path** (no retry): <1ms overhead
- **Backoff calculation**: <100us per attempt
- **Span events**: <10ms total for 5 retries

## Implementation Order

1. **Phase 1**: Core retry library (RetryConfig, decorators, tenacity wrapper)
2. **Phase 2**: Strategies (HTTP, Database, Agent pre-built strategies)
3. **Phase 3**: Observability (OpenTelemetry instrumentation, span events, metrics)
4. **Phase 4**: Tests (unit, integration, performance)
5. **Phase 5**: Documentation (guide, examples, migration paths)
6. **Phase 6**: Integration (3+ services migrated)

---

## Comparison with Alternatives

### Option 1: Custom Retry Loop (Manual)
- **Pros**: No dependency, complete control
- **Cons**: Code duplication, no observability, maintainability burden
- **Verdict**: ❌ Rejected (CLAUDE.md: "No manual retry loops")

### Option 2: Existing pybreaker (Circuit Breaker)
- **Pros**: Prevents cascading failures
- **Cons**: Different concern; doesn't handle backoff/retry logic
- **Verdict**: ✅ Complementary (pybreaker for circuit breaking, tenacity for retry)

### Option 3: tenacity (Chosen)
- **Pros**: Battle-tested, well-documented, extensible, already a dependency
- **Cons**: Requires thin wrapper for project conventions
- **Verdict**: ✅ Chosen (standard practice across industry)

### Option 4: asyncio.retry / Stamina
- **Pros**: Alternative libraries with similar features
- **Cons**: Less mature than tenacity, not in current dependencies
- **Verdict**: ❌ Rejected (prefer existing dependency)

---

## Open Questions

1. **Should we integrate with circuit breaker (pybreaker)?** Scope for Phase 2?
2. **Should we auto-retry on all HTTPExceptions or be explicit per error?** Current design: explicit
3. **Should rate-limit errors (429) always retry with exponential backoff, or use Retry-After header?** Design decision: Use Retry-After if present, else exponential

---

## Source: changes/research-library-retry/proposal.md

# Standardized Retry Library Proposal

## Overview

This proposal establishes a standardized, centralized retry logic library for **thegent** using **tenacity** as the foundation. The library will provide consistent exponential backoff, built-in observability (via OpenTelemetry), and configurable resilience patterns across all agent services, API clients, and distributed system components.

## Problem Statement

### Current State
- **No unified retry strategy**: Scattered implementations across codebase (manual loops, custom backoff logic)
- **Poor observability**: Retry attempts not instrumented; no metrics or tracing
- **Inconsistent behavior**: Different services retry with different strategies, exponential bases, max attempts
- **Code duplication**: Retry logic reimplemented per use case
- **Missed library investment**: `tenacity>=8.3.0` already in `pyproject.toml`, underutilized

### Risks
- Silent failures during transient faults (network hiccups, service restarts)
- Cascading failures due to aggressive retry patterns
- Difficulty debugging transient issues (no visibility into retries)
- Maintenance burden: updating retry logic requires changes in N places

## Goals

1. **Reduce code duplication**: Centralize retry logic into a thin, reusable library
2. **Improve observability**: Instrument all retries with OpenTelemetry metrics and traces
3. **Standardize resilience patterns**: Exponential backoff + jitter by default, configurable per use case
4. **Enable quick integration**: Drop-in decorator/context manager for new services
5. **Support domain-specific configurations**: HTTP timeouts, database transients, agent service retries

## Scope

### In Scope
- Retry library (`src/thegent/resilience/retry.py`) with tenacity wrapper
- Default exponential backoff strategy (base 2, max jitter)
- OpenTelemetry instrumentation (span attributes, metrics)
- Pre-built retry strategies for common cases:
  - HTTP requests (4xx transients, 5xx, timeouts)
  - Database operations (connection errors, transient locks)
  - Agent service calls (temporary unavailability)
- Configuration via pydantic settings (`RetryConfig`)
- Comprehensive test suite (unit + integration)
- Documentation and usage examples

### Out of Scope
- Circuit breaker logic (separate concern; `pybreaker` already present)
- Rate limiting (separate concern; tenacity + asyncio.Semaphore for advanced cases)
- Custom backoff algorithms beyond exponential (extend in future if needed)
- Automatic retry on all exceptions (explicit opt-in only)

## Non-Functional Requirements

- **Performance**: Retry overhead <1ms for typical (non-failing) path
- **Observability**: Every retry attempt emitted as span event + metric
- **Type safety**: Full type hints; strict mode compatible
- **Backward compatibility**: No breaking changes to existing APIs
- **Testability**: 100% unit test coverage for core retry logic

## Library Approach

**Library-first principle**: Use `tenacity` as the foundation, build thin wrapper exposing project conventions. No custom retry logic.

**Architecture**:
```
src/thegent/resilience/
├── __init__.py              # Public API (retry, retry_config, decorators)
├── retry.py                 # Core RetryStrategy, RetryConfig, decorators
├── strategies.py            # Pre-built strategies (http, db, agent)
├── observability.py         # OpenTelemetry instrumentation
└── exceptions.py            # Retry-specific exceptions (RetryExhausted, etc.)
```

## Success Criteria

1. **Adoption**: 3+ services migrated to library (with metrics showing >80% retry success)
2. **Observability**: All retries traced + metricated (zero dark spans)
3. **Coverage**: Retry code 100% unit tested
4. **Docs**: Usage guide + 5 worked examples (HTTP, DB, agent, async, custom)
5. **Performance**: Latency regression <1% for nominal path

## Timeline

**Phase 1 (Research & Design)**: 1 phase
**Phase 2 (Implementation)**: Core library + strategies
**Phase 3 (Integration)**: Migrate 3 service + docs
**Phase 4 (Validation)**: Test + review

Estimated: 2–3 agent work blocks (~20–30 min wall clock for autonomous agents).

---

## Related Work

- **tenacity** (8.3.0): Library of choice; battle-tested, well-documented
- **OpenTelemetry** (1.24.0): Instrumentation foundation (already a dependency)
- **Existing pybreaker**: Circuit breaker; complements retry strategy
- **Existing cachetools/diskcache**: Caching layer (separate from retry)
- **CLAUDE.md library standard**: Mandates tenacity for retry/resilience

## Decision

**DECISION: Adopt library-first approach with tenacity wrapper**

**Rationale**:
- Tenacity is proven, widely adopted, and already a project dependency
- Thin wrapper ensures project conventions are enforced
- OpenTelemetry integration provides production observability
- Pre-built strategies lower migration barrier
- Aligns with CLAUDE.md mandate: "No manual retry loops; use tenacity"

---

## Source: changes/research-library-retry/tasks.md

# Retry Library Implementation Tasks

## Phase 1: Core Retry Library

### T1.1: Set Up Module Structure & Configuration
**Status**: PENDING
**Owner**: TBD
**Depends On**: —

**Deliverables**:
- [ ] Create `src/thegent/resilience/__init__.py` with public API exports
- [ ] Create `src/thegent/resilience/retry.py` with core module (RetryConfig, RetryStrategy enum, decorators)
- [ ] Add RetryConfig to `src/thegent/config.py` (pydantic settings)
- [ ] Create `src/thegent/resilience/exceptions.py` (RetryException, RetryExhausted, RetryTimeout)
- [ ] Update `pyproject.toml` to document tenacity usage (already present at 8.3.0)

**Acceptance Criteria**:
- [ ] All types pass `basedpyright` strict mode
- [ ] Config can be loaded from environment variables (RETRY_*)
- [ ] Public API is clean (2–3 decorators, context manager)
- [ ] No dependencies added (tenacity already present)

**Notes**: Library-first principle: wrap tenacity, don't reimplement.

---

### T1.2: Implement Sync & Async Decorators
**Status**: PENDING
**Owner**: TBD
**Depends On**: T1.1

**Deliverables**:
- [ ] Implement `@retry()` decorator for sync functions
- [ ] Implement `@retry_async()` decorator for async functions
- [ ] Implement `retry_context()` context manager
- [ ] Support strategy selection (string or enum)
- [ ] Support config override (per-call kwargs or RetryConfig)
- [ ] Ensure decorators preserve function metadata (functools.wraps)

**Test Coverage**:
- [ ] Basic retry (success on 2nd attempt)
- [ ] Max attempts exhausted
- [ ] Success on first attempt (no retry)
- [ ] Config override (per-call params)
- [ ] Async functions with decorators
- [ ] Context manager behavior
- [ ] Exception propagation on exhaustion

**Performance Target**: Nominal path (no retry) <1ms overhead

**Notes**:
- Use tenacity.Retrying, tenacity.retry decorator as foundation
- Wrap stop_after_attempt and wait_random_exponential from tenacity
- Preserve stack traces (re-raise original exceptions)

---

### T1.3: Implement Pre-Built Strategies
**Status**: PENDING
**Owner**: TBD
**Depends On**: T1.1

**Deliverables**:
- [ ] Create `src/thegent/resilience/strategies.py`
- [ ] Implement HTTPStrategy (retry on 5xx, ConnectionError, TimeoutError)
- [ ] Implement DatabaseStrategy (retry on OperationalError, transient locks)
- [ ] Implement AgentStrategy (retry on 503, 500, 429, timeout)
- [ ] Implement DefaultStrategy (retry on any Exception)
- [ ] Implement CustomStrategy (user-defined exception matcher)
- [ ] Return strategy matcher function from `strategy_matcher(name: str)`

**Test Coverage**:
- [ ] HTTPStrategy: Test 5xx detection, 4xx non-retry, connection error detection
- [ ] DatabaseStrategy: Test OperationalError, transient lock detection
- [ ] AgentStrategy: Test 503, 429, timeout detection
- [ ] DefaultStrategy: Retry on generic Exception
- [ ] CustomStrategy: User-defined matchers work correctly

**Notes**:
- Each strategy returns a `Callable[[Exception], bool]` predicate
- Strategies should be importable as `from thegent.resilience.strategies import HTTPStrategy`
- Consider common error types across Python ecosystem (httpx, psycopg2, sqlalchemy, etc.)

---

### T1.4: Integrate OpenTelemetry Observability
**Status**: PENDING
**Owner**: TBD
**Depends On**: T1.2

**Deliverables**:
- [ ] Create `src/thegent/resilience/observability.py`
- [ ] Emit span events on each retry attempt (name: "retry_attempt")
- [ ] Attach span attributes (strategy, attempt, error_type, next_delay, total_delay)
- [ ] Create OTel Counter for `retry_attempts_total` (dimensions: strategy, error_type, outcome)
- [ ] Create OTel Histogram for `retry_latency_seconds` (dimensions: strategy, outcome)
- [ ] Add observability hooks to retry decorator (before_attempt, after_attempt callbacks)
- [ ] Configure observability via RetryConfig (emit_metrics, emit_traces flags)

**Test Coverage**:
- [ ] Span events emitted for each retry attempt
- [ ] Attributes correct (strategy, attempt #, error_type, backoff delay)
- [ ] Metrics recorded with correct dimensions
- [ ] Observability disabled when emit_metrics=False
- [ ] OpenTelemetry integration works with existing telemetry setup

**Notes**:
- Use OpenTelemetry API (already a dependency: 1.24.0)
- Span events should be created within existing spans (not standalone)
- Metrics should use global meter provider
- Add context baggage for tracing (optional, Phase 2)

---

## Phase 2: Testing & Documentation

### T2.1: Comprehensive Unit Tests
**Status**: PENDING
**Owner**: TBD
**Depends On**: T1.4

**Deliverables**:
- [ ] Create `tests/resilience/test_retry.py`
- [ ] Create `tests/resilience/test_strategies.py`
- [ ] Create `tests/resilience/test_observability.py`
- [ ] Achieve 100% code coverage for resilience module
- [ ] Add tests for edge cases (0 max_attempts, negative delays, etc.)
- [ ] Add performance benchmarks (nominal path overhead)

**Test Suite Structure**:
```
tests/resilience/
├── conftest.py                    # Fixtures for mocking, span capture
├── test_retry.py                  # Decorators, context managers
├── test_strategies.py             # Strategy matchers, exception detection
├── test_observability.py          # Span events, metrics
├── integration/
│   ├── test_http_retry.py         # Real HTTP client with retry
│   ├── test_agent_retry.py        # Agent service retry
│   └── test_async_retry.py        # Async operations
└── benchmark/
    └── test_performance.py        # Nominal path overhead
```

**Coverage Target**: ≥95% (prefer 100%)

**Notes**:
- Use pytest fixtures for mock tracer, meter
- Mock tenacity.Retrying for deterministic testing
- Use pytest-asyncio for async tests
- Mark slow tests with `@pytest.mark.slow`

---

### T2.2: Integration Tests (3 Services)
**Status**: PENDING
**Owner**: TBD
**Depends On**: T1.4

**Deliverables**:
- [ ] Test retry with real httpx client (mock server for 5xx errors)
- [ ] Test retry with agent service (mock unavailability)
- [ ] Test retry with database (mock connection error)
- [ ] Verify retries succeed after transient failure
- [ ] Verify spans contain all expected attributes
- [ ] Verify metrics recorded correctly

**Test Coverage**:
- [ ] HTTP 5xx with eventual success
- [ ] Agent timeout with eventual success
- [ ] Database connection error with eventual success
- [ ] All attempts exhausted (no recovery)
- [ ] Exponential backoff delays verified

**Notes**:
- Use Docker/in-memory services where possible (testcontainers for DB)
- Mock external services for speed
- Capture OpenTelemetry spans in tests (in-memory exporter)

---

### T2.3: Usage Documentation & Examples
**Status**: PENDING
**Owner**: TBD
**Depends On**: T2.1

**Deliverables**:
- [ ] Create `docs/guides/RETRY_LIBRARY_GUIDE.md` (quick start, API reference)
- [ ] Create `docs/guides/quick-start/retry-quick-start.md` (5-min intro)
- [ ] Create 5 worked examples:
  - [ ] HTTP client with retry (decorator)
  - [ ] Database query with retry (context manager)
  - [ ] Agent service call with retry (async decorator)
  - [ ] Custom retry strategy (user-defined)
  - [ ] Configuration via environment variables
- [ ] Add examples to `docs/reference/RETRY_EXAMPLES.md`
- [ ] Update `CLAUDE.md` with retry library usage guidelines

**Documentation Sections**:
1. **Quick Start**: 5-minute overview, basic usage
2. **API Reference**: All decorators, context managers, config options
3. **Strategies**: When to use each strategy (HTTP, DB, Agent, Custom)
4. **Configuration**: Environment variables, programmatic override, defaults
5. **Observability**: How to access retry metrics, traces, logs
6. **Troubleshooting**: Common issues, debugging tips
7. **Migration Guide**: How to move existing retry code to library

**Notes**:
- All examples must be runnable (tested as doctests if possible)
- Include before/after code snippets
- Highlight observability benefits

---

### T2.4: Update Project Documentation
**Status**: PENDING
**Owner**: TBD
**Depends On**: T2.3

**Deliverables**:
- [ ] Update `docs/research/LIBRARY_FIRST_AUDIT_AND_PLAN.md` to reference retry library
- [ ] Add entry to `docs/guides/anti-patterns.md`: "Don't: Manual retry loops; Do: Use retry library"
- [ ] Update `FUNCTIONAL_REQUIREMENTS.md` if retry is a requirement (FR-RESIL-001: "Retry with observability")
- [ ] Add to `docs/reference/CODE_ENTITY_MAP.md`: Retry library module -> requirements mapping
- [ ] Create `docs/reference/RETRY_TRACKER.md` to track adoption (which services use library)

**Notes**:
- Update CLAUDE.md section on Retry/Resilience to reference new library
- Add retry library to "Project Standards" table in CLAUDE.md

---

## Phase 3: Integration & Migration

### T3.1: Migrate HTTP Client
**Status**: PENDING
**Owner**: TBD
**Depends On**: T2.1

**Deliverables**:
- [ ] Identify current HTTP retry patterns in codebase (search for "retry" or backoff logic)
- [ ] Create RetryableAsyncClient wrapper around httpx.AsyncClient
- [ ] Apply @retry_async(strategy="http") to HTTP operations
- [ ] Update tests to verify retry behavior
- [ ] Verify no breaking changes to existing API

**Code Locations to Update**:
- Search for patterns in `src/thegent/**/http.py`, `src/thegent/**/client.py`
- Look for existing retry logic in agent runner, provider adapters

**Test Verification**:
- [ ] Existing tests still pass
- [ ] New retry tests cover 5xx → success scenario
- [ ] Observability metrics recorded for HTTP retries

**Notes**:
- Keep changes backward-compatible (no breaking API changes)
- Prefer decorator pattern (@retry_async) over wrapper classes where possible

---

### T3.2: Migrate Agent Service Calls
**Status**: PENDING
**Owner**: TBD
**Depends On**: T2.1

**Deliverables**:
- [ ] Identify agent service call patterns (run_agent, call_agent, etc.)
- [ ] Apply @retry_async(strategy="agent") to agent invocations
- [ ] Verify AgentStrategy correctly detects timeouts, unavailability, rate limits
- [ ] Update tests to verify retry behavior
- [ ] Collect metrics on retry success rate

**Code Locations to Update**:
- Look in `src/thegent/agents/`, `src/thegent/runner/`, `src/thegent/commands/`

**Test Verification**:
- [ ] Agent retries after timeout
- [ ] Agent succeeds after transient unavailability (503)
- [ ] Metrics show retry success rate >80%

**Notes**:
- Consider adding max_delay_seconds=120 for agent retries (longer wait for slow agents)

---

### T3.3: Migrate Database Operations (Optional)
**Status**: PENDING
**Owner**: TBD
**Depends On**: T2.1

**Deliverables**:
- [ ] Identify database retry patterns (if any)
- [ ] Apply @retry(strategy="database") to DB queries
- [ ] Test with simulated connection errors
- [ ] Measure retry success rate

**Notes**:
- Lower priority (Phase 3, defer if time-constrained)
- May require SQLAlchemy integration
- Consider connection pooling behavior

---

## Phase 4: Validation & Closure

### T4.1: Performance Benchmarking
**Status**: PENDING
**Owner**: TBD
**Depends On**: T3.1

**Deliverables**:
- [ ] Run performance benchmarks (nominal path, no retry scenario)
- [ ] Measure decorator overhead: <1ms per call
- [ ] Measure backoff calculation: <100us
- [ ] Generate benchmark report
- [ ] Compare before/after latency distributions

**Report Contents**:
- Nominal path latency (no retry)
- Backoff calculation time
- Span event creation overhead
- Memory footprint
- Conclusion: performance targets met?

---

### T4.2: Code Review & QA
**Status**: PENDING
**Owner**: TBD
**Depends On**: T2.1, T3.3

**Deliverables**:
- [ ] All code passes ruff lint (strict mode)
- [ ] All code passes basedpyright type checking (strict mode)
- [ ] Test coverage ≥95% (target 100%)
- [ ] All tests pass: unit, integration, performance
- [ ] Security review (no secret leaks, no injection vectors)
- [ ] Documentation reviewed for clarity and correctness

**Checklist**:
- [ ] No new lint suppressions without justification
- [ ] No type: ignore comments without rationale
- [ ] All public APIs documented with docstrings
- [ ] All examples tested and runnable
- [ ] Backward compatibility verified

---

### T4.3: Adoption Verification
**Status**: PENDING
**Owner**: TBD
**Depends On**: T3.2

**Deliverables**:
- [ ] Document adoption by 3+ services (HTTP, Agent, optionally DB)
- [ ] Collect metrics:
  - Total retry attempts
  - Retry success rate (should be >80%)
  - Average backoff delay
  - P99 latency for retried operations
- [ ] Update `docs/reference/RETRY_TRACKER.md` with adoption status
- [ ] Generate adoption report

**Success Criteria**:
- [ ] 3+ services migrated
- [ ] Retry success rate >80%
- [ ] No performance regression (<1% latency increase)
- [ ] Observability in place (metrics + traces visible)

---

### T4.4: Documentation Finalization
**Status**: PENDING
**Owner**: TBD
**Depends On**: T4.3

**Deliverables**:
- [ ] Finalize usage guide (`docs/guides/RETRY_LIBRARY_GUIDE.md`)
- [ ] Create troubleshooting section (common issues + solutions)
- [ ] Add to project ADR (Architecture Decision Record): "Decision: Use tenacity-based retry library for all resilience"
- [ ] Update CHANGELOG.md with retry library release notes
- [ ] Archive this change documentation to `docs/changes/archive/research-library-retry/`

**Release Notes Template**:
```
## Retry Library (v0.1.0)

### New Features
- Standardized retry library with exponential backoff
- Pre-built strategies: HTTP, Database, Agent
- OpenTelemetry observability (metrics + traces)
- Drop-in decorators: @retry, @retry_async, retry_context

### Migration
- 3 services now use retry library (HTTP client, Agent service, [DB])
- See docs/guides/RETRY_LIBRARY_GUIDE.md for usage

### Observability
- All retries emitted as OpenTelemetry spans and metrics
- Metrics: retry_attempts_total, retry_latency_seconds
```

---

## Metrics & Success Tracking

### Key Metrics
| Metric | Target | Status |
|--------|--------|--------|
| Code coverage | ≥95% | — |
| Services migrated | 3+ | — |
| Retry success rate | >80% | — |
| Nominal path overhead | <1ms | — |
| Observability coverage | 100% (all retries traced) | — |
| Documentation completeness | All sections done | — |

### Dependencies
```
T1.1 ─┬─> T1.2 ──────┬──> T2.1 ──┬─> T3.1 ──┬──> T4.3 ──┬─> T4.4
      │               │          │         │           │
      ├─> T1.3 ──────┤          ├─> T3.2 ─┤           │
      │               │          │         │           │
      └─> T1.4 ──────┴─> T2.2 ──┤         └───────────┤
                                 │                     │
                                 └─> T2.3 ────────────┤
                                                       │
                                 └────── T4.1 ────────┤
                                                       │
                                 └────── T4.2 ────────┘
```

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Performance regression | Benchmark nominal path early (T4.1), abort if >1% latency increase |
| Observability overhead | Make metrics/traces opt-out (env var RETRY_EMIT_METRICS=false) |
| Integration friction | Pre-built strategies reduce migration effort; provide migration guide |
| Dependency issues | Tenacity already present; no new external deps |
| Test complexity | Use in-memory OTel exporter for deterministic testing; mock external services |

---

## Rollback Plan

If adoption reveals issues:
1. **Disable observability** (RETRY_EMIT_METRICS=false, RETRY_EMIT_TRACES=false)
2. **Reduce max_attempts** globally (RETRY_MAX_ATTEMPTS=1 → disable retries)
3. **Revert service integration** (remove @retry decorators, use old logic)
4. **Root cause analysis** (update strategies, adjust config)
5. **Re-enable gradually** (per-service, monitored)

---

## Handoff & Continuation

### What's Done
- [x] Proposal (this document)
- [x] Design document (architecture, components, integration points)
- [x] Task breakdown (all phases)

### What's Next
1. **Assign Phase 1 tasks** to implementation agent(s)
2. **Execute T1.1 – T1.4** in parallel where possible
3. **Execute Phase 2 tests** after core library complete
4. **Migrate 3 services** (Phase 3)
5. **Validate & close** (Phase 4)

### Success Definition
- Core library (Phase 1): 100% complete, all tests passing
- Tests & docs (Phase 2): 100% coverage, adoption examples ready
- Integration (Phase 3): 3 services migrated, metrics green
- Closure (Phase 4): QA passed, documentation finalized, ADR recorded

### Contact & Questions
- **Design questions?** See design.md (architecture, trade-offs)
- **Implementation questions?** See tasks.md (specific deliverables, acceptance criteria)
- **Library questions?** See tenacity docs: https://tenacity.readthedocs.io/

---
