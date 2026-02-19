# consistency_checker API Reference

> **Source**: `src/thegent/integration/consistency_checker.py`

System-wide consistency checker.

---

## ConsistencyChecker

Check consistency across system.

This class verifies that all system components are consistent,
including version consistency, path consistency, and configuration consistency.

Examples:
    >>> checker = ConsistencyChecker()
    >>> violations = checker.check_all()
    >>> if violations:
    ...     for violation in violations:
    ...         print(f"{violation.component}.{violation.property}: "
    ...               f"expected {violation.expected_value}, "
    ...               f"got {violation.actual_value}")

### Methods

#### ConsistencyChecker.__init__

Initialize consistency checker.

```python
__init__(self)
```

#### ConsistencyChecker.check_all

Check all consistency rules.

Returns:
    List of consistency violations

```python
check_all(self)
```

---

## ConsistencyRule

Consistency rule definition.

---

## check_all

Check all consistency rules.

Returns:
    List of consistency violations

```python
check_all(self)
```

---

