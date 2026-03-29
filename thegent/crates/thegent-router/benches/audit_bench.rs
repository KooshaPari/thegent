use criterion::{black_box, criterion_group, criterion_main, BenchmarkId, Criterion};
use tempfile::tempdir;
use thegent_router::{AuditLogger, AuditRecord};

// @trace FR-OPT-008
fn bench_audit_record_new(c: &mut Criterion) {
    // Benchmark AuditRecord::new() — includes UUID generation and SHA-256 hash.
    c.bench_function("bench_audit_record_new", |b| {
        b.iter(|| {
            black_box(AuditRecord::new(
                "thegent".to_string(),
                "claude-sonnet-4.6".to_string(),
                42,
                0.001,
            ))
        })
    });
}

// @trace FR-OPT-008
fn bench_audit_logger_append_100(c: &mut Criterion) {
    // Benchmark AuditLogger::append() amortised over 100 records.
    c.bench_function("bench_audit_logger_append_100", |b| {
        b.iter_batched(
            || {
                let dir = tempdir().expect("failed to create tempdir");
                let path = dir.path().join("routing_audit.jsonl");
                let logger = AuditLogger::new(path);
                (dir, logger)
            },
            |(_dir, logger)| {
                for i in 0u64..100 {
                    let r = AuditRecord::new(
                        "lifecycle".to_string(),
                        "gemini-3-flash".to_string(),
                        i,
                        0.001,
                    );
                    logger.append(black_box(&r)).expect("append failed");
                }
            },
            criterion::BatchSize::SmallInput,
        )
    });
}

// @trace FR-OPT-008
fn bench_audit_logger_append_1000(c: &mut Criterion) {
    // Benchmark AuditLogger::append() amortised over 1000 records.
    c.bench_function("bench_audit_logger_append_1000", |b| {
        b.iter_batched(
            || {
                let dir = tempdir().expect("failed to create tempdir");
                let path = dir.path().join("routing_audit.jsonl");
                let logger = AuditLogger::new(path);
                (dir, logger)
            },
            |(_dir, logger)| {
                for i in 0u64..1000 {
                    let r = AuditRecord::new(
                        "lifecycle".to_string(),
                        "gemini-3-flash".to_string(),
                        i,
                        0.001,
                    );
                    logger.append(black_box(&r)).expect("append failed");
                }
            },
            criterion::BatchSize::SmallInput,
        )
    });
}

// @trace FR-OPT-008
fn bench_audit_logger_verify_chain(c: &mut Criterion) {
    let mut group = c.benchmark_group("bench_audit_logger_verify_chain");
    for n in [100u64, 1000u64, 10_000u64] {
        group.bench_with_input(BenchmarkId::from_parameter(n), &n, |b, &size| {
            let dir = tempdir().expect("failed to create tempdir");
            let path = dir
                .path()
                .join(format!("routing_audit_verify_{size}.jsonl"));
            let logger = AuditLogger::new(path);
            for i in 0u64..size {
                let r = AuditRecord::new(
                    "lifecycle".to_string(),
                    "gemini-3-flash".to_string(),
                    i,
                    0.001,
                );
                logger.append(&r).expect("append failed");
            }
            b.iter(|| black_box(logger.verify_chain().expect("verify_chain failed")));
        });
    }
    group.finish();
}

// @trace FR-OPT-008
fn bench_read_last_hash(c: &mut Criterion) {
    // Benchmark: open a logger on an existing 1000-record file to exercise
    // read_last_hash() — the O(1) tail-seek path used on reopen.
    c.bench_function("bench_read_last_hash", |b| {
        // Write 1000 records once; then benchmark re-opening the logger.
        let dir = tempdir().expect("failed to create tempdir");
        let path = dir.path().join("routing_audit.jsonl");
        {
            let logger = AuditLogger::new(path.clone());
            for i in 0u64..1000 {
                let r = AuditRecord::new(
                    "lifecycle".to_string(),
                    "gemini-3-flash".to_string(),
                    i * 5,
                    0.001,
                );
                logger.append(&r).expect("append failed");
            }
        }
        // Each iteration reopens the logger, which exercises read_last_hash().
        b.iter(|| {
            let logger = black_box(AuditLogger::new(path.clone()));
            // Append one record to confirm the chain was resumed correctly.
            let r = AuditRecord::new(
                "thegent".to_string(),
                "claude-sonnet-4.6".to_string(),
                1,
                0.01,
            );
            logger.append(black_box(&r)).expect("append failed");
        });
    });
}

criterion_group!(
    benches,
    bench_audit_record_new,
    bench_audit_logger_append_100,
    bench_audit_logger_append_1000,
    bench_audit_logger_verify_chain,
    bench_read_last_hash,
);
criterion_main!(benches);
