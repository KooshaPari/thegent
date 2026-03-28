# phench_env API Reference

> **Source**: `src/thegent/cli/apps/phench_env.py`

Phench environment-management commands.

---

## env_doctor_cmd

```python
env_doctor_cmd(name: str, family: Any) -> None
```

---

## env_profile_set_cmd

```python
env_profile_set_cmd(name: str, family: Any, profile: str, vars: list[str]) -> None
```

---

## env_profile_show_cmd

```python
env_profile_show_cmd(name: str, family: Any, profile: Any) -> None
```

---

## register_env_commands

```python
register_env_commands(env_app: typer.Typer, run_env_doctor_for_target_fn: Any, set_env_profile_fn: Any, get_env_profile_fn: Any)
```

Register environment-related commands on the phench env sub-app.

---

