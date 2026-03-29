# Retry Library Synthesis (2026-02-18)

## Summary
Created comprehensive library-first retry logic proposal for **thegent** using tenacity as foundation.

## Documents Created
1. **docs/changes/research-library-retry/proposal.md** (630 lines)
   - Problem statement, goals, scope, success criteria
   - Library-first approach rationale
   - Non-functional requirements (performance, observability, type safety)

2. **docs/changes/research-library-retry/design.md** (540 lines)
   - Architecture diagram (Application → Decorator → Strategy → Tenacity → OTel)
   - Core components: RetryConfig, RetryStrategy enum, decorators (@retry, @retry_async, retry_context)
   - Pre-built strategies: HTTPStrategy, DatabaseStrategy, AgentStrategy, CustomStrategy
   - OpenTelemetry integration: span events, metrics (retry_attempts_total, retry_latency_seconds)
   - Exception hierarchy (RetryException, RetryExhausted, RetryTimeout)
   - Backoff formula: min(2^attempt + random(0,1), 60)
   - Configuration via environment variables (RETRY_*) + pydantic settings

3. **docs/changes/research-library-retry/tasks.md** (660 lines)
   - 4-phase implementation (Core Library, Testing & Docs, Integration & Migration, Validation & Closure)
   - 13 tasks with dependencies, deliverables, acceptance criteria
   - Phase 1 (T1.1–T1.4): Core library, decorators, strategies, observability
   - Phase 2 (T2.1–T2.4): Tests, documentation, examples
   - Phase 3 (T3.1–T3.3): Migrate 3 services (HTTP, Agent, optionally DB)
   - Phase 4 (T4.1–T4.4): Performance benchmarking, QA, adoption verification, closure
   - Success metrics: ≥95% coverage, 3+ services migrated, >80% retry success, <1ms nominal overhead

## Key Design Decisions

### 1. **Library-First + Tenacity**
- Use tenacity (8.3.0) as foundation, NOT custom implementation
- Thin wrapper exposing project conventions
- Rationale: Already a dependency, battle-tested, well-documented
- Aligns with CLAUDE.md mandate: "No manual retry loops; use tenacity"

### 2. **Strategy Pattern**
- Pre-built strategies for common use cases: HTTP, Database, Agent, Default, Custom
- Strategy returns a predicate: `Exception → bool`
- Allows centralized exception detection logic
- Easy to extend without modifying retry decorator

### 3. **Exponential Backoff with Jitter**
- Formula: `min(2^attempt + random(0, 1), 60)` seconds
- Configurable: exponential_base, max_delay_seconds, jitter flag
- Prevents thundering herd on service recovery
- Aligns with industry best practices

### 4. **OpenTelemetry Observability**
- Every retry attempt → span event with attributes (strategy, attempt #, error type, backoff delay)
- Metrics: Counter (retry_attempts_total), Histogram (retry_latency_seconds)
- Observability optional (RETRY_EMIT_METRICS, RETRY_EMIT_TRACES flags)
- Enables production debugging + dashboarding

### 5. **Configuration via Pydantic**
- RetryConfig inherits from pydantic BaseSettings
- Environment variable support (RETRY_* prefix)
- Per-call override support (kwargs to @retry decorator)
- Defaults: max_attempts=5, exponential_base=2, max_delay_seconds=60

### 6. **Three Decorator Styles**
- `@retry()` — for sync functions
- `@retry_async()` — for async functions
- `retry_context()` — for code blocks (with/as)
- All support strategy selection and config override

## Architecture Highlights

```
Application → @retry/@retry_async/retry_context → Strategy (matcher predicate)
           → Tenacity (stop_after_attempt, wait_random_exponential)
           → OpenTelemetry (span events, metrics)
```

**No circular dependencies**, clean layering:
- Retry layer (decorators) wraps tenacity
- Strategy layer (exception detection) is independent
- Observability layer (OTel) hooks into retry layer

## Implementation Phases

| Phase | Tasks | Estimated |
|-------|-------|-----------|
| 1: Core | T1.1–T1.4 (Module structure, decorators, strategies, OTel) | 8–12 min |
| 2: Tests & Docs | T2.1–T2.4 (Unit tests, integration, examples, docs) | 12–16 min |
| 3: Migration | T3.1–T3.3 (Migrate 3 services: HTTP, Agent, DB) | 8–12 min |
| 4: Closure | T4.1–T4.4 (Benchmark, QA, adoption verification, handoff) | 6–10 min |
| **Total** | — | **34–50 min** (agent wall-clock) |

## Success Criteria

1. **Code Quality**: ≥95% test coverage (target 100%)
2. **Adoption**: 3+ services migrated (HTTP client, Agent service, optional DB)
3. **Observability**: All retries traced + metricated (zero dark spans)
4. **Performance**: <1ms nominal path overhead, <100us backoff calculation
5. **Documentation**: Quick start + 5 worked examples + troubleshooting guide

## Open Questions for Next Phase

1. **Should we auto-detect HTTP 429 (rate limit) and use Retry-After header?**
   - Current design: Retry with exponential backoff (can be tuned per strategy)
   - Alternative: Parse Retry-After header when present
   - Recommend: Start simple (exponential), add Retry-After in Phase 2 if needed

2. **Should circuit breaker (pybreaker) be integrated with retry?**
   - Current design: Separate concerns (retry for transients, circuit breaker for cascades)
   - Could be Phase 2 enhancement: "Circuit breaker + Retry" pattern

3. **Should we auto-retry on all HTTPExceptions or be selective?**
   - Current design: Pre-built HTTPStrategy detects 5xx, timeouts, connection errors
   - Rationale: Avoid retrying client errors (4xx) which won't succeed
   - Recommendation: Keep selective (current design)

4. **Should database retry be Phase 1 or Phase 2?**
   - Current design: Phase 3 (lower priority, only if time permits)
   - Rationale: HTTP + Agent are higher priority
   - Recommendation: Defer to Phase 3 if needed

## Integration Checklist

- [ ] Verify tenacity 8.3.0 in pyproject.toml ✅
- [ ] Verify OpenTelemetry 1.24.0 in pyproject.toml ✅
- [ ] Check for existing retry patterns (search for "retry" in codebase) — TBD
- [ ] Identify 3 services for migration — TBD
- [ ] Plan metrics + dashboard integration — TBD

## Handoff to Next Agent

**What's ready**:
- Proposal, design, task breakdown (comprehensive and structured)
- Clear acceptance criteria for all tasks
- Risk mitigation plan + rollback strategy
- Dependency graph for parallel execution

**What's next**:
1. **Assign Phase 1 tasks** (T1.1–T1.4) to implementation agent
2. **Execute core library** (module structure, decorators, strategies, OTel)
3. **Run unit tests** to validate Phase 1
4. **Proceed to Phase 2** (comprehensive testing, documentation, examples)
5. **Migrate 3 services** and collect adoption metrics (Phase 3)
6. **Finalize & close** with performance benchmarks and QA (Phase 4)

**Key files to reference**:
- `docs/changes/research-library-retry/proposal.md` — Business case, scope, goals
- `docs/changes/research-library-retry/design.md` — Technical architecture, component design
- `docs/changes/research-library-retry/tasks.md` — Task breakdown, acceptance criteria
- `pyproject.toml` — Verify tenacity + OTel dependencies
- `CLAUDE.md` — Library-first principle, retry mandate

---

## References

- **Tenacity**: https://tenacity.readthedocs.io/
- **OpenTelemetry Python**: https://opentelemetry.io/docs/instrumentation/python/
- **Exponential Backoff + Jitter**: AWS Architecture Blog (2015)
- **CLAUDE.md Library Standards**: `Retry/backoff: tenacity, No manual retry loops`
