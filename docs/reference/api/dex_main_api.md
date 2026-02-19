# dex_main API Reference

> **Source**: `src/thegent/dex_main.py`

Codex-backed interactive agent CLI (dex). Model-only routing (no provider filter).

---

## LazyConsole

### Methods

---

## default_dex

Default: flash (gemini-3-flash) or model from first argument. Model-only, no provider filter.

Usage:
    dex              # Uses flash model (default)
    dex flash        # Uses flash model (via subcommand)
    dex max          # Uses max model (via subcommand or positional)
    dex [model]      # Uses specified model (max, glm, haiku, opus, sonnet, ultra, flash, mini, composer, step)
    dex [model] [prompt]  # Uses model with prompt

```python
default_dex(ctx)
```

---

## dex_bg

Start a background task. Model-first, no provider filter.

```python
dex_bg(model_alias, prompt, cd, mode, timeout, owner)
```

---

## dex_composer

Start Codex with Composer 1.5 (Cursor). Use 'dex max' for minimax-m2.5.

```python
dex_composer(dangerously_bypass, resume, cd, print_mode, debug, add_dir, sandbox, full_auto, search, no_alt_screen, prompt)
```

---

## dex_flash

Gemini 3 Flash via cliproxy. Fast, cheap.

```python
dex_flash(dangerously_bypass, resume, cd, print_mode, debug, add_dir, sandbox, full_auto, search, no_alt_screen, continue_session, prompt)
```

---

## dex_free

GPT-5 mini / Copilot (free tier). Alias for dex mini.

```python
dex_free(dangerously_bypass, resume, cd, print_mode, debug, add_dir, sandbox, full_auto, search, no_alt_screen, continue_session, prompt)
```

---

## dex_glm

GLM-5 model. Balanced across glm, kilo, nim, minimax.

```python
dex_glm(dangerously_bypass, resume, cd, print_mode, debug, add_dir, sandbox, full_auto, search, no_alt_screen, continue_session, prompt)
```

---

## dex_haiku

Claude Haiku. Balanced across CC plan, antigravity, etc.

```python
dex_haiku(dangerously_bypass, resume, cd, print_mode, debug, add_dir, sandbox, full_auto, search, no_alt_screen, continue_session, prompt)
```

---

## dex_history

List execution run history (sync and background).

```python
dex_history(limit, format)
```

---

## dex_inspect

Show status and logs for one or more sessions.

```python
dex_inspect(session_ids, owner, tail, stderr, format, include_contract)
```

---

## dex_logs

Print session logs.

```python
dex_logs(session_id, follow, stderr, tail, timeout)
```

---

## dex_max

M2.5 model. Balanced across nim, kilo, minimax.

```python
dex_max(dangerously_bypass, resume, cd, print_mode, debug, add_dir, sandbox, full_auto, search, no_alt_screen, continue_session, prompt)
```

---

## dex_mini

GPT-5 mini / Copilot (free tier).

```python
dex_mini(dangerously_bypass, resume, cd, print_mode, debug, add_dir, sandbox, full_auto, search, no_alt_screen, continue_session, prompt)
```

---

## dex_opus

Claude Opus. Balanced across CC plan, antigravity, etc.

```python
dex_opus(dangerously_bypass, resume, cd, print_mode, debug, add_dir, sandbox, full_auto, search, no_alt_screen, continue_session, prompt)
```

---

## dex_ps

List registered background sessions.

```python
dex_ps(all_sessions, owner, format, include_contract)
```

---

## dex_run

Run a task. Model-first, no provider filter.

```python
dex_run(model_alias, prompt, cd, mode, timeout)
```

---

## dex_sonnet

Claude Sonnet. Balanced across CC plan, antigravity, etc.

```python
dex_sonnet(dangerously_bypass, resume, cd, print_mode, debug, add_dir, sandbox, full_auto, search, no_alt_screen, continue_session, prompt)
```

---

## dex_status

Show one session status.

```python
dex_status(session_id, format, include_contract)
```

---

## dex_stop

Stop a running session.

```python
dex_stop(session_id, force, wind_down, grace)
```

---

## dex_ultra

Llama Nemotron Ultra. NIM (FREE).

```python
dex_ultra(dangerously_bypass, resume, cd, print_mode, debug, add_dir, sandbox, full_auto, search, no_alt_screen, continue_session, prompt)
```

---

## dex_wait

Wait for session completion and return session exit code.

```python
dex_wait(session_id, timeout)
```

---

## install_links

Install dex shims: dex, dexmax, dexglm, dexhaiku, dexopus, dexsonnet, dexstep (model-only).

```python
install_links(bin_dir, force)
```

---

