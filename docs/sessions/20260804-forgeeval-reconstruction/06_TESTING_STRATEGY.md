# Testing strategy

The initial suite is deterministic and network-free:

- task schema round-trip and bounds validation;
- judge declaration without a credential field;
- result/latency serialisation and throughput calculation;
- temporal and judge-score invariants.

Future adapter tests must use local fixture processes first. External benchmark
and judge runs require a separate integration marker and fresh result storage.
