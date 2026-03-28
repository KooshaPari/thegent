# phenotype-metrics

Rust **metrics registry** with counters, gauges, timers, and a simple **Prometheus-style** text export (`MetricsRegistry`).

## Build

```bash
cargo test
cargo clippy
```

## Status

`Cargo.toml` is provided at the repo root so this crate is buildable as a standalone package.

## Relationship to other observability crates

- `phenotype-metrics` is the **minimal/simple registry** implementation.
- `thegent-metrics` is the **architected observability core** with ports/adapters, richer metric types, and multiple exporters.
- `phenotype-gauge` is **not** runtime observability; it is an xDD/testing and reporting crate.

If this crate grows further, prefer extracting shared metric naming/formatting/snapshot concepts instead of duplicating registry/export logic.

## Naming

Candidate for a **neutral** crate/repo name if extracted for general reuse (see Phenotype naming taxonomy).

## License

MIT
