# main_shortcuts API Reference

> **Source**: `src/thegent/cli/apps/main_shortcuts.py`

Top-level shortcut command registrations for thegent.

---

## doctor_cmd

```python
doctor_cmd(fix: bool, dry_run: bool)
```

Run thegent doctor from the unified top-level command surface.

---

## fork_top_level

```python
fork_top_level(session_id: str, from_turn: Any, new_session_id: Any) -> None
```

---

## hmr_top_level

```python
hmr_top_level(project_root: Path, debounce_s: float) -> None
```

---

## list_agents_cmd_wrapper

---

## list_droids_cmd_wrapper

```python
list_droids_cmd_wrapper(cd: Any) -> None
```

---

## quick_do

```python
quick_do(prompt: str) -> None
```

---

## quick_ps

```python
quick_ps(all_sessions: bool, owner: Any, format: str, include_contract: bool) -> None
```

---

## register_main_shortcuts

```python
register_main_shortcuts(app: typer.Typer, console: Console)
```

Register top-level shortcut commands onto the root CLI app.

---

## reload_top_level

---

## resume_top_level

```python
resume_top_level(session_id: Any, prompt: Any, skill: Any) -> None
```

---

## review_cmd

```python
review_cmd(prompt: str, agent: Any, model: Any, format: str) -> None
```

---

## rollback_top_level

```python
rollback_top_level(session_id: str, n_turns: int) -> None
```

---

## setup_app_command

```python
setup_app_command(api_key: Any, model: Any, openrouter_key: Any, kilo_key: Any, zai_key: Any, minimax_key: Any, wizard: bool, links: bool, hooks: bool, skills: bool, harness: bool, full: bool, agents: Any)
```

Legacy compatibility wrapper for setup flow.

---

