# ForgeEval clean-room reconstruction

## Goal

Establish a versioned, offline-safe foundation for evaluating Forgecode against
Terminal-Bench 2+, DeepSWE, custom long-horizon tasks, optional Ling 2.6 Flash
judging, and scaled latency profiling.

## Scope boundary

The historical Forge conversation is provenance only. Its transcript is not
copied, parsed, or treated as current benchmark evidence. Credentials remain
outside repository files and schemas.

## Acceptance criteria

- Versioned task, judge, latency, and result contracts exist.
- Contract validation is deterministic and test-covered offline.
- No external model or benchmark invocation occurs.
