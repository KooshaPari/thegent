# Project Instructions

**This project is managed through AgilePlus.**

## AgilePlus Mandate

All work MUST be tracked in AgilePlus:
- Reference: `/Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus`
- CLI: `cd /Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus && agileplus <command>`

## Work Requirements

1. **Check for AgilePlus spec before implementing**
2. **Create spec for new work**: `agileplus specify --title "<feature>" --description "<desc>"`
3. **Update work package status**: `agileplus status <feature-id> --wp <wp-id> --state <state>`
4. **No code without corresponding AgilePlus spec**

## Branch Discipline

- Feature branches in `repos/worktrees/<project>/<category>/<branch>`
- Canonical repository tracks `main` only
- Return to `main` for merge/integration checkpoints

## Global governance (read with `~/.claude/AGENTS.md`)

This file is short on purpose. **Full cross-project rules** live in:

- `~/.claude/AGENTS.md` — global agent contract (delegation, QA, git, billing exceptions)
- `/Users/kooshapari/CodeProjects/CLAUDE.md` — CodeProjects root (worktrees, reuse, **GitHub Actions billing**, local git alignment)
- `/Users/kooshapari/CodeProjects/AGENTS.md` — CodeProjects agent safety and delivery policy

Agents must treat those paths as **governance**, not optional context.

---

