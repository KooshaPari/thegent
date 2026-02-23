# Domain Playbooks for Delegation

## Global Defaults

1. Every task starts with classifier pass.
2. Every worker has explicit ownership boundaries.
3. Every lane requires independent verification.

## Backend

1. Delegate API/schema changes to backend specialist + test worker.
2. Require unit and integration gates by default.

## Frontend

1. Delegate UI logic and interaction tests separately.
2. Require lint, type-check, and accessibility gates.

## Infra and CI/CD

1. Separate pipeline logic from app logic workers.
2. Require dry-run plus local parity checks before promotion.

## Data and Migrations

1. Isolate migration tasks in dedicated lane or burst worktree.
2. Require backward/forward integrity checks and rollback plan.

## Security

1. Use dedicated security specialist lane.
2. Require threat-model delta and security regression checks.

## QA and Reliability

1. Assign independent verification worker(s).
2. Cover integration, e2e, and reliability probes.

## Docs and Governance

1. Update governance docs in the same change wave as policy changes.
2. Ensure docs reference executable checks and enforcement points.

## Research

1. Split source gathering and synthesis roles.
2. Prefer primary specifications and official documentation.

## Release and Operations

1. Use integration worktree and merge train.
2. Gate on smoke tests, rollback readiness, and change audit completeness.

