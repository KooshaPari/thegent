# Wave-1 Rolling Assignment Matrix (2026-02-23)

Owner: this session + resumed child-agent wave
Mode: six-agent ceiling, rolling dispatch when lanes free

## Wave Slots

- lane-a: Task 6 (explicit lane pair assignments) + Task 11 (CPython/PyPy audit sweep)
- lane-b: Task 7 (canonicalize agentapi paths) + Task 10 (OpenRouter auth/header normalization)
- lane-c: Task 8 (provider-bridge contract completion/validation hardening)
- lane-d: Task 9 (thegent CLI orchestration vs agentapi++ ref sweep)
- lane-e: Task 4 (rename reference pass verification + cleanup artifacts)
- lane-f: Task 12 (child-agent artifact capture + merge status)

## Follow-up Pairing (second pass when lanes release)

- lane-a2: Task 1/2 evidence reconciliation + immutable tracker append
- lane-b2: Task 3 (merge preflight) - unblocked branch action
- lane-c2: Task 5 (freeze artifacts) + docs status backfill

## Coordination Rules

1. Each lane updates only scoped artifacts in assignment and does not touch files outside its owner set.
2. All findings must be added to `docs/reference/WAVE1_EXECUTION_TRACKER_2026-02-23.md` immediately.
3. Merge attempt remains preflight-only (`--no-commit --no-ff`) and is only recorded when clean.
