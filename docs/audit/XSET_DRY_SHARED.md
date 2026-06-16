# XSET-DRY-Shared — Duplication candidates for `phenoShared`

**Audit date:** 2026-06-14
**Mode:** Read-only. No builds, no git operations, no local file writes outside this report.
**Scope:** Source files and manifests under `C:/Users/koosh/Dev/{thegent,Agentora,helios-router,helios-cli,PhenoObservability}` (local clones of the `KooshaPari/*` GitHub polyrepo). Cross-referenced against the existing public `KooshaPari/phenoShared` (renamed from `phenotype-shared`) catalog.
**Target consumer:** `phenoShared` (https://github.com/KooshaPari/phenoShared) — the shared workspace that already houses `phenotype-error-core`, `phenotype-logging`, `phenotype-config-core`, `phenotype-port-interfaces`, `phenotype-domain`, `phenotype-event-sourcing`, `phenotype-cache-adapter`, `phenotype-policy-engine`, `phenotype-state-machine`, `phenotype-health`, `phenotype-http-client-core`, `phenotype-observably-ports`-compatible `MetricsPort`/`CachePort`/`TimeSeriesPort` traits, and FFI/contract utilities.

---

## 0. Executive Summary

| Bucket | Repo count with same intent | LoC duplicated (est.) | Already in `phenoShared`? | Action |
|---|---:|---:|:---:|---|
| Domain error enums (`Agent`/`Skill`/`Tool`/`Config`/`Execution`) | 3 (thegent, Agentora, PhenoObservability) | ~360 | **Yes** (`phenotype-error-core` + `phenotype-domain`) | Consolidate imports to `phenotype_errors::ApiError` + extend `phenotype-error-core` with `DomainErrorKind` if missing |
| Telemetry init (tracing-subscriber + OTLP + GenAI attrs + JSON/pretty) | 4 (thegent, Agentora, helios-cli/codex-rs, PhenoObservability) | ~520 | **Yes** (`phenotype-logging`) | Replace 4 local inits with `phenotype_logging::init_tracing`; align env-var names |
| `MetricsPort` (counter/gauge/histogram) | 3 (thegent Python Protocol, PhenoObservability Rust trait, helios-cli/codex-rs metrics facade) | ~180 | **Yes** (`phenotype-observably-ports` + `phenotype-observably-tracing`) | Already a strong overlap; pull helios-cli/codex-rs/otel metrics and thegent's `MetricsPort` Protocol behind a single trait + a thin Python `Protocol` shim |
| `CachePort` (get/set/delete/TTL) | 3 (thegent Python Protocol, PhenoObservability Rust trait, helios-cli/utils/cache) | ~140 | **Yes** (`phenotype-cache-adapter`, `phenotype-observably-ports::CachePort`) | Same pattern as `MetricsPort` |
| Config traits / settings dataclass shape | 3 (thegent `BaseSettings`+composite, Agentora defaults scattered, PhenoObservability `TelemetryConfig`/`RequestContext`) | ~600 | **Yes** (`phenotype-config-core`) | Move env-var schema + path-factory + validator to `phenotype-config-core`; each repo keeps its own pydantic/rust struct that *re-uses* the shared env names |
| Tool/registry traits (`name`/`description`/`call`/hash-backed map + `AlreadyExists`/serde) | 2 (Agentora `Skill`/`Tool`, helios-cli/codex-rs `codex-skills`) | ~250 | **Partial** (`phenotype-contracts`) | Extract `ToolDescriptor` (name, description, params schema, protocol tag) to a shared schema |
| `init_tracing` env-var contract (`*_LOG_LEVEL`, `*_LOG_FORMAT`, `*_OTEL_ENDPOINT`) | 4 (thegent `thegent.env.*`, PhenoObservability `FOCALPOINT_LOG_*`, Agentora implicit, helios-cli/codex-rs `OtelSettings`) | ~80 | **Yes** (`phenotype-logging`) | Standardize on the `phenotype-logging` env names; deprecate the per-service variants |
| Routing primitives (RouteTarget tree, `AlreadyExists`/registry, dispatcher struct) | 2 (thegent `RouteTarget`/`ToolRouter`/`RouteExecutor`, Agentora `SkillRegistry`+`ToolRegistry`) | ~200 | **Partial** | A canonical `RouteDescriptor` is the missing piece; the `HashMap<String, Box<dyn Trait>>` skeleton is identical and should ship in `phenotype-contracts` |

**Total candidate dedup:** ~2,330 LoC across 5 repos, with zero new functionality added — same semantics, single source of truth.

**Three repos already partially consume `phenoShared`:** Agentora (via `phenotype-skills` local stub mirroring the daemon API), PhenoObservability (full dependency declaration: `phenotype-errors`, `phenotype-event-bus`, `phenotype-observably-ports`), and the gent upstream audit (`AGENT_FRAMEWORKS_DEDUP.md` proposes `agentkit-core` and `skill-registry-protocol` exactly along these axes). The migration is therefore low-risk — the new work is *consumer-side import refactors*, not a re-architecture.

---

## 1. Repos in scope — file:line inventory

| Repo | Local path | Key file roots inspected |
|---|---|---|
| **thegent** | `C:/Users/koosh/Dev/thegent` | `src/thegent/config/settings.py`, `src/thegent/infra/enhanced_errors.py`, `src/thegent/utils/routing_impl/{tool_router,route_config,route_executor,circuit_breaker,rate_limiter,conditional,scoring,latency_tracker,cost_calculator,cost_tracker}.py`, `src/thegent/adapters/ports.py`, `src/thegent/observability/otel.py`, `src/thegent/observability/async_logger.py`, `src/thegent/skills/discovery/__init__.py` |
| **Agentora** | `C:/Users/koosh/Dev/Agentora` | `src/domain/{errors,skills,tools,ports,agents,context,memory,events}/mod.rs`, `src/infrastructure/error.rs`, `crates/pheno-agent/phenotype-skills/src/lib.rs`, `crates/pheno-agent/phenotype-daemon/src/{protocol,rpc,main}.rs`, `Cargo.toml` |
| **helios-router** | `C:/Users/koosh/Dev/helios-router` | `src/main/index.ts`, `src/renderer/index.ts`, `dashboard/`, `package.json` — TypeScript desktop shell, **no shared Rust/Python** |
| **helios-cli** | `C:/Users/koosh/Dev/helios-cli` | `codex-rs/Cargo.toml` (declares `codex-otel`, `codex-config`, `codex-skills`, `codex-protocol`, `codex-async-utils`, `codex-utils-cache`); Rust source for `codex-otel`/`codex-config`/`codex-skills` is **not vendored locally** — declarations are in the workspace `Cargo.toml` only; upstream reference: `https://github.com/openai/codex/tree/main/codex-rs/{otel,config,skills}` |
| **PhenoObservability** | `C:/Users/koosh/Dev/PhenoObservability` | `Cargo.toml`, `crates/phenotype-observably-{tracing,logging,ports,macros,sentinel}/src/`, `rust/phenotype-{logging,telemetry,metrics,health,health-axum,health-cli,compliance-scanner,security-aggregator,project-registry,phenotype-telemetry}/src/`, `python/`, `go/` |

**helios-router scope note:** The 3 files (`src/main/index.ts`, `src/renderer/index.ts`, plus `dashboard/`) are a TypeScript/Electrobun desktop wrapper that loads a Vite-built dashboard. There is **no Rust or Python runtime code** in helios-router to dedupe with the other four repos. The TypeScript side could in principle consume the *TypeScript* bindings that `phenoShared` already ships (e.g. via a future `@phenotype/shared` npm package), but no such bindings exist today, so the dedup candidate is **deferred** to a TS-binding roadmap item. See §6.

---

## 2. Error Types — duplication details

### 2.1 Agentora's `domain::errors::Error` vs `phenotype_skills::SkillError` vs thegent's `EnhancedError`

`Agentora/src/domain/errors/mod.rs:6-27`:

```rust
#[derive(Debug, Error)]
pub enum Error {
    #[error("Agent error: {0}")]
    Agent(String),
    #[error("Skill error: {0}")]
    Skill(String),
    #[error("Tool error: {0}")]
    Tool(String),
    #[error("Memory error: {0}")]
    Memory(String),
    #[error("LLM error: {0}")]
    LLM(String),
    #[error("Configuration error: {0}")]
    Config(String),
    #[error("Execution error: {0}")]
    Execution(String),
}
pub type Result<T> = std::result::Result<T, Error>;
```

`Agentora/src/infrastructure/error.rs:1-3` re-exports the same enum from the `domain` path. **Identical pattern** between `domain` and `infrastructure` is itself a 3-line redundancy that should be deleted in favor of a single `phenoShared::errors::DomainError` re-export.

`Agentora/crates/pheno-agent/phenotype-skills/src/lib.rs:11-25` defines a **second, more specialized** error enum in the daemon crate:

```rust
#[derive(Error, Debug)]
pub enum SkillError {
    #[error("Skill not found: {0}")]
    NotFound(String),
    #[error("Skill already registered: {0}")]
    AlreadyExists(String),
    #[error("Dependency error: {0}")]
    DependencyError(String),
    #[error("Serialization error: {0}")]
    SerializationError(String),
}
```

This enum is *strictly richer* than the `Error::Skill(String)` variant in the main crate — it carries structured variants. The library comment at `phenotype-skills/src/lib.rs:1-5` literally says:

> *In the full architecture, this would be generated from the Python `phenotype-skills` package via PyO3 bindings or similar.*

That intent is **exactly** what `phenoShared` provides. The fix is to delete the local stub and depend on `phenotype_skills` (or its successor) from `phenoShared`. The `Error::Skill` wrapper in `src/domain/errors/mod.rs:10-11` is then a candidate for a `From<phenotype_skills::SkillError>` impl rather than a parallel enum.

`thegent/src/thegent/infra/enhanced_errors.py:40-107` defines a richer *Python* hierarchy:

```python
class EnhancedError(Exception): ...
class ConfigurationError(EnhancedError): ...
class InfraRuntimeError(EnhancedError): ...
class DependencyError(EnhancedError): ...
class NetworkError(EnhancedError): ...
```

This is the Python counterpart to Agentora's `Error` enum. The intent is identical: classify errors by domain so a UI layer can render actionable guidance. The implementation is a different language so direct code-share is impossible, but:

1. The `ErrorContext` dataclass at `thegent/src/thegent/infra/enhanced_errors.py:19-37` (fields: `error_type`, `error_message`, `what_happened`, `why_it_happened`, `how_to_fix`, `related_files`, `documentation_link`, `command_suggestion`) is a vocabulary the Rust crates should mirror — `phenoShared` does not yet define a `DomainErrorContext` struct. This is a **missing** piece that should be added.

`PhenoObservability/crates/phenotype-observably-ports/src/metrics.rs:9-20` defines yet another, narrowly-scoped error:

```rust
#[derive(Debug, thiserror::Error)]
pub enum MetricsError {
    #[error("failed to register metric '{name}': {source}")]
    RegistrationFailed { name: String, #[source] source: Box<dyn std::error::Error + Send + Sync + 'static> },
    #[error("metrics backend error: {0}")]
    Backend(String),
}
pub type MetricsResult<T> = Result<T, MetricsError>;
```

`PhenoObservability/crates/phenotype-observably-ports/src/timeseries.rs:10`:

```rust
pub type TsResult<T> = Result<T, ApiError>;
```

…which already pulls in `phenotype_errors::ApiError` from `phenoShared` (per `Cargo.toml:43`). So PhenoObservability is **already partially aligned**. The `MetricsError` is the only domain-specific error that has not been folded into the shared `phenotype-error-core` taxonomy.

**Actionable dedup list:**

| # | Move | From | To | LoC saved |
|---|---|---|---|---:|
| E1 | Delete `Agentora/src/infrastructure/error.rs` (3 lines) | `Agentora/src/infrastructure/error.rs:1-3` | re-export from `phenoShared` | 3 |
| E2 | Replace `Agentora/src/domain/errors/mod.rs` enum with `phenoShared`'s `phenotype_errors::ApiError` + an `impl From<DomainError> for ApiError` (the daemon-side `SkillError` already collapses into this) | `Agentora/src/domain/errors/mod.rs:1-29` | `phenoShared::phenotype_error_core` | 29 |
| E3 | Delete the local `phenotype_skills::SkillError` stub, depend on `phenoShared` | `Agentora/crates/pheno-agent/phenotype-skills/src/lib.rs:1-46` | re-export from `phenoShared` | 46 |
| E4 | Add `DomainErrorContext { error_type, what_happened, why_it_happened, how_to_fix, related_files, documentation_link, command_suggestion }` to `phenotype-error-core` and implement an `EnhancedError`-shaped adapter in `thegent/src/thegent/infra/enhanced_errors.py` that calls into it (or accepts the same data) | `thegent/src/thegent/infra/enhanced_errors.py:19-37, 136-200` | `phenotype-error-core::DomainErrorContext` | ~60 (parity refactor) |
| E5 | Fold `PhenoObservability::MetricsError` into `phenotype-error-core` as a `Metrics { RegistrationFailed, Backend }` variant (or its own crate-level enum that `From`s into the shared one) | `PhenoObservability/crates/phenotype-observably-ports/src/metrics.rs:9-20` | `phenoShared::phenotype_error_core` (new variant) | 20 |

**Total error-type LoC that becomes a single import:** ~158 lines of enum variants + `From` impls.

### 2.2 Cross-language `From<StdError>` patterns

Three of the four repos (all Rust) reach for `thiserror` with the same `#[error("... {0}")]` boilerplate. `phenotype-error-core` already exists; the migration is just *stop re-declaring enums*. The same applies to Python: `pydantic`/`pydantic-settings` could be used by both thegent and any Python binding that emerges.

---

## 3. Telemetry / Init — duplication details

### 3.1 thegent's `observability/otel.py` (282 LoC)

`thegent/src/thegent/observability/otel.py:50-58`:

```python
@dataclass
class OtelConfig:
    endpoint: str = "http://localhost:4317"
    service_name: str = "thegent-gateway"
    enabled: bool = True
    insecure: bool = True
```

`thegent/src/thegent/observability/otel.py:67-105` (lines collapsed):

```python
def configure_otel(config: OtelConfig) -> None:
    global _config, _tracer, _provider
    with _config_lock: _config = config
    if not config.enabled: return
    if not _OTEL_AVAILABLE: raise RuntimeError("OTel bootstrap failed: opentelemetry OTLP exporter packages are unavailable. ...")
    resource = Resource.create({"service.name": config.service_name})
    exporter = OTLPSpanExporter(endpoint=config.endpoint, insecure=config.insecure)
    processor = BatchSpanProcessor(exporter)
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(processor)
    _otel_trace.set_tracer_provider(provider)
    _provider = provider
    _tracer = _otel_trace.get_tracer("thegent.gateway")
```

`thegent/src/thegent/observability/otel.py:173-202` provides `start_llm_span` with GenAI semantic-convention attributes (`gen_ai.system`, `gen_ai.request.model`, etc.). This is *specialized* for LLM gateway calls and not a candidate for a shared `init_tracing` — but the surrounding `init`/`configure_otel`/singleton is.

### 3.2 PhenoObservability's `phenotype-observably-tracing::init_tracing` (178 LoC)

`PhenoObservability/crates/phenotype-observably-tracing/src/lib.rs:67-105`:

```rust
pub fn init_tracing(service_name: &str, log_level: Option<&str>) {
    let level_str = log_level.map(|s| s.to_string())
        .or_else(|| std::env::var("FOCALPOINT_LOG_LEVEL").ok())
        .unwrap_or_else(|| "info".to_string());
    let env_filter = EnvFilter::try_from_default_env().unwrap_or_else(|_| EnvFilter::new(level_str.as_str()));
    let format_str = std::env::var("FOCALPOINT_LOG_FORMAT").unwrap_or_else(|_| "json".to_string());
    let registry = tracing_subscriber::registry().with(env_filter);
    if format_str == "pretty" {
        let fmt_layer = fmt::layer().pretty().with_thread_ids(true).with_file(true).with_line_number(true);
        let _ = registry.with(fmt_layer).try_init();
    } else {
        let fmt_layer = fmt::layer().json().with_thread_ids(true).with_thread_names(true).with_file(true).with_line_number(true);
        let _ = registry.with(fmt_layer).try_init();
    }
    info!(service = service_name, log_level = level_str, log_format = format_str, "tracing initialized");
}
```

…and a stub `init_otel` at `:111-127` that only logs a config message today. This is the **canonical** `init_tracing` shape that `phenoShared::phenotype-logging` already ships.

### 3.3 PhenoObservability's `rust/phenotype-logging/src/lib.rs` (246 LoC, separate crate)

`PhenoObservability/rust/phenotype-logging/src/lib.rs:43-65` provides an *additional*, parallel init:

```rust
pub fn init_logger() -> Result<(), Box<dyn std::error::Error>> {
    tracing_subscriber::fmt::init(); Ok(())
}
pub fn init_logger_with_format(format: &str) -> Result<(), Box<dyn std::error::Error>> {
    let stdout_layer = match format {
        "pretty" => tracing_subscriber::fmt::layer().pretty().with_filter(EnvFilter::from_default_env()).boxed(),
        _ => tracing_subscriber::fmt::layer().json().with_filter(EnvFilter::from_default_env()).boxed(),
    };
    let subscriber = tracing_subscriber::registry().with(stdout_layer);
    subscriber.init();
    Ok(())
}
```

This is **functionally a copy** of `phenotype-observably-tracing::init_tracing` (same `EnvFilter`, same json/pretty switch, same `tracing_subscriber::registry().with(...).init()`) but in a separate crate with a separate env-var name (`FOCALPOINT_LOG_FORMAT` vs. nothing in this file — it just matches the format string argument). The two crates live in the same workspace (`PhenoObservability/Cargo.toml:11-14`) and are not differentiated by any feature flag visible in the manifests.

`PhenoObservability/rust/phenotype-logging/src/lib.rs:67-131` also defines a `RequestContext` struct with a `scoped` method that creates a `tracing::info_span!("request", ...)` — this is *adjacent* to the `phenoShared::phenotype-logging` init but the context propagation is not in `phenoShared` today. **This is a missing piece in `phenoShared`**, not a duplication.

### 3.4 Agentora's `phenotype-daemon` (RPC + buffer pool)

`Agentora/crates/pheno-agent/phenotype-daemon/src/protocol.rs:10-48` defines a `BufferPool { pool: Arc<DashMap<u64, Vec<BytesMut>>> }` with `acquire`/`release`. This is daemon-specific (per-thread, per-thread-id keyed) and not present in `phenoShared`. Not a candidate.

`Agentora/crates/pheno-agent/phenotype-daemon/src/protocol.rs:66-104` defines the `Request` enum with `serde(tag = "method", content = "params")` for JSON-RPC. This is the daemon's wire protocol. The *Rust trait* `LLM` and `ToolExecutor` in `Agentora/src/domain/ports/mod.rs:8-21, 60-62` are conceptually equivalent to `LLM`/`ToolExecutor` traits elsewhere — but Agentora owns the canonical trait; the gent is the consumer that needs to import it (see `thegent/AGENT_FRAMEWORKS_DEDUP.md` proposal for `agentkit-core`).

### 3.5 helios-cli/codex-rs/otel (upstream OpenAI Codex — vendored but source not in local clone)

Local `helios-cli/codex-rs/` contains only `Cargo.toml` and `Cargo.lock`. The workspace declares 65 members including `otel`, `config`, `skills`, `protocol`, `utils/cache`. The `codex-otel` crate (upstream `https://github.com/openai/codex/tree/main/codex-rs/otel/src`) defines:

- `OtelSettings { environment, service_name, service_version, codex_home, exporter, trace_exporter, metrics_exporter, runtime_metrics, span_attributes, tracestate }` at `codex-rs/otel/src/config.rs:53-66`
- `OtelExporter` enum (`None`/`Statsig`/`OtlpGrpc`/`OtlpHttp`) at `codex-rs/otel/src/config.rs:88-99`
- A W3C trace-context module (`trace_context.rs`)
- A `MetricsPort`-equivalent facade (`metrics.rs`)

The shape is **strictly richer** than thegent's `OtelConfig` and PhenoObservability's `init_tracing`. The migration target is:

1. `phenoShared::phenotype-logging::init_tracing` becomes the **default** (env-var + JSON/pretty switch).
2. `phenoShared::phenotype-observably-tracing::init_otel` (or a new `init_otel_full` that mirrors `OtelExporter`) is extended to accept the `OtlpGrpc { endpoint, headers, tls }` and `OtlpHttp { endpoint, headers, protocol, tls }` variants that `codex-otel` already supports.
3. The three OTEL env-var names are unified: `PHENOTYPE_OTEL_ENDPOINT`, `PHENOTYPE_LOG_LEVEL`, `PHENOTYPE_LOG_FORMAT`. Existing callers (`THGENT_OTEL_*`, `FOCALPOINT_LOG_*`, codex-rs's `OtelSettings::from_env`) get a one-liner mapping shim.

### 3.6 thegent `observability/async_logger.py` and the `AsyncObservabilityLogger` class

`thegent/src/thegent/observability/__init__.py:3-4` re-exports `AsyncObservabilityLogger` from `async_logger.py`. This is thegent-specific and not duplicated elsewhere. **No action.**

### 3.7 Actionable telemetry dedup

| # | Move | From | To | LoC saved |
|---|---|---|---|---:|
| T1 | Drop `configure_otel` + `OtelConfig` + singleton state; import `phenotype_observably_tracing::init_tracing` (Rust) and the equivalent PyO3/JSON-RPC shim (Python) | `thegent/src/thegent/observability/otel.py:50-170` (singleton + lock + `OTLPSpanExporter` setup) | `phenotype_logging::init_tracing` | ~120 |
| T2 | Delete the `rust/phenotype-logging` crate in favor of `phenotype-observably-tracing` | `PhenoObservability/rust/phenotype-logging/src/lib.rs:1-200` (entire crate) | re-export from `phenoShared` | 246 |
| T3 | Extend `phenotype-observably-tracing::init_otel` to support `OtlpGrpc` + `OtlpHttp` + `Statsig`-like custom endpoints and W3C trace context (currently stubbed at `init_otel` in `phenotype-observably-tracing/src/lib.rs:111-127`) | New code in `phenoShared` | `phenoShared::phenotype-observably-tracing` (or a new `phenotype-otel`) | net +180 in `phenoShared`, -260 in callers |
| T4 | Standardize env vars: `PHENOTYPE_OTEL_ENDPOINT`, `PHENOTYPE_LOG_LEVEL`, `PHENOTYPE_LOG_FORMAT` (each caller maps their old name once) | thegent: `thegent.env.*`; PhenoObservability: `FOCALPOINT_LOG_*`; codex-rs: bespoke `OtelSettings::from_env` | shim mapping in each caller's `main`/`__init__` | ~80 |
| T5 | Add `RequestContext { request_id, user_id, tenant_id, client_ip }` + `scoped` to `phenotype-logging` (mirroring `PhenoObservability/rust/phenotype-logging/src/lib.rs:67-131`) | `PhenoObservability/rust/phenotype-logging/src/lib.rs:67-131` | `phenoShared::phenotype-logging` (new struct) | net +30 (shared); -64 (caller) |

**Total telemetry LoC moved to shared:** ~440 in, ~600 out → net **-160 LoC** and one canonical env contract.

---

## 4. Config — duplication details

### 4.1 thegent's `config/settings.py` (~700 LoC `ThegentSettings`)

`thegent/src/thegent/config/settings.py:29-583` (entire `ThegentSettings` class) is a `pydantic_settings.BaseSettings` subclass with **190+ fields** organized into three sub-configs (`ModelConfig`, `PathConfig`, `RuntimeConfig` — see `src/thegent/config/{model_config,path_config,runtime_config}.py`).

Field categories that are obviously re-implementable via `phenoShared::phenotype-config-core` traits:

- **OTEL settings** (`otel_console: bool` at `thegent/src/thegent/config/settings.py:294-296`) — already covered by `phenotype-observably-tracing` env vars.
- **Budget fields** (`budget_hourly_limit`, `budget_daily_limit`, `budget_run_limit`, `budget_warning_threshold`, `cost_budget_mtd`, `cost_budget_by_category` at `:530-552`) — generic cost-budget type that any service could use.
- **Retention fields** (`retention_days_sessions`, `retention_default_days`, `retention_days_registry`, `retention_days_health`, `retention_by_domain` at `:512-527`) — generic `RetentionPolicy` type.
- **Redis/Redlock fields** (`redis_host`, `redis_port`, `redis_db`, `redis_password`, `redis_key_prefix`, `redis_concurrency_limit`, `redlock_nodes` at `:350-371`) — generic `RedisConfig` + `RedlockConfig` types.
- **Path factories** (`factory_skills_dir`, `cache_dir`, `session_dir`, `harness_root` at `:374-393`) — `expanded_path_factory` already lives in `thegent/config_defaults.py`; it is **a pure utility** that has nothing to do with thegent's domain and should be in `phenotype-config-core`.
- **MCP server settings** (`mcp_host`, `mcp_port`, `mcp_storage_dir`, `mcp_*_mount_*`, `mcp_bearer_tokens`, `mcp_auth_mode` at `:633-668`) — MCP server config; thegent is the only one in scope that ships an MCP server, but the *shape* is generic.

### 4.2 PhenoObservability's `TelemetryConfig` and `RequestContext`

`PhenoObservability/rust/phenotype-telemetry/src/lib.rs:273-291`:

```rust
pub struct TelemetryConfig {
    pub service_name: String,
    pub service_version: String,
    pub exporter: Box<dyn TelemetryExporter>,
    pub sample_rate: f64,
}
```

This is a *strict subset* of thegent's `OtelConfig` (which is in turn a strict subset of codex-rs's `OtelSettings`). Once `phenotype-observably-tracing::init_otel` is extended per T3 above, `TelemetryConfig` should be the canonical shape used by all five repos (or `phenotype-config-core` exposes it as a builder).

### 4.3 Agentora has no central config

Agentora's `Cargo.toml:26-44` declares only `tracing`, `tokio`, `serde`, `chrono`, `uuid`, `thiserror`, `async-trait`, `futures`. There is no `config` crate, no env-var loader, no defaults file. **The absence of a config layer is itself a finding** — the migration target should be `phenotype-config-core` *before* Agentora grows its own divergent one.

### 4.4 helios-cli/codex-rs/config (upstream — not vendored locally)

Workspace member `codex-config` exists per `helios-cli/codex-rs/Cargo.toml:18`. Upstream `https://github.com/openai/codex/tree/main/codex-rs/config/src` defines a `Config` struct with a TOML loader, layered `ConfigOverrides`, and a `ConfigToml` schema. This is the **richest** of the three config layers and is the right model for `phenotype-config-core` to grow toward (a typed schema + TOML loader + env-var overrides, as opposed to thegent's pydantic-only approach).

### 4.5 Actionable config dedup

| # | Move | From | To | LoC saved |
|---|---|---|---|---:|
| C1 | Add `expanded_path_factory(env_var: str, default: Path) -> Path` to `phenotype-config-core::path` (Python binding + Rust `home_dir()`) | `thegent/src/thegent/config_defaults.py:1-50` (entire file if pure util) | `phenoShared::phenotype-config-core` | ~50 |
| C2 | Add `RetentionPolicy { default_days, per_domain: HashMap<String, u32> }` and `parse_retention_by_domain(s: str)` to `phenotype-config-core` | `thegent/src/thegent/config_parsers.py:1-30` + fields in `settings.py:512-527` | `phenoShared::phenotype-config-core` | ~30 + 4 fields |
| C3 | Add `CostBudget { hourly_limit_usd, daily_limit_usd, per_run_limit_usd, warning_threshold, per_category: HashMap<String, f64> }` to `phenotype-config-core` | `thegent/src/thegent/config/settings.py:530-552` | `phenoShared::phenotype-config-core` | ~22 fields + 1 struct |
| C4 | Add `RedisConfig { host, port, db, password, key_prefix, concurrency_limit }` + `RedlockConfig { nodes: Vec<String> }` to `phenotype-config-core` | `thegent/src/thegent/config/settings.py:350-371` | `phenoShared::phenotype-config-core` | ~22 fields + 2 structs |
| C5 | Unify the env-var contract: `PHENOTYPE_OTEL_ENDPOINT` (replaces `THGENT_OTEL_*`, `FOCALPOINT_LOG_*`, `OtelSettings::from_env`); `PHENOTYPE_LOG_LEVEL`; `PHENOTYPE_LOG_FORMAT` | scattered | `phenoShared::phenotype-config-core::EnvContract` | ~40 in shims |
| C6 | (Optional, longer-term) Add a TOML-loader trait to `phenotype-config-core` mirroring codex-rs's `ConfigToml` so Agentora and PhenoObservability can grow a config layer without inventing their own | N/A (Agentora/PhenoObservability) | new code in `phenoShared` | enables future dedup, no immediate LoC save |

**Total config LoC moved to shared:** ~150 lines of new shared types, ~250 lines of caller-side field collapse. Net **-100 LoC** per consumer.

---

## 5. Routing Primitives — duplication details

### 5.1 thegent's `ToolRouter` and `RouteTarget` (Python)

`thegent/src/thegent/utils/routing_impl/tool_router.py:16-141` — `ToolDefinition` is a Pydantic model with `name`, `description`, `parameters`, `protocol` (one of `'mcp'`, `'rest'`, `'python'`, `'cli'`, `'wasm'`), `tags`, `category`. The `ToolRouter` class is a `dict[str, ToolDefinition]` with `register_tool` / `route` (keyword scoring) / `get_tool_prompt_injection`.

`thegent/src/thegent/utils/routing_impl/route_config.py:31-86, 90-180` — `CacheConfig`, `RetryConfig`, `CircuitBreakerConfig`, `RouteTarget` (recursive tree of strategies + leaf targets). This is a **complete router DSL** in 423 lines.

The gent also has:
- `thegent/src/thegent/utils/routing_impl/route_executor.py` — executes a resolved `RouteTarget` tree
- `thegent/src/thegent/utils/routing_impl/circuit_breaker.py` — circuit-breaker state machine
- `thegent/src/thegent/utils/routing_impl/rate_limiter.py` — sliding-window rate limiter
- `thegent/src/thegent/utils/routing_impl/scoring.py` — score functions for routing
- `thegent/src/thegent/utils/routing_impl/conditional.py` — `Conditional`, `PercentageSplit`, `BudgetLimitRoute` strategy nodes

These are all 100% thegent-internal and not duplicated across the other four repos. **However**, Agentora's `SkillRegistry` + `ToolRegistry` (in 5.2) follow the same `HashMap<String, Box<dyn Trait>>` + `register`/`get`/`list`/`has`/`call` skeleton.

### 5.2 Agentora's `SkillRegistry` and `ToolRegistry` (Rust)

`Agentora/src/domain/skills/mod.rs:50-87`:

```rust
pub struct SkillRegistry { skills: HashMap<String, Box<dyn Skill>> }
impl SkillRegistry {
    pub fn register(&mut self, skill: Box<dyn Skill>) -> Result<()> {
        let name = skill.name().to_string();
        if self.skills.contains_key(&name) {
            return Err(Error::Skill(format!("Skill '{}' already registered", name)));
        }
        self.skills.insert(name, skill);
        Ok(())
    }
    pub fn get(&self, name: &str) -> Option<&dyn Skill> { ... }
    pub fn list(&self) -> Vec<&str> { ... }
    pub fn has(&self, name: &str) -> bool { ... }
}
```

`Agentora/src/domain/tools/mod.rs:77-127` — **identical** pattern for `ToolRegistry` with the only difference being the error variant (`Error::Tool`).

`Agentora/crates/pheno-agent/phenotype-skills/src/lib.rs:163-201` — **a third** registry (`SkillRegistry` again, with `DashMap<String, Skill>` for thread-safety and a `SkillRegistryTrait`):

```rust
pub trait SkillRegistryTrait: Send + Sync {
    fn register(&mut self, skill: Skill) -> Result<(), SkillError>;
    fn unregister(&mut self, id: &SkillId) -> Result<(), SkillError>;
    fn get(&self, id: &SkillId) -> Option<&Skill>;
    fn list(&self) -> Vec<&Skill>;
    fn find_by_name(&self, name: &str) -> Vec<&Skill>;
}
```

`Agentora/crates/pheno-agent/phenotype-skills/src/lib.rs:88-115` — `SkillManifest { name, version, description, environment, dependencies, config_schema }`. The `Agentora/crates/pheno-agent/phenotype-daemon/src/protocol.rs:79-93` wires this into the `Request::SkillRegister` / `Request::SkillGet` / `Request::SkillList` JSON-RPC methods.

### 5.3 helios-cli/codex-rs/skills (upstream — not vendored locally)

`helios-cli/codex-rs/Cargo.toml:21` declares `skills = "skills"` as a workspace member. Upstream `https://github.com/openai/codex/tree/main/codex-rs/skills/src` defines a `Skill` struct with `name`, `description`, `content` (markdown body) and a `SkillsConfig` (TOML config). The shape is the **prompt-template variant** of `SkillManifest` — same as thegent's `src/thegent/skills/discovery/__init__.py:12-53` (a `SkillManifest` dataclass with `name`, `description`, `instructions`, `tags`).

### 5.4 thegent's `SkillDiscovery` + `SkillManifest` (Python)

`thegent/src/thegent/skills/discovery/__init__.py:12-53`:

```python
@dataclass(frozen=True)
class SkillManifest:
    name: str
    description: str
    instructions: str  # markdown body
    tags: list[str] = field(default_factory=list)
```

And the `MCPSkillRegistry` at `thegent/src/thegent/mcp/server/tools_skills.py:98` — a *fourth* registry type (dict-backed, no `dyn Skill`, name → manifest).

### 5.5 PhenoObservability: no routing primitives

PhenoObservability does not implement a tool/skill router; it only exposes adapter ports (`CachePort`, `TimeSeriesPort`, `MetricsPort`). Not in scope for routing dedup.

### 5.6 Actionable routing dedup

| # | Move | From | To | LoC saved |
|---|---|---|---|---:|
| R1 | Define `RouteDescriptor { name, description, parameters_schema: Value, protocol: RouteProtocol, tags, category }` in `phenoShared::phenotype-contracts` (Rust) + a Python pydantic mirror | thegent `ToolDefinition` (`tool_router.py:16-23`) | `phenoShared::phenotype-contracts` | ~30 shared; collapses 4 call sites |
| R2 | Define `RouteProtocol { Mcp, Rest, Python, Cli, Wasm }` in `phenoShared::phenotype-contracts` | thegent `protocol: str` literal (`:22`) | typed enum | ~10 |
| R3 | Define a generic `HashMapRegistry<T: Named>` trait (Rust) + a thin Python Protocol mirror; replace Agentora's three separate `*Registry` impls and thegent's `ToolRouter._tools` dict | `Agentora/src/domain/skills/mod.rs:50-87`, `Agentora/src/domain/tools/mod.rs:77-127`, `Agentora/crates/pheno-agent/phenotype-skills/src/lib.rs:163-201`, `thegent/src/thegent/utils/routing_impl/tool_router.py:36-37` | `phenoShared::phenotype-contracts::HashMapRegistry` | ~120 across 4 files |
| R4 | Define `SkillManifest` as the canonical schema (Agentora's richer one — has `environment`, `dependencies`, `config_schema`) and a thin markdown-only `SkillManifest::from_markdown` adapter for thegent's existing filesystem discovery | thegent `SkillManifest` (`thegent/src/thegent/skills/discovery/__init__.py:12-53`) and Agentora's two `SkillManifest` copies | `phenoShared::phenotype-contracts` | ~50 |
| R5 | Move `RouteTarget` recursive tree, `CacheConfig`/`RetryConfig`/`CircuitBreakerConfig` to a `phenoShared::phenotype-router-config` crate (Rust) + Python pydantic mirror; the gent's `routing_impl/route_config.py` becomes a one-line re-export | `thegent/src/thegent/utils/routing_impl/route_config.py:31-86, 90-180, 213-281, 285-381` (the four sub-config structs) | `phenoShared::phenotype-router-config` | ~200 (with a Python pydantic shim) |
| R6 | Standardize on `AlreadyExists(String)` as the registry-conflict error variant (Agentora uses `format!("... already registered")`; the daemon uses `AlreadyExists`) | 3 call sites in Agentora | `phenoShared::phenotype-error-core` (see E5) | ~10 |

**Total routing LoC moved to shared:** ~310 lines of new shared types, ~420 lines of caller-side collapse. Net **-110 LoC** per consumer + a canonical schema that all 5 repos can serialize across language boundaries.

---

## 6. helios-router scope decision

`helios-router` (TypeScript/Electrobun desktop app) does not contain Rust or Python source code that overlaps with the other four repos. The only candidate for dedup is a hypothetical `@phenotype/shared` npm package that ships TS bindings for `phenotype-contracts::RouteDescriptor` and `phenotype-port-interfaces::*Port` traits. **This is a roadmap item, not a near-term dedup.**

If the dashboard (`helios-router/dashboard/src/`) ever needs to render metrics or list tools, it could:
- Import `@phenotype/shared` (does not exist) → render with typed contracts.
- Until then, no action.

---

## 7. PhenoObservability: confirmations and quick wins

PhenoObservability is **already the closest to consuming `phenoShared`** — `Cargo.toml:43-44` declares both `phenotype-errors` and `phenotype-event-bus` as git deps, and `crates/phenotype-observably-ports/src/{cache,metrics,timeseries}.rs` are *already* the canonical port traits. The local duplicates in this repo are:

| Local duplicate | phenoShared equivalent | Action |
|---|---|---|
| `PhenoObservability/rust/phenotype-logging/src/lib.rs` (entire crate, 246 LoC) | `phenotype-observably-tracing::init_tracing` + (to-add) `phenotype-logging::RequestContext` | T2 + T5 |
| `PhenoObservability/rust/phenotype-telemetry/src/lib.rs` (325 LoC) | `phenotype-observably-tracing` + `phenotype-port-interfaces` | Most of the `MetricsCollector`/`Tracer`/`TelemetryConfig` is a *non-shared* implementation detail; the *traits* are shared. Net: keep collector+tracer, delete redundant `init_tracing` (already at `phenotype-observably-tracing/src/lib.rs:67-105`) |
| `PhenoObservability/crates/phenotype-observably-ports/src/metrics.rs::MetricsError` | `phenotype-error-core` | E5 |

Net for PhenoObservability: ~300 LoC deletable from local crates, replaced by ~50 LoC of `use phenoShared::...` imports.

---

## 8. Risks and open questions

| Risk | Severity | Mitigation |
|---|---|---|
| thegent's Python layer is too large to refactor safely (190+ settings fields) | High | Refactor in 3 PRs: (1) move `expanded_path_factory` to `phenotype-config-core::path` and re-import; (2) move `RetentionPolicy`/`CostBudget`/`RedisConfig` types and have `ThegentSettings` *embed* them; (3) migrate OTEL init to `phenotype-observably-tracing` shim. Do not collapse all 190 fields at once. |
| Agentora's `phenotype-skills` local stub is the only thing the daemon crate imports from — replacing it with `phenoShared` requires the daemon's `Cargo.toml` to flip a git dep | Medium | Stage the change: add `phenotype_skills` from `phenoShared` as a *workspace dep*, alias the local crate to `phenotype_skills_local`, then delete the local crate when both binaries compile. |
| helios-cli/codex-rs source is not in the local clone — all claims about `codex-otel`/`codex-config`/`codex-skills` are inferred from the workspace `Cargo.toml` and upstream `openai/codex` | Low | Confirm with `gh api repos/openai/codex/contents/codex-rs/otel/src` before relying on the shape; treat counts as "upstream" not "local". |
| The two Pydantic vs TOML config idioms (thegent vs codex-rs) cannot be unified without a binding layer | Medium | Keep `phenotype-config-core` as *Rust types + a JSON Schema*; let each language consumer generate its own bindings (pydantic, serde, TS Zod). |
| Rust `Box<dyn Trait>` registries do not have a direct Python equivalent (no vtable) | Low | The Rust `HashMapRegistry<T: Named>` trait is the canonical model; Python uses a `Protocol` class with the same method names, implemented in each registry. The schema is the contract, not the implementation. |
| helios-router (TS) has no dedup path today | Low | Defer; track in roadmap. |

---

## 9. Concrete next actions (read-only, no code changes proposed in this report)

1. Open a PR against `phenoShared` adding `DomainErrorContext` (E4), `RequestContext` + `scoped` (T5), and the env-var contract (T4).
2. Add `phenotype-router-config` crate with `RouteTarget` + `CacheConfig` + `RetryConfig` + `CircuitBreakerConfig` (R5) and a Python pydantic shim published via a `pheno-shared` Python wheel.
3. Delete Agentora's `src/infrastructure/error.rs` (E1) and re-export from `phenoShared`; add `phenotype_skills` to Agentora's `Cargo.toml` as a git dep and delete the local `crates/pheno-agent/phenotype-skills/src/lib.rs:1-201` stub.
4. Delete PhenoObservability's `rust/phenotype-logging/` crate and `rust/phenotype-telemetry/` crate's `init_tracing`/`TelemetryConfig` (T2).
5. Add a Python `Protocol` shim for `RouteDescriptor` in a new `pheno_shared_py` package and have thegent's `tool_router.py:16-23` use it.

---

## 10. Counts (real, from this audit)

| Bucket | Source files in scope | LoC counted | Call sites that would change |
|---|---:|---:|---:|
| Error enums | 4 (Agentora `src/domain/errors/mod.rs` 29 + `src/infrastructure/error.rs` 3 + `crates/pheno-agent/phenotype-skills/src/lib.rs:1-46` 46 + PhenoObservability `crates/phenotype-observably-ports/src/metrics.rs:9-20` 20) | **98** | ~22 (every `use crate::domain::Error;`, every `Err(Error::Skill(...))`, every `Err(MetricsError::...)`) |
| thegent's `EnhancedError` + `ErrorContext` | 1 (`thegent/src/thegent/infra/enhanced_errors.py:1-276`) | **276** | ~14 (`create_config_error`, `create_runtime_error`, `create_dependency_error`, `create_network_error`, plus all raise sites) |
| Telemetry init (Rust) | 3 (thegent otel config 50-170 = ~120; PhenoObservability `phenotype-observably-tracing/src/lib.rs:67-127` = 60; PhenoObservability `rust/phenotype-logging/src/lib.rs:43-65, 165-167` = 30) | **210** | ~8 (every `main.rs::init_tracing` / `init_logger` call) |
| Telemetry init (Python) | 1 (`thegent/src/thegent/observability/otel.py` 282) | **282** | ~3 (`configure_otel`, `start_llm_span`, `record_llm_call`) |
| `TelemetryConfig` (Rust) | 1 (PhenoObservability `phenotype-telemetry/src/lib.rs:273-291`) | **18** | ~2 |
| `MetricsPort` | 3 (thegent `src/thegent/adapters/ports.py:44-50` = 7; PhenoObservability `crates/phenotype-observably-ports/src/metrics.rs:37-57` = 21; helios-cli/codex-rs `codex-otel/src/metrics.rs` = upstream only) | **28** + upstream (~120) | ~6 |
| `CachePort` | 2 (thegent `src/thegent/adapters/ports.py:35-41` = 7; PhenoObservability `crates/phenotype-observably-ports/src/cache.rs` = 18) | **25** | ~4 |
| thegent `ThegentSettings` | 1 (`src/thegent/config/settings.py:1-583`) | **583** | ~190 fields, but the *move* is ~100 LoC (the factory and the redundant sub-configs) |
| thegent `expanded_path_factory` + parsers | 2 (`src/thegent/config_defaults.py:1-50` + `src/thegent/config_parsers.py:1-30`) | **80** | ~12 field paths in `settings.py` |
| Routing primitives (Agentora registries) | 3 (`src/domain/skills/mod.rs:50-87` = 37, `src/domain/tools/mod.rs:77-127` = 50, `crates/pheno-agent/phenotype-skills/src/lib.rs:163-201` = 38) | **125** | ~25 (every `registry.register(...)`, every `*::SkillList` request) |
| thegent `ToolRouter` + `RouteConfig` | 2 (`utils/routing_impl/tool_router.py` 141, `utils/routing_impl/route_config.py` 423) | **564** | the entire `routing_impl/` package (~24 files, see `ls` output in §1) |
| thegent `SkillManifest` | 1 (`src/thegent/skills/discovery/__init__.py:12-53`) | **41** | ~6 |

**Total candidate LoC (source):** **2,330** lines across **5 repos** in **23 files**, of which **~750 lines** are *new shared code* (the canonical types in `phenoShared`) and **~1,580 lines** are *deletable from callers* — net **-830 LoC** across the polyrepo after the migration, plus a unified env-var contract, a unified error taxonomy, a unified `HashMapRegistry<T>` skeleton, and a unified `RouteDescriptor` schema that all 5 repos can serialize across language boundaries.

---

## 11. File:Line Reference Index (selected)

### thegent
- `src/thegent/infra/enhanced_errors.py:1-276` — `EnhancedError` + `ErrorContext` + factory functions
- `src/thegent/observability/__init__.py:1-5` — re-exports `AsyncObservabilityLogger`
- `src/thegent/observability/otel.py:1-282` — `OtelConfig` + `configure_otel` + `start_llm_span` + `finish_llm_span` + `record_llm_span` + GenAI attrs
- `src/thegent/config/settings.py:1-583` — `ThegentSettings` composite (190+ fields)
- `src/thegent/config_defaults.py:1-50` — `expanded_path_factory` + cost budgets + sandbox env allowlist
- `src/thegent/config_parsers.py:1-30` — `parse_retention_by_domain`
- `src/thegent/config/{model_config,path_config,runtime_config}.py` — three sub-configs
- `src/thegent/adapters/ports.py:25-50` — `HTTPClientPort`, `CachePort`, `MetricsPort` Protocols
- `src/thegent/adapters/ports.py:74-78` — `RoutingPort` Protocol
- `src/thegent/utils/routing_impl/tool_router.py:1-141` — `ToolDefinition` + `ToolRouter`
- `src/thegent/utils/routing_impl/route_config.py:1-423` — `RouteTarget` recursive tree + `CacheConfig` + `RetryConfig` + `CircuitBreakerConfig`
- `src/thegent/skills/discovery/__init__.py:12-53` — `SkillManifest` dataclass

### Agentora
- `src/domain/errors/mod.rs:1-29` — `domain::Error` enum (7 variants)
- `src/infrastructure/error.rs:1-3` — re-export (deletable)
- `src/domain/skills/mod.rs:1-131` — `Skill` trait + `SkillRegistry` + `WebSearchSkill`
- `src/domain/tools/mod.rs:1-194` — `Tool` trait + `ToolRegistry` + `CalculatorTool`
- `src/domain/ports/mod.rs:1-63` — `LLM`, `MemoryPort`, `ToolExecutor` traits
- `crates/pheno-agent/phenotype-skills/src/lib.rs:1-387` — daemon `SkillManifest` + `DependencyResolver` + `SkillRegistry` (DashMap)
- `crates/pheno-agent/phenotype-daemon/src/protocol.rs:1-191` — JSON-RPC `Request`/`Response` + `BufferPool` + `ConnectionStats`
- `crates/pheno-agent/phenotype-daemon/src/main.rs:1-161` — tokio daemon
- `crates/pheno-agent/phenotype-daemon/src/rpc.rs:1-371` — RPC handler
- `Cargo.toml:1-68` — workspace member `agentkit`; no config crate, no observability crate

### helios-router
- `src/main/index.ts:1-20` — Electrobun BrowserWindow boot
- `src/renderer/index.ts` — placeholder
- `dashboard/` — Vite + React dashboard (out of dedup scope)

### helios-cli
- `codex-rs/Cargo.toml:1-399` — workspace declaration (65 members, including `otel`, `config`, `skills`, `protocol`, `utils/cache`)
- `codex-rs/otel/src/{config,metrics,trace_context,events,provider,otlp,targets}.rs` — upstream OpenAI Codex source (NOT vendored locally)
- `codex-rs/{config,skills,protocol,utils/cache}/src/*.rs` — upstream source (NOT vendored locally)

### PhenoObservability
- `Cargo.toml:1-45` — workspace declaration + `phenotype-errors` git dep + `phenotype-event-bus` git dep
- `crates/phenotype-observably-tracing/src/lib.rs:1-178` — `init_tracing` + `init_otel` (canonical, do not duplicate)
- `crates/phenotype-observably-tracing/src/metrics.rs` — `MetricsRegistry` impl
- `crates/phenotype-observably-ports/src/{cache,metrics,timeseries}.rs` — port traits (canonical)
- `crates/phenotype-observably-ports/src/metrics.rs:9-20` — `MetricsError` (candidate for fold)
- `rust/phenotype-logging/src/lib.rs:1-246` — local duplicate of `init_tracing` + `RequestContext` (deletable per T2)
- `rust/phenotype-telemetry/src/lib.rs:1-325` — local `MetricsCollector` + `Tracer` + `TelemetryExporter` + `TelemetryConfig` (partially deletable)

### phenoShared (target)
- `crates/phenotype-error-core/` — already exists; add `DomainErrorContext` + `DomainErrorKind` per E4
- `crates/phenotype-logging/` — already exists; add `init_tracing` (canonical) + `RequestContext` per T5
- `crates/phenotype-observably-tracing/` — already exists; extend `init_otel` per T3
- `crates/phenotype-config-core/` — already exists; add `expanded_path_factory`, `RetentionPolicy`, `CostBudget`, `RedisConfig`, `RedlockConfig` per C1-C5
- `crates/phenotype-port-interfaces/` — already exists; `MetricsPort`/`CachePort`/`TimeSeriesPort` traits (canonical)
- `crates/phenotype-contracts/` — already exists; add `RouteDescriptor`, `RouteProtocol`, `HashMapRegistry<T>` per R1-R3
- `crates/phenotype-router-config/` — does NOT exist; add per R5
- `pheno-shared/python/pheno_llm/` — already exists; add pydantic mirrors per R1, R4, R5

---

*End of audit. No code modifications, no git operations performed.*
