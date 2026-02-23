## Local GitHub Actions and Hook Emulation (thegent)

This project keeps CI parity checks split across three lanes:

- **Local hook stages** (`pre-commit`, `pre-push`) for developer feedback.
- **Dockerless GitHub Actions emulation** for lightweight task-mapped CI smoke.
- **`act` emulation** for full workflow replay when Docker is available.

### Run the same guardrails before push (no Docker)

```sh
task ci:local:pre-commit
task ci:local:pre-push
```

These tasks run only changed files by default for fast local feedback.

```sh
THEGENT_PRE_COMMIT_SCOPE=full task ci:local:pre-commit
THEGENT_PRE_COMMIT_SCOPE=full task ci:local:pre-push
```

Use the full-scope mode only when you explicitly need a repo-wide pre-commit baseline.

### Run both hook stages in one command (Dockerless)

```sh
task ci:local-gha:stages
```

### Run dockerless job-mapped CI checks (pre-commit/pre-push)

```sh
task ci:local-gha:pre-commit
task ci:local-gha:pre-push
```

### Run local emulation with `act` (Docker required)

```sh
task ci:local-gha:deps      # install act if missing
task ci:local-gha           # full pull_request event map
task ci:local-gha:push      # full push event map
task ci:local-gha:pre-commit # single pre-commit lane
task ci:local-gha:pre-push   # single pre-push lane
task ci:local-gha:pre-commit:full
task ci:local-gha:pre-push:full
task ci:local-gha:stages:full
```

### Run local job groups

```sh
task ci:local-gha:all
task ci:local-gha:all:push
task ci:local-gha:test
task ci:local-gha:quality
task ci:local-gha:coverage
task ci:local-gha:template-collect
task ci:local-gha:leak-detection
task ci:local-gha:integration
task ci:local-gha:zig-readiness
task ci:local-gha:quality-unified
```

All `ci:local-gha:*:dockerless` variants are intended to run without Docker; they execute mapped local tasks directly.

`task ci:local-gha:stages` and `task ci:local-gha:pre-commit`/`pre-push` are configured to run dockerless by default for local environments that do not use containerized `act`.

For a student/free GH account, prefer the Dockerless hooks/tasks above first to avoid consuming Actions minutes.

### Why remote runs can fail on Student/Free plans

- Public repos: mostly unlimited Actions usage.
- Private repos: limited monthly minutes and throughput by repository plan/capability.

If you see unexpected `queued`/`complete/failure` transitions while no code changed, check **Settings → Actions → Usage/Minutes** for your account-level quota first.
On a constrained plan, repeated workflow traffic can hit the minute/concurrency ceiling before a code issue appears.

### Run all local lanes (no Actions minutes)

- `task ci:local:hooks` → pre-commit + pre-push hook gates only.
- `task ci:local-gha:stages` → dockerless pre-commit then pre-push.
- `task ci:local-gha:pre-commit` → dockerless pre-commit only.
- `task ci:local-gha:pre-push` → dockerless pre-push only.
