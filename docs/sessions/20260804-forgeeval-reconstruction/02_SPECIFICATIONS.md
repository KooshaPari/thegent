# Specifications

## Contract versions

| Contract | Version | Responsibility |
| --- | --- | --- |
| Task | `forgeeval.task.v1` | Identifies a reproducible task and safety limits. |
| Judge | `forgeeval.judge.v1` | Names an optional judge without credentials. |
| Latency | `forgeeval.latency.v1` | Captures wall time, TTFT, ITL, tokens, concurrency. |
| Result | `forgeeval.result.v1` | Links one task execution to optional judge output. |

## Invariants

- Task and run IDs are stable lowercase identifiers.
- Timeout, durations, token counts, and concurrency are non-negative or bounded.
- Completion cannot precede start.
- A judge score cannot exist without a judge specification.
- Secrets, raw prompts containing credentials, and model calls are out of scope.
