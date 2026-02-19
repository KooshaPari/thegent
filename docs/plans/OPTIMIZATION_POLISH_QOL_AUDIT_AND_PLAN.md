# Optimization, Polish, QOL & Maximal Engineering — Audit & Plan

**Date:** 2026-02-19  
**Scope:** ADX/AX/UX improvements, intuitive design, practical features, engineering excellence  
**Status:** Audit complete, plan ready

---

## Executive Summary

This audit identifies gaps and opportunities to make thegent feel like a **quality-first, popular third-party tool** — installable, discoverable, and delightful to use. Focus: first-run success, discoverability, error recovery, and polish.

---

## 1. Critical UX Gaps (Fix First)

### 1.1 `thegent doctor` Not in Main CLI

**Issue:** Docs say "run `thegent doctor`" but the main app has no top-level `doctor` command. It exists only in `clode doctor`, `dex doctor`, `roid doctor`, `thegent shell doctor`.

**Impact:** New users following INSTALLATION.md get "Unknown command" or similar.

**Fix:** Add `app.command("doctor")(doctor_cmd)` to `main.py`:

```python
@app.command("doctor")
def doctor_cmd(fix: bool = typer.Option(False, "--fix", help="Attempt to fix detected issues")) -> None:
    """Verify environment health and fix performance bottlenecks."""
    from thegent.doctor import run_doctor
    success = run_doctor(fix=fix)
    raise typer.Exit(0 if success else 1)
```

**Priority:** P0

---

### 1.2 Bootstrap Script Error Handling

**Issue:** Bootstrap uses `2>/dev/null || true` for install/setup steps — failures are silently ignored. User may think setup succeeded when it didn't.

**Fix:**
- Remove `2>/dev/null` or make it conditional on `THGENT_BOOTSTRAP_QUIET=1`
- On failure: print clear message + suggested fix (e.g. "Run `thegent doctor` to diagnose")
- Exit 1 if critical step fails

**Priority:** P0

---

### 1.3 Shell Completion

**Issue:** No `thegent --generate-completion` or similar. Typer supports it; thegent may not expose it.

**Fix:** Ensure `thegent --install-completion zsh` (or bash/fish) works. Typer has `--install-completion` / `--show-completion`. Add to INSTALLATION.md.

**Priority:** P1

---

## 2. Discoverability & Onboarding

### 2.1 First-Run Experience

| Gap | Fix |
|-----|-----|
| No post-install hint | After `pip install thegent`, print: "Run `thegent setup` to configure. Run `thegent doctor` to verify." (via post-install script or README) |
| `thegent` with no args | `no_args_is_help=True` — good. Consider adding a "quick start" hint in the help footer |
| Version visibility | Add `thegent --version` (Typer default). Ensure it's prominent |

**Priority:** P1

---

### 2.2 README vs INSTALLATION Alignment

**Issue:** README says `brew bundle` and `thegent setup --build-extensions`; INSTALLATION says bootstrap one-liner. Inconsistent entry points.

**Fix:** Unify "Quick Start" in README to match INSTALLATION one-command flow. Add "For developers" section for build-extensions.

**Priority:** P2

---

### 2.3 `thegent help` / Subcommand Discovery

**Issue:** 100+ commands; new users may not find `run`, `plan`, `doctor`, `setup`.

**Fix:**
- Add `thegent` (no args) to print a "Getting started" panel: `run`, `plan do-next`, `doctor`, `setup`
- Consider `thegent quickstart` that runs setup + doctor + prints next steps

**Priority:** P2

---

## 3. Error Handling & Recovery

### 3.1 Actionable Error Messages

**Issue:** Generic Python tracebacks or "Error: ..." without next steps.

**Fix:**
- Wrap common failures (provider not configured, MCP not reachable, PATH missing) with `fix_hint` or `suggestion`
- Doctor already has `fix_hint` — ensure it's surfaced in CLI errors

**Priority:** P1

---

### 3.2 `doctor --fix` Completeness

**Issue:** Scratchpad says "Implement proactive `doctor --fix` for detected issues" — partial implementation.

**Fix:** Audit `_apply_fixes()` in doctor.py; ensure all checks with `fix_hint` have corresponding fix logic. Document which issues are auto-fixable.

**Priority:** P2

---

### 3.3 Graceful Degradation

**Issue:** If rg/fd/jaq missing, some commands may fail hard.

**Fix:** Shims already have fallbacks. Ensure doctor reports "optional tools (rg, fd, jaq) missing — install for 10x speedup" as warn, not fail.

**Priority:** P2

---

## 4. Performance & Startup

### 4.1 CLI Startup Time

**Issue:** Large CLI with many subcommands; lazy imports help but first `thegent` run can be slow.

**Fix:**
- Profile `thegent --help` and `thegent run --help` startup
- Defer heavy imports (litellm, playwright, etc.) until needed
- Consider `thegent run` as a separate entry point for hot path

**Priority:** P2

---

### 4.2 thegent-shims (Rust) Consolidation

**Issue:** Scratchpad: "Ship thegent-shims (Rust) for git/grep/find/agent" — Phase 2 FULL_SHELL_TO_RUST. Bash shims add ~20–50ms/call.

**Fix:** Track in WORK_STREAM; not blocking for "quality first" but improves perceived speed.

**Priority:** P3

---

## 5. Documentation & DX

### 5.1 Single-Page Quick Reference

**Issue:** THGENT_CLI_REFERENCE is comprehensive but long. New users need a one-pager.

**Fix:** Add `docs/guides/QUICK_REFERENCE.md` — top 15 commands with one-line examples.

**Priority:** P2

---

### 5.2 In-CLI Help Quality

**Issue:** Some options have terse help; examples in `--help` improve discoverability.

**Fix:** Add `epilog` or `rich_help_panel` for key commands (run, plan, setup) with 2–3 example invocations.

**Priority:** P2

---

### 5.3 Troubleshooting Flow

**Issue:** TROUBLESHOOTING.md exists but isn't linked from error messages.

**Fix:** When doctor finds issues, print: "See docs/guides/TROUBLESHOOTING.md" or a short URL.

**Priority:** P3

---

## 6. Nix & Packaging

### 6.1 Nix Package Build

**Issue:** Build fails when `nix/` not tracked by Git. Some deps (granian, fastmcp) may be missing from nixpkgs.

**Fix:**
- Document `git add nix/` in nix/README.md (done)
- Consider `mach-nix` or `poetry2nix` for full dep resolution; or maintain overlay for missing packages

**Priority:** P2

---

### 6.2 Version from Git Tag

**Issue:** pyproject has `version = "0.1.0"` hardcoded.

**Fix:** Use `dynamic = ["version"]` with `hatch-vcs` or similar for `0.1.0+git.abcd123`.

**Priority:** P3

---

## 7. Optional Enhancements

### 7.1 Upgrade Check

**Issue:** No "A new version is available" prompt.

**Fix:** Optional `thegent upgrade` or check on first run of the day (with `--no-check-updates` to disable).

**Priority:** P3

---

### 7.2 Config Wizard

**Issue:** `thegent setup` has wizard for providers; could be more guided for first-time users.

**Fix:** Add `thegent setup --wizard` (or make default) that asks: "Which agents do you use? (Cursor, Claude Code, Codex)" and configures only those.

**Priority:** P3

---

### 7.3 Project Detection

**Issue:** `thegent` in a project dir could auto-detect `.cursor`, `AGENTS.md`, etc. and suggest `setup --hooks` or `setup --skills`.

**Fix:** `thegent status` or `thegent doctor` could print: "Project has .git. Run `thegent setup --hooks` for git hooks."

**Priority:** P3

---

## 8. Implementation Priority Matrix

| ID | Item | Priority | Effort | Impact |
|----|------|----------|--------|--------|
| 1 | Add `thegent doctor` to main CLI | P0 | S | H |
| 2 | Bootstrap error handling (no silent fail) | P0 | S | H |
| 3 | Shell completion (--install-completion) | P1 | S | M |
| 4 | First-run hint (post-install) | P1 | S | M |
| 5 | Actionable error messages | P1 | M | H |
| 6 | doctor --fix completeness | P2 | M | M |
| 7 | README/INSTALLATION alignment | P2 | S | M |
| 8 | thegent (no args) quick start panel | P2 | S | M |
| 9 | QUICK_REFERENCE.md | P2 | S | M |
| 10 | In-CLI help examples (epilog) | P2 | S | M |
| 11 | Nix package deps (overlay/mach-nix) | P2 | M | M |
| 12 | Graceful degradation (optional tools) | P2 | S | M |
| 13 | CLI startup profiling | P2 | M | M |
| 14 | Upgrade check | P3 | M | L |
| 15 | Config wizard improvements | P3 | M | L |
| 16 | Project detection hints | P3 | S | L |

---

## 9. Suggested Implementation Order

**Phase 1 (1–2 days):** Critical UX
- Add `thegent doctor` to main
- Bootstrap: fail loudly, suggest doctor on error

**Phase 2 (2–3 days):** Discoverability
- Shell completion
- First-run hint
- README/INSTALLATION alignment
- Quick start panel for `thegent` (no args)

**Phase 3 (2–3 days):** Error recovery
- Actionable errors
- doctor --fix audit
- QUICK_REFERENCE.md
- In-CLI help examples

**Phase 4 (ongoing):** Polish
- Nix deps, startup profiling, upgrade check, project hints

---

## 10. Success Criteria

1. **First-run:** `curl \| sh` → `thegent doctor` passes (or gives clear fix)
2. **Discoverability:** `thegent` with no args shows "Getting started" in &lt;2s
3. **Recovery:** Any error includes a "Try: ..." or "See: ..." hint
4. **Completeness:** `thegent doctor --fix` resolves &gt;80% of common issues

---

## See Also

- [INSTALL_SETUP_AND_NIX_COMPREHENSIVE_PLAN.md](../../../docs/INSTALL_SETUP_AND_NIX_COMPREHENSIVE_PLAN.md)
- [PRODUCTION_PACKAGING_POLISH_OPTIMIZATION_AUDIT_AND_PLAN.md](../research/PRODUCTION_PACKAGING_POLISH_OPTIMIZATION_AUDIT_AND_PLAN.md)
- [session_review.md](../scratchpad/session_review.md)
