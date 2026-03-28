# dex_model_cmds API Reference

> **Source**: `src/thegent/dex_model_cmds.py`

Model commands for dex CLI.

These commands provide shortcuts to specific models via Codex.
Extracted from dex_main.py for maintainability.

---

## create_dex_model_command

```python
create_dex_model_command(app: typer.Typer, name: str, model_alias: str, help_text: str)
```

Create a dex model command and register it with the app.

**Parameters**:

- `app`: Typer app to register command with
- `name`: Command name
- `model_alias`: Model alias to pass to runner
- `help_text`: Help text for command

---

## model_cmd

```python
model_cmd(resume: Any, cd: Any, print_mode: bool, full: bool, debug: bool, add_dir: list[str], native: bool, prompt: Any)
```

Model shortcut command.

---

## register_dex_model_commands

```python
register_dex_model_commands(app: typer.Typer)
```

Register all dex model commands with the app.

**Parameters**:

- `app`: Typer app to register commands with

---

