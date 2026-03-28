# run_harness API Reference

> **Source**: `src/thegent/use_cases/run_harness.py`

Use case: Run a harness (Claude/Codex) with model/provider routing.

---

## RunHarness

Orchestrate harness execution (run_interactive, run_exec, etc.).

### Methods

#### RunHarness.__init__

```python
__init__(self: Any, harness_type: str)
```

Initialize with harness type ('claude' or 'codex').

---

#### RunHarness.ensure_harness_installed

```python
ensure_harness_installed(self: Any)
```

Ensure harness binary is installed. Returns path.

---

#### RunHarness.run_interactive

```python
run_interactive(self: Any, model_alias: str, provider: Optional[str], resume: Optional[str], prompt: Optional[str])
```

Start interactive session with model/provider routing.

---

#### RunHarness.run_native

```python
run_native(self: Any, args: Optional[list[str]])
```

Bypass proxy and run native binary directly.

---

---

## ensure_harness_installed

```python
ensure_harness_installed(self: Any)
```

Ensure harness binary is installed. Returns path.

---

## run_interactive

```python
run_interactive(self: Any, model_alias: str, provider: Optional[str], resume: Optional[str], prompt: Optional[str])
```

Start interactive session with model/provider routing.

---

## run_native

```python
run_native(self: Any, args: Optional[list[str]])
```

Bypass proxy and run native binary directly.

---

