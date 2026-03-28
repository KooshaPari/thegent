# run_budget API Reference

> **Source**: `src/thegent/cli/services/run_budget.py`

Budget checking helpers for run execution.

Extracted from run_execution_core_helpers.py for maintainability.

---

## check_budget_limits

```python
check_budget_limits(settings: ThegentSettings)
```

Check if budget limits have been exceeded.

**Parameters**:

- `settings`: Thegent settings with budget configuration

**Returns**: Tuple of (blocked, error_message)

---

## check_budget_warning

```python
check_budget_warning(settings: ThegentSettings)
```

Check if budget is approaching limits (warning).

**Parameters**:

- `settings`: Thegent settings with budget configuration

**Returns**: Tuple of (warning, warning_message)

---

