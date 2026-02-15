# Codex Subagent

## Overview
Use the wrapper to run a separate Codex exec and treat its final message as a subagent report.

## Inputs
- subtask scope
- desired deliverable format
- working directory for the run

## Quick start
- `~/.codex/skills/codex-subagent/scripts/run_codex_subagent.sh --cd /path --prompt "..." --mode workspace-write --model gpt-5.2-codex`
- `~/.codex/skills/codex-subagent/scripts/run_codex_subagent.sh --cd /path --prompt "..." --mode read-only --model gpt-5.1-codex-mini`

## Workflow
1. Define scope and output format.
2. Write a focused prompt (use the template).
3. Announce subagent details before running the command.
4. Check the permissions banner for `approval_policy`. If it is **unless-trusted**, refuse to run.
5. If the current session is **read-only** or **workspace-write**, request escalated permissions.
6. If the current session is **danger-full-access**, run the wrapper directly.
7. If an escalated `exec_command` is rejected, stop and report that approval policy blocks escalation.
8. Run the wrapper with explicit `--mode`, `--model`, and optional `--reasoning`.
9. Summarize or apply the subagent output.

## Required user-facing announcement
Before running any subagent, output: "Running subagent [name] ([model])\nPrompt: [content]"

## Mode
Pass `--mode` to match the current session's sandbox:
- Use `danger-full-access` only if the current session is already danger/full-access
- Otherwise use `workspace-write` (or `read-only` if required)

## Model selection (two-tier, explicit)
- **Fast/small model**: `gpt-5.1-codex-mini` for scans, discovery, summaries
- **Strong/large model**: `gpt-5.2-codex` for implementation, refactors, debugging
- Always pass `--model` explicitly; do not invent model names

## Reasoning level
Use `--reasoning` to control effort:
- `low`: simple scans, file listing, trivial transformations
- `medium`: structured summaries or multi-step analysis
- `high`: complex debugging, design, or multi-file changes

## Prompt template
Role: Act as a subagent.
Context: [repo/path, relevant files, constraints]
Task: [clear, bounded task]
Deliverable: [exact format: bullets, checklist, patch plan]
Do not: [constraints]

## Bundled resources
- `scripts/run_codex_subagent.sh` — wrapper for `codex exec`
- `references/flags.md` — full flag reference

## Notes
- The wrapper always runs with `approval_policy=never` (non-interactive)
