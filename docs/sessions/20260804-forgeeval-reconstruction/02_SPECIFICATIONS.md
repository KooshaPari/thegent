# Specifications

## Contract versions

| Contract | Version | Responsibility |
| --- | --- | --- |
| Task | `forgeeval.task.v1` | Identifies a reproducible task and safety limits. |
| Judge | `forgeeval.judge.v1` | Names an optional judge without credentials. |
| Latency | `forgeeval.latency.v1` | Captures wall time, TTFT, ITL, tokens, concurrency. |
| Result | `forgeeval.result.v1` | Links one task execution to optional judge output. |
| Catalog | `forgeeval.catalog.v1` | Declares local synthetic fixtures and their provenance. |
| Fixture | `forgeeval.fixture.v1` | Requires an exact set of deterministic local checks. |
| Offline request | `forgeeval.offline-run-request.v1` | Carries one validated observation packet. |
| Profile | `forgeeval.profile.v1` | Records bounded, monotonic concurrent adapter execution. |

## Invariants

- Task and run IDs are stable lowercase identifiers.
- Timeout, durations, token counts, and concurrency are non-negative or bounded.
- Completion cannot precede start.
- A judge score cannot exist without a judge specification.
- Secrets, raw prompts containing credentials, and model calls are out of scope.
- Bundled fixtures are synthetic and CC0-1.0; they do not claim to be copied
  Terminal-Bench or DeepSWE tasks.
- The offline runner accepts only exact local check identifiers and emits no
  judge score, provider request, or inferred benchmark conclusion.
- The profiler accepts an injected async adapter but performs no network/model
  call itself. It bounds active tasks, preserves input order, records only
  task IDs/status/error class/monotonic duration, and uses nearest-rank p50,
  p90, and p99 summaries. Exception messages are deliberately excluded.
