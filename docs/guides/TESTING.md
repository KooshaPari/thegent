# thegent Testing Guide

This guide defines the testing philosophy and standards for `thegent`.

## 1. Test Pyramid Targets

We maintain a strict test distribution to ensure fast feedback and high reliability:

-   **Unit Tests (70%)**: Fast, isolated tests for individual functions and classes. Found in `tests/` with `@pytest.mark.unit`.
-   **Integration Tests (20%)**: Testing interaction between components (e.g., runners and registries). Marked with `@pytest.mark.integration`.
-   **E2E Tests (10%)**: End-to-end CLI/MCP flows. Marked with `@pytest.mark.e2e`.

Use `task test:pyramid` to validate the current distribution.

## 2. Methodology

### Test-First (TDD)
Implementations should follow the Red-Green-Refactor loop. Every new feature requires a corresponding test file **before** implementation.

### FR Traceability
Every test function **must** reference a functional requirement ID using the `@trace` tag or marker.

```python
@pytest.mark.requirement("FR-CORE-001")
def test_core_functionality():
    # ...
```

## 3. Tooling

-   **Pytest**: Primary test runner.
-   **pytest-xdist**: Used for parallel execution (`task test`).
-   **Coverage**: We target > 80% line coverage.
-   **Traceability Validator**: `task quality` runs `scripts/traceability-validator.sh`.

## 4. Canonical Naming

Test files must be named based on the **concern** they test, not the level.
-   ✅ `tests/test_adapters.py`
-   ❌ `tests/test_unit_adapters.py`
