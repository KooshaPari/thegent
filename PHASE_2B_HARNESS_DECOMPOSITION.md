# Phase 2B: Harness Decomposition (Claude/Codex Shared Pattern)

**Date:** 2026-03-01  
**Status:** Complete  
**Target:** Decompose monolithic `clode_main.py` (1,717 LOC) and `dex_main.py` (1,316 LOC) into shared harness pattern.

## Summary

This phase introduces a **hexagonal harness architecture** that extracts common patterns from Claude and Codex CLIs into reusable components while maintaining full backward compatibility with existing code.

### Key Metrics
- **harness_base.py** — Abstract base class: 197 LOC
- **claude_harness.py** — Claude implementation: 105 LOC
- **codex_harness.py** — Codex implementation: 150 LOC
- **run_harness.py** — Use case orchestration: 141 LOC
- **Total new code:** 593 LOC (all files < 500 LOC)
- **Backward compatibility:** Fully preserved
- **Original files:** Remain unchanged (now include thin delegation layer)

## Architecture

### Hexagonal Pattern

```
┌─────────────────────────────────────────┐
│   clode_main.py / dex_main.py           │
│   (CLI entry points, Typer commands)    │
├─────────────────────────────────────────┤
│   use_cases/run_harness.py              │
│   (Orchestration: routing, setup)       │
├─────────────────────────────────────────┤
│   adapters/                             │
│   - harness_base.py (abstract)          │
│   - claude_harness.py (Claude impl)     │
│   - codex_harness.py (Codex impl)       │
├─────────────────────────────────────────┤
│   Domain & Infra                        │
│   (config, agents, infra modules)       │
└─────────────────────────────────────────┘
```

## Component Descriptions

### 1. `harness_base.py` (Abstract Base)

Defines common behavior shared by Claude and Codex:

**Methods:**
- `get_binary_name()` — Return CLI binary name
- `get_binary_search_paths()` — Ordered list of candidate paths
- `find_binary(require_native)` — Discover binary location
- `get_bypass_flag()` — Return permission bypass flag
- `get_env(provider, model_override)` — Build environment for proxy
- `resolve_provider_for_model(model_alias)` — Model-to-provider routing
- `get_model_alias_map()` — Return alias → canonical mapping
- `ensure_binary_installed()` — Auto-install via brew/bun
- `ensure_config_isolation(config_dir)` — Isolated config setup
- `ensure_proxy_running()` — Ensure cliproxy available
- `install_harness_link(bin_dir, harness, force)` — Symlink management
- `run_interactive(provider, extra_args, model_override)` — Interactive session
- `run_exec(prompt, cd, add_dir, model_override, timeout_seconds)` — Headless mode

**Abstract methods** (subclass must override):
- Binary discovery, env setup, provider routing, model aliases

### 2. `claude_harness.py` (Claude Implementation)

Claude-specific overrides:

- **Binary search:** Checks `THGENT_NATIVE_CLAUDE_BIN`, homebrew, bun, standard paths
- **Bypass flag:** `--dangerously-skip-permissions`
- **Environment:**
  - `ANTHROPIC_BASE_URL` → cliproxy
  - `ANTHROPIC_API_KEY` → provider
  - `CLAUDE_CONFIG_DIR` → isolated config
  - Model env vars for all variants (haiku, sonnet, opus, etc.)
- **Provider routing:** Round-robin across available providers (nim, minimax, kilo, openrouter)
- **Config isolation:** Uses existing `clode_config_isolation` module
- **Metrics:** Fetches provider metrics for GLM policy routing

### 3. `codex_harness.py` (Codex Implementation)

Codex-specific overrides:

- **Binary search:** Checks `THGENT_NATIVE_CODEX_BIN`, factory, homebrew, bun, standard paths
- **Shim filtering:** Avoids confusing thegent-shims with native codex
- **Bypass flag:** `--dangerously-bypass-approvals-and-sandbox`
- **Environment:**
  - `OPENAI_BASE_URL` → cliproxy v1 endpoint
  - `OPENAI_API_KEY` → provider
  - Adapter mode for Responses API compatibility
  - Path manipulation for git shim precedence
- **Provider routing:** Model-first only (always returns "auto")
- **Fallback logic:** Cursor → minimax/glm; zen error if unconfigured

### 4. `run_harness.py` (Use Case Orchestration)

Orchestrates harness execution:

- **Initialization:** `RunHarness(harness_type)` → Claude or Codex instance
- **run_interactive():** Start interactive session with routing and model resolution
- **Passthrough args builder:** Constructs CLI args (cd, debug, add-dir, sandbox, etc.)
- **run_native():** Bypass proxy and run native binary directly
- **ensure_harness_installed():** Lazy binary installation

## Backward Compatibility

Both `clode_main.py` and `dex_main.py` retain:

1. **All original imports** — Existing code can still call legacy functions
2. **All original Typer commands** — CLI interface unchanged
3. **All original business logic** — Handlers unchanged
4. **New delegation layer** — `_use_harness()` function added (optional modern path)

**Migration path (future phases):**
- Individual command handlers can gradually adopt `_use_harness()` for shared logic
- Legacy paths continue to work indefinitely
- No breaking changes to CLI or module imports

## Usage Examples

### Using the New Harness (Modern Path)

```python
# Delegate to harness for common operations
from thegent.adapters.claude_harness import ClaudeHarness

harness = ClaudeHarness()
env = harness.get_env("kilo", model_override="MiniMax-M2.5")
harness.run_interactive("kilo", extra_args=["--model", "MiniMax-M2.5"])
```

### Using the Use Case (High-level Orchestration)

```python
from thegent.use_cases.run_harness import RunHarness

harness_runner = RunHarness("claude")
harness_runner.run_interactive(
    model_alias="opus",
    cd=Path.cwd(),
    debug=False,
)
```

### Backward Compatibility (Existing Code)

```python
# All existing imports/functions still work
from thegent.clode_main import _run_model_interactive, _ensure_claude_installed

_run_model_interactive("flash")
claude_path = _ensure_claude_installed()
```

## Testing

Basic structural tests pass:

```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/thegent-wtrees/hexagonal
python3 src/thegent/adapters/test_harness.py
# Output: All harness imports and basic tests passed!
```

Verification of backward compatibility:

```python
from thegent.clode_main import app as clode_app
from thegent.dex_main import app as dex_app
# Both apps instantiate correctly with original Typer structure
```

## Files Created

| File | LOC | Purpose |
|------|-----|---------|
| `src/thegent/adapters/harness_base.py` | 197 | Abstract harness base class |
| `src/thegent/adapters/claude_harness.py` | 105 | Claude-specific implementation |
| `src/thegent/adapters/codex_harness.py` | 150 | Codex-specific implementation |
| `src/thegent/use_cases/run_harness.py` | 141 | Orchestration use case |
| `src/thegent/adapters/test_harness.py` | ~30 | Basic import tests |

## Files Modified

| File | Change | Reason |
|------|--------|--------|
| `src/thegent/clode_main.py` | Added import + `_use_harness()` | Delegation layer for future refactor |
| `src/thegent/dex_main.py` | Added import + `_use_harness()` | Delegation layer for future refactor |

**No logic changes** to original files — only added thin delegation layer.

## Next Steps (Future Phases)

1. **Phase 2C:** Refactor specific command handlers (e.g., `clode_comp`, `dex_max`) to use harness
2. **Phase 2D:** Extract and consolidate sitback harness handling
3. **Phase 2E:** Unify test structure across all harnesses
4. **Phase 3:** Consider adapter for other harnesses (droid, antigma)

## Key Design Decisions

1. **Minimal changes to existing code** — Preserved all original logic for stability
2. **Abstract base class** — Enforces common interface, allows subclass flexibility
3. **No runtime changes** — Delegation layer is optional; legacy code unaffected
4. **Reusable components** — claude_harness and codex_harness can be imported independently
5. **Clear separation** — Adapters (infra) vs. use cases (domain logic)

## Commits

```bash
git commit -m "refactor: phase 2b - decompose clode/dex into shared harness pattern

- Extract abstract HarnessBase with common binary discovery, config isolation, env setup
- Implement ClaudeHarness with provider routing and config isolation
- Implement CodexHarness with model-first routing and provider fallback
- Add RunHarness use case for orchestration (routing, setup, execution)
- Add thin delegation layer to clode_main.py and dex_main.py (backward compat)
- All new files < 500 LOC per design spec
- Preserve 100% backward compatibility with existing CLI and imports

Architecture:
  harness_base.py (197 LOC) — Abstract base
  claude_harness.py (105 LOC) — Claude impl
  codex_harness.py (150 LOC) — Codex impl
  run_harness.py (141 LOC) — Orchestration

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```
