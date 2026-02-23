# Ln Delegation Architecture

## Objective

Define universal delegation planning for all domains and task types across `L1 -> ... -> Ln`.

## Role Layers

1. `L1` Orchestrator: scope, constraints, global decisions, final integration.
2. `L2` Domain Managers: backend, frontend, infra, data, security, docs, release.
3. `L3` Specialists: protocol, schema, CI, performance, reliability, compliance.
4. `Ln` Workers: execution units with explicit file/domain ownership.

## Universal Delegation Decision Engine

Classify each task by:

1. Domain.
2. Scale (`XS/S/M/L/XL`).
3. Risk (`low/medium/high/critical`).
4. Coupling (`isolated/cross-module/cross-repo`).
5. Runtime profile (`cpu/io/interactive/long-running`).
6. Validation depth (`lint/unit/integration/e2e/security/perf/chaos/accessibility`).

The engine outputs:

1. Required layer (`L2/L3/Ln`) and count.
2. Worktree placement mode.
3. Commit package strategy.
4. Required test and governance gates.

## Delegation Contracts

Every delegated task must include:

1. Goal and acceptance criteria.
2. Allowed and forbidden paths.
3. Required checks/tests.
4. Output contract: patch, evidence, risks, next actions.
5. Timeout and escalation behavior.

## Concurrency and Contention Rules

1. Prefer parallel workers when ownership sets are disjoint.
2. Use file-claim registry before edits.
3. Escalate to burst worktree when overlap-risk exceeds threshold.
4. Preserve both branches/artifacts on conflict.

## Optimization Extensions

1. Cost model: estimated runtime, CI minutes, token spend.
2. Confidence scoring for worker outputs.
3. Auto-rebalance for blocked/late tasks.
4. Independent verification lane separate from implementation lane.
5. Consolidation pass before integration merge.

## Metrics and SLOs

1. Delegation efficiency (`% tasks completed without L1 manual intervention`).
2. Conflict rate (`collisions per 100 tasks`).
3. Rework rate (`superseded pkg rate`).
4. First-pass validation success.
5. Mean time from task start to verified merge.

