# Package Replacement Implementation Plan

> **Status**: Ready for Implementation | **Date**: 2026-02-18  
> **Source**: Consolidated from LIBRARY_REPLACEMENT_COMPLETE.md, LIBRARY_REPLACEMENT_CONSOLIDATED.md, LIBRARY_REPLACEMENT_PHASE_DWBS.md  
> **Purpose**: Complete implementation guide for all package replacement tasks

---

## Executive Summary

This plan consolidates all package replacement tasks from the library replacement audit into a single, actionable implementation plan. All tasks are prioritized, have clear acceptance criteria, and include migration patterns.

**Total Tasks**: 9 major replacements + 4 enhancements  
**Total Effort**: ~40-60 hours  
**Priority Breakdown**: P1 (Critical): 3 tasks, P2 (High Value): 6 tasks, P3 (Polish): 4 tasks

---

## Task Inventory

### Priority 1 (P1) - Critical Replacements

| Task ID | Title | Files | Effort | Status | Source |
|---------|-------|-------|--------|--------|--------|
| **IMPL-LIB-001** | Replace urllib with httpx | 7+ files | 2-3 hrs | ⏳ Pending | Phase 1 |
| **IMPL-LIB-002** | Migrate retry to tenacity | 4 files | 4-6 hrs | ⏳ Pending | Phase 2 |
| **IMPL-LIB-003** | Replace polling with watchdog | 1 file | 2-4 hrs | ⏳ Pending | Phase 3 |

### Priority 2 (P2) - High Value Replacements

| Task ID | Title | Files | Effort | Status | Source |
|---------|-------|-------|--------|--------|--------|
| **IMPL-LIB-101** | Replace custom caching with cachetools | 5+ files | 2-3 hrs | ⏳ Pending | Phase 5 |
| **IMPL-LIB-102** | Replace circuit breaker with pybreaker | 1 file | 2-3 hrs | ⏳ Pending | Phase 8 |
| **IMPL-LIB-103** | Replace PyYAML with ruamel.yaml | 15+ files | 3-4 hrs | ⏳ Pending | Phase 4.3 |
| **IMPL-LIB-104** | Replace ANSI stripping with rich | 5 files | 1 hr | ⏳ Pending | Phase 4 |
| **IMPL-LIB-105** | Replace scrapers cache with diskcache | 1 file | 1 hr | ⏳ Pending | Phase 6 |
| **IMPL-LIB-106** | Add psutil for resource monitoring | 2 files | 2-3 hrs | ⏳ Pending | Phase 7 |

### Priority 3 (P3) - Quick Wins & Enhancements

| Task ID | Title | Files | Effort | Status | Source |
|---------|-------|-------|--------|--------|--------|
| **IMPL-LIB-201** | Replace md5 with sha256 | 1 file | 0.5 hr | ⏳ Pending | Phase 9 |
| **IMPL-LIB-202** | Consolidate os.environ → ThegentSettings | 15+ files | 2-3 hrs | ⏳ Pending | Phase 10 |
| **IMPL-LIB-203** | Replace _CWD_CACHE with cachetools | 1 file | 0.5 hr | ⏳ Pending | Phase 21 |
| **IMPL-LIB-204** | Add tomlkit to dependencies | pyproject.toml | 0.5 hr | ⏳ Pending | Phase 19 |

---

## Detailed Task Breakdown

### IMPL-LIB-001: Replace urllib with httpx (P1)

**Priority**: P1 (Critical)  
**Effort**: 2-3 hours  
**Dependencies**: None (httpx already in deps)

#### Files Affected
1. `models/scrapers.py` - `_scrape_proxy_models`, `_scrape_openai_models`
2. `agents/cliproxy_manager.py` - Health check, model fetch
3. `agents/cursor_api_runner.py` - Health check
4. `execution.py` - Policy check URL
5. `mcp_manage.py` - Config fetch (2 calls)
6. `clode_main.py` - Health URL check
7. `routing/alerting.py` - Webhook POST
8. `mgmt_manage.py` - (if present)

#### Migration Pattern

**Before**:
```python
import urllib.request
import urllib.error

try:
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=2) as resp:
        data = resp.read().decode()
except urllib.error.URLError as e:
    handle_error(e)
except urllib.error.HTTPError as e:
    handle_error(e)
```

**After**:
```python
import httpx

try:
    resp = httpx.get(url, timeout=2)
    resp.raise_for_status()
    data = resp.text
except httpx.RequestError as e:
    handle_error(e)
except httpx.HTTPStatusError as e:
    handle_error(e)
```

#### Exception Mapping
- `urllib.error.URLError` → `httpx.RequestError` or `httpx.ConnectError`
- `urllib.error.HTTPError` → `httpx.HTTPStatusError` (check `resp.raise_for_status()`)

#### Acceptance Criteria
- [ ] All urllib imports removed
- [ ] All HTTP calls use httpx
- [ ] Exception handling updated
- [ ] Tests pass
- [ ] No regressions in functionality

#### Testing
- Unit tests for each file
- Integration tests for HTTP endpoints
- Error handling tests

---

### IMPL-LIB-002: Migrate retry to tenacity (P1)

**Priority**: P1 (Critical)  
**Effort**: 4-6 hours  
**Dependencies**: None (tenacity already in deps)

#### Files Affected
1. `cli_impl.py` - EAGAIN retry (if present), DAG retry backoff (if present)
2. `agents/loop_controller.py` - Retry loop (verify current state)
3. `agents/state_machine.py` - Verify already uses tenacity ✅

#### Migration Pattern

**Before**:
```python
max_retries = 3
backoff = 1
for attempt in range(max_retries):
    try:
        result = do_work()
        break
    except Exception as e:
        if attempt == max_retries - 1:
            raise
        time.sleep(backoff * (2 ** attempt))
```

**After**:
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    reraise=True
)
def do_work():
    # Implementation
    pass
```

#### Acceptance Criteria
- [ ] All manual retry loops replaced with tenacity decorators
- [ ] Retry behavior matches original
- [ ] Tests pass
- [ ] Performance maintained or improved

#### Notes
- Some patterns may not exist (see LIBRARY_REPLACEMENT_PHASE_DWBS.md Phase 2 notes)
- Verify current state before migrating

---

### IMPL-LIB-003: Replace polling with watchdog (P1)

**Priority**: P1 (Critical)  
**Effort**: 2-4 hours  
**Dependencies**: Add `watchdog>=4.0.0` to dependencies

#### Files Affected
1. `governance/triggers.py` - Replace `os.walk` polling with `Observer`

#### Migration Pattern

**Before**:
```python
import os
import time

while True:
    for root, dirs, files in os.walk(directory):
        # Check mtime, trigger if changed
        pass
    time.sleep(2)  # Poll every 2 seconds
```

**After**:
```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class TriggerHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory:
            trigger_cycle(event.src_path)

observer = Observer()
observer.schedule(TriggerHandler(), directory, recursive=True)
observer.start()
```

#### Acceptance Criteria
- [ ] `watchdog>=4.0.0` added to dependencies
- [ ] Polling replaced with Observer
- [ ] FileSystemEventHandler implemented
- [ ] exclude_dirs behavior preserved
- [ ] Tests pass
- [ ] CPU usage reduced

---

### IMPL-LIB-101: Replace custom caching with cachetools (P2)

**Priority**: P2 (High Value)  
**Effort**: 2-3 hours  
**Dependencies**: Add `cachetools>=5.0.0` to dependencies

#### Files Affected
1. `models/speed_values.py` - `_CACHE`
2. `models/quality_values.py` - `_CACHE`
3. `models/catalog.py` - Route cache
4. `cli_impl.py` - `_CWD_CACHE` (see IMPL-LIB-203)

#### Migration Pattern

**Before**:
```python
class CustomCache:
    def __init__(self, ttl=3600):
        self.cache = {}
        self.timestamps = {}
    
    def get(self, key):
        if key in self.cache:
            if time.time() - self.timestamps[key] < self.ttl:
                return self.cache[key]
            del self.cache[key]
            del self.timestamps[key]
        return None
```

**After**:
```python
from cachetools import TTLCache

cache = TTLCache(maxsize=1000, ttl=3600)

# Usage
value = cache.get(key)
if value is None:
    value = compute_value()
    cache[key] = value
```

#### Acceptance Criteria
- [ ] `cachetools>=5.0.0` added to dependencies
- [ ] All custom caches replaced with TTLCache
- [ ] Cache behavior matches original
- [ ] Tests pass
- [ ] Memory usage improved

---

### IMPL-LIB-102: Replace circuit breaker with pybreaker (P2)

**Priority**: P2 (High Value)  
**Effort**: 2-3 hours  
**Dependencies**: Add `pybreaker>=1.0.0` to dependencies

#### Files Affected
1. `agents/resilience.py` - `ToolCircuitBreaker`

#### Migration Pattern

**Before**:
```python
class ToolCircuitBreaker:
    def __init__(self):
        self.failures = []
        self.state = "closed"
    
    def call(self, func, *args, **kwargs):
        if self.state == "open":
            raise CircuitBreakerOpen()
        try:
            result = func(*args, **kwargs)
            self.record_success()
            return result
        except Exception as e:
            self.record_failure()
            raise
```

**After**:
```python
from pybreaker import CircuitBreaker

breaker = CircuitBreaker(
    fail_max=5,
    timeout_duration=60
)

@breaker
def call_tool():
    # Implementation
    pass
```

#### Acceptance Criteria
- [ ] `pybreaker>=1.0.0` added to dependencies
- [ ] Custom circuit breaker replaced
- [ ] State machine behavior matches
- [ ] Tests pass
- [ ] Thread-safe operation verified

---

### IMPL-LIB-103: Replace PyYAML with ruamel.yaml (P2)

**Priority**: P2 (High Value)  
**Effort**: 3-4 hours  
**Dependencies**: Add `ruamel.yaml>=0.18.0` to dependencies

#### Files Affected
15+ files using PyYAML

#### Migration Pattern

**Before**:
```python
import yaml

with open('config.yaml') as f:
    config = yaml.safe_load(f)

# Edit config
config['key'] = 'value'

# Save (loses comments, key order)
with open('config.yaml', 'w') as f:
    yaml.dump(config, f)
```

**After**:
```python
from ruamel.yaml import YAML

yaml = YAML()
yaml.preserve_quotes = True

with open('config.yaml') as f:
    config = yaml.load(f)

# Edit config
config['key'] = 'value'

# Save (preserves comments, key order)
with open('config.yaml', 'w') as f:
    yaml.dump(config, f)
```

#### Acceptance Criteria
- [ ] `ruamel.yaml>=0.18.0` added to dependencies
- [ ] All PyYAML imports replaced
- [ ] Comments preserved in config files
- [ ] Key order preserved
- [ ] Tests pass
- [ ] Round-trip safety verified

---

### IMPL-LIB-104: Replace ANSI stripping with rich (P2)

**Priority**: P2 (High Value)  
**Effort**: 1 hour  
**Dependencies**: None (rich already in deps)

#### Files Affected
1. `agents/codex_proxy.py`
2. `agents/direct_agents.py`
3. `agents/droid.py`
4. `agents/cursor_api_runner.py`
5. `parser.py`

#### Migration Pattern

**Before**:
```python
import re

def strip_ansi(text):
    return re.sub(r'\x1b\[[0-9;]*m', '', text)
```

**After**:
```python
from rich.console import strip_control_codes

def strip_ansi(text):
    return strip_control_codes(text)
```

#### Acceptance Criteria
- [ ] Create `thegent.utils.strip_ansi` utility
- [ ] Replace all custom ANSI stripping
- [ ] Tests pass
- [ ] Edge cases handled correctly

---

### IMPL-LIB-105: Replace scrapers cache with diskcache (P2)

**Priority**: P2 (High Value)  
**Effort**: 1 hour  
**Dependencies**: Add `diskcache>=5.0.0` to dependencies

#### Files Affected
1. `models/scrapers.py` - `_load_cached`, `_save_cache`

#### Migration Pattern

**Before**:
```python
# Custom file-based cache
def _load_cached(key):
    cache_file = f"/tmp/cache/{key}.json"
    if os.path.exists(cache_file):
        # Check TTL, load if valid
        pass

def _save_cache(key, value):
    cache_file = f"/tmp/cache/{key}.json"
    # Save with timestamp
    pass
```

**After**:
```python
import diskcache

cache = diskcache.Cache('/tmp/cache', size_limit=1e9)

def _load_cached(key):
    return cache.get(key)

def _save_cache(key, value, expire=3600):
    cache.set(key, value, expire=expire)
```

#### Acceptance Criteria
- [ ] `diskcache>=5.0.0` added to dependencies
- [ ] File-based cache replaced
- [ ] TTL behavior matches
- [ ] Tests pass
- [ ] Disk usage optimized

---

### IMPL-LIB-106: Add psutil for resource monitoring (P2)

**Priority**: P2 (High Value)  
**Effort**: 2-3 hours  
**Dependencies**: Add `psutil>=5.9.0` to dependencies

#### Files Affected
1. `orchestration/load_based_limits.py` - `_get_fd_usage`, `_get_memory_mb`, `_get_load_avg`
2. `discovery.py` - Process discovery via ps parsing

#### Migration Pattern

**Before**:
```python
import subprocess

def get_memory_usage():
    result = subprocess.run(['ps', '-o', 'rss=', str(pid)], capture_output=True)
    return int(result.stdout.strip())
```

**After**:
```python
import psutil

def get_memory_usage():
    process = psutil.Process(pid)
    return process.memory_info().rss
```

#### Acceptance Criteria
- [ ] `psutil>=5.9.0` added to dependencies
- [ ] Subprocess-based monitoring replaced
- [ ] Cross-platform compatibility verified
- [ ] Tests pass
- [ ] Performance improved

---

### IMPL-LIB-201: Replace md5 with sha256 (P3)

**Priority**: P3 (Quick Win)  
**Effort**: 0.5 hour  
**Dependencies**: None

#### Files Affected
1. `tools/cache.py` - ETag uses md5

#### Migration Pattern

**Before**:
```python
import hashlib

etag = hashlib.md5(content).hexdigest()
```

**After**:
```python
import hashlib

etag = hashlib.sha256(content).hexdigest()
```

#### Acceptance Criteria
- [ ] md5 replaced with sha256
- [ ] Tests pass
- [ ] No breaking changes

---

### IMPL-LIB-202: Consolidate os.environ → ThegentSettings (P3)

**Priority**: P3 (Enhancement)  
**Effort**: 2-3 hours  
**Dependencies**: None (pydantic-settings already in deps)

#### Files Affected
15+ files using `os.environ.get`

#### Migration Pattern

**Before**:
```python
import os

api_key = os.environ.get('API_KEY')
timeout = int(os.environ.get('TIMEOUT', '30'))
```

**After**:
```python
from thegent.config import settings

api_key = settings.api_key
timeout = settings.timeout
```

#### Acceptance Criteria
- [ ] All THGENT_* env vars in ThegentSettings
- [ ] os.environ.get calls replaced
- [ ] Type validation working
- [ ] Tests pass
- [ ] Default values preserved

---

### IMPL-LIB-203: Replace _CWD_CACHE with cachetools (P3)

**Priority**: P3 (Quick Win)  
**Effort**: 0.5 hour  
**Dependencies**: cachetools (from IMPL-LIB-101)

#### Files Affected
1. `cli_impl.py` - `_CWD_CACHE`

#### Migration Pattern

**Before**:
```python
_CWD_CACHE = {}

def _resolve_cwd(path):
    if path in _CWD_CACHE:
        return _CWD_CACHE[path]
    # Resolve logic
    _CWD_CACHE[path] = resolved
    return resolved
```

**After**:
```python
from cachetools import TTLCache

_cwd_cache = TTLCache(maxsize=100, ttl=300)

def _resolve_cwd(path):
    if path in _cwd_cache:
        return _cwd_cache[path]
    # Resolve logic
    _cwd_cache[path] = resolved
    return resolved
```

#### Acceptance Criteria
- [ ] _CWD_CACHE replaced with TTLCache
- [ ] TTL behavior matches
- [ ] Tests pass

---

### IMPL-LIB-204: Add tomlkit to dependencies (P3)

**Priority**: P3 (Quick Win)  
**Effort**: 0.5 hour  
**Dependencies**: None

#### Files Affected
1. `pyproject.toml` - Add to dependencies

#### Migration Pattern

**Before**:
```toml
[project]
dependencies = [
    # ... existing deps
]
```

**After**:
```toml
[project]
dependencies = [
    # ... existing deps
    "tomlkit>=0.12.0",
]
```

#### Acceptance Criteria
- [ ] `tomlkit>=0.12.0` added to dependencies
- [ ] No breaking changes

---

## Implementation Order (Recommended)

### Phase 1: Quick Wins (1-2 hours)
1. **IMPL-LIB-204** - Add tomlkit (5 min)
2. **IMPL-LIB-201** - md5→sha256 (5 min)
3. **IMPL-LIB-104** - ANSI strip (1 hr)
4. **IMPL-LIB-203** - _CWD_CACHE (30 min)

### Phase 2: Critical Replacements (8-13 hours)
1. **IMPL-LIB-001** - urllib→httpx (2-3 hrs)
2. **IMPL-LIB-002** - retry→tenacity (4-6 hrs)
3. **IMPL-LIB-003** - polling→watchdog (2-4 hrs)

### Phase 3: High Value Replacements (12-18 hours)
1. **IMPL-LIB-101** - cachetools (2-3 hrs)
2. **IMPL-LIB-105** - diskcache (1 hr)
3. **IMPL-LIB-106** - psutil (2-3 hrs)
4. **IMPL-LIB-102** - pybreaker (2-3 hrs)
5. **IMPL-LIB-103** - ruamel.yaml (3-4 hrs)

### Phase 4: Enhancements (2-3 hours)
1. **IMPL-LIB-202** - os.environ→ThegentSettings (2-3 hrs)

**Total Effort**: ~23-36 hours

---

## Testing Strategy

### Unit Tests
- Each replacement: >90% coverage
- Critical paths: >95% coverage
- Error handling: >85% coverage

### Integration Tests
- HTTP requests with various endpoints
- Retry behavior under failures
- File watching with real filesystem
- Cache behavior with TTL
- Circuit breaker state transitions

### Performance Tests
- HTTP: <50ms (p95)
- File watch: <100ms latency
- Cache lookup: <0.5ms (p95)

---

## Success Metrics

### Performance Improvements
- ✅ HTTP: Connection pooling, HTTP/2 (httpx)
- ✅ File watch: Real-time (watchdog vs 2s polling)
- ✅ Cache: Automatic TTL, LRU (cachetools)
- ✅ Resource monitoring: Cross-platform (psutil)

### Code Quality
- ✅ Reduced custom code: -500+ lines
- ✅ Improved maintainability: Battle-tested libraries
- ✅ Better error handling: Library error types
- ✅ Security: Regular library updates

---

## Risk Mitigation

### Technical Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| API incompatibility | High | Comprehensive testing, gradual migration |
| Behavior changes | Medium | Feature flags, rollback plan |
| Performance regression | Low | Benchmarking, monitoring |
| Dependency issues | Medium | Version pinning, dependency audit |

### Migration Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking changes | High | Backward compatibility, feature flags |
| Testing gaps | Medium | Comprehensive test coverage |
| Rollback complexity | Medium | Phased rollout, monitoring |

---

## References

### Source Documents
- [LIBRARY_REPLACEMENT_COMPLETE.md](../research/LIBRARY_REPLACEMENT_COMPLETE.md) - Complete audit
- [LIBRARY_REPLACEMENT_CONSOLIDATED.md](../research/LIBRARY_REPLACEMENT_CONSOLIDATED.md) - Consolidated plan
- [LIBRARY_REPLACEMENT_PHASE_DWBS.md](../research/LIBRARY_REPLACEMENT_PHASE_DWBS.md) - Detailed task breakdowns

### External Resources
- [httpx Documentation](https://www.python-httpx.org/)
- [tenacity Documentation](https://tenacity.readthedocs.io/)
- [watchdog Documentation](https://python-watchdog.readthedocs.io/)
- [cachetools Documentation](https://cachetools.readthedocs.io/)
- [pybreaker Documentation](https://pybreaker.readthedocs.io/)
- [ruamel.yaml Documentation](https://yaml.readthedocs.io/)

---

## Next Steps

1. **Review this plan** with team
2. **Add missing tasks to WORK_STREAM.md** BACKLOG
3. **Start with Phase 1** (Quick Wins)
4. **Implement Phase 2** (Critical Replacements)
5. **Continue with Phase 3** (High Value)
6. **Complete Phase 4** (Enhancements)

---

**Status**: Ready for implementation  
**Last Updated**: 2026-02-18
