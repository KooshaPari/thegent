# Migration PR plans — config, middleware, logging families

**Tasks 9–11** — outlines only; execute per repo after ADRs and graph pass.

## Config family

1. Freeze **schema** (OpenAPI / Zod / Rust types) in **one** source repo.
2. PR1: Publish **types-only** package bump.
3. PR2..N: Consumer repos bump + remove duplicate local schemas.

**Repos:** `phenotype-config`, `phenotype-config-ts`, `heliosApp`, `heliosCLI`, `thegent` (as applicable).

## Middleware family

1. Define **port** interfaces per language.
2. Extract **generic** middleware to neutral kit name (see rename backlog).
3. PR stack: kit → first consumer → remaining consumers.

## Logging family

1. Pick **one** structured logging facade per language (already partially in `phenotype-logging-*`).
2. Migrate adapters; delete duplicate formatters.

**Dependency:** `rust-shared-workspace-decision.md` for Rust pieces.
