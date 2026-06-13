# SSOT — Single Source of Truth (thegent)

This document records the canonical authority for cross-cutting facts in the
thegent repository. When a fact conflicts across docs, the source listed
here wins.

## Scope

| Domain | Authoritative source |
| --- | --- |
| Build & test commands | `Taskfile.yml` / `pyproject.toml` scripts |
| Release & versioning | `cliff.toml` + `CHANGELOG.md` (git-cliff generated) |
| Security disclosure process | `SECURITY.md` |
| Dependency updates | `.github/dependabot.yml` |
| Branch & commit policy | `.github/workflows/governance.yml` |
| Repository health score | `.github/workflows/scorecard.yml` (OpenSSF) |
| Editor / formatting baseline | `.editorconfig` |
| Agent operating model | `AGENTS.md` |

## Precedence order

1. Executable config (workflows, `Taskfile.yml`, `pyproject.toml`) — observed behavior.
2. `*.md` governance files in this SSOT table.
3. `AGENTS.md` operating-loop rules.
4. Anything else.

## Updating this file

- Keep the table narrow and unambiguous.
- Cite the canonical file by path; do not duplicate content.
- Update via a `chore(governance):` commit referencing the change.
