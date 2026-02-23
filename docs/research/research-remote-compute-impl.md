# Research — Remote Compute Implementation

**WORK_STREAM ID:** `research-remote-compute-impl`
**Priority:** P2
**Status:** ✅ Research complete

## Purpose

Define how `thegent run --remote` and companion commands should execute via ssh remotes for hybrid compute strategy.

## Research Output

- Execution and schema are already specified in `docs/plans/REMOTE_COMPUTE_IMPLEMENTATION_DETAIL.md` (client/host mapping, command contract, remote session commands).
- Current state: architecture complete, implementation not yet executed.

## Recommended Command Contract

- `thegent run --remote <host> <prompt> [agent]`
- `thegent bg --remote <host> ...`
- `thegent ps/logs/stop/wait --remote <host> ...`

## Decision

- Close research item as complete due to sufficient plan depth.
- Next step should be implementation of host loading + command dispatch + registry validation.

## Links

- `docs/plans/REMOTE_COMPUTE_IMPLEMENTATION_DETAIL.md`
- `docs/research/CONVERSATION_DUMP_2026-02-16.md`
