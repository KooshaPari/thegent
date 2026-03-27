# gauge

Modern benchmarking + xDD testing framework for Rust with statistical analysis and beautiful HTML reports.

## Features

### Benchmarking
- **Statistical Analysis**: Mean, median, p95, p99, stddev
- **HTML Reports**: Interactive flamegraphs and charts
- **Load Testing**: Concurrent benchmarking
- **Comparisons**: Compare benchmark runs over time

### xDD Testing (from xdd-lib)
- **Property Testing**: Reusable strategies for proptest/quickcheck
- **Contract Testing**: Port/Adapter verification framework
- **Mutation Testing**: Coverage tracking utilities
- **SpecDD**: Specification parsing and validation

## Installation

```toml
[dependencies]
gauge = { git = "https://github.com/KooshaPari/gauge" }
```

## Usage

### Benchmarking
```rust
use gauge::{benchmark, group};

benchmark!("my_function").run(|| {
    my_function();
});

group!("string_ops", || {
    benchmark!("concat").run(|| format!("{} {}", "a", "b"));
});
```

### Property Testing
```rust
use gauge::proptest::{regex_strategy, numeric_range};

proptest!(|(s in regex_strategy(r"\w+"))| {
    prop_assert!(validate(&s));
});
```

## Architecture

```
src/
├── benchmarking/   # Criterion-based benchmarking
├── proptest/     # Property testing strategies
├── quickcheck/   # QuickCheck integration
├── mutation/     # Mutation testing
├── contracts/    # Contract testing (SpecDD)
└── reporters/    # HTML, JSON, CSV output
```

## Relationship to metrics crates

This crate is **not** a runtime observability or metrics registry package.

- `phenotype-metrics` and `thegent-metrics` handle runtime telemetry / metric collection.
- `gauge` handles test-quality and benchmark reporting for xDD workflows.

Keep this boundary intact to avoid mixing benchmarking/reporting concerns with live telemetry.

## License

MIT
