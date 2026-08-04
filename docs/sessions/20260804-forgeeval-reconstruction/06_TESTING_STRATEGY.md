# Testing strategy

The initial suite is deterministic and network-free:

- task schema round-trip and bounds validation;
- judge declaration without a credential field;
- result/latency serialisation and throughput calculation;
- temporal and judge-score invariants.
- synthetic catalog provenance and task-family coverage;
- exact-check validation, success/failure result generation, JSONL persistence,
  duplicate run rejection, and malformed persisted-evidence rejection.
- bounded concurrent profiling, stable input ordering, status accounting,
  timeout/error sanitization, empty evidence, and nearest-rank percentile rules.

Future adapter tests must use local fixture processes first. External benchmark
and judge runs require a separate integration marker and fresh result storage.
