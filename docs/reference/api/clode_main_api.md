# clode_main API Reference

> **Source**: `src/thegent/clode_main.py`

Claude-backed interactive agent CLI (clode).

HEXAGONAL PHASE 2B: This file is now a thin shim delegating to:
- src/thegent/adapters/harness_base.py — Common harness logic
- src/thegent/adapters/claude_harness.py — Claude-specific implementation
- src/thegent/use_cases/run_harness.py — Use case orchestration

Legacy imports preserved for backward compatibility.

---

## LazyConsole

### Methods

---

## clode_bg

```python
clode_bg(prompt: str, cd: Any, mode: str, timeout: int, owner: Any, model: str)
```

Start a background task via Claude Code using the proxy.

---

## clode_bg_global

```python
clode_bg_global(model_alias: str, prompt: str, cd: Any, mode: str, timeout: int, owner: Any, remote: Any)
```

Start a background task via Claude Code. Model-first, no provider filter.

---

## clode_comp

```python
clode_comp(provider: Any, resume: Any, cd: Any, print_mode: bool, debug: bool, add_dir: list[str], output_format: Any, continue_session: bool, prompt: Any)
```

Composer 1 (via Cursor). Use -x cursor to lock.

---

## clode_composer

```python
clode_composer(provider: Any, resume: Any, cd: Any, print_mode: bool, debug: bool, add_dir: list[str], output_format: Any, continue_session: bool, prompt: Any)
```

Composer 1.5 (via Cursor). Use -x cursor to lock.

---

## clode_config

```python
clode_config(legacy: bool)
```

Open interactive config manager (translation layer for existing config backends).

---

## clode_doctor

```python
clode_doctor(fix: bool, dry_run: bool)
```

Run thegent doctor (harness-equiv).

---

## clode_flash

```python
clode_flash(provider: Any, resume: Any, cd: Any, print_mode: bool, debug: bool, add_dir: list[str], output_format: Any, continue_session: bool, prompt: Any)
```

Gemini 3 Flash via cliproxy. Fast, cheap.

---

## clode_free

```python
clode_free(resume: Any, cd: Any, print_mode: bool, debug: bool, add_dir: list[str], output_format: Any, continue_session: bool, prompt: Any)
```

Base free tier: Copilot gpt-5-mini via cliproxy. Alias for clode mini.

---

## clode_glm

```python
clode_glm(policy: str, prefer: str, force: bool, resume: Any, cd: Any, print_mode: bool, debug: bool, add_dir: list[str], output_format: Any, continue_session: bool, model: Any, prompt: Any)
```

Start an interactive GLM session with policy-based balancing.

---

## clode_haiku

```python
clode_haiku(provider: Any, resume: Any, cd: Any, print_mode: bool, debug: bool, add_dir: list[str], output_format: Any, continue_session: bool, prompt: Any)
```

Claude Haiku 4.5 balanced across claude, antigravity, codex (proxy API), kiro.

---

## clode_high

```python
clode_high(provider: Any, resume: Any, cd: Any, print_mode: bool, debug: bool, add_dir: list[str], output_format: Any, continue_session: bool, prompt: Any)
```

Codex 5.3 high.

---

## clode_history

```python
clode_history(limit: int, format: Any)
```

List execution run history (sync and background).

---

## clode_inspect

```python
clode_inspect(session_ids: list[str], owner: Any, tail: int, stderr: bool, format: Any, include_contract: bool)
```

Show status and logs for one or more sessions.

---

## clode_logs

```python
clode_logs(session_id: str, follow: bool, stderr: bool, tail: int, timeout: int)
```

Print session logs.

---

## clode_max

```python
clode_max(provider: Any, resume: Any, cd: Any, print_mode: bool, debug: bool, add_dir: list[str], output_format: Any, continue_session: bool, force: bool, prompt: Any)
```

MiniMax-M2.5 balanced across minimax and kilo.

---

## clode_mini

```python
clode_mini(resume: Any, cd: Any, print_mode: bool, debug: bool, add_dir: list[str], output_format: Any, continue_session: bool, prompt: Any)
```

GPT-5 mini / Copilot (free tier). Alias for clode free.

---

## clode_opus

```python
clode_opus(provider: Any, resume: Any, cd: Any, print_mode: bool, debug: bool, add_dir: list[str], output_format: Any, continue_session: bool, prompt: Any)
```

Claude Opus 4.6 balanced across claude, antigravity, kiro.

---

## clode_opus1m

```python
clode_opus1m(provider: Any, resume: Any, cd: Any, print_mode: bool, debug: bool, add_dir: list[str], output_format: Any, continue_session: bool, prompt: Any)
```

Claude Opus 4.6 with 1M context. Balanced across claude, antigravity, kiro.

---

## clode_ps

```python
clode_ps(all_sessions: bool, owner: Any, format: Any, include_contract: bool)
```

List registered background sessions.

---

## clode_run

```python
clode_run(prompt: str, cd: Any, mode: str, timeout: int, model: str)
```

Run a task via Claude Code using the proxy (synchronous).

---

## clode_run_global

```python
clode_run_global(model_alias: str, prompt: str, cd: Any, mode: str, timeout: int, remote: Any)
```

Run a task via Claude Code. Model-first, no provider filter.

---

## clode_sonnet

```python
clode_sonnet(provider: Any, resume: Any, cd: Any, print_mode: bool, debug: bool, add_dir: list[str], output_format: Any, continue_session: bool, prompt: Any)
```

Claude Sonnet 4.6 via OpenRouter.

---

## clode_status

```python
clode_status(session_id: str, format: Any, include_contract: bool)
```

Show one session status.

---

## clode_step

```python
clode_step(provider: Any, resume: Any, cd: Any, print_mode: bool, debug: bool, add_dir: list[str], output_format: Any, continue_session: bool, prompt: Any)
```

Step 3.5 Flash via NIM. Fast, cheap.

---

## clode_stop

```python
clode_stop(session_id: str, force: bool, wind_down: bool, grace: int)
```

Stop a running session.

---

## clode_wait

```python
clode_wait(session_id: str, timeout: int)
```

Wait for session completion and return session exit code.

---

## clode_xhigh

```python
clode_xhigh(provider: Any, resume: Any, cd: Any, print_mode: bool, debug: bool, add_dir: list[str], output_format: Any, continue_session: bool, prompt: Any)
```

Codex 5.3 xhigh.

---

## create_provider_app

```python
create_provider_app(provider: str)
```

Create a subcommand group for a provider.

---

## default_clode

```python
default_clode(ctx: typer.Context, native: bool)
```

Start Claude Code with model-first routing. Default: flash (Gemini 3 Flash).

---

## install_links

```python
install_links(bin_dir: Path, force: bool)
```

Install/update clode harness aliases -> thegent-shims under ~/.local/bin.

---

## main

```python
main(ctx: typer.Context)
```

Default to interactive shell if no subcommand is given.

---

## sitback_cmd

```python
sitback_cmd(agent: str, provider: Any, model: Any, dex: bool, cd: Any, skill: Any, profile: str, tmux: bool, no_dashboard: bool, tui: bool)
```

Start a Sitback harness (claude/codex/droid/antigma) with Sitback Agent persona.

**Examples**:

```python
thegent sitback                    # claude harness, flash model
thegent sitback -a codex -M glm    # codex harness with GLM-5
thegent sitback -a droid -M free   # droid harness with gpt-5-mini
thegent sitback -a fanta -M max    # antigma harness with MiniMax-M2.5
thegent sitback -M haiku -P kiro   # claude harness with provider override
thegent sitback --skill thegent-skills
thegent sitback --profile full
thegent sitback --tmux
thegent sitback --no-dashboard
thegent sitback --tui             # Launch TUI compositor
```

---

