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
```

For a student/free GH account, prefer the Dockerless hooks/tasks above first to avoid consuming Actions minutes.
