# session_owner_helpers API Reference

> **Source**: `src/thegent/cli/commands/session_owner_helpers.py`

Session owner/tag and scope path helpers extracted from CLI impl.

---

## compose_owner_tag

```python
compose_owner_tag(user: str, cwd: Path, scope: str)
```

Build deterministic owner tags with optional scope expansion.

---

## default_owner_tag

```python
default_owner_tag(cwd: Any) -> str
```

---

## scope_key

```python
scope_key(owner: str) -> str
```

---

## session_dir

```python
session_dir(settings: ThegentSettings, owner: str) -> Path
```

---

## session_scope_dirs

```python
session_scope_dirs(base: Path, owner: str)
```

Return session scope directories for an owner key, including pid-scoped variants.

---

