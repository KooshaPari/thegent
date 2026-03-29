
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

