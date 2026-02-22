# WL-110 Implementation Plan (Stable Resume API)

## Goal
Make `thegent resume` a stable, documented session-resume interface with optional follow-up prompt and predictable state file behavior.

## Current Block
Current `resume_cmd` only marks registry state as resumed; it does not perform run continuation or persist a stable `state.json` contract per session.

## Ready-to-Implement Steps
1. Extend CLI command signature in `src/thegent/cli/commands/cli.py`:
- `resume_cmd(session_id: str | None = None, prompt: str | None = None)`
2. Add `resume_impl` in `src/thegent/cli/commands/impl.py`:
- resolve latest session when `session_id` omitted
- load session state from `~/.thegent/sessions/<id>/state.json`
- run continuation path using existing continuation prompt helpers.
3. Persist stable state file during run/bg creation:
- write `state.json` with `session_id`, `run_id`, `agent`, `model`, `cwd`, timestamps.
4. Add `session list` parity checks:
- ensure sessions shown can be resumed by returned IDs.

## Acceptance Criteria
- `thegent resume` without args resumes most recent resumable session.
- `thegent resume <id> --prompt "..."` appends prompt on resumed context.
- Session state contract is documented and consistently written.

## Validation Commands
- `python -m py_compile src/thegent/cli/commands/cli.py src/thegent/cli/commands/impl.py`
- `pytest -q tests/test_wl110_resume_contract.py`
