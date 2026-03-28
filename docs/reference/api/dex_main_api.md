# dex_main API Reference

> **Source**: `src/thegent/dex_main.py`

Codex-backed interactive agent CLI (dex). Model-only routing (no provider filter).

HEXAGONAL PHASE 2B: This file is now a thin shim delegating to:
- src/thegent/adapters/harness_base.py — Common harness logic
- src/thegent/adapters/codex_harness.py — Codex-specific implementation
- src/thegent/use_cases/run_harness.py — Use case orchestration

Legacy code and imports preserved for backward compatibility.

---

## LazyConsole

### Methods

---

## default_dex

```python
default_dex(ctx: typer.Context, force: bool, native: bool)
```

Default: flash (gemini-3-flash) or model from first argument. Model-only, no provider filter.

Usage:
    dex              # Uses flash model (default)
    dex dex          # Uses codex 5.3 non-spark model (alias)
    dex flash        # Uses flash model (via subcommand)
    dex max          # Uses max model (via subcommand or positional)
    dex [model]      # Uses specified model (dex, high, xhigh, max, glm, haiku, opus, sonnet, ultra, flash, mini, composer, step)
    dex [model] [prompt]  # Uses model with prompt

---

## dex_bg

```python
dex_bg(model_alias: str, prompt: str, cd: Any, mode: str, timeout: int, owner: Any, remote: Any)
```

Start a background task. Model-first, no provider filter.

---

## dex_composer

```python
dex_composer(dangerously_bypass: bool, resume: Any, cd: Any, print_mode: bool, debug: bool, add_dir: list[str], sandbox: Any, full_auto: bool, search: bool, no_alt_screen: bool, prompt: Any)
```

Start Codex with Composer 1.5 (Cursor). Use 'dex max' for minimax-m2.5.

---

## dex_config

```python
dex_config(legacy: bool)
```

Open interactive config manager (translation layer for existing config backends).

---

## dex_doctor

```python
dex_doctor(fix: bool, dry_run: bool)
```

Run thegent doctor (harness-equiv).

---

## dex_flash

```python
dex_flash(dangerously_bypass: bool, resume: Any, cd: Any, print_mode: bool, debug: bool, add_dir: list[str], sandbox: Any, full_auto: bool, search: bool, no_alt_screen: bool, continue_session: bool, prompt: Any)
```

Gemini 3 Flash via cliproxy. Fast, cheap.

---

## dex_fork

```python
dex_fork(args: list[str])
```

Passthrough to native `codex fork` for human-facing session continuation.

---

## dex_free

```python
dex_free(dangerously_bypass: bool, resume: Any, cd: Any, print_mode: bool, debug: bool, add_dir: list[str], sandbox: Any, full_auto: bool, search: bool, no_alt_screen: bool, continue_session: bool, prompt: Any)
```

GPT-5 mini / Copilot (free tier). Alias for dex mini.

---

## dex_glm

```python
dex_glm(dangerously_bypass: bool, resume: Any, cd: Any, print_mode: bool, debug: bool, add_dir: list[str], sandbox: Any, full_auto: bool, search: bool, no_alt_screen: bool, continue_session: bool, prompt: Any)
```

GLM-5 model. Balanced across glm, kilo, nim, minimax.

---

## dex_haiku

```python
dex_haiku(dangerously_bypass: bool, resume: Any, cd: Any, print_mode: bool, debug: bool, add_dir: list[str], sandbox: Any, full_auto: bool, search: bool, no_alt_screen: bool, continue_session: bool, prompt: Any)
```

Claude Haiku. Balanced across CC plan, antigravity, etc.

---

## dex_high

```python
dex_high(dangerously_bypass: bool, resume: Any, cd: Any, print_mode: bool, debug: bool, add_dir: list[str], sandbox: Any, full_auto: bool, search: bool, no_alt_screen: bool, continue_session: bool, prompt: Any)
```

Codex 5.3 high.

---

## dex_history

```python
dex_history(limit: int, format: Any)
```

List execution run history (sync and background).

---

## dex_inspect

```python
dex_inspect(session_ids: list[str], owner: Any, tail: int, stderr: bool, format: Any, include_contract: bool)
```

Show status and logs for one or more sessions.

---

## dex_logs

```python
dex_logs(session_id: str, follow: bool, stderr: bool, tail: int, timeout: int)
```

Print session logs.

---

## dex_max

```python
dex_max(dangerously_bypass: bool, resume: Any, cd: Any, print_mode: bool, debug: bool, add_dir: list[str], sandbox: Any, full_auto: bool, search: bool, no_alt_screen: bool, continue_session: bool, prompt: Any)
```

M2.5 model. Balanced across nim, kilo, minimax.

---

## dex_mini

```python
dex_mini(dangerously_bypass: bool, resume: Any, cd: Any, print_mode: bool, debug: bool, add_dir: list[str], sandbox: Any, full_auto: bool, search: bool, no_alt_screen: bool, continue_session: bool, prompt: Any)
```

GPT-5 mini / Copilot (free tier).

---

## dex_opus

```python
dex_opus(dangerously_bypass: bool, resume: Any, cd: Any, print_mode: bool, debug: bool, add_dir: list[str], sandbox: Any, full_auto: bool, search: bool, no_alt_screen: bool, continue_session: bool, prompt: Any)
```

Claude Opus. Balanced across CC plan, antigravity, etc.

---

## dex_ps

```python
dex_ps(all_sessions: bool, owner: Any, format: Any, include_contract: bool)
```

List registered background sessions.

---

## dex_resume

```python
dex_resume(args: list[str])
```

Passthrough to native `codex resume` for human-facing session continuation.

---

## dex_run

```python
dex_run(model_alias: str, prompt: str, cd: Any, mode: str, timeout: int, remote: Any)
```

Run a task. Model-first, no provider filter.

---

## dex_sonnet

```python
dex_sonnet(dangerously_bypass: bool, resume: Any, cd: Any, print_mode: bool, debug: bool, add_dir: list[str], sandbox: Any, full_auto: bool, search: bool, no_alt_screen: bool, continue_session: bool, prompt: Any)
```

Claude Sonnet. Balanced across CC plan, antigravity, etc.

---

## dex_status

```python
dex_status(session_id: str, format: Any, include_contract: bool)
```

Show one session status.

---

## dex_stop

```python
dex_stop(session_id: str, force: bool, wind_down: bool, grace: int)
```

Stop a running session.

---

## dex_ultra

```python
dex_ultra(dangerously_bypass: bool, resume: Any, cd: Any, print_mode: bool, debug: bool, add_dir: list[str], sandbox: Any, full_auto: bool, search: bool, no_alt_screen: bool, continue_session: bool, prompt: Any)
```

Llama Nemotron Ultra. NIM (FREE).

---

## dex_wait

```python
dex_wait(session_id: str, timeout: int)
```

Wait for session completion and return session exit code.

---

## dex_xhigh

```python
dex_xhigh(dangerously_bypass: bool, resume: Any, cd: Any, print_mode: bool, debug: bool, add_dir: list[str], sandbox: Any, full_auto: bool, search: bool, no_alt_screen: bool, continue_session: bool, prompt: Any)
```

Codex 5.3 xhigh.

---

## install_links

```python
install_links(bin_dir: Path, force: bool)
```

Install/update dex -> thegent-shims harness shim under ~/.local/bin.

---

