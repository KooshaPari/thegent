# clode_model_cmds API Reference

> **Source**: `src/thegent/clode_model_cmds.py`

Model commands for clode CLI.

These commands provide shortcuts to specific models.
Extracted from clode_main.py for maintainability.

---

## create_model_command

```python
create_model_command(app: typer.Typer, name: str, model_alias: str, help_text: str)
```

Create a model command and register it with the app.

**Parameters**:

- `app`: Typer app to register command with
- `name`: Command name
- `model_alias`: Model alias to pass to runner
- `help_text`: Help text for command

---

## model_cmd

```python
model_cmd(provider: Any, resume: Any, cd: Any, print_mode: bool, debug: bool, add_dir: list[str], output_format: Any, continue_session: bool, prompt: Any)
```

Model shortcut command.

---

## register_model_commands

```python
register_model_commands(app: typer.Typer)
```

Register all model commands with the app.

**Parameters**:

- `app`: Typer app to register commands with

---

