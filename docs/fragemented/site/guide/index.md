# Guide

This section helps you install, configure, and run `thegent` day-to-day.

## Start Here

- [Getting Started](./getting-started) for a 5-minute first run.
- [Installation](./installation) for bootstrap, pip, and source installs.
- [CLI Reference](./cli-reference) for command syntax and flags.
- [Providers](./providers) for provider/model setup.
- [Architecture](./architecture) for runtime design.
- [Governance](./governance) for policy and quality controls.

## Typical Workflow

```bash
thegent doctor
thegent run "summarize current repo status" free
thegent plan do-next
thegent plan loop
```

Use `thegent ps` to inspect running and completed sessions.
