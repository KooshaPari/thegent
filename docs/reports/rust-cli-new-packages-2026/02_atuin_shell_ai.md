# Rust CLI 2026: Shell History and Shell AI Tooling

## Scope

This report focuses on `libs.tech` Rust CLI list entries introduced in the 2026 cycle that are directly relevant to terminal productivity with a shell-history or AI-assisted coding workflow emphasis.

Primary source:
- [libs.tech Rust CLI Libraries 2026](https://libs.tech/rust/cli-libraries)

## Candidate set (adjacent context)

- `atuinsh/atuin`
- `nukesor/pueue`
- `bodo-run/yek`

These are positioned near each other in the Rust CLI list and represent the strongest fit for shell-history, command orchestration, and AI preparation workflows.

## Evaluation

### 1) `atuinsh/atuin`

- Source links:
  - [libs.tech project page](https://libs.tech/project/301244405/atuin)
  - [GitHub](https://github.com/atuinsh/atuin)
  - [Atuin docs (Install)](https://docs.atuin.sh/)

- **Value**
  - Replaces local shell history with a SQLite-backed history store that records richer command context (status, cwd, duration, host/session), and supports search across sessions/machines.
  - Optional encrypted sync supports both self-hosted and managed modes.
  - Strong developer experience signals: high adoption and frequent maintenance activity on the recent 2026 list.

- **Risks**
  - Relatively high issue volume at the time of listing, so there is non-trivial triage and edge-case risk.
  - Shell hook integration adds operational complexity (especially in nonstandard shells), and shell compatibility must be verified before broad rollout.
  - Any command-history synchronization introduces additional security/compliance review requirements.

- **Recommended adoption criteria**
  - Pilot with a single team segment and compare command-recall latency plus sync reliability versus existing shell-history tooling.
  - Validate shell hooks on all supported shells and terminals before organization-wide enablement.
  - Confirm retention/encryption model for command metadata aligns with team policy; define local purge and self-hosting posture.
  - Require rollback path (disable sync and clear local config) in rollout plan.

### 2) `nukesor/pueue`

- Source links:
  - [libs.tech project page](https://libs.tech/project/41925963/pueue)
  - [GitHub](https://github.com/nukesor/pueue)

- **Value**
  - CLI-native queue for shell command execution, including pause/resume, concurrency limits, task groups, and persistence across disconnections.
  - Useful when teams need command orchestration from the terminal without introducing a full scheduler stack.
  - Works across platforms and keeps logs/discrete task state for recovery.

- **Risks**
  - Project states it is feature-complete with only minor updates, reducing velocity for new capabilities.
  - Not intended as scriptable enterprise scheduler replacement; some use cases may outgrow its scope.
  - Command execution passes through shell layer; escaping and environment behavior must be handled consistently.

- **Recommended adoption criteria**
  - Introduce for long-running/interactive command workflows where lightweight queue semantics are enough.
  - Confirm behavior for shell escaping, daemon lifecycle, and crash recovery in representative environments.
  - Set hard governance around task naming, queue policies, and logging retention before deployment.

### 3) `bodo-run/yek`

- Source links:
  - [libs.tech project page](https://libs.tech/project/915358848/yek)
  - [GitHub](https://github.com/mohsen1/yek)

- **Value**
  - CLI utility that serializes repo files for LLM consumption using .gitignore/git-history-aware heuristics and context-sized output controls.
  - Useful bridge for shell-based AI workflows (prompting and context prep) with strong defaults for terminal usage.

- **Risks**
  - Smaller ecosystem footprint than larger CLI staples; maintenance cadence and dependency changes should be monitored.
  - Can surface sensitive file content if ignore rules are not curated.
  - Pipe/stream behavior and token cap decisions can silently drop low-priority files, which affects reproducibility if not documented.

- **Recommended adoption criteria**
  - Require explicit allow/deny profile templates before any team-wide use; lock a repo-specific ignore policy.
  - Run controlled evaluation on representative monorepos to confirm output determinism and chunking behavior.
  - Add audit checkpoints in AI workflows to prevent accidental inclusion of secrets or credentials.

## Recommended sequence

1. Start with `pueue` for command orchestration and `atuin` for history recall in a controlled pilot.
2. After shell adoption stabilizes, evaluate `yek` in a strict AI-prompt prep workflow.
3. Expand by adding guardrails first: shell compatibility matrix, security review, and a documented rollback plan for each package.
