# clode_main API Reference

> **Source**: `src/thegent/clode_main.py`

Claude-backed interactive agent CLI (clode).

---

## LazyConsole

### Methods

---

## clode_bg

Start a background task via Claude Code using the proxy.

```python
clode_bg(prompt, cd, mode, timeout, owner, model)
```

---

## clode_bg_global

Start a background task via Claude Code. Model-first, no provider filter.

```python
clode_bg_global(model_alias, prompt, cd, mode, timeout, owner)
```

---

## clode_comp

Composer 1 (via Cursor). Use -x cursor to lock.

```python
clode_comp(provider, resume, cd, print_mode, debug, add_dir, output_format, continue_session, prompt)
```

---

## clode_composer

Composer 1.5 (via Cursor). Use -x cursor to lock.

```python
clode_composer(provider, resume, cd, print_mode, debug, add_dir, output_format, continue_session, prompt)
```

---

## clode_flash

Gemini 3 Flash via cliproxy. Fast, cheap.

```python
clode_flash(provider, resume, cd, print_mode, debug, add_dir, output_format, continue_session, prompt)
```

---

## clode_free

Base free tier: Copilot gpt-5-mini via cliproxy. Alias for clode mini.

```python
clode_free(resume, cd, print_mode, debug, add_dir, output_format, continue_session, prompt)
```

---

## clode_glm

Start an interactive GLM session with policy-based balancing.

```python
clode_glm(policy, prefer, dangerously_skip_permissions, resume, cd, print_mode, debug, add_dir, output_format, continue_session, model, prompt)
```

---

## clode_haiku

Claude Haiku 4.5 balanced across claude, antigravity, codex (proxy API), kiro.

```python
clode_haiku(provider, resume, cd, print_mode, debug, add_dir, output_format, continue_session, prompt)
```

---

## clode_history

List execution run history (sync and background).

```python
clode_history(limit, format)
```

---

## clode_inspect

Show status and logs for one or more sessions.

```python
clode_inspect(session_ids, owner, tail, stderr, format, include_contract)
```

---

## clode_logs

Print session logs.

```python
clode_logs(session_id, follow, stderr, tail, timeout)
```

---

## clode_max

MiniMax-M2.5 balanced across minimax and kilo.

```python
clode_max(provider, resume, cd, print_mode, debug, add_dir, output_format, continue_session, prompt)
```

---

## clode_mini

GPT-5 mini / Copilot (free tier). Alias for clode free.

```python
clode_mini(resume, cd, print_mode, debug, add_dir, output_format, continue_session, prompt)
```

---

## clode_opus

Claude Opus 4.6 balanced across claude, antigravity, kiro.

```python
clode_opus(provider, resume, cd, print_mode, debug, add_dir, output_format, continue_session, prompt)
```

---

## clode_opus1m

Claude Opus 4.6 with 1M context. Balanced across claude, antigravity, kiro.

```python
clode_opus1m(provider, resume, cd, print_mode, debug, add_dir, output_format, continue_session, prompt)
```

---

## clode_ps

List registered background sessions.

```python
clode_ps(all_sessions, owner, format, include_contract)
```

---

## clode_run

Run a task via Claude Code using the proxy (synchronous).

```python
clode_run(prompt, cd, mode, timeout, model)
```

---

## clode_run_global

Run a task via Claude Code. Model-first, no provider filter.

```python
clode_run_global(model_alias, prompt, cd, mode, timeout)
```

---

## clode_sonnet

Claude Sonnet 4.6 via OpenRouter.

```python
clode_sonnet(provider, resume, cd, print_mode, debug, add_dir, output_format, continue_session, prompt)
```

---

## clode_status

Show one session status.

```python
clode_status(session_id, format, include_contract)
```

---

## clode_step

Step 3.5 Flash via NIM. Fast, cheap.

```python
clode_step(provider, resume, cd, print_mode, debug, add_dir, output_format, continue_session, prompt)
```

---

## clode_stop

Stop a running session.

```python
clode_stop(session_id, force, wind_down, grace)
```

---

## clode_wait

Wait for session completion and return session exit code.

```python
clode_wait(session_id, timeout)
```

---

## cost_key

```python
cost_key(b)
```

---

## create_provider_app

Create a subcommand group for a provider.

```python
create_provider_app(provider)
```

---

## default_clode

Start Claude Code with model-first routing. Default: flash (Gemini 3 Flash).

```python
default_clode(ctx)
```

---

## install_links

Install/update clode + claudeglm + claudemax shims under ~/.local/bin.

```python
install_links(bin_dir, force)
```

---

## main

Default to interactive shell if no subcommand is given.

```python
main(ctx)
```

---

## sitback_cmd

Start Claude Code or Codex with Sitback Agent persona (dashboard + terminal list + ps).

Examples:
  thegent sitback                    # minimax, Claude Code
  thegent sitback --dex              # Codex (max model), use when claude not installed
  thegent sitback --dex -M glm       # Codex with GLM-5
  thegent sitback -M haiku           # Claude Code with Haiku
  thegent sitback -a kilo            # sibling via kilo
  thegent sitback --skill agent-orchestra
  thegent sitback --profile full
  thegent sitback --tmux
  thegent sitback --no-dashboard

```python
sitback_cmd(agent, model, dex, cd, skill, profile, tmux, no_dashboard)
```

---

