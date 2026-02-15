# Anti-Pattern Detection Guide

Hooks in `hooks/suppress-*.sh` detect and prevent common agent anti-patterns at Write/Edit time. Each hook runs during PreToolUse events.

---

## 1. Custom Retry Logic (`suppress-custom-retry.sh`)

**Pattern**: Manual retry loops (`while retry`, `for i in range(max_retries)`, `sleep` + retry).

**Why it's bad**: tenacity is already in project deps. Manual retry loops are error-prone (missing jitter, no backoff, no configurable stop conditions).

**Fix**:
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(5), wait=wait_exponential())
def fetch(url: str) -> httpx.Response:
    return httpx.get(url, timeout=10)
```

**Enforcement**: Advisory (warning only).

---

## 2. V2/Duplicate Files (`suppress-v2-files.sh`)

**Pattern**: Files named `*_v2.*`, `*_new.*`, `*_old.*`, `*_backup.*`, `*_copy.*`, `*.bak`.

**Why it's bad**: Duplicates create maintenance burden and divergent implementations. The original file should be refactored instead.

**Fix**: Refactor the original file. Use git branches for experimental changes.

**Enforcement**: **BLOCKING** (prevents file creation).

---

## 3. Hardcoded Provider Strings (`suppress-hardcoded-strings.sh`)

**Pattern**: `provider = "openai"`, `model = "gpt-4"` in non-config files.

**Why it's bad**: Hardcoded providers make switching impossible without code changes. Config-driven selection enables multi-provider support.

**Fix**:
```python
from myproject.config import settings
provider = registry.get(settings.llm_provider)
```

**Enforcement**: Advisory (warning only).

---

## 4. Print Statements (`suppress-print-statements.sh`)

**Pattern**: `print()` calls in non-CLI source code (2+ occurrences).

**Why it's bad**: print() produces unstructured output that can't be filtered, aggregated, or routed. structlog provides structured, context-rich logging.

**Fix**:
```python
import structlog
logger = structlog.get_logger()
logger.info("message", key="value")
```

**Enforcement**: Advisory (warning only). CLI entry points (main.py, cli.py) are excluded.

---

## 5. God Classes (`suppress-isolated-classes.sh`)

**Pattern**: Classes with >15 methods, or 3+ Manager/Handler/Service classes in one file.

**Why it's bad**: God classes violate single responsibility. Multiple Manager-pattern classes suggest a missing generic registry.

**Fix**: Decompose into smaller classes. Use Protocol/ABC for shared interfaces. Consider a registry pattern for N similar classes.

**Enforcement**: Advisory (warning only).

---

## 6. Direct HTTP / Wrong Library (`suppress-direct-http.sh`)

**Pattern**: `import requests`, `import urllib`, or custom HTTP wrapper classes without httpx.

**Why it's bad**: httpx is the project standard (async-capable, modern API). requests is sync-only. urllib is low-level. Custom wrappers duplicate httpx functionality.

**Fix**:
```python
import httpx
response = httpx.get(url, timeout=10)

# Async
async with httpx.AsyncClient() as client:
    response = await client.get(url, timeout=10)
```

**Enforcement**: Advisory (warning only).

---

## Hook Integration

All hooks receive these environment variables from the dispatcher:
- `FILE_PATH` — absolute path to the file being written/edited
- `TOOL_CONTENT` — full file content (Write)
- `TOOL_NEW_STRING` — replacement text (Edit)
- `TOOL_NAME` — "Write" or "Edit"

### Blocking vs Advisory

| Hook | Behavior | Exit Code |
|------|----------|-----------|
| suppress-v2-files | **Blocking** | 2 (with JSON) |
| All others | Advisory | 0 (always) |

### Consolidated Detector

`agent-antipattern-detector.sh` combines all patterns into a single hook for performance. The individual `suppress-*.sh` hooks exist for targeted use or when only specific patterns should be checked.
