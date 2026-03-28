# context_budget API Reference

> **Source**: `src/thegent/tui/context_budget.py`

Context budget indicator for TUI status bar and ANSI CLI output.

# @trace WL-108

---

## ContextBudget

Computed context budget for a single agent run.

# @trace WL-108

### Methods

#### ContextBudget.color

```python
color(self: Any)
```

Severity color: 'green' (<60%), 'yellow' (<80%), 'red' (>=80%).

---

#### ContextBudget.format_bar

```python
format_bar(self: Any)
```

Format as ``[CTX: 12k/128k]`` with optional ANSI color escape codes.

**Parameters**:

- `ansi`: When True (default), wrap output in ANSI color escapes.
Pass False for plain-text output (e.g. JSON serialisation).

**Returns**: A string like ``[CTX: 12k/128k]``, optionally ANSI-colored.

---

#### ContextBudget.ratio

```python
ratio(self: Any)
```

Fraction of context window consumed (0.0 – 1.0).

---

---

## color

```python
color(self: Any)
```

Severity color: 'green' (<60%), 'yellow' (<80%), 'red' (>=80%).

---

## context_budget_from_result

```python
context_budget_from_result(result: RunResult)
```

Build a :class:`ContextBudget` from a :class:`~thegent.agents.base.RunResult`.

Returns ``None`` when *result* does not carry full context token data
(i.e. when either ``context_tokens_used`` or ``context_window_max`` is
``None`` or when ``context_window_max`` is zero).

# @trace WL-108

**Parameters**:

- `result`: The completed agent run result.

**Returns**: A :class:`ContextBudget` instance, or ``None``.

---

## context_budget_indicator

```python
context_budget_indicator(result: RunResult)
```

Return a formatted ``[CTX: 12k/128k]`` indicator string for CLI/TUI use.

Convenience wrapper around :func:`context_budget_from_result` and
:meth:`ContextBudget.format_bar`.  Returns ``None`` when the result
does not carry context token data.

# @trace WL-108

**Parameters**:

- `result`: The completed agent run result.
- `ansi`:   Forward to :meth:`ContextBudget.format_bar`.

**Returns**: Formatted indicator string, or ``None``.

---

## format_bar

```python
format_bar(self: Any)
```

Format as ``[CTX: 12k/128k]`` with optional ANSI color escape codes.

**Parameters**:

- `ansi`: When True (default), wrap output in ANSI color escapes.
Pass False for plain-text output (e.g. JSON serialisation).

**Returns**: A string like ``[CTX: 12k/128k]``, optionally ANSI-colored.

---

## ratio

```python
ratio(self: Any)
```

Fraction of context window consumed (0.0 – 1.0).

---

