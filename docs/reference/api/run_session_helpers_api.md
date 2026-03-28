# run_session_helpers API Reference

> **Source**: `src/thegent/cli/services/run_session_helpers.py`

Session/model helper facade extracted from cli.commands.impl (WL-125).

---

## compose_owner_tag

```python
compose_owner_tag(user: str, cwd: Path, scope: str) -> str
```

---

## default_owner_tag

```python
default_owner_tag(cwd: Any) -> str
```

---

## new_session_id

---

## resolve_agent_model

---

## resolve_cwd

```python
resolve_cwd(cd: Any)
```

Resolve cwd: explicit --cd, or infer from current dir if project-like.

---

## resolve_droids_dir

```python
resolve_droids_dir(cwd: Any, settings: ThegentSettings)
```

Resolve droids dir: project .factory/droids first, then config.

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

## session_paths

---

## session_scope_dirs

```python
session_scope_dirs(base: Path, owner: str) -> list[Path]
```

---

