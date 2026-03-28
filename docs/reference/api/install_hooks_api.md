# install_hooks API Reference

> **Source**: `src/thegent/install_hooks.py`

Hook installation functions for thegent.

Extracted from install.py for maintainability.

---

## setup_harness

```python
setup_harness(verbose: bool)
```

Setup the test harness.

**Parameters**:

- `verbose`: If True, print details

**Returns**: True if setup succeeded

---

## setup_hooks

```python
setup_hooks(cwd: Any, dry_run: bool, verbose: bool)
```

Install thegent hooks into .git/hooks.

**Parameters**:

- `cwd`: Working directory (defaults to cwd)
- `dry_run`: If True, don't make changes
- `verbose`: If True, print details

**Returns**: Dict with counts: installed, skipped, errors

---

## setup_rust_dispatcher

```python
setup_rust_dispatcher(verbose: bool)
```

Setup the Rust dispatcher binary.

**Parameters**:

- `verbose`: If True, print details

**Returns**: True if setup succeeded

---

## setup_skills

```python
setup_skills(skills_dir: Any, dry_run: bool, verbose: bool)
```

Setup skills from factory directory.

**Parameters**:

- `skills_dir`: Target directory for skills
- `dry_run`: If True, don't make changes
- `verbose`: If True, print details

**Returns**: Dict with counts: installed, skipped, errors

---

