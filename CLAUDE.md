
# Project Instructions

**This project is managed through AgilePlus.**

## AgilePlus Mandate

All work MUST be tracked in AgilePlus:
- Reference: /Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus
- CLI: cd /Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus && agileplus <command>

## Work Requirements

1. Check for AgilePlus spec before implementing
2. Create spec for new work: agileplus specify --title "<feature>" --description "<desc>"
3. Update work package status: agileplus status <feature-id> --wp <wp-id> --state <state>
4. No code without corresponding AgilePlus spec

## Branch Discipline

- Feature branches in repos/worktrees/<project>/<category>/<branch>
- Canonical repository tracks main only
- Return to main for merge/integration checkpoints

## Disk Budget & Multi-Session (Phenotype repos)

- Pre-dispatch check: `df -h /System/Volumes/Data | tail -1`. Abort dispatch if <10Gi free; purge before retry.
- Multi-agent cargo builds: stacking >4 concurrent pre-push workspace-verify runs blows disk. Dispatch serially when possible.
- Long pushes (≥3 min): use `nohup git push ... & disown` to survive session kills. Verify via `git ls-remote`.
- Multi-session coordination: `repos/.argis-helios-bus/` for Argis↔Helios. Do not write to `FocalPoint/target` (Helios workspace).
- APFS `~/.Trash` does NOT reclaim space until emptied — use `rm -rf` on orphaned worktree targets.
- Full playbooks: `repos/docs/governance/{disk_budget_policy,multi_session_coordination,long_push_pattern,enospc_playbook}.md`.

## Local quality (Task)

From this repository root:

- `task quality` — Tach boundaries, Vale on invariant Markdown, Ruff (`src/` + `tests/`), phenotype CLIProxy model-check unit tests.
- `task quality:full` — same plus `ruff format --check`.
- `task vale:install` — install Vale via Homebrew when missing (macOS).

## UTF-8 Encoding

All markdown files must use UTF-8. Validate with:
```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus
agileplus validate-encoding --all --fix
```

## AgilePlus Reference

- Specs: AgilePlus/kitty-specs/<feature-id>/
- Docs: AgilePlus/docs/
- Workflows: AgilePlus/docs/workflow/
- Worklog: AgilePlus/.work-audit/worklog.md

## Worklogs (All Projects)

All agents MUST write worklogs for research, decisions, and significant findings:

- **Location:** `/Users/kooshapari/CodeProjects/Phenotype/repos/worklogs/`
- **Index:** `worklogs/README.md`
- **Aggregation:** `./worklogs/aggregate.sh [project|priority|category|all]`
- **Onboarding:** `worklogs/AGENT_ONBOARDING.md`

### Worklog Categories

| Category | File | Purpose |
|----------|------|---------|
| ARCHITECTURE | `worklogs/ARCHITECTURE.md` | ADRs, library extraction |
| DUPLICATION | `worklogs/DUPLICATION.md` | Cross-project duplication |
| DEPENDENCIES | `worklogs/DEPENDENCIES.md` | External deps, forks, modernization |
| INTEGRATION | `worklogs/INTEGRATION.md` | External integrations |
| PERFORMANCE | `worklogs/PERFORMANCE.md` | Optimization, benchmarking |
| RESEARCH | `worklogs/RESEARCH.md` | Starred repo analysis |
| GOVERNANCE | `worklogs/GOVERNANCE.md` | Policy, evidence, quality gates |

### When to Write Worklogs

Write for: research completions, decisions made, issues found (duplication, performance), work completions, or planning (fork candidates, migration plans).

### Project Tags

- `[AgilePlus]` - AgilePlus Rust monorepo
- `[thegent]` - TheGent dotfiles manager
- `[heliosCLI]` - HeliosCLI framework
- `[cross-repo]` - Cross-repo work

## Scripting Language Hierarchy

**Canonical policy:** `/Users/kooshapari/CodeProjects/Phenotype/repos/docs/governance/scripting_policy.md`

Applies to **every** script, tool, or pipeline component across Phenotype-org repositories.

1. **Rust** — default. Toolbelt: `clap` + `anyhow` + `serde` + `tokio` + `walkdir`.
2. **Zig, Mojo, Go** — acceptable alternates with a one-line top-of-file justification (e.g., "Go for an ffmpeg CLI driver because `os/exec` + `filepath.Walk` is tighter than Rust here").
3. **Python, TypeScript** — second-layer fallback, only when the runtime must live inside an existing Python/TS process (Streamlit page, Playwright spec, Jupyter notebook, VitePress config). **Not** for standalone CLI tools.
4. **Bash / sh / zsh / fish / PowerShell** — only for ≤5-line platform glue where a real-language replacement is a net loss (e.g., a wrapper that sources the user's shell rc before `exec`ing a Rust binary). Every surviving shell script **must** carry a top-of-file comment justifying why Rust/Go/etc. are worse for this specific case.

**Legacy call-out:** previous patterns in hwLedger, AgilePlus, thegent, and phenotype-infrakit accumulated dozens of `.sh` scripts for CI, sync, codegen, and hooks. **New work must not add shell; existing shell must be migrated when touched.** See the canonical doc for migration guidance and the PR review rubric.

## Design System (Impeccable)

Impeccable is installed globally. Design skills and commands are available:
- Skills: `frontend-design`, `audit`, `critique`, `polish`, `normalize`, `animate`, `arrange`, `typeset`, `colorize`, `bolder`, `quieter`, `distill`, `extract`, `harden`, `optimize`, `overdrive`, `delight`, `onboard`, `adapt`, `clarify`
- Run `/teach-impeccable` in any project to establish persistent design context
- Global design context for Phenotype ecosystem: `/Users/kooshapari/CodeProjects/Phenotype/repos/.impeccable.md`
- CSS baseline (impeccable reset): add to all VitePress `custom.css` and app `globals.css`

```css
/* impeccable CSS baseline — github.com/pbakaus/impeccable */
*, *::before, *::after { box-sizing: border-box; }
html { -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; text-rendering: optimizeLegibility; }
img, video { max-width: 100%; height: auto; }
input, button, textarea, select { font: inherit; }
p, h1, h2, h3, h4, h5, h6 { overflow-wrap: break-word; }
```

