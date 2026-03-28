# Tasks: phenotype-prefix migration

| ID | Task | Status |
|----|------|--------|
| T0 | Root README for every `phenotype-*` repo under the hub that lacked one | Done (2026-03-25) |
| T0b | `phenotype-logger` / `phenotype-metrics`: `Cargo.toml` + `cargo test` green | Done |
| T0c | `phenotype-logging-zig`: Zig 0.15 compatibility + `zig test` green | Done |
| T1 | ADR: neutral naming pattern for hex kits (per language) | Draft in `adr-001-hex-kits.md` |
| T2 | ADR: infrakit + marketplace crates (`cipher`, `sentinel`, …) | Draft in `adr-002-infra-and-generic-crates.md` |
| T3 | GitHub rename runbook (redirects, cargo/git URLs, CI) | Done — see `GITHUB_RENAME_RUNBOOK.md` |
| T4 | Resolve `phenotype-auth-ts` incomplete exports vs `src/index.ts` | Done — ports, adapters, `package.json`, Vitest green |
| T4b | `phenotype-auth-ts` `npm audit` clean (Vitest 4.x) | Done |
| T5 | `build.zig` for `phenotype-logging-zig` | Done — `zig build test` |
