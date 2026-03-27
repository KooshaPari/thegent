# Domain Wave 1

## Added Domain Repos

1. template-domain-webapp
2. template-domain-service-api

## Composition Model

- domain layer depends on commons + one primary language layer
- optional language layer supported where needed
- reconcile remains non-destructive by default (`smart`)

## Validation

```bash
bash scripts/validate-foundation.sh
bash scripts/validate-domains.sh
```

## Wave 2.5 Language Extension

Added `template-lang-rust` for Rust-heavy repos (`tokenledger`, `phenotype-config`) with the same contract/reconcile baseline.
