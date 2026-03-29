# Zsh Hang & Droid Command Fix

**Symptom:** zsh hangs on start; droid/roid command never starts and can't be terminated.

**Status:** Fix applied to `~/.envrc` (2026-02-18). Guard `[ -f flake.nix ]` prevents use flake in home.

---

## Root Causes

### 1. direnv + ~/.envrc recursion
- `~/.envrc` runs `use flake` when nix is available
- Home dir has no `flake.nix` → nix errors
- direnv hook fires on every prompt → repeated loads → FUNCNEST recursion

### 2. Shell startup chain
- `.zshenv` → `.zsh_bundle.zsh` → optimization → safeguards → advanced
- Optimization runs `_thegent_evalcache direnv hook zsh` at startup
- direnv hook runs on precmd; if ~/.envrc blocks or recurses, shell hangs

### 3. Droid/roid command
- If shell hangs before prompt appears, no command can run
- If roid runs but blocks (e.g. waiting on proxy, MCP, or subprocess), Ctrl+C may not propagate

---

## Emergency Bypass (Get a Working Shell)

### Option A: Disable direnv temporarily
```bash
# In a different terminal (e.g. Terminal.app) or via exec -c
export DIRENV_DISABLE=1
exec zsh
```

### Option B: Use minimal zsh (skip thegent config)
```bash
ZDOTDIR=/tmp zsh
# or
zsh -f  # Skip .zshenv, .zshrc
```

### Option C: Fix ~/.envrc first
```bash
# Edit ~/.envrc - only use flake when flake.nix exists
cat > ~/.envrc << 'EOF'
if has nix_direnv || has nix; then
  [ -f flake.nix ] && use flake
elif [ -d .venv ]; then
  source .venv/bin/activate
  export PYTHONPATH="${PYTHONPATH:+$PYTHONPATH:}$(pwd)/src"
  export PATH="$(pwd)/.venv/bin:${HOME}/.local/bin:${PATH}"
fi
EOF
```

---

## Permanent Fixes

### 1. Fix ~/.envrc (required)
Add guard so `use flake` only runs when `flake.nix` exists:

```bash
# In ~/.envrc
if has nix_direnv || has nix; then
  [ -f flake.nix ] && use flake
else
  [ -d .venv ] && source .venv/bin/activate
  export PYTHONPATH="${PYTHONPATH:+$PYTHONPATH:}$(pwd)/src"
  export PATH="${PATH}:$(pwd)/.venv/bin:${HOME}/.local/bin"
fi
```

### 2. Disable thegent async loading (if still hanging)
Add to `~/.zshrc.local` (create if missing):

```bash
# Disable async loading - prevents background jobs that can block
export THEGENT_ASYNC_LOADING_ENABLED=0
export THEGENT_INSTANT_PROMPT_ENABLED=0
```

### 3. Skip direnv when in home
In `thegent/shell/.zsh_optimization.zsh`, the evalcache runs `direnv hook zsh`. The hook will fire in home and load ~/.envrc. Fix ~/.envrc (step 1) so it doesn't recurse.

### 4. Kill stuck processes
If roid/droid or a subprocess is stuck:

```bash
# Find thegent/roid processes
ps aux | grep -E "thegent|roid|droid"

# Kill by PID
kill -9 <pid>

# Or kill all thegent Python
pkill -9 -f "thegent"
```

---

## Droid/Roid "Can't Be Terminated"

If the command runs but ignores Ctrl+C:

1. **Subprocess not in same process group** – thegent may spawn roid in a way that doesn't forward signals
2. **Blocking I/O** – waiting on proxy, MCP, or network
3. **Try:** `Ctrl+Z` to suspend, then `kill -9 %1` to kill the job

---

## Verification

After applying fixes:

```bash
# 1. Fix ~/.envrc
# 2. Open new terminal or exec zsh
exec zsh

# 3. Should get prompt within 2–3 seconds
# 4. Test roid
roid --help
```

---

## Files to Modify

| File | Change |
|------|--------|
| `~/.envrc` | Guard `use flake` with `[ -f flake.nix ]` |
| `~/.zshrc.local` | Add `THEGENT_ASYNC_LOADING_ENABLED=0` if needed |

---

## Related Docs

- [PATCHES_OPTIMIZATION_INDEX.md](./PATCHES_OPTIMIZATION_INDEX.md) — Single entry point for install targets
- [PATCHES_OPTIMIZATION_AUDIT_AND_PLAN.md](./PATCHES_OPTIMIZATION_AUDIT_AND_PLAN.md) — Full audit
- `thegent/docs/research/DIRENV_FIX_2026-02-18.md`
- `thegent/docs/research/DIRENV_HANG_FORK_GUARD_FIX_2026-02-18.md`

---

## ~/.envrc, Shell, and System Shims Long-Term Fix

**Command:** `thegent install -t all`

**Install targets included in `all`:**
- `envrc` — installs `~/.envrc` with guards (prevents home flake recursion)
- `shell` — installs optimized `.zshenv`, `.zsh_bundle.zsh`, etc. to `~`
- `git-lock-cleanup` — launchd service to remove stale .git/index.lock

**Manual run (recommended for first-time setup):**
```bash
thegent install -t envrc    # Install guarded ~/.envrc
thegent install -t shell    # Install optimized thegent shell config to home
thegent install-shims --system  # (Optional) Install git/tool shims to /usr/local/bin
```

**Template:** `thegent/shell/envrc.home.template` — installed to `~/.envrc` by `thegent install -t envrc`.
**Shell configs:** `thegent/shell/*.zsh` — installed to `~/*.zsh` by `thegent install -t shell`.

**Changes:**
- Guard `[ -f flake.nix ]` before `use flake` — prevents nix error in home (no flake)
- Non-interactive skip — `exit 0` when `! -t 0` to avoid hangs
- `DIRENV_IN_ENVRC` marker — fork guard skips during direnv load
- Venv fallback only when `[ -d .venv ]`
- **Shell targets:** Ensures users get the guarded, optimized versions of all Zsh startup scripts.

**Verification:**
```bash
thegent install -t envrc
thegent install -t shell
direnv reload
exec zsh   # Should get prompt within 2–3s
```
