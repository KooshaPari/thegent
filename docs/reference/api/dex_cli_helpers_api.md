# dex_cli_helpers API Reference

> **Source**: `src/thegent/dex_cli_helpers.py`

Shared helpers for dex CLI command assembly and parsing.

---

## add_filtered_interactive_args

```python
add_filtered_interactive_args(cmd: list[str], extra_args: Any, bypass_flag: str)
```

Append interactive args while filtering duplicate/legacy bypass flags and model overrides.

---

## build_codex_exec_command

```python
build_codex_exec_command(codex_path: str, model: str, prompt: str)
```

Build the codex exec command preserving dex flag semantics.

---

## canonical_model

```python
canonical_model(model_alias: str, alias_map: Mapping[(str, str)])
```

Normalize a model alias to its canonical identifier.

---

## extract_dex_command_args

```python
extract_dex_command_args(argv: list[str])
```

Extract arguments after the dex command token from argv.

---

## resolve_codex_cli_path

Find the codex binary using PATH first, then ~/.local/bin fallback.

---

