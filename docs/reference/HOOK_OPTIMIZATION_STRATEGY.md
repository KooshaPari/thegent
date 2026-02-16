# Hook Optimization Strategy

## Current State Analysis

The hooks already implement several optimizations:
1. **Git-aware caching** - Cache results keyed on git state
2. **Cross-hook shared results** - Changed files computed once
3. **Circuit breaker** - Fast-fail for broken tools
4. **Smart skip** - Only run if relevant files changed
5. **Async test runner** - Run affected tests after edits

## Implementation Status

| Priority | Optimization | Status | Location |
|----------|-------------|--------|----------|
| P0 | Fix timeout issue | Done | hook-config.yaml `timeout_overrides` |
| P1 | Affected test selection | Done | common.sh `affected_tests_for_file`, `get_affected_tests` |
| P2 | Pre-warm caches | Done | common.sh `hook_prewarm_all`, qa-preflight.sh |
| P3 | Parallel pipeline | Done | quality-gate.sh staged execution |
| P4 | Speculative execution | Done | async-test-runner uses `get_affected_tests`, speculative-stop-prewarmer |
| P5 | Learning-based skip | Done (infra) | common.sh `hook_learning_record`, `hook_learning_should_skip` |

## Remaining Optimizations (Next Steps)

### 1. Incremental Analysis (P6)
- Only re-analyze changed functions, not entire files
- For Python: use ast parse to find changed functions
- For TypeScript: use ts-morph or similar
- **Effort:** High | **Impact:** Medium

### 2. Coverage-Based Test Selection (P7)
- Use pytest-cov, vitest --coverage, cargo-tarpaulin
- Map changed files → affected functions → affected tests via coverage data
- **Effort:** Medium | **Impact:** High (more precise than file-pattern matching)

### 3. Background Daemon Mode (P8)
- Optional: Run lightweight watcher to pre-process
- Keep index of code → test mappings hot
- Pre-warm caches on file system events
- **Effort:** High | **Impact:** Low (diminishing returns)

### 4. Wire Learning-Based Skip (P5 completion)
- Integrate `hook_learning_record` / `hook_learning_should_skip` into quality-gate
- Set `learning_skip: true` in hook-config when ready
- **Effort:** Low | **Impact:** Low (opt-in, conservative)

## Configuration

Current hook-config.yaml settings:
```yaml
settings:
  cache_ttl: 600
  smart_skip: true
  prewarm_on_session_start: true
  parallel_stages: true
  speculative: true
  learning_skip: false  # opt-in
  timeout_overrides:
    quality-gate: 300
    task-completion: 300
    security-pipeline: 600
```
