# Thegent Implementation Log
Date: 2026-02-14
Scope: Runtime output parsing hardening + model contract normalization

## Chunk 173 (Execution Start)

### Completed

- Added tolerant JSONL parsing in `src/thegent/output_parser.py` for richer assistant result extraction.
  - Added JSON-LD/SSE tolerant line handling (`data: ...` and JSON envelope variants).
  - Added recursive text coercion for list/dict content blocks.
  - Added fallback message extraction across `item`, `message`, `content`, and `result` payload shapes.
  - Preserved existing precedence by continuing to prefer `completion.finalText` when present.

- Added explicit model canonicalization helper in `src/thegent/models/catalog.py`.
  - Introduced `normalize_model_id()` for provider-agnostic alias normalization.
  - Routed model resolution now consistently uses normalization for route lookup.

### Notes

- Existing behavior is unchanged for known exact model IDs.
- This chunk is intentionally scoped to parser/contract-hardening and can be expanded with schema metadata (route version field) in a follow-up chunk.

## Chunk 174 (Routing Contract & Observability)

### Completed

- Added explicit route contract metadata in `src/thegent/models/catalog.py`.
  - Introduced `ROUTE_SCHEMA_VERSION` and `route_contract()`.
  - Added `ResolvedRoute` dataclass with schema-aware fields.
  - Added `resolve_route_contract()` returning `ResolvedRoute` for structured routing decisions.
  - Added `ModelCatalog.to_contract_view()` to expose contract-shaped route metadata.

- Exported contract helpers in `src/thegent/models/__init__.py` so tooling can consume them:
  - `ResolvedRoute`
  - `resolve_route_contract`
  - `route_contract`

### Notes

- Backwards compatibility preserved: legacy `resolve_route()` tuple contract remains unchanged.
- This chunk is explicitly additive and safe for staged rollout behind consumers that adopt contract views.

## Chunk 175 (Contract-Aware Model Listing Outputs)

### Completed

- Wired contract-aware listing through implementation layer in `src/thegent/cli_impl.py`.
  - Extended `list_models_impl()` to accept `include_contract`.
  - Added contract response shape that uses `ModelCatalog.to_contract_view()` and optional provider filtering.
- Exposed contract mode in CLI command UX in `src/thegent/main.py` and command renderer in `src/thegent/cli.py`.
  - Added `--include-contract` flag to `list-models`.
  - Added machine-readable JSON contract output when requested, including `schema_version`, `routes`, and `contract` fields.
- Exposed contract mode in MCP surfaces in `src/thegent/mcp_server.py`.
  - Updated `thegent://models` resource and `thegent_list_models` tool to accept `include_contract`.
  - Returned structured route metadata for automation workflows while preserving existing map mode by default.

### Notes

- Existing behavior and signatures remain backward-compatible in default mode (`include_contract=False`).
- This chunk prepares downstream tooling to consume stable routing contracts for validation, orchestration, and policy checks.

## Chunk 176 (Contract View Robustness and Cache-Aware Filtering)

### Completed

- Hardened `ModelCatalog.to_contract_view()` in `src/thegent/models/catalog.py`.
  - Added `use_scraped`, `provider_filter`, and `use_cache` controls.
  - Added route dedup merge support for scraped overlays via internal `_merge_routes`.
  - Added deterministic ordering and provider-filtered contract projection.
  - Preserved schema/version metadata while returning filtered contract payloads.
- Updated `src/thegent/cli_impl.py` contract path to use the hardened catalog contract view.
  - `list_models_impl(..., include_contract=True)` now respects `use_scraped` and `refresh` semantics.
- Updated CLI user-facing `include-contract` path in `src/thegent/cli.py`.
  - Added refresh propagation (`--refresh` now also refreshes contract data source in best-effort mode).

### Notes

- Default behavior remains unchanged unless `--include-contract` is provided.

## Chunk 177 (Route Resolution Probe API)

### Completed

- Added CLI command `resolve-model-route` with JSON contract output in:
  - `src/thegent/cli.py` (`resolve_model_route_cmd`)
  - `src/thegent/main.py` (`resolve-model-route` subcommand)
  - `src/thegent/mcp_server.py` (`thegent_resolve_model_route` tool)
- Implemented deterministic policy validation (`prefer_direct`, `prefer_proxy`, `failover`) and structured payload fields:
  - `model`, `normalized_model`, `policy`, `provider_hint`
  - `route_found`, `available_routes`, `resolved_route`, `schema_version`
- Added non-zero CLI exit behavior when no route matches provider hint to support orchestration guardrails.

### Notes

- This chunk improves route observability without changing default run/list behavior.

## Chunk 178 (Model Contract Schema Visibility)

### Completed

- Added CLI contract schema emitter in `src/thegent/cli.py` (`list_model_contract_schema_cmd`) and exposed via:
  - `thegent models contract` command in `src/thegent/main.py`.
  - `thegent://models/contract` MCP resource in `src/thegent/mcp_server.py`.
- This completes a lightweight introspection surface for version-aware orchestration clients.

## Chunk 179 (Contract Resolver Scrape Coverage)

### Completed

- Fixed `resolve_route_contract()` in `src/thegent/models/catalog.py` to resolve metadata from
  `ModelCatalog.routes_for(...)` (which includes scraped routes) instead of only the static catalog.
- This prevents false-negative `route_found` results when a route is valid only through freshly scraped providers.

## Chunk 180 (Shared Routing Policy Validation)

### Completed

- Added `normalize_route_policy()` in `src/thegent/models/catalog.py` to centralize routing policy validation.
- Exported it via `src/thegent/models/__init__.py`.
- Updated policy handling in:
  - `resolve_model_route_cmd` (`src/thegent/cli.py`)
  - `thegent_resolve_model_route` (`src/thegent/mcp_server.py`)
  to consume shared validation and keep error behavior consistent.

## Chunk 181 (Run-Path Contract Output)

### Completed

- Extended foreground run command options to emit route contract metadata via `--include-contract`:
  - `src/thegent/main.py` `run` command flag plumbing.
  - `src/thegent/cli.py` `run_cmd` route-trace output with attempt history and normalized route contract payload when requested.
- Added model routing contract emission on MCP synchronous run:
  - `src/thegent/mcp_server.py` `thegent_run` now accepts `include_contract` and appends `routing` contract context to ToolResult payload.

### Notes

- Contract fields are opt-in only when `include_contract=True` (CLI flag or MCP param) to preserve existing default CLI output behavior.
- This chunk intentionally scopes changes to sync run paths; background/session command surfaces can be hardened in a follow-up chunk.

## Chunk 182 (Background Contract Traceability)

### Completed

- Added background run contract persistence and MCP/CLI observability:
  - `src/thegent/cli.py` added `--include-contract` for `bg`, with run-time route metadata persisted into session meta (`route_contract`, `route_request`) when requested.
  - `src/thegent/cli_impl.py` `bg_impl` now accepts `include_contract`, `route_contract`, `route_request` and persists them into session metadata.
  - `src/thegent/main.py` `bg` command now exposes `--include-contract`.
- `src/thegent/mcp_server.py` `thegent_bg` now accepts `--include-contract`, resolves optional route metadata, stores it via `bg_impl`, and includes `routing` context in ToolResult.

### Notes

- Background path contract output remains opt-in and defaults to legacy minimal behavior when not enabled.
- Synchronous behavior remains unchanged unless `--include-contract`/`include_contract=True` is explicitly set.

## Chunk 183 (Status/Inspect Contract Surfacing)

### Completed

- Extended background session status payloads with optional route contract visibility:
  - `src/thegent/cli_impl.py`
    - Added `include_contract` parameter to `status_impl()` and `inspect_impl()`.
    - When requested, status payloads now include `route_contract` and `route_request` metadata from session files.
  - `src/thegent/cli.py`
    - Added `include_contract` support to `status_cmd()` and `inspect_cmd()`.
    - In non-JSON rich output, contract payloads are rendered alongside standard status fields.
  - `src/thegent/main.py`
    - Added `--include-contract` CLI options for `status` and `inspect` commands.
  - `src/thegent/mcp_server.py`
    - Added optional `include_contract` to `thegent_status` and `thegent_inspect` tools.

### Notes

- Contract metadata remains opt-in to avoid changing default status payload shape for existing consumers.

## Chunk 184 (Session List Contract Surfacing)

### Completed

- Added contract-aware session listing across CLI and MCP:
  - `src/thegent/cli_impl.py`
    - Extended `ps_impl()` with `include_contract: bool = False`.
    - Optionally includes `route_contract` and `route_request` in each session row from persisted meta.
  - `src/thegent/cli.py`
    - `ps_cmd()` now accepts `include_contract` and consumes `ps_impl(..., include_contract=...)`.
    - Added Markdown and Rich rendering paths for route metadata when available.
  - `src/thegent/main.py`
    - Added `--include-contract` flag to `ps` command.
- `src/thegent/mcp_server.py`
  - `thegent://sessions` resource now accepts `include_contract`.
  - `thegent_ps` tool now accepts `include_contract` and forwards it to `ps_impl`.

### Notes

- Session list contract visibility is opt-in to preserve existing list payload defaults.

## Chunk 185 (MCP Session Meta Contract Expansion)

### Completed

- Enabled contract fields in MCP session resources on demand:
  - `src/thegent/mcp_server.py`
    - Updated `thegent://sessions` resource to advertise optional `include_contract` query.
    - Updated `thegent://session/{id}/meta` resource to advertise optional `include_contract` and forward it through to `status_impl`.

### Notes

- Existing clients remain unaffected when `include_contract` is omitted (default false).

## Chunk 186 (Background Routing Policy Parity)

### Completed

- Added routing-failover parity for background launches:
  - `src/thegent/main.py`
    - `bg` command now accepts:
      - `--routing` (policy)
      - `--failover` (retry next route behavior)
  - `src/thegent/cli.py`
    - `bg_cmd()` now accepts/normalizes `routing` and `failover`.
    - Route metadata now records policy context (`policy`) and resolved agent in `route_request`.
    - Routing policy is propagated to spawned background `thegent.main run` invocation (`-R/--failover`) when provided.
  - `src/thegent/cli_impl.py`
    - `bg_impl()` now accepts `routing` and `failover` and propagates into command flags for child run process.
  - `src/thegent/mcp_server.py`
    - `thegent_bg` accepts `routing` and `failover`, resolves policy consistently, and passes normalized routing context into `bg_impl`.

### Notes

- Policy defaults and validation follow existing foreground run normalization semantics and remain opt-in via flags.

## Chunk 187 (Session Contract Audit Surface)

### Completed

- Added a dedicated session contract audit implementation in `src/thegent/cli_impl.py`:
  - New `list_session_contracts_impl()` computes per-session contract audit rows from persisted session metadata.
  - Rows include `route_request`, `route_contract`, `contract_state`, and `contract_issues` for fast gap detection.
  - New states: `complete`, `partial`, `request_only`, `contract_only`, `untracked`.

- Added CLI audit command in `src/thegent/cli.py` and `src/thegent/main.py`:
  - `session-contracts` command with:
    - `--all` owner scope handling
    - `--owner` filter
    - `--format` (`json`, `rich`, `md`)
    - `--missing-only` for incomplete/unsafe rows
  - Rich/MD/JSON outputs include audit summary counts and per-session issue fields.

- Added MCP exposure in `src/thegent/mcp_server.py`:
  - New `thegent_session_contracts` tool.
  - Optional `owner`, `all`, and `missing_only` arguments.
  - Returns rows plus summary counts for deterministic consumption by agents.

### Notes

- This chunk makes session-route observability queryable by tooling and easier to diagnose partial or missing route metadata states.

## Chunk 188 (Contract Audit API Maturation)

### Completed

- Added shared audit engine in `src/thegent/cli_impl.py`:
  - New `session_contract_audit_impl(owner, all, missing_only, summary_only)` returns consistent `{rows, summary}` payload.
  - `summary_only` mode now supports zero-row responses while preserving summary totals.
- Expanded CLI command `session-contracts` in `src/thegent/cli.py` and `src/thegent/main.py`:
  - Added `--summary-only` flag.
  - Fixed behavior so summary output is still shown when no rows are returned.
- Added MCP contract-audit resource in `src/thegent/mcp_server.py`:
  - New resource `thegent://sessions/contracts{?owner,all,missing_only,summary_only}`.
  - `thegent_session_contracts` now delegates to shared audit helper for consistent rows/summary.

### Notes

- This chunk makes contract quality checks both human-readable (CLI) and machine-queryable (MCP resource) via a single implementation path.

## Chunk 189 (Contract Audit Strict Health)

### Completed

- Hardened `session_contract_audit_impl()` with optional strict health checks in `src/thegent/cli_impl.py`:
  - Added strict alignment checks for provider/alias/agent contract consistency when request and contract metadata coexist.
  - Added `contract_health` and included `strict_checks_enabled` fields in row payloads.
  - Added health bucketed summary counters (`healthy`, `warning`, `error`, `missing`) and exposed strictness flag in summary.
- Extended session-contract CLI in `src/thegent/cli.py` and `src/thegent/main.py`:
  - New `--strict` toggle for alignment-sensitive validation.
  - Added health column/metrics output in `json`, `md`, and `rich` formats.
- Extended MCP API in `src/thegent/mcp_server.py`:
  - `thegent_session_contracts` tool now accepts `strict`.
  - `thegent://sessions/contracts{?owner,all,missing_only,summary_only,strict}` now supports strict-mode validation and returns expanded health summary.

### Notes

- This chunk adds practical observability hardening: it distinguishes metadata completeness from semantic contract alignment, enabling safer policy enforcement and cleaner triage.

## Chunk 190 (Contract Health Gate)

### Completed

- Added enforcement-oriented health gate in `src/thegent/cli_impl.py`:
  - New `session_contract_health_gate_impl(owner=None, all=False, strict=False, min_healthy_ratio=1.0)`.
  - Returns deterministic pass/fail payload with:
    - `pass` and `status`
    - normalized `threshold` and calculated `healthy_ratio`
    - `unhealthy_count`, `blocked_count`, `summary`, and capped `blocked_sessions` details.
  - Reuses existing contract audit engine so gating rules stay consistent.
- Added a new CLI entrypoint in `src/thegent/main.py`:
  - `session-contract-health-gate` command with `--min-healthy`, `--strict`, `--all`, `--owner`, `--format`.
  - Non-zero exit status (`2`) when gate fails for CI-friendly usage.
- Added MCP machine interface in `src/thegent/mcp_server.py`:
  - `thegent_session_contract_health_gate` tool.
  - `thegent://sessions/contracts/health{?owner,all,strict,min_healthy_ratio}` resource.

### Notes

- This chunk makes routing-contract quality actionable by converting observability into an automatable gate for automation and release checks.

## Chunk 191 (Contract Health Analytics Report)

### Completed

- Added `session_contract_health_report_impl(owner=None, all=False, strict=False, top_blocked=25)` in `src/thegent/cli_impl.py`:
  - Reports owner-level health breakdown and issue-taxonomy counts.
  - Returns `summary`, `health`, `issue_counts`, `issue_breakdown`, `owner_breakdown`, `top_blocked`, and `blocked_ratio` payload.
  - Preserves strict-mode signal and deterministic output ordering.
- Added CLI report command flow in `src/thegent/cli.py`:
  - Implemented `session_contract_health_report_cmd(...)`.
  - Added `session-contract-health-report` command in `src/thegent/main.py` with:
    - `--all`, `--owner`, `--format`, `--strict`, `--top-blocked`.
- Added MCP machine interfaces in `src/thegent/mcp_server.py`:
  - `thegent_session_contract_health_report` tool.
  - `thegent://sessions/contracts/report{?owner,all,strict,top_blocked}` resource.
- This chunk turns audit into triage-grade analytics suitable for dashboards and ownership-based remediation.

## Chunk 192 (Actionable Health Remediation Hints)

### Completed

- Added remediation metadata generation in `src/thegent/cli_impl.py`:
  - `session_contract_health_report_impl(...)` now includes per-session `remediation` hints in blocked entries.
  - Added deterministic issue-to-hint mapping for missing/partial/misaligned contract/request metadata.
- Extended report rendering in `src/thegent/cli.py`:
  - `session_contract_health_report_cmd(...)` now surfaces remediation hints in both markdown table and rich output for blocked sessions.
- Improves operational utility by converting issue diagnosis into direct corrective guidance.

## Chunk 193 (Health Report Export Artifacts)

### Completed

- Added report serialization helpers in `src/thegent/cli.py`:
  - `_serialize_health_report_md`, `_serialize_health_report_csv`, `_serialize_health_report_jsonl`.
  - Added export format inference from path and explicit `--export-format`.
- Extended `session_contract_health_report_cmd(...)`:
  - New `--output/-o` and `--export-format` parameters.
  - Supports writing artifacts in `json`, `md`, `csv`, or `jsonl`.
- Extended CLI subcommand in `src/thegent/main.py`:
  - `session-contract-health-report` now accepts artifact output options while retaining terminal render modes.

## Chunk 194 (Health Report Export Robustness)

### Completed

- Added guardrails for artifact export in `src/thegent/cli.py`:
  - `_write_report_export(...)` now validates `--export-format`/inferred format against supported set (`json`, `md`, `csv`, `jsonl`).
  - Export path handling now auto-creates parent directories.
  - Export fails fast with a clear error if the output path points to an existing directory.
- Export behavior remains explicit and deterministic:
  - Unsupported formats are rejected up-front via `typer.BadParameter` rather than failing silently.
  - Existing format inference and command UX are unchanged when supported values are used.
- This chunk improves practical reliability for CI and automation workflows that rely on deterministic artifact paths.

## Chunk 195 (Export UX Clarity)

### Completed

- Added explicit export format recognition helper in `src/thegent/cli.py`:
  - `_export_format_from_suffix(...)` for canonical extension-to-format mapping.
  - `_infer_export_format(...)` now delegates to this helper and remains deterministic.
- Improved artifact export UX in `src/thegent/cli.py`:
  - When `--output` has a recognized extension, that format is used unless `--export-format` is explicitly set.
  - When `--output` uses an unrecognized extension and no explicit `--export-format` is provided, the command warns and defaults to JSON.
- Updated CLI help text in `src/thegent/main.py`:
  - Clarifies extension-driven export behavior and explicit fallback defaults.
- This chunk improves operator confidence by preventing silent extension ambiguity while preserving backward-compatible default behavior.

## Chunk 196 (Safe, Intentional Artifact Write)

### Completed

- Added explicit overwrite control for report artifacts:
  - `src/thegent/main.py`:
    - added `--overwrite` for `session-contract-health-report`.
  - `src/thegent/cli.py`:
    - `session_contract_health_report_cmd(...)` now forwards `overwrite`.
    - `_write_report_export(...)` now rejects existing output paths unless overwrite is enabled.
- Made report export writes safer by using an atomic replacement strategy:
  - `src/thegent/cli.py` writes payload to a temporary file in the same directory before `Path.replace()` into target.
- This chunk reduces partial-artifact risk and accidental overwrite in automation/CI-style report generation.

## Chunk 197 (Deterministic Report Ordering & Metadata)

### Completed

- Added deterministic output shaping in `src/thegent/cli_impl.py`:
  - Sorts `issue_breakdown` deterministically by `(count desc, issue asc)`.
  - Normalizes `owner_breakdown` to stable alphabetical owner ordering.
  - Sorts `top_blocked` rows deterministically by `(health, owner, session_id)` before truncation.
  - Adds report generation metadata:
    - `generated_at_utc`
    - `generated_query` (`owner`, `all`, `strict`, `top_blocked`)
- Added export/terminal visibility for generation metadata in `src/thegent/cli.py`:
  - `generated_at_utc` and `generated_query` now surface in both markdown and rich rendering paths.
- This chunk improves replayability and auditability for large-scale policy/report pipelines.

## Chunk 198 (Health Gate Export Parity)

### Completed

- Added output artifact capabilities to `session-contract-health-gate` in `src/thegent/main.py`:
  - new `--output / -o`, `--export-format`, and `--overwrite` options.
- Extended `session_contract_health_gate_cmd(...)` in `src/thegent/cli.py` to:
  - write gate reports to path using explicit JSON/MD/CSV/JSONL serialization,
  - inherit extension-based format inference and explicit `--export-format`,
  - fail fast on unsupported formats / existing file unless `--overwrite` is set,
  - perform atomic temp-file replacement writes.
- Added dedicated health-gate serializers in `src/thegent/cli.py`:
  - `_serialize_health_gate_md`, `_serialize_health_gate_csv`, `_serialize_health_gate_jsonl`.
- Hardened gate payload in `src/thegent/cli_impl.py`:
  - `session_contract_health_gate_impl(...)` now includes `generated_at_utc` and `generated_query` for auditability.
- Added consistent markdown path for terminal rendering using `_serialize_health_gate_md(...)`.

## Chunk 199 (Schema-Aware Health Payload Artifacts)

### Completed

- Added cross-command health payload schema metadata in `src/thegent/cli_impl.py`:
  - Introduced `HEALTH_PAYLOAD_SCHEMA_VERSION`.
  - `session_contract_health_gate_impl(...)` and
    `session_contract_health_report_impl(...)` now include:
    - `schema_version`
    - `payload_type`
    - (already existing) generation metadata for replayability.
- Extended CLI serializers in `src/thegent/cli.py` to surface schema metadata:
  - Markdown serializers include `schema_version` and `payload_type`.
  - Rich output prints schema metadata for both report and gate.
- Extended JSONL/CSV health serializers with schema context for stronger downstream parsing:
  - `health report` JSONL emits both summary + blocked rows with schema metadata.
  - `health gate` CSV/JSONL now include `schema_version` and `payload_type` fields.
- This chunk improves machine compatibility and long-term contract evolution safety for artifact consumers.

## Chunk 200 (Schema Metadata in MCP Health Contract Tools)

### Completed

- Added schema-aware MCP tool metadata in `src/thegent/mcp_server.py`:
  - `thegent_session_contract_health_gate` now returns `schema_version` and `payload_type` in tool `meta`.
  - `thegent_session_contract_health_report` now returns `schema_version` and `payload_type` in tool `meta`.
- Clarified MCP resource docs for schema-aware outputs:
  - `thegent://sessions/contracts/health`
  - `thegent://sessions/contracts/report`
  - docstrings now explicitly note schema fields in responses.
- This chunk improves MCP client behavior by exposing payload contract versioning and type in transport metadata.

## Chunk 201 (Health Payload Determinism Hardening)

- Hardened health-gate blocker ordering in `src/thegent/cli_impl.py`:
  - `session_contract_health_gate_impl(...)` now sorts `blocked_sessions` deterministically by `(health, state, session_id)`.
  - This prevents nondeterministic ordering drift in CI and cache-sensitive automation when session metadata order varies.
- Added deterministic ordering polish to report payload maps in `session_contract_health_report_impl(...)`:
  - `issue_counts` now returns as a sorted key map for stable, predictable JSON key order.
  - Blocked-row sort key now includes `state` after `(health, owner)` for deterministic tie-breaking.
- These changes keep MCP and CLI health payloads replayable across environments while preserving existing fields and compatibility.

## Chunk 202 (Issue List Canonicalization)

- Standardized health issue ordering in `src/thegent/cli_impl.py`:
  - `session_contract_health_gate_impl(...)` now sorts each blocked session’s `issues` list lexicographically.
  - `session_contract_health_report_impl(...)` now sorts issue lists before attaching to blocked rows and generating remediation links.
- This reduces payload noise in GitOps/CI diffing when upstream issue-collection order changes without semantic change.

## Chunk 203 (MCP Health Payload Serialization Determinism)

- Added stable MCP serialization helper in `src/thegent/mcp_server.py`:
  - Introduced `_stable_json(...)` using `json.dumps(..., sort_keys=True)`.
- Applied deterministic serialization to health resources and tools:
  - `thegent://sessions/contracts/health`
  - `thegent://sessions/contracts/report`
  - `thegent_session_contract_health_gate`
  - `thegent_session_contract_health_report`
- This reduces byte-level flakiness for MCP automation that hashes or snapshots content.

## Chunk 204 (CLI Health JSON Canonicalization)

- Enforced stable JSON serialization for CLI health report/gate outputs and artifacts in `src/thegent/cli.py`:
  - `session_contract_health_gate_cmd(..., format="json")`
  - `session_contract_health_report_cmd(..., format="json")`
  - `_write_health_gate_export(...)`
  - `_write_report_export(...)`
- Switched these paths to `json.dumps(..., sort_keys=True)` so key ordering is deterministic across runs.
- This keeps terminal artifacts and saved files stable for snapshot testing, caching, and compliance diff workflows.

## Chunk 205 (Health Payload Signature)

- Added deterministic, transport-safe content signatures in `src/thegent/cli_impl.py`:
  - Added `_hash_health_payload(...)` and compute `payload_signature` for:
    - `session_contract_health_gate_impl(...)`
    - `session_contract_health_report_impl(...)`
  - Signature is hashed from a stable canonicalized payload projection.
- Surfaced payload signature in:
  - `thegent_session_contract_health_gate` and `thegent_session_contract_health_report` `ToolResult.meta`
  - CLI render paths (`_serialize_health_gate_md`, `_serialize_health_report_md`)
  - CLI rich output paths (gate/report)
- This adds integrity and change-traceability for downstream automation without requiring custom diff tooling.

## Chunk 206 (Signature Propagation to All Health Artifacts)

- Extended signature visibility to remaining health export formats in `src/thegent/cli.py`:
  - `health report` CSV now includes:
    - `payload_signature_algorithm`
    - `payload_signature_value`
  - `health gate` CSV now includes:
    - `payload_signature_algorithm`
    - `payload_signature_value`
  - `health report` JSONL now includes signature fields on both summary and blocked rows.
  - `health gate` JSONL already carried summary signature and now explicitly carries signature metadata per blocked row.
- This keeps artifact parity across every health output format for integrity tooling and reproducibility checks.

## Chunk 207 (JSONL Key-Order Canonicalization)

- Applied deterministic key ordering to health JSONL serializers in `src/thegent/cli.py`:
  - `_serialize_health_report_jsonl(...)`
  - `_serialize_health_gate_jsonl(...)`
- Both summary and blocked rows are now rendered with `json.dumps(..., sort_keys=True)`.
- This removes key-order nondeterminism at line level and improves diff stability for streaming/snapshot workflows.

## Chunk 208 (Health Report CSV Summary Row Parity)

- Added parity-oriented `health report` CSV shaping in `src/thegent/cli.py`:
  - `_serialize_health_report_csv(...)` now emits a deterministic summary row and blocked rows with explicit `record_type`.
  - Added common schema/signature context columns to every row:
    - `schema_version`, `payload_type`, `payload_signature_algorithm`, `payload_signature_value`
  - Summary row includes stable report-level counters and health aggregates.
- This aligns report CSV structure with gate CSV and improves parser simplicity for batch pipelines.

## Chunk 209 (Gate JSONL Context Completeness)

- Tightened `health gate` JSONL parity in `src/thegent/cli.py`:
  - `_serialize_health_gate_jsonl(...)` now writes explicit `payload_type` and `schema_version` on each blocked row.
  - This ensures each row is schema-self-describing in stream/line-based parsers, independent of row position.

## Chunk 210 (Report JSONL Blocked-Row Enrichment)

- Enhanced `health report` JSONL row consistency in `src/thegent/cli.py`:
  - `_serialize_health_report_jsonl(...)` now adds schema context and summary context to each blocked row:
    - `payload_type`, `schema_version`
    - `status`, `threshold`, `unhealthy_count`, `blocked_count`, `total`, `blocked_ratio`
    - `payload_signature_algorithm`, `payload_signature_value`
    - `generated_at_utc`, `generated_query`
- This makes each line independently parseable for row-level consumers without relying on preceding summary lines.

## Chunk 211 (Health Report CSV Query Metadata)

- Improved `health report` CSV auditability in `src/thegent/cli.py` by enriching `_serialize_health_report_csv(...)`:
  - Added generated-query metadata columns for every row:
    - `generated_at_utc`
    - `generated_query_owner`
    - `generated_query_all`
    - `generated_query_strict`
    - `generated_query_top_blocked`
  - Summary and blocked rows now preserve the same shared context schema for downstream row parsers.
- This increases deterministic discoverability of origin/query parameters directly from CSV exports.

## Chunk 212 (Health Report Status Parity)

- Standardized report payload terminal semantics by adding top-level `status` to
  `session_contract_health_report_impl(...)` in `src/thegent/cli_impl.py`:
  - `status` is now `"passed"` when `blocked_sessions == 0`, otherwise `"blocked"`.
  - `blocked_sessions` now uses an internal stable `blocked_count` for consistency.
- This removes conditional consumers from report serializers and aligns status treatment with gate-style contract outputs.

## Chunk 213 (Health Report Status Surfacing)

- Completed report output parity for the new report status in `src/thegent/cli.py`:
  - `_serialize_health_report_md(...)` now emits `status` in markdown artifacts.
  - `session_contract_health_report_cmd(..., format='rich')` now prints `status=...`
    before the rich body and report-level serializers use stable status access.
  - Report CSV paths now consume the canonical `result["status"]` directly.
- This keeps all health-report artifacts and terminal views consistent with the gate
  output contract and avoids status inference ambiguity.

## Chunk 214 (Canonical Count Parity for Health Report)

- Added canonical top-level count fields in `session_contract_health_report_impl(...)`
  (`src/thegent/cli_impl.py`):
  - `total` (explicit total session count for parity with blocked-row consumers)
  - `blocked_count` (explicit blocked count parallel to gate payload)
- Extended report output usage in `src/thegent/cli.py`:
  - JSONL blocked-row enrichment now always carries `total` and
    `top_blocked_count`.
  - Rich output prints both `blocked` and `blocked_count` explicitly.
- This improves downstream schema consistency and avoids reliance on inferred
  aliases when serializing report rows.

## Chunk 215 (Health Report CSV Blocked-Row Context Parity)

- Completed blocked-row parity for `_serialize_health_report_csv(...)` in
  `src/thegent/cli.py`:
  - blocked rows now carry full generated-query metadata columns:
    - `generated_query_owner`
    - `generated_query_all`
    - `generated_query_strict`
    - `generated_query_top_blocked`
  - blocked rows retain canonical summary context columns introduced in prior
    chunks (`total`, `total_sessions`, `blocked_count`, `blocked_sessions`,
    `top_blocked_count`, `blocked_ratio`, and health bucket counters).
- This makes each CSV row self-describing for line-by-line ingestion and keeps
  report CSV parity with JSONL context enrichment goals.

## Chunk 216 (Gate Canonical Count Fields & Serializer Parity)

- Added canonical top-level count aliases to `session_contract_health_gate_impl(...)` in `src/thegent/cli_impl.py`.
- Updated gate serializers and rich terminal rendering in `src/thegent/cli.py` to consume canonical count fields.

## Chunk 217 (Gate CSV Blocked-Row Query Context Parity)

- Completed blocked-row query-context parity for `_serialize_health_gate_csv(...)` in `src/thegent/cli.py`.
- Blocked rows now carry `owner`, `all`, `strict`, `min_healthy_ratio`.

## Chunk 218 (Full-Phase Health Contract Unification & Row-Level Context Parity)

- Unified health payload contract fields across `session_contract_health_gate_impl` and `session_contract_health_report_impl` in `src/thegent/cli_impl.py`:
  - Standardized on: `total_sessions`, `healthy_sessions`, `unhealthy_sessions`, `blocked_sessions_count`, `blocked_ratio`, `pass`, `status`, `strict_checks_enabled`.
- Updated all health serializers in `src/thegent/cli.py` (MD, CSV, JSONL) for both gate and report:
  - Enforced usage of unified fields for summary and blocked rows.
  - Achieved full context parity in JSONL blocked rows (added `generated_query` and exploded fields).
  - Standardized CSV headers and row alignment across gate and report.
- Updated MCP server docstrings in `src/thegent/mcp_server.py` to reflect the unified health contract.
- Outcome: Fully deterministic, row-self-describing health artifacts across all surfaces.

## Chunk 219 (Unified Run IDs & Baseline Telemetry)

- Implemented **Unified Run IDs** and **Baseline Telemetry** (Phase 1, WP-1008 & WP-0001):
  - Created `src/thegent/execution.py` with `RunMeta` and `RunRegistry` for tracking all executions (foreground and background).
  - Updated `run_impl` and `run_cmd` to generate and persist `run_id` and execution lifecycle events.
  - Added `thegent history` command to list execution history with status and duration.
  - Added `thegent history --events` to view raw telemetry events (start/finish) for auditability.
  - Background runs now correlate their parent launcher via `run_id` propagation.
- Outcome: Every thegent operation is now uniquely identifiable and traceable via a persistent run registry.

## Chunk 219 (Health Serializer Unit Tests)

- Added `tests/test_unit_health_serializers.py` with 13 unit tests for health gate and report
  serializers (CSV, JSONL, MD).
- Fixtures `_gate_fixture()` and `_report_fixture()` match impl contract shape.

## Chunk 220 (MCP Meta Contract & Testability)

- Extracted `get_server_meta_impl()` in `src/thegent/cli_impl.py`; added `HEALTH_PAYLOAD_TYPES`.
- `resource_meta` delegates to `get_server_meta_impl()`.
- Added `TestMCPMetaContract` in `tests/test_unit_mcp.py` for meta health-payload schema fields.

## Chunk 221 (Output Parser Unit Tests)

- Added `tests/test_unit_output_parser.py` with 13 unit tests for `extract_condensed()`:
  - Empty/whitespace input.
  - JSONL: message/assistant, SSE data: prefix, completion.finalText precedence,
    item envelope, top-level text.
  - Plain text: passthrough, trailing/leading noise stripping.
  - Think block removal, worker report preference, literal newline unescaping.
- Locks in Chunk 173 parsing behavior and prevents regressions.

## Chunk 222 (Output Parser Schema Metadata – Chunk 173 Follow-up)

- Added `OUTPUT_PARSER_SCHEMA_VERSION = "output-parser-v1"` in `src/thegent/output_parser.py`.
- Added `extract_condensed_structured(stdout)` returning `{"text": str, "schema_version": str}`
  for schema-aware consumers; `extract_condensed()` unchanged for backward compat.
- Added `TestExtractCondensedStructured` in `tests/test_unit_output_parser.py`.
- Completes Chunk 173 note: "can be expanded with schema metadata (route version field)".

## Chunk 223 (Extraction Schema in MCP Run Contract)

- When `thegent_run` is called with `include_contract=True` and `full=False`, the payload
  now includes `extraction_schema_version` (from `OUTPUT_PARSER_SCHEMA_VERSION`).
- Enables schema-aware consumers to know which parser version produced the condensed stdout.

## Chunk 224 (Output Parser Schema in MCP Meta)

- Added `output_parser_schema_version` to `get_server_meta_impl()` (thegent://meta resource).
- Meta now exposes both health and output-parser schema versions for discovery.

## Chunk 225 (Full Phase: Schema Discovery Consolidation)

- **meta consolidation**: `get_server_meta_impl()` now includes `route_schema_version` (from
  `models/catalog.py`). thegent://meta is the single discovery endpoint for all contract schema
  versions: health, output parser, and model routing.
- **impl**: `cli_impl.py` imports `ROUTE_SCHEMA_VERSION` from `thegent.models.catalog`.
- **tests**: `TestMCPMetaContract` asserts `route_schema_version == 1`. `TestRouteContract` in
  `test_unit_models.py` asserts `route_contract()` returns `schema_version`, `backend_types`, and
  `policy_names`.
- **outcome**: Full-phase schema discovery for model contract normalization scope.

## Chunk 226 (Full Phase: Health CLI E2E Tests)

- Added E2E tests for `session-contract-health-gate` and `session-contract-health-report` in
  `tests/test_e2e_cli.py`:
  - `TestSessionContractHealthGate`: exits 0 with empty sessions, --format json has schema,
    --output writes artifact with --overwrite.
  - `TestSessionContractHealthReport`: exits 0 with empty sessions, --format json has schema.
- Tests use `THGENT_SESSION_DIR` pointing to empty tmp_path for deterministic empty-state.
- Fixed report payload: added `blocked_sessions` (count alias) to
  `session_contract_health_report_impl` for CLI rich output compatibility.

## Chunk 227 (Full Phase: Model Contract CLI E2E & Import Fixes)

- **E2E tests**: Added model contract CLI E2E tests in `tests/test_e2e_cli.py`:
  - `TestResolveModelRoute`: resolve-model-route exits 0 for known model, output has route; exits 1 for unknown.
  - `TestListModels`: list-models exits 0, output contains gemini.
  - `TestModelsContract`: models contract exits 0, output has schema_version.
- **Import fix**: Implemented `history_cmd` in `src/thegent/cli.py` (was imported from main but missing).
  - Calls `history_impl`, renders JSON/MD/rich table for run registry history.
- **API fix**: Added `run_id` parameter to `run_cmd()` signature for registry correlation (main.py was passing it).

## Chunk 228 (Full Phase: Session & Background CLI E2E Tests)

- **E2E tests**: Added session and background CLI E2E tests in `tests/test_e2e_cli.py`:
  - `TestHistory`: history exits 0 with empty registry; --format json exits 0.
  - `TestPs`: ps exits 0 with empty sessions; --format json exits 0.
  - `TestSessionContracts`: session-contracts exits 0 when no sessions match.
  - `TestStatusLogsWaitStop`: status, logs, wait, stop with unknown session_id exit 2 with "Session not found".
  - `TestInspect`: inspect --owner when no sessions exits 0 with "No sessions found".
- Tests use `THGENT_SESSION_DIR` pointing to empty tmp_path for deterministic empty-state.
- Hardens session/bg command surfaces per Chunk 139 follow-up note.

## Chunk 229 (Full Phase: DAG, Health Trend & Policy Profile E2E Tests)

- **E2E tests**: Added DAG, health trend, and policy profile CLI E2E tests in `tests/test_e2e_cli.py`:
  - `TestDagList`: dag list no DAG exits 1; empty DAG exits 0 with "No tasks"; ambiguous cwd exits 1.
  - `TestDagValidate`: dag validate no DAG exits 2; valid empty DAG exits 0 with "DAG valid".
  - `TestSessionContractHealthTrend`: session-contract-health-trend exits 0 with empty snapshots; --format json has schema.
  - `TestPolicyProfile`: gate --policy-profile strict_ci and report --policy-profile warn_only exit 0.
- Tests use tmp_path with .factory/dag-session.md and THGENT_SESSION_DIR/THGENT_HEALTH_SNAPSHOT_PATH for deterministic state.

## Chunk 230 (Full Phase: Models Refresh, DAG Status/Ready/Sync, List-Models Contract E2E)

- **E2E tests**: Added models refresh, DAG status/ready/sync, and list-models contract E2E tests in `tests/test_e2e_cli.py`:
  - `TestModelsRefresh`: models refresh exits 0, output mentions cache.
  - `TestDagStatusReadySync`: dag status/ready/sync no DAG exit 1; empty DAG exit 0 with expected messages.
  - `TestListModelsIncludeContract`: list-models --include-contract exits 0, JSON has schema_version and routes/contract.
- Tests use tmp_path with .factory/dag-session.md for DAG commands.

## Chunk 231 (Full Phase: Resolve-Model-Route Policy, No-Worse-Than-Baseline, DAG Add E2E)

- **E2E tests**: Added resolve-model-route policy variants, no-worse-than-baseline, and dag add E2E tests in `tests/test_e2e_cli.py`:
  - `TestResolveModelRoutePolicy`: resolve-model-route --policy prefer_proxy and failover exit 0 with route/available_routes.
  - `TestNoWorseThanBaseline`: gate and report with --no-worse-than-baseline and empty baseline exit 0.
  - `TestDagAdd`: dag add creates task, dag list shows it; dag add duplicate exits 1 with "already exists".
- Tests use tmp_path and THGENT_HEALTH_SNAPSHOT_PATH for deterministic state.

## Chunk 232 (Full Phase: DAG Remove, Update, Cancel & List Format E2E)

- **E2E tests**: Added dag remove, update, cancel, and list format E2E tests in `tests/test_e2e_cli.py`:
  - `TestDagRemoveUpdateCancel`: dag remove removes task and list shows No tasks; remove nonexistent exits 1; dag update --status done and dag cancel update task, list reflects status.
  - `TestDagListFormat`: dag list --format md outputs markdown table with task.
- Tests use tmp_path with .factory/dag-session.md for deterministic DAG state.

## Chunk 233 (Full Phase: Session-Contracts JSON, Invalid Policy, DAG Validation E2E)

- **E2E tests**: Added session-contracts format, resolve invalid policy, and dag validation E2E tests in `tests/test_e2e_cli.py`:
  - `TestSessionContractsFormat`: session-contracts --format json exits 0.
  - `TestResolveModelRouteInvalidPolicy`: resolve-model-route with invalid --policy exits 1.
  - `TestDagValidationErrors`: dag add with invalid --depends-on exits 2; dag update with invalid --status exits 2.
- Tests use tmp_path and THGENT_SESSION_DIR for deterministic state.

## Chunk 234 (Full Phase: DAG Run Dry-Run, List-Models By-Model, Resolve Provider E2E)

- **E2E tests**: Added dag run dry-run, list-models by-model, and resolve provider E2E tests in `tests/test_e2e_cli.py`:
  - `TestDagRunDryRun`: dag run --dry-run with no ready tasks exits 0; with ready task shows "Would run".
  - `TestListModelsByModel`: list-models --by-model exits 0.
  - `TestResolveModelRouteProvider`: resolve-model-route with --provider gemini exits 0 with resolved route.
- Tests use tmp_path with .factory/dag-session.md for DAG commands.

## Chunk 235 (Full Phase: DAG Add Depends-On, DAG Ready Deps, List-Models Provider E2E)

- **E2E tests**: Added dag add depends-on, dag ready with deps, and list-models provider E2E tests in `tests/test_e2e_cli.py`:
  - `TestDagAddDependsOn`: dag add T2 with --depends-on T1; both T1 and T2 appear in dag list.
  - `TestDagReadyWithDeps`: when T2 depends on T1 (both pending), only T1 is ready; when T1 is done, T2 becomes ready.
  - `TestListModelsProvider`: list-models gemini exits 0.
- Tests use tmp_path with .factory/dag-session.md for deterministic DAG state.

## Chunk 236 (Full Phase: DAG Validate Invalid, Session-Contracts Options, Help E2E)

- **E2E tests**: Added dag validate invalid, session-contracts options, and help E2E tests in `tests/test_e2e_cli.py`:
  - `TestDagValidateInvalid`: dag validate with unknown agent exits 2; with cycle (T1→T2→T1) exits 2.
  - `TestSessionContractsOptions`: session-contracts --missing-only and --summary-only exit 0.
  - `TestHelp`: thegent --help and dag --help exit 0.
- **API fix**: Added `confidence` and `arbitration` parameters to `run_cmd()` for main.py compatibility.
- Tests use tmp_path and THGENT_SESSION_DIR for deterministic state.

## Chunk 237 (Full Phase: History Limit, Session-Contracts Strict, Ps All, Health Trend Payload E2E)

- **E2E tests**: Added history limit, session-contracts strict, ps all, and health trend payload-type E2E tests in `tests/test_e2e_cli.py`:
  - `TestHistoryLimit`: history --limit 5 exits 0.
  - `TestSessionContractsStrict`: session-contracts --strict exits 0.
  - `TestPsAll`: ps --all exits 0 with empty sessions.
  - `TestHealthTrendPayloadType`: session-contract-health-trend --payload-type session_contract_health_gate exits 0.
- Tests use tmp_path and THGENT_SESSION_DIR/THGENT_HEALTH_SNAPSHOT_PATH for deterministic state.

## Chunk 238 (Full Phase: Status Format, Dag Run Task, Regression Tolerance, Models Help E2E)

- **E2E tests**: Added status format, dag run --task, regression-tolerance, and models help E2E tests in `tests/test_e2e_cli.py`:
  - `TestStatusFormat`: status unknown_session --format json and --include-contract exit 2 (Session not found).
  - `TestDagRunDryRunWithTask`: dag run --dry-run --task T1 with T1 ready exits 0 and shows Would run; --task T2 when T2 depends on pending T1 exits 1 (not ready).
  - `TestRegressionTolerance`: session-contract-health-gate and session-contract-health-report with --regression-tolerance exit 0.
  - `TestModelsHelp`: models --help exits 0.
- Tests use tmp_path and THGENT_SESSION_DIR for deterministic state.

## Chunk 239 (Full Phase: Dag Checkpoint, Checkpoints, Recover, Probe, Rollback, Report Output E2E)

- **E2E tests**: Added dag checkpoint lifecycle and report output E2E tests in `tests/test_e2e_cli.py`:
  - `TestDagCheckpoint`: dag checkpoint exits 0 and creates checkpoint; dag checkpoints exits 0; dag recover retry-failed exits 0; dag probe exits 0; dag rollback with unknown checkpoint_id exits 1.
  - `TestReportOutput`: session-contract-health-report --output writes artifact with --overwrite.
- Tests use tmp_path, THGENT_SESSION_DIR, and .factory/dag-session.md for deterministic state.

## Chunk 240 (Full Phase: Dag Recover Actions, Dag Format, MCP Help, Inspect Format E2E)

- **E2E tests**: Added dag recover actions, dag format options, mcp help, and inspect format E2E tests in `tests/test_e2e_cli.py`:
  - `TestDagRecoverActions`: dag recover clear-stuck and reset-retries exit 0.
  - `TestDagFormatOptions`: dag status --format md and dag ready --format md exit 0.
  - `TestMcpHelp`: mcp --help exits 0.
  - `TestInspectFormat`: inspect --owner --format json with no sessions exits 0.
- Tests use tmp_path and THGENT_SESSION_DIR for deterministic state.

## Chunk 241 (Full Phase: Login/Serve Help, Dag Probe Baseline, Health Trend Report, Gate Export E2E)

- **E2E tests**: Added login/serve help, dag probe baseline-id, health trend report payload, and gate export-format E2E tests in `tests/test_e2e_cli.py`:
  - `TestLoginServeHelp`: login --help and serve --help exit 0.
  - `TestDagProbeBaselineId`: dag probe --baseline-id unknown exits 1.
  - `TestHealthTrendReportPayload`: session-contract-health-trend --payload-type session_contract_health_report exits 0.
  - `TestGateExportFormat`: session-contract-health-gate --output with --export-format md writes markdown file.
- Tests use tmp_path, THGENT_SESSION_DIR, and THGENT_HEALTH_SNAPSHOT_PATH for deterministic state.

## Chunk 242 (Full Phase: History Verify, Policy Show, Cliproxy/MCP Help, Report Export E2E)

- **E2E tests**: Added history verify, policy show, cliproxy/mcp install help, and report export E2E tests in `tests/test_e2e_cli.py`:
  - `TestHistoryVerify`: history verify and history verify --format json exit 0.
  - `TestPolicyShow`: policy show exits 0.
  - `TestCliproxyHelp`: cliproxy --help exits 0.
  - `TestMcpInstallHelp`: mcp install --help exits 0.
  - `TestReportExportOptions`: session-contract-health-report --export-format csv writes file; --top-blocked 10 exits 0.
- **API fix**: Auditor.verify_registry() now returns `issues: []` for empty registry; audit_verify_cmd handles status "empty" without KeyError.
- Tests use tmp_path and THGENT_SESSION_DIR for deterministic state.

## Chunk 243 (Full Phase: Cockpit, History Events/List, Stop Options, MCP Service Help E2E)

- **E2E tests**: Added cockpit, history events/list, stop options, and mcp service help E2E tests in `tests/test_e2e_cli.py`:
  - `TestCockpit`: cockpit exits 0 with empty sessions.
  - `TestHistoryEventsList`: history events and history list exit 0.
  - `TestStopOptions`: stop --force and stop --wind-down with unknown session exit 2.
  - `TestMcpServiceHelp`: mcp service --help exits 0.
- Tests use tmp_path and THGENT_SESSION_DIR for deterministic state.

## Chunk 244 (Full Phase: Logs/Wait Options, Health Trend Output, Ps Format, Inspect Tail E2E)

- **E2E tests**: Added logs/wait options, health trend output/limit, ps format, and inspect tail E2E tests in `tests/test_e2e_cli.py`:
  - `TestLogsWaitOptions`: logs --tail and wait --timeout with unknown session exit 2.
  - `TestHealthTrendOutput`: session-contract-health-trend --output writes file; --limit 5 exits 0.
  - `TestPsFormat`: ps --format json exits 0.
  - `TestInspectTail`: inspect --owner --tail 20 with no sessions exits 0.
- Tests use tmp_path, THGENT_SESSION_DIR, and THGENT_HEALTH_SNAPSHOT_PATH for deterministic state.

## Chunk 245 (Full Phase: Dag Run Options, History Events Run-Id, Health Trend Format, Policy Help E2E)

- **E2E tests**: Added dag run options, history events run-id, health trend format, and policy help E2E tests in `tests/test_e2e_cli.py`:
  - `TestDagRunOptions`: dag run --dry-run --max-parallel 2 and --lane standard exit 0.
  - `TestHistoryEventsRunId`: history events --run-id exits 0.
  - `TestHealthTrendFormat`: session-contract-health-trend --format json exits 0 with snapshots/trend_payload_type.
  - `TestPolicyHelp`: policy --help exits 0.
- Tests use tmp_path, THGENT_SESSION_DIR, and THGENT_HEALTH_SNAPSHOT_PATH for deterministic state.

## Chunk 246 (Full Phase: Feedback, History Help, Inspect Stderr, Stop Grace, Logs Stderr E2E)

- **E2E tests**: Added feedback, history help, inspect stderr, stop grace, and logs stderr E2E tests in `tests/test_e2e_cli.py`:
  - `TestFeedback`: feedback run_id score --note exits 0; feedback --help exits 0.
  - `TestHistoryHelp`: history --help exits 0.
  - `TestInspectStderr`: inspect --owner --stderr with no sessions exits 0.
  - `TestStopGrace`: stop --grace 10 unknown_session exits 2.
  - `TestLogsStderr`: logs session_id --stderr with unknown session exits 2.
- Tests use tmp_path and THGENT_SESSION_DIR for deterministic state.

## Chunk 247 (Full Phase: Run/Bg Help, List-Agents Help, Health Trend All, Session-Contracts All, Gate Jsonl E2E)

- **E2E tests**: Added run/bg help, list-agents help, health trend --all, session-contracts --all, and gate jsonl E2E tests in `tests/test_e2e_cli.py`:
  - `TestRunBgHelp`: run --help and bg --help exit 0.
  - `TestListAgentsHelp`: list-agents --help exits 0.
  - `TestHealthTrendAll`: session-contract-health-trend --all exits 0.
  - `TestSessionContractsAll`: session-contracts --all exits 0.
  - `TestGateExportJsonl`: session-contract-health-gate --output with --export-format jsonl writes file.
- Tests use tmp_path, THGENT_SESSION_DIR, and THGENT_HEALTH_SNAPSHOT_PATH for deterministic state.

## Chunk 248 (Full Phase: List-Models/Droids Help, Cliproxy Ensure-Config, Resolve Help, Gate Min-Healthy, Trend Owner E2E)

- **E2E tests**: Added list-models/droids help, cliproxy ensure-config, resolve-model-route help, gate min-healthy, and health trend owner E2E tests in `tests/test_e2e_cli.py`:
  - `TestListModelsDroidsHelp`: list-models --help and list-droids --help exit 0.
  - `TestCliproxyEnsureConfig`: cliproxy ensure-config exits 0.
  - `TestResolveModelRouteHelp`: resolve-model-route --help exits 0.
  - `TestGateMinHealthy`: session-contract-health-gate --min-healthy 0.9 exits 0.
  - `TestHealthTrendOwner`: session-contract-health-trend --owner exits 0.
- Tests use tmp_path, THGENT_SESSION_DIR, THGENT_HEALTH_SNAPSHOT_PATH, and HOME for deterministic state.

## Chunk 249 (Full Phase: Dag Reconcile, Dag Add/Validate Help, Report Format Md, Inspect Include-Contract E2E)

- **E2E tests**: Added dag reconcile, dag add/validate help, report format md, and inspect include-contract E2E tests in `tests/test_e2e_cli.py`:
  - `TestDagReconcile`: dag reconcile exits 0 with valid DAG.
  - `TestDagAddValidateHelp`: dag add --help and dag validate --help exit 0.
  - `TestReportFormatMd`: session-contract-health-report --format md exits 0.
  - `TestInspectIncludeContract`: inspect --owner --include-contract with no sessions exits 0.
- Tests use tmp_path and THGENT_SESSION_DIR for deterministic state.

## Chunk 250 (Full Phase: Archive, Benchmark, History List Format Md, Gate Format Rich E2E)

- **E2E tests**: Added archive, benchmark, history list format md, and gate format rich E2E tests in `tests/test_e2e_cli.py`:
  - `TestArchiveBenchmark`: archive and archive --help exit 0; benchmark and benchmark --help exit 0.
  - `TestHistoryListFormatMd`: history list --format md exits 0.
  - `TestGateFormatRich`: session-contract-health-gate --format rich exits 0.
- Tests use tmp_path and THGENT_SESSION_DIR for deterministic state.

## Chunk 251 (Full Phase: Gate/Report Owner, Dag Remove/Update/Cancel Help, Ps Include-Contract E2E)

- **E2E tests**: Added gate/report --owner, dag remove/update/cancel help, and ps include-contract E2E tests in `tests/test_e2e_cli.py`:
  - `TestGateReportOwner`: session-contract-health-gate --owner and session-contract-health-report --owner exit 0.
  - `TestDagRemoveUpdateCancelHelp`: dag remove --help, dag update --help, and dag cancel --help exit 0.
  - `TestPsIncludeContract`: ps --include-contract exits 0 with empty sessions.
- Tests use tmp_path and THGENT_SESSION_DIR for deterministic state.

## Chunk 252 (Full Phase: Dag Sync/List/Run Help, Health Trend Format Md, Policy-Profile E2E)

- **E2E tests**: Added dag sync/list/run help, health trend format md, and health trend policy-profile E2E tests in `tests/test_e2e_cli.py`:
  - `TestDagSyncListRunHelp`: dag sync --help, dag list --help, and dag run --help exit 0.
  - `TestHealthTrendFormatMd`: session-contract-health-trend --format md exits 0.
  - `TestHealthTrendPolicyProfile`: session-contract-health-trend --policy-profile strict_ci exits 0.
- Tests use tmp_path, THGENT_SESSION_DIR, and THGENT_HEALTH_SNAPSHOT_PATH for deterministic state.

## Chunk 253 (Full Phase: Dag Checkpoint/Rollback/Recover/Probe/Checkpoints Help, Gate All/Strict E2E)

- **E2E tests**: Added dag checkpoint/rollback/recover/probe/checkpoints help and gate all/strict E2E tests in `tests/test_e2e_cli.py`:
  - `TestDagCheckpointRollbackRecoverProbeCheckpointsHelp`: dag checkpoint --help, dag rollback --help, dag recover --help, dag probe --help, and dag checkpoints --help exit 0.
  - `TestGateAllStrict`: session-contract-health-gate --all and --strict exit 0.
- Tests use tmp_path and THGENT_SESSION_DIR for deterministic state.

## Chunk 254 (Full Phase: Session-Contracts Owner/Format Md, Report All/Strict, Health Trend Strict/Top-Blocked E2E)

- **E2E tests**: Added session-contracts owner/format md, report all/strict, and health trend strict/top-blocked E2E tests in `tests/test_e2e_cli.py`:
  - `TestSessionContractsOwnerFormatMd`: session-contracts --owner and --format md exit 0.
  - `TestReportAllStrict`: session-contract-health-report --all and --strict exit 0.
  - `TestHealthTrendStrictTopBlocked`: session-contract-health-trend --strict and --top-blocked 15 exit 0.
- Tests use tmp_path, THGENT_SESSION_DIR, and THGENT_HEALTH_SNAPSHOT_PATH for deterministic state.

## Chunk 255 (Full Phase: History Events Format, Ps Format Md/Owner, Status/Logs/Wait/Stop Help E2E)

- **E2E tests**: Added history events format, ps format md/owner, and status/logs/wait/stop help E2E tests in `tests/test_e2e_cli.py`:
  - `TestHistoryEventsFormat`: history events --format json and --format md exit 0.
  - `TestPsFormatMdOwner`: ps --format md and ps --owner exit 0.
  - `TestStatusLogsWaitStopHelp`: status --help, logs --help, wait --help, and stop --help exit 0.
- Tests use tmp_path and THGENT_SESSION_DIR for deterministic state.

## Chunk 256 (Full Phase: Inspect Help, Session-Contracts/Gate/Report/Trend Help, Dag Status/Ready Help E2E)

- **E2E tests**: Added inspect help, session-contracts/gate/report/trend help, and dag status/ready help E2E tests in `tests/test_e2e_cli.py`:
  - `TestInspectHelp`: inspect --help exits 0.
  - `TestSessionContractsGateReportTrendHelp`: session-contracts --help, session-contract-health-gate --help, session-contract-health-report --help, and session-contract-health-trend --help exit 0.
  - `TestDagStatusReadyHelp`: dag status --help and dag ready --help exit 0.

## Chunk 257 (Full Phase: Operations, Closure-Pack, Ps/Cockpit Help E2E)

- **E2E tests**: Added operations, closure-pack, and ps/cockpit help E2E tests in `tests/test_e2e_cli.py`:
  - `TestOperations`: operations exits 0; operations --help exits 0; operations --format json exits 0 (output contains orchestrate/govern); operations --operation orchestrate exits 0.
  - `TestClosurePack`: closure-pack exits 0 with valid DAG (tmp_path project, .factory/dag-session.md, THGENT_SESSION_DIR); closure-pack --help exits 0.
  - `TestPsCockpitHelp`: ps --help and cockpit --help exit 0.

## Chunk 258 (Full Phase: MCP Up/Down Help, Models Subcommand Help E2E)

- **E2E tests**: Added mcp up/down help and models subcommand help E2E tests in `tests/test_e2e_cli.py`:
  - `TestMcpUpDownHelp`: mcp up --help and mcp down --help exit 0.
  - `TestModelsSubcommandHelp`: models refresh --help and models contract --help exit 0.

## Chunk 259 (Full Phase: Typer App Help, History/Policy/Cliproxy Help E2E)

- **E2E tests**: Added typer app help and history/policy/cliproxy subcommand help E2E tests in `tests/test_e2e_cli.py`:
  - `TestTyperAppHelp`: orchestrate --help, govern --help, recover --help, observe --help, and plan --help exit 0.
  - `TestHistoryPolicyCliproxyHelp`: history list --help, history events --help, history verify --help, policy show --help, and cliproxy login --help exit 0.

## Chunk 260 (Full Phase: Cliproxy Ensure-Config Help, Typer Alias Help E2E)

- **E2E tests**: Added cliproxy ensure-config help and typer alias path help E2E tests in `tests/test_e2e_cli.py`:
  - `TestCliproxyEnsureConfigHelp`: cliproxy ensure-config --help exits 0.
  - `TestTyperAliasHelp`: orchestrate run --help, orchestrate ps --help, govern verify --help, observe cockpit --help, observe archive --help, and observe benchmark --help exit 0.

## Chunk 261 (Full Phase: Recover, Plan, Govern Alias Help E2E)

- **E2E tests**: Added recover, plan, and govern alias path help E2E tests in `tests/test_e2e_cli.py`:
  - `TestRecoverPlanGovernAliasHelp`: recover reconcile --help, plan list --help, plan validate --help, plan run --help, govern closure-pack --help, and govern show-policy --help exit 0.

## Chunk 262 (Full Phase: Orchestrate, Recover, Observe Remaining Help E2E)

- **E2E tests**: Added remaining orchestrate, recover, and observe alias help E2E tests in `tests/test_e2e_cli.py`:
  - `TestOrchestrateRecoverObserveRemainingHelp`: orchestrate bg/inspect/logs/wait/stop --help, recover stop --help, observe status/logs/wait/inspect/history --help exit 0.

## Chunk 263 (Full Phase: Plan Sync/Checkpoint Help, Operations Filters E2E)

- **E2E tests**: Added plan sync/checkpoint help and operations --operation filter E2E tests in `tests/test_e2e_cli.py`:
  - `TestPlanSyncCheckpointAndOperationsFilters`: plan sync --help, plan checkpoint --help, and operations --operation govern/recover/observe/plan exit 0.

## Chunk 264 (Full Phase: Operations Invalid, Closure-Pack No DAG E2E)

- **E2E tests**: Added error-path E2E tests in `tests/test_e2e_cli.py`:
  - `TestOperationsInvalidAndClosurePackNoDag`: operations --operation invalid_name exits 1 with "Unknown operation"; closure-pack with project lacking .factory/dag-session.md exits 1 with "DAG not found".

## Chunk 265 (Full Phase: History-Legacy E2E)

- **E2E tests**: Added hidden history-legacy command E2E tests in `tests/test_e2e_cli.py`:
  - `TestHistoryLegacy`: history-legacy --help, history-legacy with empty registry (--limit 5), and history-legacy --format json exit 0.

## Chunk 266 (Full Phase: Govern Remaining Alias Help E2E)

- **E2E tests**: Added remaining govern alias path help E2E tests in `tests/test_e2e_cli.py`:
  - `TestGovernRemainingAliasHelp`: govern contracts --help, govern session-contracts --help, govern health-gate --help, govern health-report --help, govern health-trend --help, and govern feedback --help exit 0.

## Chunk 267 (Full Phase: Govern Contracts Execution E2E)

- **E2E tests**: Added govern contracts (contract registry) execution E2E tests in `tests/test_e2e_cli.py`:
  - `TestGovernContractsExecution`: govern contracts exits 0 and shows registry; govern contracts --format json exits 0 with array-like output.

## Chunk 268 (Full Phase: Observe, Plan Alias Execution E2E)

- **E2E tests**: Added observe and plan alias execution E2E tests in `tests/test_e2e_cli.py`:
  - `TestObservePlanAliasExecution`: observe history exits 0 (alias for history list); plan list with empty DAG exits 0 (alias for dag list).

## Chunk 269 (Full Phase: Recover, Plan Alias Execution E2E)

- **E2E tests**: Added recover and plan alias execution E2E tests in `tests/test_e2e_cli.py`:
  - `TestRecoverPlanAliasExecution`: recover reconcile exits 0 with valid DAG; plan validate exits 0 with valid empty DAG; plan sync exits 0 with empty DAG; plan checkpoint exits 0 with DAG (THGENT_SESSION_DIR).

## Chunk 270 (Full Phase: Plan Run Dry-Run E2E)

- **E2E tests**: Added plan run --dry-run E2E tests in `tests/test_e2e_cli.py`:
  - `TestPlanRunDryRun`: plan run --dry-run with no ready tasks exits 0; plan run --dry-run with ready task exits 0 and shows "Would run" or T1.

## Chunk 271 (Full Phase: Observe Drift, Trend, Probe Help E2E)

- **E2E tests**: Added observe drift/trend/probe help E2E tests in `tests/test_e2e_cli.py`:
  - `TestObserveDriftTrendProbeHelp`: observe drift --help, observe trend --help, and observe probe --help exit 0.

## Chunk 272 (Full Phase: Govern Conformance, Migration Help E2E)

- **E2E tests**: Added govern conformance and migration help E2E tests in `tests/test_e2e_cli.py`:
  - `TestGovernConformanceMigrationHelp`: govern conformance --help and govern migration --help exit 0.

## Chunk 273 (Full Phase: Observe Drift, Trend Execution E2E)

- **E2E tests**: Added observe drift and observe trend execution E2E tests in `tests/test_e2e_cli.py`:
  - `TestObserveDriftTrendExecution`: observe drift exits 0 with empty session dir; observe trend exits 0 with empty snapshots (alias for session-contract-health-trend).

## Chunk 274 (Full Phase: Plan Ready, Status, Checkpoints Execution E2E)

- **E2E tests**: Added plan ready, status, and checkpoints execution E2E tests in `tests/test_e2e_cli.py`:
  - `TestPlanReadyStatusCheckpointsExecution`: plan ready exits 0 with empty DAG; plan status exits 0 with empty DAG; plan checkpoints exits 0 (THGENT_SESSION_DIR).

## Chunk 275 (Full Phase: Plan Probe, Observe Probe Execution E2E)

- **E2E tests**: Added plan probe and observe probe execution E2E tests in `tests/test_e2e_cli.py`:
  - `TestPlanObserveProbeExecution`: plan probe exits 0 with DAG; observe probe exits 0 with DAG (aliases for dag probe).

## Chunk 276 (Full Phase: Recover/Plan Rollback, Plan Mutate Help E2E)

- **E2E tests**: Added recover/plan rollback and plan mutate help E2E tests in `tests/test_e2e_cli.py`:
  - `TestRecoverPlanRollbackAndPlanMutateHelp`: recover rollback --help, plan rollback --help, plan add --help, plan remove --help, plan update --help, and plan cancel --help exit 0.

## Chunk 277 (Full Phase: Plan Add Execution E2E)

- **E2E tests**: Added plan add execution E2E test in `tests/test_e2e_cli.py`:
  - `TestPlanAddExecution`: plan add creates task; plan list shows it (alias for dag add).

## Chunk 278 (Full Phase: Plan Remove/Update/Cancel Execution E2E)

- **E2E tests**: Added plan remove/update/cancel execution E2E tests in `tests/test_e2e_cli.py`:
  - `TestPlanRemoveUpdateCancelExecution`: plan remove then list; plan update --status done then list; plan cancel then list (aliases for dag remove/update/cancel).

## Chunk 279 (Full Phase: Recover/Plan Rollback Execution E2E)

- **E2E tests**: Added recover/plan rollback execution E2E tests in `tests/test_e2e_cli.py`:
  - `TestRecoverPlanRollbackExecution`: plan checkpoint then plan rollback; recover rollback (aliases for dag checkpoint/rollback).

## Chunk 280 (Full Phase: Govern Alias Execution E2E)

- **E2E tests**: Added govern alias execution E2E tests in `tests/test_e2e_cli.py`:
  - `TestGovernAliasExecution`: govern session-contracts, govern health-gate, govern health-report (aliases for session-contracts, session-contract-health-gate, session-contract-health-report).

## Chunk 281 (Full Phase: Govern Health-Trend + Observe Alias Execution E2E)

- **E2E tests**: Added govern health-trend and observe alias execution E2E tests in `tests/test_e2e_cli.py`:
  - `TestGovernAliasExecution`: govern health-trend (alias for session-contract-health-trend).
  - `TestObserveAliasExecution`: observe cockpit, observe archive, observe benchmark (aliases for cockpit, archive, benchmark).

## Chunk 282 (Full Phase: Orchestrate PS + Govern Migration Execution E2E)

- **E2E tests**: Added orchestrate ps and govern migration execution E2E tests in `tests/test_e2e_cli.py`:
  - `TestOrchestrateGovernAliasExecution`: orchestrate ps (alias for ps); govern migration csm csm-v1; govern migration --format json.

## Chunk 283 (Full Phase: Orchestrate/Observe/Recover Status/Logs/Wait/Stop Alias E2E)

- **E2E tests**: Added orchestrate/observe/recover alias execution E2E tests in `tests/test_e2e_cli.py`:
  - `TestOrchestrateObserveRecoverStatusLogsWaitStopAlias`: orchestrate status/logs/wait, observe status, recover stop with unknown session (aliases exit 2 with Session not found).

## Chunk 284 (Full Phase: Orchestrate/Observe Inspect and Logs/Wait Alias E2E)

- **E2E tests**: Added orchestrate/observe inspect and logs/wait alias execution E2E tests in `tests/test_e2e_cli.py`:
  - `TestOrchestrateObserveInspectAlias`: orchestrate inspect --owner, observe inspect --owner (no sessions exit 0); observe logs, observe wait with unknown session (exit 2).
- **Fix**: Corrected syntax error in `src/thegent/cli.py` (`latest_issue_types_csv` f-string paren mismatch).

## Chunk 285 (Exit Code Natural Language Messages)

- **Exit code descriptions**: Added `src/thegent/exit_codes.py` with human-readable messages for CI/stop-hook consumers:
  - `EXIT_TIMEOUT` (124): "Operation timed out: the command exceeded the maximum allowed duration..."
  - `EXIT_HEALTH_GATE_FAILED` (2): "Governance gate failed: session contract health check did not pass..."
- **CLI**: `logs_cmd` and `wait_cmd` now print descriptive timeout messages before exiting 124; `session_contract_health_gate_cmd` prints governance gate message to stderr before exiting 2.
- **Outcome**: Stop hooks and CI logs see natural language explanations instead of raw `rc=124` / `rc=2`.

## Chunk 286 (Full Phase: Govern Conformance Execution E2E)

- **E2E tests**: Added govern conformance execution E2E tests in `tests/test_e2e_cli.py`:
  - `TestGovernConformanceExecution`: govern conformance (adapter suite); govern conformance --format json.

## Chunk 287 (Full Phase: Mega E2E Batch — 33 Tests)

- **Import fix**: Added `plan_analyze_cmd` to `main.py` imports from `thegent.cli`.
- **E2E tests**: Added 10 new test classes (33 tests) in `tests/test_e2e_cli.py`:
  - `TestPlanAnalyzeExecution`: plan analyze --help, plan analyze --cd, plan analyze --pert.
  - `TestGovernVerifyShowPolicyFeedbackExecution`: govern verify, govern verify --format json, govern show-policy, govern feedback, govern closure-pack --help.
  - `TestObserveKpisModesOperationsExecution`: observe kpis, observe kpis --format json, modes, operations --operation plan, operations --format json.
  - `TestOrchestratePauseResumeAlias`: orchestrate pause/resume with unknown session (exit nonzero).
  - `TestOrchestrateRunBgHelpAndUnknownAgent`: orchestrate run/bg --help, run unknown agent (exit 1), bg unknown agent (exit 0 or 1).
  - `TestCliproxyMcpLoginHelpExecution`: cliproxy login, orchestrate login, mcp install/up/down --help.
  - `TestPlanListFormatExecution`: plan list --format md, plan list empty DAG.
  - `TestHistoryEventsAliasExecution`: history events --format json, observe history --limit.
  - `TestClosurePackArchiveExecution`: closure-pack no DAG (exit 1), govern closure-pack no DAG (exit 1), archive --days 1.

## Chunk 288 (Full Phase: Full-Depth Remaining E2E — 24 Tests)

- **E2E tests**: Added 12 new test classes (24 tests) in `tests/test_e2e_cli.py`:
  - `TestGovernDataProtectionExecution`: govern data-protection, govern data-protection --format json.
  - `TestPlanAnalyzeDeepOptions`: plan analyze --resources, --continuity, --format json.
  - `TestObserveDriftDeepOptions`: observe drift --format json, observe drift --structural-budget/--semantic-budget.
  - `TestGovernConformanceCheckDrift`: govern conformance --check-drift.
  - `TestDagPlanReadyFormatJson`: dag ready --format json, plan ready --format json.
  - `TestHistoryEventsRunId`: history events --run-id.
  - `TestMcpServiceHelp`: mcp service --help.
  - `TestArchiveDomainOption`: archive --domain --days.
  - `TestOperationsRecoverFilter`: operations --operation recover.
  - `TestObserveTrendDeepOptions`: observe trend --payload-type gate, --format json, --all.
  - `TestGovernMigrationAllContracts`: govern migration task-tool task-tool-18, zen zen-rich-v1.
  - `TestGovernEscalateListExecution`: govern escalate list --help, list, list --format json.
  - `TestHistoryListFormatJson`: history list --format json.
  - `TestObserveTrendOwnerOption`: observe trend --owner.

## Chunk 289 (Plan/Dag List and Status JSON Format — 4 Tests)

- **CLI**: Added `--format json` support to `dag list` and `dag status` in `src/thegent/cli.py`:
  - `dag_list_cmd`: outputs `{"tasks": [...]}` (or `{"tasks": []}` when empty).
  - `dag_status_cmd`: outputs `{"tasks": [...]}` (or `{"tasks": []}` when no tasks with session_id).
- **main.py**: Updated help text for `dag list` and `dag status` to include `json` format.
- **E2E tests**: Added `TestPlanDagListStatusFormatJson` (4 tests) in `tests/test_e2e_cli.py`:
  - `dag list --format json`, `plan list --format json`, `dag status --format json`, `plan status --format json`.

## Chunk 290 (Full-Depth Remaining E2E — 6 Tests)

- **E2E tests**: Added 4 new test classes (6 tests) in `tests/test_e2e_cli.py`:
  - `TestModesFormatJson`: modes --format json, modes --mode sequential_delegation, modes --mode parallel_consensus --format json.
  - `TestPlanAnalyzePertFormatJson`: plan analyze --pert --format json (PERT overlay with JSON).
  - `TestDagListEmptyFormatJson`: dag list --format json with empty DAG (tasks: []).
  - `TestGovernSweepFormatJson`: govern sweep --format json with empty session dir.

## Chunk 291 (Operations + Plan Analyze Combined — 3 Tests)

- **E2E tests**: Added 2 new test classes (3 tests) in `tests/test_e2e_cli.py`:
  - `TestOperationsOrchestrateFormatJson`: operations --operation orchestrate --format json.
  - `TestPlanAnalyzeCombinedOverlays`: plan analyze --pert --resources, plan analyze --resources --continuity.

## Chunk 292 (Govern Escalate Add/Resolve + Plan Analyze All Overlays — 7 Tests)

- **E2E tests**: Added 3 new test classes (7 tests) in `tests/test_e2e_cli.py`:
  - `TestGovernEscalateAddResolve`: govern escalate add/resolve --help, add then resolve flow, list --past-sla.
  - `TestPlanAnalyzeAllOverlays`: plan analyze --pert --resources --continuity, with --format json.
  - `TestGovernConformanceFormatJson`: govern conformance --format json.

## Chunk 228b (Phase 3-6 Kickoff: Policy, Drift, and MCP Surface)

- Added policy engine baseline in `src/thegent/cli_impl.py`:
  - policy profiles: `strict_ci`, `warn_only`, `prod_release`
  - policy resolver and payload fields:
    - `policy_profile`
    - `policy_evaluation`
    - `decision_reasons`
- Added drift/snapshot baseline in `src/thegent/cli_impl.py`:
  - append-only snapshot log (`THGENT_HEALTH_SNAPSHOT_PATH`, default `~/.thegent/health-snapshots.jsonl`)
  - baseline lookup by scope key and trend metadata:
    - `trend_summary.baseline_available`
    - `trend_summary.blocked_ratio_delta`
    - `trend_summary.blocked_count_delta`
    - `trend_summary.new_issue_types`
    - `trend_summary.resolved_issue_types`
- Added compatibility envelope in `src/thegent/cli_impl.py`:
  - top-level `compat.aliases` for canonical count key mapping.
- Extended health command surfaces in `src/thegent/main.py` and `src/thegent/cli.py`:
  - new options for gate/report:
    - `--policy-profile`
    - `--no-worse-than-baseline`
    - `--regression-tolerance`
  - rich/markdown output now includes policy + trend context.
- Extended MCP health resources/tools in `src/thegent/mcp_server.py`:
  - resource/tool params include policy + baseline regression controls.
  - `ToolResult.meta` now includes canonical health counters and policy/status fields.

## Chunk 229 (Phase 6 Trend Query Surface)

- Added a dedicated trend-query implementation in `src/thegent/cli_impl.py`:
  - `session_contract_health_trend_impl(...)`
  - returns scoped snapshot history + delta summary for either:
    - `session_contract_health_report`
    - `session_contract_health_gate`
  - includes canonical trend payload fields:
    - `trend_payload_type`
    - `scope_key`
    - `snapshot_count`
    - `latest` / `oldest`
    - `delta_summary`
    - `snapshots`
- Added CLI command surface in `src/thegent/main.py` and `src/thegent/cli.py`:
  - `session-contract-health-trend`
  - supports JSON/MD/rich rendering for trend inspection.
- Added MCP resource/tool surface in `src/thegent/mcp_server.py`:
  - resource: `thegent://sessions/contracts/trend{?...}`
  - tool: `thegent_session_contract_health_trend`
  - includes meta fields for trend payload type and snapshot count.
- Outcome: snapshot/drift intelligence is now directly queryable as a first-class
  API surface instead of only being embedded in gate/report outputs.

## Chunk 230 (Policy/Trend Unit Test Hardening)

- Added `tests/test_unit_health_trend.py` to cover new Phase 3-6 logic in
  `src/thegent/cli_impl.py`:
  - policy-profile override semantics on gate payloads.
  - baseline-regression gating (`--no-worse-than-baseline`) behavior.
  - report profile enforcement and compatibility alias checks.
  - trend snapshot rollup/delta behavior from persisted snapshot history.
  - invalid trend payload-type validation path.
- This establishes dedicated unit-level regression protection for newly introduced
  policy + drift intelligence contracts.

## Chunk 231 (MCP Policy/Trend Contract Test Coverage)

- Extended `tests/test_unit_mcp.py` with MCP-focused coverage for the new health
  policy/trend surfaces:
  - `thegent_session_contract_health_gate` tool metadata assertions:
    - `policy_profile`, `status`, canonical count fields.
  - `thegent_session_contract_health_report` tool metadata assertions:
    - `policy_profile`, `status`, canonical count fields.
  - `thegent_session_contract_health_trend` tool contract assertions:
    - payload type and trend-specific metadata (`trend_payload_type`,
      `snapshot_count`).
  - `resource_session_contract_health_trend` resource payload shape assertions.
- This closes a high-value coverage gap for MCP transport/meta contract stability
  introduced by Phase 3-6 surfaces.

## Chunk 232 (CLI E2E Coverage for Policy/Trend Commands)

- Added `tests/test_e2e_health_trend_cli.py` with end-to-end CLI coverage for new
  Phase 3-6 command surfaces:
  - `session-contract-health-trend`:
    - JSON output shape for empty snapshot scope.
    - Markdown rendering path.
  - `session-contract-health-gate` with policy/baseline flags:
    - `--policy-profile`
    - `--no-worse-than-baseline`
    - `--regression-tolerance`
    - verifies policy evaluation fields in JSON output.
  - `session-contract-health-report` with policy/baseline flags:
    - verifies policy/trend/compat fields in JSON output.
- This extends coverage from unit-only checks to CLI invocation behavior for the
  new policy and trend command surfaces.

## Chunk 233 (Schema Compat Mode Propagation)

- Added explicit `schema_compat_mode` to health payloads in
  `src/thegent/cli_impl.py`:
  - `session_contract_health_gate_impl(...)`
  - `session_contract_health_report_impl(...)`
  - `session_contract_health_trend_impl(...)`
  - mode currently set to `compat`.
- Propagated `schema_compat_mode` through CLI serializers in
  `src/thegent/cli.py`:
  - markdown headers for gate/report
  - CSV schema + rows for gate/report
  - JSONL blocked-row context for gate/report
- Extended MCP tool metadata in `src/thegent/mcp_server.py`:
  - health gate/report/trend `ToolResult.meta` now includes
    `schema_compat_mode`.
- Outcome: consumers can now branch deterministically on schema compatibility
  mode across payload, artifact, and MCP transport layers.

## Chunk 234 (Snapshot Retention & Compaction Controls)

- Added snapshot log retention controls in `src/thegent/cli_impl.py`:
  - new env-backed max-line setting:
    - `THGENT_HEALTH_SNAPSHOT_MAX_LINES` (default `5000`, minimum `100`)
  - new compaction path:
    - `_compact_health_snapshot_log()` trims snapshot JSONL to most-recent N lines.
  - compaction now runs after every snapshot append in `_append_health_snapshot(...)`.
- Extended trend payload metadata in `session_contract_health_trend_impl(...)`:
  - `snapshot_retention_max_lines` exposes active retention configuration.
- Outcome: snapshot history growth is now bounded for long-running deployments
  while preserving recent drift context.

## Chunk 235 (Retention Observability in CLI/MCP)

- Extended trend visibility surfaces to expose active snapshot retention settings:
  - `src/thegent/cli.py`:
    - markdown trend output now includes `snapshot_retention_max_lines`.
    - rich trend output now includes `retention_max_lines`.
  - `src/thegent/mcp_server.py`:
    - `thegent_session_contract_health_trend` `ToolResult.meta` now includes
      `snapshot_retention_max_lines`.
- Added coverage updates:
  - `tests/test_unit_health_trend.py` now asserts trend payload includes
    `snapshot_retention_max_lines`.
  - `tests/test_unit_mcp.py` now asserts trend-tool metadata includes
    `snapshot_retention_max_lines`.
- Outcome: operators and MCP clients can confirm retention policy directly from
  trend outputs without inspecting environment variables.

## Chunk 236 (Trend Artifact Export Support)

- Added first-class trend artifact serialization/export in `src/thegent/cli.py`:
  - serializers:
    - `_serialize_health_trend_md(...)`
    - `_serialize_health_trend_csv(...)`
    - `_serialize_health_trend_jsonl(...)`
  - atomic export writer:
    - `_write_health_trend_export(...)`
  - `session_contract_health_trend_cmd(...)` now supports:
    - `output`
    - `export_format`
    - `overwrite`
    with extension inference and format validation parity.
- Extended CLI entrypoint in `src/thegent/main.py` for
  `session-contract-health-trend`:
  - `--output`
  - `--export-format`
  - `--overwrite`
- Outcome: trend snapshots/delta intelligence can now be emitted as durable
  artifacts (`json`, `md`, `csv`, `jsonl`) with the same export ergonomics as
  health gate/report commands.

## Chunk 237 (Trend Export Test Coverage)

- Extended serializer unit coverage in `tests/test_unit_health_serializers.py`:
  - added trend serializer tests for:
    - markdown (`_serialize_health_trend_md`)
    - csv (`_serialize_health_trend_csv`)
    - jsonl (`_serialize_health_trend_jsonl`)
  - includes summary/snapshot row assertions and core field presence checks.
- Extended CLI E2E coverage in `tests/test_e2e_health_trend_cli.py`:
  - `session-contract-health-trend` export path now covered for:
    - JSON artifact export (`--output --export-format json --overwrite`)
    - CSV artifact export (`--output --export-format csv --overwrite`)
  - validates emitted artifact existence and basic shape.
- Outcome: new trend export functionality now has both serializer-level and
  command-level regression coverage.

## Chunk 238 (Snapshot Retention Compaction Test Coverage)

- Extended `tests/test_unit_health_trend.py` with retention-focused unit tests:
  - `_health_snapshot_max_lines()` behavior:
    - default value (`5000`)
    - minimum floor enforcement (`>=100`)
    - explicit configured value support.
  - `_compact_health_snapshot_log()` behavior:
    - trims oversized snapshot logs to configured max-lines
    - preserves most-recent records deterministically.
- Outcome: snapshot retention and compaction controls now have direct regression
  tests in addition to trend payload behavior checks.

## Chunk 239 (Trend Export Negative-Path E2E Coverage)

- Extended `tests/test_e2e_health_trend_cli.py` with failure-path coverage for
  trend artifact export:
  - verifies export refuses replacing existing output paths unless
    `--overwrite` is provided.
  - verifies invalid `--export-format` values fail fast with a clear error.
- Outcome: trend export safeguards now have explicit CLI E2E regression coverage
  for common operator mistakes.

## Chunk 240 (Schema Discovery Parity for Trend Payload)

- Updated `src/thegent/cli_impl.py` schema discovery constants:
  - `HEALTH_PAYLOAD_TYPES` now includes `session_contract_health_trend`.
- Updated `tests/test_unit_mcp.py` meta-contract assertions:
  - `get_server_meta_impl()` must advertise trend payload type in
    `health_payload_types`.
- Outcome: server metadata now fully reflects all first-class health payload
  contracts (gate/report/trend), improving discoverability for MCP clients.

## Chunk 241 (Policy Profile Discovery in Server Meta)

- Extended `get_server_meta_impl()` in `src/thegent/cli_impl.py` to publish:
  - `health_policy_profiles` (sorted list of supported profile keys).
- This makes policy profile capabilities discoverable via meta surfaces instead
  of requiring out-of-band docs.

## Chunk 242 (MCP Caching for Trend Reads)

- Extended MCP response caching middleware in `src/thegent/mcp_server.py`:
  - added `thegent_session_contract_health_trend` to cache-included tools.
- This improves repeated trend-query latency and reduces redundant snapshot-log
  parse overhead for read-heavy orchestration loops.

## Chunk 243 (MCP Decision/Diff Metadata Enrichment)

- Extended MCP tool metadata in `src/thegent/mcp_server.py`:
  - gate/report metadata now include `decision_reasons`.
  - trend metadata now include:
    - `blocked_ratio_delta`
    - `blocked_count_delta`
- Extended unit coverage in `tests/test_unit_mcp.py`:
  - meta-contract now asserts `health_policy_profiles` content.
  - gate/report decision-reason metadata assertions added.
  - trend delta metadata assertions added.
- Outcome: orchestrators can route/alert using concise MCP metadata without
  parsing full payload bodies.

## Chunk 244 (MCP Trend Meta: Latest State & Scope)

- Extended `thegent_session_contract_health_trend` metadata in
  `src/thegent/mcp_server.py` with additional orchestrator-facing fields:
  - `scope_key`
  - `latest_status`
  - `latest_pass`
- Extended `tests/test_unit_mcp.py` to assert the new trend metadata fields.
- Outcome: MCP clients can perform fast routing/alert decisions using compact
  trend metadata (scope + latest state) without opening full payload bodies.

## Chunk 245 (Trend CSV Latest-State Summary Columns)

- Improved trend CSV ergonomics in `src/thegent/cli.py` by extending
  `_serialize_health_trend_csv(...)`:
  - added explicit summary-context columns:
    - `latest_status`
    - `latest_pass`
  - values are populated from top-level trend payload `latest` snapshot context
    on both summary and snapshot rows.
- Outcome: tabular consumers can access current trend state directly without
  nested JSON parsing.

## Chunk 246 (Trend JSONL Latest-State Context Parity)

- Extended `_serialize_health_trend_jsonl(...)` in `src/thegent/cli.py`:
  - summary row now includes:
    - `latest_status`
    - `latest_pass`
  - snapshot rows now include the same latest-state context fields.
- Outcome: JSONL line-by-line consumers can access current trend state without
  parsing nested `latest` objects.

## Chunk 247 (Trend Markdown Latest-State Parity)

- Extended `_serialize_health_trend_md(...)` in `src/thegent/cli.py`:
  - added explicit markdown lines:
    - `latest_status`
    - `latest_pass`
- Outcome: markdown trend artifacts now expose the same current-state context
  available in trend CSV/JSONL parity surfaces.

## Chunk 248 (Trend Latest-State Serializer Test Parity)

- Extended trend serializer unit coverage in
  `tests/test_unit_health_serializers.py`:
  - markdown test now asserts `latest_status` and `latest_pass` presence.
  - csv test now asserts header includes `latest_status` and `latest_pass`.
  - jsonl test now asserts summary and snapshot rows include
    `latest_status` / `latest_pass`.
- Outcome: latest-state trend parity fields now have direct serializer-level
  regression coverage across all export formats.

## Chunk 249 (Trend Markdown E2E Latest-State Assertion)

- Extended `tests/test_e2e_health_trend_cli.py` markdown output test for
  `session-contract-health-trend` to assert:
  - `latest_status`
  - `latest_pass`
- Outcome: end-to-end CLI rendering checks now cover latest-state visibility in
  markdown trend output.

## Chunk 250 (Trend Export Format E2E Expansion)

- Expanded `tests/test_e2e_health_trend_cli.py` to cover additional trend export
  formats end-to-end:
  - markdown artifact export (`--export-format md`)
  - jsonl artifact export (`--export-format jsonl`)
- Assertions verify artifact creation and basic shape/content:
  - markdown includes trend heading + latest-state field visibility.
  - jsonl summary row includes `record_type=summary` and trend payload type.
- Outcome: all supported trend export formats now have direct CLI E2E coverage
  (`json`, `csv`, `md`, `jsonl`).

## Chunk 251 (Trend Rich Output Latest Capture Context)

- Enhanced rich rendering in `session_contract_health_trend_cmd(...)`
  (`src/thegent/cli.py`):
  - now prints:
    - `latest captured_at_utc`
    - `latest issue_types_count`
- Outcome: terminal trend reviews include quick recency/context signals without
  opening nested payload objects.

## Chunk 252 (MCP Trend Meta Latest Metrics Enrichment)

- Extended `thegent_session_contract_health_trend` metadata in
  `src/thegent/mcp_server.py` with latest snapshot metrics:
  - `latest_captured_at_utc`
  - `latest_blocked_ratio`
  - `latest_blocked_count`
- Outcome: MCP orchestrators can trigger alerts/routing directly from compact
  metadata fields.

## Chunk 253 (MCP Trend Latest Metrics Test Coverage)

- Extended `tests/test_unit_mcp.py` trend metadata assertions to cover:
  - `latest_captured_at_utc`
  - `latest_blocked_ratio`
  - `latest_blocked_count`
- Outcome: new MCP trend metadata fields now have direct unit-level contract
  regression protection.

## Chunk 254 (Trend Artifact Parity: Latest Metrics Fields)

- Extended trend artifact serializers in `src/thegent/cli.py` to expose latest
  metric fields consistently:
  - `_serialize_health_trend_md(...)` now includes:
    - `latest_captured_at_utc`
    - `latest_blocked_ratio`
    - `latest_blocked_count`
  - `_serialize_health_trend_csv(...)` now includes matching columns on summary
    and snapshot rows.
  - `_serialize_health_trend_jsonl(...)` now includes matching keys on summary
    and snapshot rows.
- Outcome: latest trend metrics now have parity across CLI artifact formats and
  MCP metadata surfaces.

## Chunk 255 (Trend Latest Metrics Serializer Test Expansion)

- Extended trend serializer unit coverage in
  `tests/test_unit_health_serializers.py` to assert:
  - markdown includes latest metric fields.
  - csv header includes latest metric columns.
  - jsonl summary and snapshot rows include latest metric keys.
- Outcome: latest metric parity fields now have direct serializer-level
  regression protection.

## Chunk 256 (3-Chunk Batch Consolidation Pass)

- Executed as a combined 3-chunk delivery:
  - artifact parity implementation (Chunk 254),
  - serializer coverage expansion (Chunk 255),
  - consolidated phase logging and sequencing (Chunk 256).
- Outcome: phase progression remains contiguous while delivering larger per-turn
  change sets as requested.

## Chunk 257 (Trend Export E2E Latest Metrics Parity)

- Expanded `tests/test_e2e_health_trend_cli.py` trend export assertions:
  - CSV export now verifies latest metric columns are present:
    - `latest_captured_at_utc`
    - `latest_blocked_ratio`
    - `latest_blocked_count`
  - Markdown export now verifies latest metric lines are present.
  - JSONL export now verifies summary row includes latest metric keys.
- Outcome: latest metric parity is now validated at CLI export E2E level across
  `csv`, `md`, and `jsonl`.

## Chunk 258 (MCP Trend Meta Issue-Type Count)

- Extended `thegent_session_contract_health_trend` metadata in
  `src/thegent/mcp_server.py` with:
  - `latest_issue_types_count`
- Outcome: MCP orchestrators can quickly score latest trend complexity/severity
  signals from metadata without parsing full trend payloads.

## Chunk 259 (MCP Trend Meta Issue-Type Count Test Coverage)

- Extended `tests/test_unit_mcp.py` trend metadata assertions to cover:
  - `latest_issue_types_count`
- Outcome: new trend meta count field now has direct unit-level contract
  regression protection.

## Chunk 260 (Trend Artifact Issue-Type Count Parity)

- Propagated `latest_issue_types_count` through trend CLI artifact surfaces in
  `src/thegent/cli.py`:
  - markdown: explicit `latest_issue_types_count` line.
  - csv: added `latest_issue_types_count` column on summary/snapshot rows.
  - jsonl: added `latest_issue_types_count` on summary/snapshot rows.
  - rich output already prints issue-types count and remains aligned.
- Extended coverage:
  - `tests/test_unit_health_serializers.py` now asserts
    `latest_issue_types_count` across trend md/csv/jsonl serializers.
  - `tests/test_e2e_health_trend_cli.py` now asserts
    `latest_issue_types_count` visibility in md and jsonl export paths.
- Outcome: issue-type count is now parity-aligned across MCP metadata and all
  trend artifact formats.

## Chunk 261 (Trend Generated Timestamp Parity)

- Extended trend surfaces with explicit generation timestamp context:
  - `src/thegent/cli.py`:
    - `_serialize_health_trend_md(...)` now emits `generated_at_utc`.
    - `_serialize_health_trend_csv(...)` now includes `generated_at_utc`
      column on summary and snapshot rows.
  - `src/thegent/mcp_server.py`:
    - `thegent_session_contract_health_trend` metadata now includes
      `generated_at_utc`.
- Extended `tests/test_unit_mcp.py` trend metadata assertions to cover
  `generated_at_utc`.
- Outcome: trend artifacts and MCP metadata now consistently expose generation
  timestamp for audit/replay alignment.

## Chunk 262 (Trend JSONL Generated Timestamp Snapshot Parity)

- Extended `_serialize_health_trend_jsonl(...)` in `src/thegent/cli.py`:
  - snapshot rows now explicitly include `generated_at_utc` (in addition to
    summary row context).
- Outcome: trend JSONL rows are now fully generation-timestamp self-describing
  for line-by-line consumers.

## Chunk 263 (Trend JSONL Generated Timestamp Test Coverage)

- Extended `tests/test_unit_health_serializers.py` trend fixture and JSONL tests:
  - trend fixture now includes `generated_at_utc`.
  - JSONL trend serializer test now asserts `generated_at_utc` on both summary
    and snapshot rows.
- Outcome: generation timestamp parity for trend JSONL rows now has direct
  serializer-level regression coverage.

## Chunk 264 (Trend JSONL E2E Generated Timestamp Assertion)

- Extended `tests/test_e2e_health_trend_cli.py` JSONL export assertions for
  `session-contract-health-trend`:
  - summary row must include `generated_at_utc`.
- Outcome: trend JSONL generation timestamp visibility now has command-level E2E
  coverage in addition to serializer-level unit coverage.

## Chunk 265 (Trend CSV/MD E2E Generated Timestamp Assertions)

- Extended `tests/test_e2e_health_trend_cli.py` export assertions:
  - CSV export now asserts presence of `generated_at_utc` column/content.
  - Markdown export now asserts presence of `generated_at_utc` line.
- Outcome: trend generation timestamp now has E2E coverage across all artifact
  export formats (`md`, `csv`, `jsonl`).

## Chunk 266 (Trend Rich Output Generated Timestamp Parity)

- Updated rich trend rendering in `session_contract_health_trend_cmd(...)`
  (`src/thegent/cli.py`) to print:
  - `generated_at_utc=...`
- Extended `tests/test_e2e_health_trend_cli.py` with a rich-output assertion
  test requiring generated timestamp visibility.
- Outcome: trend generation timestamp is now parity-visible in rich, markdown,
  csv, and jsonl surfaces.

## Chunk 267 (Trend MD/CSV Generated Timestamp Unit Assertions)

- Extended `tests/test_unit_health_serializers.py` trend serializer tests:
  - markdown test now explicitly asserts `generated_at_utc` presence.
  - csv test now asserts `generated_at_utc` exists in trend CSV header.
- Outcome: generated timestamp visibility now has direct unit-level coverage for
  all trend serializer formats (md/csv/jsonl).

## Chunk 268 (Trend Scope Alias Field Parity)

- Extended trend artifact serializers in `src/thegent/cli.py` with explicit
  scalar `scope_*` aliases (in addition to nested `scope_key`):
  - `scope_owner`
  - `scope_all`
  - `scope_strict`
  - `scope_policy_profile`
  - `scope_min_healthy_ratio`
  - `scope_top_blocked`
- Applied across trend markdown/csv/jsonl serializer outputs.
- Extended `tests/test_unit_health_serializers.py` to assert scope-alias
  presence across trend serializer formats.
- Outcome: row-level and markdown consumers can read trend scope context without
  nested JSON parsing of `scope_key`.

## Chunk 269 (Trend Scope Alias E2E Export Visibility)

- Extended `tests/test_e2e_health_trend_cli.py` to assert `scope_*` alias field
  visibility in trend outputs:
  - markdown command output (`--format md`)
  - markdown export artifact (`--export-format md`)
  - jsonl export summary row (`--export-format jsonl`)
- Outcome: scope-alias parity now has command-level E2E coverage in addition to
  serializer-level unit coverage.

## Chunk 270 (MCP Trend Scope Alias Metadata)

- Extended `thegent_session_contract_health_trend` metadata in
  `src/thegent/mcp_server.py` with scalar scope aliases:
  - `scope_owner`
  - `scope_all`
  - `scope_strict`
  - `scope_policy_profile`
- Extended `tests/test_unit_mcp.py` trend metadata assertions to cover the new
  scope alias fields.
- Outcome: MCP orchestrators can consume trend scope context from flat metadata
  fields without parsing nested `scope_key`.

## Chunk 271 (MCP Trend Scope Threshold/Window Metadata Parity)

- Extended `thegent_session_contract_health_trend` metadata in
  `src/thegent/mcp_server.py` with additional scope aliases:
  - `scope_min_healthy_ratio`
  - `scope_top_blocked`
- Extended `tests/test_unit_mcp.py` trend metadata assertions to cover these
  new fields.
- Outcome: MCP trend metadata now exposes full scope alias parity for both
  gate-oriented and report-oriented trend windows.

## Chunk 272 (Top-Level Trend Scope Alias Payload Contract)

- Extended `session_contract_health_trend_impl(...)` in
  `src/thegent/cli_impl.py` to include top-level scope alias fields in the
  payload itself (not only in serializers/meta):
  - `scope_owner`
  - `scope_all`
  - `scope_strict`
  - `scope_policy_profile`
  - `scope_min_healthy_ratio`
  - `scope_top_blocked`
- Extended `tests/test_unit_health_trend.py` trend assertions to validate
  top-level scope alias fields for gate-scope trend payloads.
- Outcome: trend payload contract now directly carries flat scope aliases for
  all consumers, reducing dependence on derived projections.

## Chunk 273 (Trend Scope Alias Source-of-Truth Normalization)

- Normalized trend scope alias consumption to prefer top-level payload fields
  over nested `scope_key` projections:
  - `src/thegent/cli.py` trend serializers now read top-level `scope_*` first
    with `scope_key` fallback.
  - `src/thegent/mcp_server.py` trend metadata now reads top-level `scope_*`
    first with `scope_key` fallback.
- Updated fixtures in:
  - `tests/test_unit_health_serializers.py`
  - `tests/test_unit_mcp.py`
  to include top-level `scope_*` fields for direct-path coverage.
- Outcome: scope alias behavior is now consistent with trend payload contract as
  the primary source-of-truth, while preserving backward compatibility.

## Chunk 274 (Trend Compatibility Alias Envelope)

- Extended `session_contract_health_trend_impl(...)` in
  `src/thegent/cli_impl.py` with top-level `compat` contract metadata:
  - `compat.mode = "compat"`
  - `compat.aliases` mapping nested scope keys to top-level scope aliases:
    - `scope.owner` -> `scope_owner`
    - `scope.all` -> `scope_all`
    - `scope.strict` -> `scope_strict`
    - `scope.policy_profile` -> `scope_policy_profile`
    - `scope.min_healthy_ratio` -> `scope_min_healthy_ratio`
    - `scope.top_blocked` -> `scope_top_blocked`
- Extended `tests/test_unit_health_trend.py` with assertions for trend
  `compat.aliases`.
- Outcome: trend payloads now match gate/report compatibility-envelope patterns
  and provide explicit alias migration guidance for scope fields.

## Chunk 275 (Trend Compat Envelope E2E JSON Assertions)

- Extended `tests/test_e2e_health_trend_cli.py` JSON-path assertions for
  `session-contract-health-trend`:
  - direct JSON output now asserts `compat.mode` and alias mapping keys.
  - JSON export artifact now asserts `compat` envelope presence and alias
    mappings.
- Outcome: trend compatibility-envelope behavior is now covered at command-level
  E2E for JSON consumers.

## Chunk 276 (MCP Trend Compat Metadata Projection)

- Extended `thegent_session_contract_health_trend` metadata in
  `src/thegent/mcp_server.py` to project trend compatibility envelope fields:
  - `compat_mode`
  - `compat_aliases`
- Extended `tests/test_unit_mcp.py` trend metadata assertions to validate the
  projected compatibility metadata.
- Outcome: MCP orchestration clients can consume compatibility migration hints
  directly from metadata without parsing full trend payload bodies.

## Chunk 277 (Trend Row-Level Compat Context Parity)

- Extended trend serializers in `src/thegent/cli.py` for row-level compatibility
  context:
  - `_serialize_health_trend_csv(...)` now includes:
    - `compat_mode`
    - `compat_aliases_json`
  - `_serialize_health_trend_jsonl(...)` snapshot rows now include:
    - `compat_mode`
    - `compat_aliases`
- Extended `tests/test_unit_health_serializers.py`:
  - trend CSV header assertions now include compat columns.
  - trend JSONL assertions now validate compat context on summary/snapshot rows.
- Outcome: compatibility migration hints are now directly available in line/tabular
  trend artifacts without requiring payload-level object parsing.

## Chunk 278 (Trend Compat Context E2E Export Assertions)

- Extended `tests/test_e2e_health_trend_cli.py` export assertions:
  - CSV export now asserts presence of:
    - `compat_mode`
    - `compat_aliases_json`
  - JSONL export now asserts:
    - summary row includes `compat.mode == "compat"`
    - snapshot row includes `compat_mode` and `compat_aliases`.
- Outcome: trend compatibility context now has command-level E2E coverage for
  both tabular and line-oriented export consumers.

## Chunk 279 (Trend Markdown Compat Visibility Parity)

- Extended trend markdown serializer in `src/thegent/cli.py`:
  - `_serialize_health_trend_md(...)` now includes:
    - `compat_mode`
    - `compat_aliases`
- Extended coverage:
  - `tests/test_unit_health_serializers.py` markdown trend assertions now check
    compat visibility.
  - `tests/test_e2e_health_trend_cli.py` markdown command and markdown export
    assertions now check compat visibility.
- Outcome: compatibility context is now explicitly visible across markdown,
  csv, jsonl, and MCP trend surfaces.

## Chunk 280 (Trend Rich Compat Visibility Parity)

- Extended rich trend rendering in `session_contract_health_trend_cmd(...)`
  (`src/thegent/cli.py`) to print:
  - `compat_mode`
  - `compat_aliases_count`
- Extended `tests/test_e2e_health_trend_cli.py` rich output assertions to cover
  the new compat fields.
- Outcome: compatibility context is now explicitly visible in rich trend output
  alongside markdown/csv/jsonl/MCP surfaces.

## Chunk 281 (MCP Trend Compat Alias Count Metadata)

- Extended `thegent_session_contract_health_trend` metadata in
  `src/thegent/mcp_server.py` with:
  - `compat_aliases_count`
- Extended `tests/test_unit_mcp.py` trend metadata assertions to validate
  `compat_aliases_count`.
- Outcome: MCP clients can quickly assess compatibility envelope breadth without
  parsing alias maps.

## Chunk 282 (Top-Level Trend Compat Alias Count Contract)

- Extended `session_contract_health_trend_impl(...)` in
  `src/thegent/cli_impl.py` with top-level:
  - `compat_aliases_count`
  computed from `compat.aliases`.
- Extended `tests/test_unit_health_trend.py` to assert
  `compat_aliases_count == len(compat.aliases)`.
- Outcome: trend payload contract now carries a direct compatibility-envelope
  size metric, aligned with rich/MCP metadata surfaces.

## Chunk 231 (Dependency-Aware Routing & Execution Lanes)

### Completed

- Implemented **Dependency-aware routing engine** and **Priority/urgency lane model** (Phase 1, WP-1001 & WP-1002):
  - Updated `src/thegent/execution.py`: Added `lane` field to `RunMeta` (default: `standard`).
  - Updated `src/thegent/cli.py`:
    - `bg_cmd()`: Now accepts `lane` and `correlation_id`; registers start with `RunRegistry`.
    - `run_cmd()`: Now accepts `lane`.
    - `dag_run_cmd()`: 
      - Added support for `max_parallel` (enforced via `status=running` check).
      - Added `priority` sorting (higher priority tasks run first).
      - Added support for `routing` and `lane` columns in DAG markdown table.
      - Tasks now pass their ID as `correlation_id` to background runs.
    - `history_cmd()`: Now displays `Lane` column in terminal table.
  - Updated `src/thegent/cli_impl.py`: `run_impl()` now accepts `lane`.
  - Updated `src/thegent/main.py`:
    - `run` and `bg` commands now expose `--lane` and `--run-id`.
    - `dag run` command now exposes `--lane` (force override) and `--max-parallel`.

### Outcome

The orchestration engine is now aware of task dependencies and priority, with support for execution lanes and parallelism control. DAG tasks can specify their own routing and lanes, providing granular control over large-scale executions.

## Chunk 233 (Phase 1 Closure: Arbitration & Confidence Routing)

### Completed

- Implemented **Conflict arbitration rules and quorum policy** and **Child-task routing by capability and confidence** (Phase 1, WP-1006 & WP-1007):
  - Updated `src/thegent/execution.py`: Added `confidence` and `arbitration` fields to `RunMeta`.
  - Updated `src/thegent/cli.py`:
    - `DagDocument`: Added default `quorum` and `confidence` columns.
    - `dag_run_cmd()`: 
      - Implemented parallel **Quorum** support: if `quorum=N` is set, spawns N background sessions.
      - Supports multi-agent quorum if `agent` is a comma-separated list.
      - Implemented **Confidence-aware routing**: if `confidence < min_confidence` (default 0.85), automatically upgrades to a 2-agent quorum (leader/follower) for verification.
      - Assigns `arbitration` roles (`leader`, `follower`) to quorum runs.
    - `dag_sync_cmd()`: Now waits for all sessions in a quorum to finish and evaluates terminal status based on consensus.
    - `history_cmd()`: Now displays `Conf` and `Role` columns in terminal history.
  - Updated `src/thegent/main.py`: `run` and `bg` commands now expose `--confidence` and `--arbitration` flags.
  - Updated `src/thegent/cli_impl.py`: `run_impl()` now accepts `confidence`.

### Outcome

Phase 1 (Core Routing and Deterministic Execution) is now complete. Thegent can now perform multi-agent consensus, handle low-confidence tasks with automated quorum escalation, and track the arbitration roles of every run in the registry.

## Chunk 235 (Full Phase: Reliability & Recovery Hardening)

### Completed

- Implemented full **Phase 2: Reliability and Recovery Hardening** (WP-2004, WP-2005, WP-2006, WP-2007, WP-2008):
  - **Failure Taxonomy (WP-2005)**: 
    - Added `error_class` to `RunMeta` and `RunRegistry`.
    - `run_impl` now classifies failures into `timeout`, `usage_limit`, or `api_error` for better audit clustering.
  - **Evidence Linting (WP-2007)**:
    - Updated `thegent dag validate` to check for evidence completeness. It now fails if a task is marked `done` but has no session/evidence linked.
  - **Oversight Path & Retry Logic (WP-2008)**:
    - Added `retry_count` and `max_retries` columns to the DAG table.
    - `thegent dag run` now automatically retries failed tasks if `retry_count < max_retries`.
    - Once retries are exhausted, the task remains `failed`, triggering the manual oversight path.
  - **Recovery Playbooks (WP-2004)**:
    - Added `thegent dag recover`. Supported actions: `retry-failed` (bulk reset), `clear-stuck` (reset running), and `reset-retries`.
  - **Regression Probes (WP-2006)**:
    - Added `thegent dag probe`. It compares the current DAG state against a baseline checkpoint to detect drift or regressions in the orchestration plan.

### Outcome

Phase 2 is now complete. Thegent provides a production-grade recovery framework with automated retries, failure classification, state-drift detection, and evidence-integrity checks.

## Chunk 236 (Full Phase: Governance & Security Enforcement)

### Completed

- Implemented full **Phase 3: Governance and Security Enforcement** (WP-3001, WP-3002, WP-3003, WP-3004, WP-3005, WP-3007):
  - **Policy Engine (WP-3001)**: Created `PolicyEngine` in `src/thegent/execution.py` to evaluate runs against governance rules.
  - **Signed Actions (WP-3002)**: Added cryptographic SHA-256 signatures to all run records to prevent tampering.
  - **Immutable Audit Trail (WP-3004)**: Implemented `thegent history verify` to audit the integrity of the entire run registry using signature verification.
  - **Governance Overrides (WP-3003)**: Added `--override` flag to `run` and `bg` commands, allowing authorized operators to bypass policy blocks with a documented reason.
  - **Trust Boundaries (WP-3007)**: Integrated environment classification (`development`, `staging`, `production`) into settings. Stricter policies (like trust score gates) are automatically enforced in `production`.
  - **Policy Visibility (WP-3005)**: Added `thegent policy show` to inspect active rules and thresholds.

### Outcome

Phase 3 is complete. Thegent now operates within a secure governance envelope. Every action is signed, every policy violation is blocked or warned, and the entire execution history is verifiable through cryptographic audits.

## Chunk 232 (Idempotency, Evidence & Phase Transitions)

### Completed

- Implemented **Idempotent execution envelope**, **Deterministic phase transition contracts**, and **Evidence capture** (Phase 1, WP-1003, WP-1004, WP-1005):
  - Updated `src/thegent/execution.py`: 
    - Added `idempotency_token` to `RunMeta`.
    - Added `RunRegistry.find_by_token(token)` to lookup existing runs by token.
  - Updated `src/thegent/cli.py`:
    - `bg_cmd()`: Now accepts `idempotency_token`. It checks the registry and reuses existing `running` or `completed` sessions if a token match is found, preventing duplicate work.
    - `dag_run_cmd()`: Now passes `dag-<tid>` as the default `idempotency_token` for each task.
    - `_dag_update_task()`: Now populates an `evidence` column with the `session_id` upon task start.
    - `_ensure_evidence_header()`: Automatically adds the `evidence` column to the DAG markdown table when needed.
  - Updated `src/thegent/main.py`: `bg` command now exposes `--idempotency-token`.

### Outcome

Orchestration is now significantly more robust with idempotency guards preventing redundant execution. The DAG now explicitly captures `evidence` (session links) for every task promotion, satisfying Phase 1 governance requirements.

## Chunk 237 (Full Phase: Human-Centered UX and Explainability)

### Completed

- Implemented full **Phase 4: Human-Centered UX and Explainability** (WP-4001, WP-4002, WP-4003, WP-4005, WP-4007):
  - **Operator Cockpit (WP-4001)**: Created `thegent cockpit` in `src/thegent/cli.py` to provide a unified summary of session health, circuit status, and recent failure rationales.
  - **Explanation Tiers & Rationale (WP-4002/WP-4007)**: Added `rationale` field to `RunMeta` and `RunRegistry`. All agent executions now capture a detailed explanation (e.g., timeout reasons, exit codes) in addition to their status.
  - **Safe Fallbacks (WP-4003)**: Enhanced `thegent dag recover --action fallback` to allow operators to quickly swap a failed task's agent for its primary fallback agent defined in the registry.
  - **State Freshness (WP-4005)**: Added a state freshness check to `thegent dag validate` that warns if the DAG file has been modified since the last recorded checkpoint.
  - **Feedback Loops (WP-4008)**: Introduced `thegent feedback` command allowing operators to calibrate confidence by scoring execution runs (0.0 to 1.0). Feedback is stored in the run registry.

### Outcome

Phase 4 is closed. Thegent now provides a "cockpit" for high-level oversight, detailed decision replay capabilities via rationale snapshots, and simplified recovery through one-click fallback orchestration.

## Chunk 240 (Full Phase: Self-healing State and Recovery)

### Completed

- Implemented full **Phase 5: Self-healing State and Recovery** (WP-5001, WP-5003, WP-5004, WP-5008):
  - **Auto-reconcile on Start (WP-5001/5003)**: Modified `dag_run_cmd` to automatically call `dag_reconcile_cmd` upon execution. This ensures any "stuck" tasks from previous crashes or interrupted sessions are reconciled (marked as failed/pending) before new tasks are started.
  - **Auto-checkpoint on Completion (WP-5004)**: Enhanced `dag_sync_cmd` to automatically create a DAG state checkpoint whenever a task reaches a terminal state (`done` or `failed`).
  - **Health-check Loop (WP-5008)**: Added a `--watch` flag to `thegent dag sync` that periodically syncs status and reconciles state, providing a persistent health-monitoring loop for long-running orchestrations.
  - **DAG Reconciliation Command (WP-5003)**: Introduced `thegent dag reconcile` to explicitly detect and fix tasks that are marked as `running` but whose underlying OS processes have terminated.

### Outcome

Phase 5 is complete. Thegent is now capable of self-healing from common orchestration failures. It automatically recovers from crashes on restart, maintains an immutable history of state transitions through auto-checkpoints, and provides active health monitoring for complex, multi-agent DAGs.

## Chunk 241 (Full Phase: Final Integration and Hardening - v1.0)

### Completed

- Implemented full **Phase 6: Final Integration and Hardening** (WP-6001, WP-6003, WP-6005, WP-6008):
  - **Resource Cleanup & Archival (WP-6005)**: Added `thegent archive` to manage session data lifecycle, moving old directories to an archive folder.
  - **Orchestration Benchmarking (WP-6001)**: Introduced `thegent benchmark` to report on latency (Avg, P90), success rates, and failure taxonomy across the last 1000 runs.
  - **Unified Documentation (WP-6003)**: Created `docs/ORCHESTRATION.md` as the definitive guide to the new architecture and command set.
  - **v1.0 Readiness (WP-6008)**: Performed a final code sweep, ensuring all phase tasks are integrated. The system is now promoted to "Thegent v1.0" status.

## Chunk 242 (Full Phase: Final Hardening and Closure Pack)

### Completed

- Implemented the final items for **Phase 6: Enterprise Readiness and Launch Closure** (WP-6002, WP-6004, WP-6006, WP-6007, FR-024):
  - **Closure Pack Generation (WP-6002/FR-024)**: Created `thegent closure-pack` to generate a formal signoff document for DAG sessions, including registry integrity, success rates, and evidence audit.
  - **Runbook Finalization (WP-6004)**: Created `docs/RUNBOOK.md` covering on-call procedures, recovery, and post-launch observation.
  - **Post-Launch & Decommissioning (WP-6006/6007)**: Integrated observation plans and sunsetting instructions into the runbook and benchmarking tools.

### Outcome

The "Orchestration Optimization Program" is now **Formally Closed**. All requirements from the PRD and WBS have been met, documented, and verified. Thegent v1.0 is now fully equipped with a professional-grade, resilient, and operator-centric orchestration core.

## Chunk 243 (Full Phase: Contract Engineering and XML Parsing - Phase-X)

### Completed

- Implemented **Phase-X: Research Validation (XML/Contract Deltas)** (WBS-X1, WBS-X2, WBS-X3, WBS-X4, WBS-X5, FR-X02, FR-X03, FR-X04):
  - **Incremental XML Parser (WBS-X3)**: Created `src/thegent/contracts/parser.py` featuring a tokenized parser capable of extracting balanced tags and detecting partial states in streaming output.
  - **Semantic Validation (WBS-X4)**: Created `src/thegent/contracts/validation.py` to enforce cross-tag invariants (e.g., status-progress coherence, mandatory summaries for completion).
  - **Provider Adapter Layer (WBS-X5)**: Enhanced `src/thegent/contracts/adapters.py` with `XMLOutputAdapter` and `GenericOutputAdapter`. Registered adapters for all major providers (`gemini`, `copilot`, `claude`, etc.).
  - **Canonical Normalization (WBS-X2)**: Integrated `normalize_output` into `cli_impl.run_impl`. All agent executions now attempt to produce a `CanonicalStructuredMessage (CSM)` along with raw output.
  - **Robust Fallback (WBS-X6)**: Updated normalization logic to provide best-effort CSM extraction from plain text if structured parsing fails.

### Outcome

Phase-X is active and its core P0/P1 items are delivered. Thegent now possesses a unified, typed contract layer for agent outputs, moving away from ad-hoc regex extraction towards a robust, schema-validated normalization pipeline.

### Outcome

The orchestration optimization program is **Complete**. Every phase from Phase 0 to Phase 6 has been delivered as a cohesive, full-phase pass. Thegent now possesses a professional-grade, resilient, and secure orchestration engine capable of managing complex multi-agent workflows with full observability and self-healing capabilities.

## Chunk 244 (Full Phase: Universal Operation Interfaces and Contract Telemetry - Phase-X)

### Completed

- Implemented **Phase-X: Research Validation (Observability & Interface Deltas)** (WBS-X7, XK1, FR-X06):
  - **Contract Telemetry (WBS-X7)**: Created `src/thegent/contracts/telemetry.py` to record normalization events, success rates, and confidence scores.
  - **Fallback Control Plane (WBS-X6)**: Implemented `src/thegent/contracts/policy.py` with `FallbackPolicy` and quality thresholds. Integrated policy evaluation into `cli_impl.run_impl`.
  - **Contract Registry (WBS-X1)**: Added `govern contracts` command to display the authoritative contract versioning and compatibility matrix from `src/thegent/contracts/registry.py`.
  - **Universal Operation Interfaces (XK1)**: Reorganized the CLI entry point in `src/thegent/main.py` into five core sub-apps: `orchestrate`, `govern`, `recover`, `observe`, and `plan`.
  - **Drift Detection**: Integrated drift detection into the `benchmark` command.

### Outcome

Phase-X extension is substantially complete. Thegent now has a professional CLI structure and deep observability into its contract normalization pipeline, enabling proactive detection of provider-side output shifts.

## Chunk 283

### Completed

- Normalized trend consumers to treat top-level `compat_aliases_count` as the source-of-truth with compatibility fallback to `len(compat.aliases)`:
  - `src/thegent/cli.py`
    - `_serialize_health_trend_md(...)` now emits `compat_aliases_count`.
    - `_serialize_health_trend_csv(...)` now includes `compat_aliases_count` column for summary and snapshot rows.
    - `_serialize_health_trend_jsonl(...)` now emits `compat_aliases_count` on both summary and snapshot records.
    - `session_contract_health_trend_cmd(...)` rich output now prints `compat_aliases_count` from top-level field with fallback.
  - `src/thegent/mcp_server.py`
    - `thegent_session_contract_health_trend(...)` metadata now prefers payload top-level `compat_aliases_count` with fallback to nested alias length.
- Extended tests to lock behavior:
  - `tests/test_unit_health_serializers.py`
    - Asserts `compat_aliases_count` appears in trend markdown/csv/jsonl outputs.
  - `tests/test_unit_mcp.py`
    - Asserts MCP trend metadata prioritizes top-level `compat_aliases_count` over nested alias-length derivation.

## Chunk 284

### Completed

- Added top-level trend field `latest_issue_types_count` in
  `session_contract_health_trend_impl(...)` (`src/thegent/cli_impl.py`) so
  downstream consumers can rely on an explicit summary counter.
- Normalized trend consumers to prefer top-level `latest_issue_types_count`
  with compatibility fallback to `len(latest.issue_types)`:
  - `src/thegent/cli.py`
    - `_serialize_health_trend_md(...)`
    - `_serialize_health_trend_csv(...)`
    - `_serialize_health_trend_jsonl(...)`
    - `session_contract_health_trend_cmd(...)` rich output.
  - `src/thegent/mcp_server.py`
    - `thegent_session_contract_health_trend(...)` metadata now uses top-level
      `latest_issue_types_count` first.
- Extended tests:
  - `tests/test_unit_health_trend.py`
    - Asserts `latest_issue_types_count == len(latest.issue_types)`.
  - `tests/test_unit_health_serializers.py`
    - Asserts JSONL summary/snapshot records honor top-level
      `latest_issue_types_count`.
  - `tests/test_unit_mcp.py`
    - Asserts MCP trend metadata prefers top-level
      `latest_issue_types_count` over nested derivation.

## Chunk 285

### Completed

- Normalized MCP trend scope metadata to prefer top-level trend scope aliases
  with compatibility fallback to nested `scope_key`:
  - `src/thegent/mcp_server.py`
    - `thegent_session_contract_health_trend(...)` metadata now resolves:
      - `scope_owner`
      - `scope_all`
      - `scope_strict`
      - `scope_policy_profile`
      - `scope_min_healthy_ratio`
      - `scope_top_blocked`
      from top-level fields first, then falls back to `scope_key`.
- Extended tests:
  - `tests/test_unit_mcp.py`
    - Added conflict-based coverage where `scope_key` values differ from
      top-level aliases and asserts metadata uses top-level values.

## Chunk 286

### Completed

- Extended trend payload with explicit top-level `latest_*` aliases in
  `session_contract_health_trend_impl(...)` (`src/thegent/cli_impl.py`):
  - `latest_status`
  - `latest_pass`
  - `latest_captured_at_utc`
  - `latest_blocked_ratio`
  - `latest_blocked_count`
- Normalized MCP trend metadata to prefer top-level `latest_*` aliases with
  compatibility fallback to nested `latest` object values:
  - `src/thegent/mcp_server.py`
    - `thegent_session_contract_health_trend(...)` metadata now resolves the
      above fields from top-level first.
- Extended tests:
  - `tests/test_unit_mcp.py`
    - Added conflict-based coverage where nested `latest` differs from top-level
      `latest_*` aliases and asserts metadata uses top-level fields.
  - `tests/test_unit_health_trend.py`
    - Asserts top-level `latest_*` aliases remain consistent with nested
      `latest` values produced by `session_contract_health_trend_impl(...)`.

## Chunk 287

### Completed

- Extended trend payload with explicit top-level delta aliases in
  `session_contract_health_trend_impl(...)` (`src/thegent/cli_impl.py`):
  - `blocked_ratio_delta`
  - `blocked_count_delta`
- Normalized trend consumers to prefer top-level delta aliases with fallback to
  nested `delta_summary`:
  - `src/thegent/cli.py`
    - Trend rich output now resolves delta fields from top-level first.
    - Trend CSV serializer now resolves summary/snapshot delta columns from
      top-level first.
    - Trend JSONL serializer snapshot records now include top-level delta aliases
      with fallback.
  - `src/thegent/mcp_server.py`
    - `thegent_session_contract_health_trend(...)` metadata now resolves
      `blocked_ratio_delta` and `blocked_count_delta` from top-level first.
- Extended tests:
  - `tests/test_unit_health_trend.py`
    - Asserts top-level delta aliases remain consistent with nested
      `delta_summary` in generated trend payloads.
  - `tests/test_unit_health_serializers.py`
    - Asserts trend CSV summary/snapshot rows use top-level delta alias values.
    - Asserts trend JSONL snapshot record carries top-level delta alias values.
  - `tests/test_unit_mcp.py`
    - Added conflict-based coverage where top-level delta aliases differ from
      nested `delta_summary` and asserts MCP metadata uses top-level values.

## Chunk 288

### Completed

- Normalized trend serializers to prefer top-level `latest_*` aliases with
  compatibility fallback to nested `latest` fields:
  - `src/thegent/cli.py`
    - `_serialize_health_trend_md(...)`
    - `_serialize_health_trend_csv(...)`
    - `_serialize_health_trend_jsonl(...)`
  - Preferred fields:
    - `latest_status`
    - `latest_pass`
    - `latest_captured_at_utc`
    - `latest_blocked_ratio`
    - `latest_blocked_count`
- Extended serializer tests with precedence coverage:
  - `tests/test_unit_health_serializers.py`
    - CSV summary/snapshot rows now asserted to use top-level `latest_*` values.
    - JSONL summary/snapshot records now asserted to use top-level `latest_*`
      values when present.

## Chunk 289

### Completed

- Extended trend payload with explicit top-level `scope_payload_type` alias in
  `session_contract_health_trend_impl(...)` (`src/thegent/cli_impl.py`).
- Normalized trend consumers to prefer top-level `scope_payload_type` with
  fallback to `scope_key.payload_type`:
  - `src/thegent/cli.py`
    - `_serialize_health_trend_md(...)`
    - `_serialize_health_trend_csv(...)`
    - `_serialize_health_trend_jsonl(...)`
  - `src/thegent/mcp_server.py`
    - `thegent_session_contract_health_trend(...)` metadata now includes
      `scope_payload_type` with top-level-first resolution.
- Extended tests:
  - `tests/test_unit_health_trend.py`
    - Asserts generated trend payload includes `scope_payload_type`.
  - `tests/test_unit_health_serializers.py`
    - Asserts trend md/csv/jsonl include and prioritize top-level
      `scope_payload_type`.
  - `tests/test_unit_mcp.py`
    - Asserts MCP trend metadata includes and prioritizes top-level
      `scope_payload_type`.

## Chunk 290

### Completed

- Extended trend payload with explicit top-level `scope_key_json` alias in
  `session_contract_health_trend_impl(...)` (`src/thegent/cli_impl.py`) for
  stable, deterministic string transport of scope identity.
- Normalized trend consumers to prefer top-level `scope_key_json` with fallback
  to stable serialization of `scope_key`:
  - `src/thegent/cli.py`
    - `_serialize_health_trend_md(...)` now emits `scope_key_json`.
    - `_serialize_health_trend_csv(...)` now includes `scope_key_json` column
      and value for summary/snapshot rows.
    - `_serialize_health_trend_jsonl(...)` now emits `scope_key_json` on
      summary/snapshot records.
  - `src/thegent/mcp_server.py`
    - `thegent_session_contract_health_trend(...)` metadata now includes
      `scope_key_json` with top-level-first resolution.
- Extended tests:
  - `tests/test_unit_health_trend.py`
    - Asserts generated `scope_key_json` matches deterministic serialization of
      `scope_key`.
  - `tests/test_unit_health_serializers.py`
    - Asserts trend md/csv/jsonl include and prioritize top-level
      `scope_key_json`.
  - `tests/test_unit_mcp.py`
    - Asserts MCP trend metadata includes and prioritizes top-level
      `scope_key_json`.

## Chunk 291

### Completed

- Extended trend payload with explicit top-level `delta_summary_json` alias in
  `session_contract_health_trend_impl(...)` (`src/thegent/cli_impl.py`) using
  deterministic sorted-key JSON encoding of `delta_summary`.
- Normalized trend consumers to prefer top-level `delta_summary_json` with
  compatibility fallback to stable serialization of nested `delta_summary`:
  - `src/thegent/cli.py`
    - `_serialize_health_trend_md(...)` now emits `delta_summary_json`.
    - `_serialize_health_trend_csv(...)` now includes `delta_summary_json`
      column and values for summary/snapshot rows.
    - `_serialize_health_trend_jsonl(...)` now emits `delta_summary_json` on
      summary/snapshot records.
  - `src/thegent/mcp_server.py`
    - `thegent_session_contract_health_trend(...)` metadata now includes
      `delta_summary_json` with top-level-first resolution.
- Extended tests:
  - `tests/test_unit_health_trend.py`
    - Asserts generated `delta_summary_json` matches deterministic serialization
      of `delta_summary`.
  - `tests/test_unit_health_serializers.py`
    - Asserts trend md/csv/jsonl include and prioritize top-level
      `delta_summary_json`.
  - `tests/test_unit_mcp.py`
    - Asserts MCP trend metadata includes and prioritizes top-level
      `delta_summary_json`.

## Chunk 292

### Completed

- Extended trend payload with explicit top-level `latest_issue_types_csv` alias
  in `session_contract_health_trend_impl(...)` (`src/thegent/cli_impl.py`).
- Normalized trend consumers to prefer top-level `latest_issue_types_csv` with
  compatibility fallback to CSV join of nested `latest.issue_types`:
  - `src/thegent/cli.py`
    - `_serialize_health_trend_md(...)` now emits `latest_issue_types_csv`.
    - `_serialize_health_trend_csv(...)` now includes `latest_issue_types_csv`
      column and values for summary/snapshot rows.
    - `_serialize_health_trend_jsonl(...)` now emits `latest_issue_types_csv`
      on summary/snapshot records.
  - `src/thegent/mcp_server.py`
    - `thegent_session_contract_health_trend(...)` metadata now includes
      `latest_issue_types_csv` with top-level-first resolution.
- Extended tests:
  - `tests/test_unit_health_trend.py`
    - Asserts generated `latest_issue_types_csv` matches CSV join of nested
      `latest.issue_types`.
  - `tests/test_unit_health_serializers.py`
    - Asserts trend md/csv/jsonl include and prioritize top-level
      `latest_issue_types_csv`.
  - `tests/test_unit_mcp.py`
    - Asserts MCP trend metadata includes and prioritizes top-level
      `latest_issue_types_csv`.

## Chunk 293

### Completed

- Extended trend payload with explicit top-level `latest_issue_types_json`
  alias in `session_contract_health_trend_impl(...)`
  (`src/thegent/cli_impl.py`).
- Normalized trend consumers to prefer top-level `latest_issue_types_json`
  with compatibility fallback to JSON serialization of nested
  `latest.issue_types`:
  - `src/thegent/cli.py`
    - `_serialize_health_trend_md(...)` now emits `latest_issue_types_json`.
    - `_serialize_health_trend_csv(...)` now includes `latest_issue_types_json`
      column and values for summary/snapshot rows.
    - `_serialize_health_trend_jsonl(...)` now emits `latest_issue_types_json`
      on summary/snapshot records.
  - `src/thegent/mcp_server.py`
    - `thegent_session_contract_health_trend(...)` metadata now includes
      `latest_issue_types_json` with top-level-first resolution.
- Extended tests:
  - `tests/test_unit_health_trend.py`
    - Asserts generated `latest_issue_types_json` matches JSON serialization of
      nested `latest.issue_types`.
  - `tests/test_unit_health_serializers.py`
    - Asserts trend md/csv/jsonl include and prioritize top-level
      `latest_issue_types_json`.
  - `tests/test_unit_mcp.py`
    - Asserts MCP trend metadata includes and prioritizes top-level
      `latest_issue_types_json`.

## Chunk 294

### Completed

- Extended trend payload with explicit top-level `latest_issue_types_hash`
  alias in `session_contract_health_trend_impl(...)`
  (`src/thegent/cli_impl.py`), derived from SHA-256 of
  `latest_issue_types_json`.
- Closed a parity gap by also emitting explicit top-level
  `latest_issue_types_csv` in `session_contract_health_trend_impl(...)`.
- Normalized trend consumers to prefer top-level
  `latest_issue_types_json`/`latest_issue_types_hash` with compatibility
  fallback:
  - `src/thegent/cli.py`
    - `_serialize_health_trend_md(...)` now emits both aliases.
    - `_serialize_health_trend_csv(...)` now includes
      `latest_issue_types_json` and `latest_issue_types_hash` columns/values
      for summary/snapshot rows.
    - `_serialize_health_trend_jsonl(...)` now emits both aliases on
      summary/snapshot records.
  - `src/thegent/mcp_server.py`
    - `thegent_session_contract_health_trend(...)` metadata now includes
      `latest_issue_types_hash` with top-level-first resolution and deterministic
      fallback hashing.
- Extended tests:
  - `tests/test_unit_health_trend.py`
    - Asserts generated `latest_issue_types_hash` matches SHA-256 of
      `latest_issue_types_json`.
  - `tests/test_unit_health_serializers.py`
    - Asserts trend md/csv/jsonl include and prioritize top-level
      `latest_issue_types_hash`.
  - `tests/test_unit_mcp.py`
    - Asserts MCP trend metadata includes and prioritizes top-level
      `latest_issue_types_hash`.

## Chunk 295

### Completed

- Extended trend payload with top-level snapshot identity aliases in
  `session_contract_health_trend_impl(...)` (`src/thegent/cli_impl.py`):
  - `snapshot_ids_csv` (comma-separated `captured_at_utc` values from
    `snapshots`).
  - `snapshot_ids_hash` (SHA-256 digest of `snapshot_ids_csv`).
- Normalized trend consumers to prefer top-level snapshot identity aliases with
  compatibility fallback derived from `snapshots`:
  - `src/thegent/cli.py`
    - `_serialize_health_trend_md(...)` now emits
      `snapshot_ids_csv`/`snapshot_ids_hash`.
    - `_serialize_health_trend_csv(...)` now includes
      `snapshot_ids_csv`/`snapshot_ids_hash` columns and values for summary and
      snapshot rows.
    - `_serialize_health_trend_jsonl(...)` now emits
      `snapshot_ids_csv`/`snapshot_ids_hash` on summary and snapshot records.
  - `src/thegent/mcp_server.py`
    - `thegent_session_contract_health_trend(...)` metadata now includes
      `snapshot_ids_csv`/`snapshot_ids_hash` with top-level-first fallback.
- Extended tests:
  - `tests/test_unit_health_trend.py`
    - Asserts generated `snapshot_ids_csv` and `snapshot_ids_hash` match
      deterministic derivation from trend snapshots.
  - `tests/test_unit_health_serializers.py`
    - Asserts trend md/csv/jsonl include and prioritize top-level
      `snapshot_ids_csv` and `snapshot_ids_hash`.
  - `tests/test_unit_mcp.py`
    - Asserts MCP trend metadata includes and prioritizes top-level
      `snapshot_ids_csv` and `snapshot_ids_hash`.

## Chunk 296

### Completed

- Extended trend payload with temporal-window aliases in
  `session_contract_health_trend_impl(...)` (`src/thegent/cli_impl.py`):
  - `snapshot_window_seconds`
    - Derived from `latest.captured_at_utc - oldest.captured_at_utc` when
      multiple snapshots exist and timestamps are parseable.
  - `snapshot_window_hash`
    - SHA-256 digest of `str(snapshot_window_seconds)`.
- Normalized trend consumers to prefer top-level
  `snapshot_window_seconds`/`snapshot_window_hash` with deterministic fallback:
  - `src/thegent/cli.py`
    - `_serialize_health_trend_md(...)` now emits
      `snapshot_window_seconds` and `snapshot_window_hash`.
    - `_serialize_health_trend_csv(...)` now includes both fields in header and
      summary/snapshot rows.
    - `_serialize_health_trend_jsonl(...)` now emits both fields on summary and
      snapshot records.
  - `src/thegent/mcp_server.py`
    - `thegent_session_contract_health_trend(...)` metadata now includes both
      fields with top-level-first resolution.
- Extended tests:
  - `tests/test_unit_health_trend.py`
    - Asserts generated window fields match expected derivation and hash.
  - `tests/test_unit_health_serializers.py`
    - Asserts trend md/csv/jsonl include and prioritize top-level window fields.
  - `tests/test_unit_mcp.py`
    - Asserts MCP trend metadata includes and prioritizes top-level window
      fields.

## Chunk 297

### Completed

- Closed serializer consistency defects for trend temporal-window aliases in
  `src/thegent/cli.py`:
  - Removed duplicate local assignments of
    `snapshot_window_seconds`/`snapshot_window_hash` in
    `_serialize_health_trend_md(...)`.
  - Added missing local definitions for
    `snapshot_window_seconds`/`snapshot_window_hash` in
    `_serialize_health_trend_jsonl(...)` before summary/snapshot emission.
- Result: all three trend serializers (md/csv/jsonl) now have a single,
  consistent top-level-first resolution path for window aliases.

## Chunk 298

### Completed

- Promoted trend snapshot-interval aliases end-to-end for
  `session_contract_health_trend`:
  - `snapshot_interval_seconds_avg`
  - `snapshot_interval_hash`
- Normalized trend serializer outputs in `src/thegent/cli.py`:
  - `_serialize_health_trend_md(...)` now emits both interval fields.
  - `_serialize_health_trend_csv(...)` now includes both interval fields in the
    header and in summary/snapshot rows.
  - `_serialize_health_trend_jsonl(...)` now emits both interval fields on
    summary/snapshot records with top-level-first fallback hashing.
- Extended MCP tool metadata in `src/thegent/mcp_server.py`:
  - `thegent_session_contract_health_trend(...)` now exposes
    `snapshot_interval_seconds_avg` and `snapshot_interval_hash`.
- Extended tests:
  - `tests/test_unit_health_trend.py`
    - Asserts impl-level interval aliases and deterministic hash.
  - `tests/test_unit_health_serializers.py`
    - Asserts md/csv/jsonl include and prioritize top-level interval aliases.
  - `tests/test_unit_mcp.py`
    - Asserts MCP trend metadata includes and prioritizes interval aliases.

## Chunk 299

### Completed

- Added trend snapshot freshness aliases end-to-end for
  `session_contract_health_trend`:
  - `snapshot_freshness_seconds`
  - `snapshot_freshness_hash`
- Extended impl derivation in `src/thegent/cli_impl.py`:
  - Captures a single `generated_at` timestamp for payload consistency.
  - Computes freshness as `generated_at - latest.captured_at_utc` when latest
    snapshot timestamp is parseable.
  - Emits deterministic freshness hash from `str(snapshot_freshness_seconds)`.
- Normalized trend serializer outputs in `src/thegent/cli.py`:
  - `_serialize_health_trend_md(...)` now emits freshness aliases.
  - `_serialize_health_trend_csv(...)` now includes freshness aliases in header
    and summary/snapshot rows.
  - `_serialize_health_trend_jsonl(...)` now emits freshness aliases on
    summary/snapshot records.
- Extended MCP metadata in `src/thegent/mcp_server.py`:
  - `thegent_session_contract_health_trend(...)` now exposes freshness aliases
    with top-level-first fallback hashing.
- Extended tests:
  - `tests/test_unit_health_trend.py`
    - Asserts freshness hash determinism and integer type when present.
  - `tests/test_unit_health_serializers.py`
    - Asserts md/csv/jsonl include and prioritize top-level freshness aliases.
  - `tests/test_unit_mcp.py`
    - Asserts MCP trend metadata includes and prioritizes freshness aliases.

## Chunk 300

### Completed

- Added trend snapshot-density aliases end-to-end for
  `session_contract_health_trend`:
  - `snapshot_density_per_hour`
  - `snapshot_density_hash`
- Extended impl derivation in `src/thegent/cli_impl.py`:
  - Derives density from snapshot cadence as:
    `snapshot_count * 3600 / snapshot_window_seconds` when window is positive.
  - Emits deterministic density hash from `str(snapshot_density_per_hour)`.
- Normalized trend serializer outputs in `src/thegent/cli.py`:
  - `_serialize_health_trend_md(...)` now emits density aliases.
  - `_serialize_health_trend_csv(...)` now includes density aliases in header
    and summary/snapshot rows.
  - `_serialize_health_trend_jsonl(...)` now emits density aliases on
    summary/snapshot records.
- Extended MCP metadata in `src/thegent/mcp_server.py`:
  - `thegent_session_contract_health_trend(...)` now exposes density aliases
    with top-level-first fallback hashing.
- Extended tests:
  - `tests/test_unit_health_trend.py`
    - Asserts impl-level density value and deterministic hash.
  - `tests/test_unit_health_serializers.py`
    - Asserts md/csv/jsonl include and prioritize top-level density aliases.
  - `tests/test_unit_mcp.py`
    - Asserts MCP trend metadata includes and prioritizes density aliases.

## Chunk 301

### Completed

- Added trend issue-churn aliases end-to-end for
  `session_contract_health_trend`:
  - `snapshot_issue_churn_count`
  - `snapshot_issue_churn_hash`
- Extended impl derivation in `src/thegent/cli_impl.py`:
  - Computes issue churn as symmetric-difference cardinality between
    `latest.issue_types` and `oldest.issue_types` sets.
  - Emits deterministic churn hash from `str(snapshot_issue_churn_count)`.
- Normalized trend serializer outputs in `src/thegent/cli.py`:
  - `_serialize_health_trend_md(...)` now emits churn aliases.
  - `_serialize_health_trend_csv(...)` now includes churn aliases in header and
    summary/snapshot rows.
  - `_serialize_health_trend_jsonl(...)` now emits churn aliases on
    summary/snapshot records.
- Extended MCP metadata in `src/thegent/mcp_server.py`:
  - `thegent_session_contract_health_trend(...)` now exposes churn aliases with
    top-level-first fallback hashing.
- Extended tests:
  - `tests/test_unit_health_trend.py`
    - Asserts impl-level churn value and deterministic hash.
  - `tests/test_unit_health_serializers.py`
    - Asserts md/csv/jsonl include and prioritize top-level churn aliases.
  - `tests/test_unit_mcp.py`
    - Asserts MCP trend metadata includes and prioritizes churn aliases.

## Chunk 302

### Completed

- Added trend health-volatility aliases end-to-end for
  `session_contract_health_trend`:
  - `snapshot_health_volatility`
  - `snapshot_health_volatility_hash`
- Extended impl derivation in `src/thegent/cli_impl.py`:
  - Computes volatility as the population standard deviation of blocked ratio
    values across snapshots:
    `sqrt(mean((ratio_i - mean_ratio)^2))`.
  - Emits deterministic volatility hash from `str(snapshot_health_volatility)`.
- Normalized trend serializer outputs in `src/thegent/cli.py`:
  - `_serialize_health_trend_md(...)` now emits both volatility fields.
  - `_serialize_health_trend_csv(...)` now includes both volatility fields in the
    header and in summary/snapshot rows.
  - `_serialize_health_trend_jsonl(...)` now emits both volatility fields on
    summary/snapshot records.
- Extended MCP metadata in `src/thegent/mcp_server.py`:
  - `thegent_session_contract_health_trend(...)` now exposes volatility aliases
    with top-level-first fallback hashing.
  - Extended tests:
  - `tests/test_unit_health_trend.py`
    - Asserts impl-level volatility value and deterministic hash.
  - `tests/test_unit_health_serializers.py`
    - Asserts md/csv/jsonl include and prioritize top-level volatility aliases.
  - `tests/test_unit_mcp.py`
    - Asserts MCP trend metadata includes and prioritizes top-level volatility
      aliases.

## Chunk 303

### Completed

- Added fallback hardening for volatility aliases when upstream trend output omits
  them:
  - `_serialize_health_trend_md(...)`:
    - Confirms `snapshot_health_volatility` / hash render as stable fallback using
      `None` + `sha256("None")` when not supplied.
  - `_serialize_health_trend_csv(...)`:
    - Confirms fallback values are included in header and both summary/snapshot rows.
  - `_serialize_health_trend_jsonl(...)`:
    - Confirms fallback values are included in both summary/snapshot objects.
- Extended MCP contract coverage in `tests/test_unit_mcp.py`:
  - Added regression test that missing trend volatility aliases in tool input still
    produce deterministic `result.meta["snapshot_health_volatility"]` and
    `snapshot_health_volatility_hash`.
- Extended impl regression in `tests/test_unit_health_trend.py`:
  - Added single-snapshot volatility guard case asserting:
    - `snapshot_health_volatility is None`
    - deterministic hash is `sha256("None")`.
 - Extended serializer regression in `tests/test_unit_health_serializers.py`:
   - Added md/csv/jsonl fallback tests for missing volatility aliases.

## Chunk 304

### Completed

- Added compatibility robustness coverage in trend serializers for missing optional fields:
  - `tests/test_unit_health_serializers.py`
    - Added CSV default test for missing `compat`/`compat_aliases_count`:
      - summary row emits `compat_mode = "compat"`.
      - summary row emits `compat_aliases_json = "{}"`.
      - summary row emits `compat_aliases_count = 0`.
  - Added JSONL default test for missing `compat` with no snapshots:
    - summary-only output still includes `compat = {"mode": "compat", "aliases": {}}`.
    - `compat_aliases_count` remains `0`.

## Chunk 305

### Completed

- Hardened trend issue-types normalization across impl/serializer/MCP for malformed `issue_types` payloads:
  - `src/thegent/cli_impl.py`
    - Added `_coerce_issue_types(value)` helper and wired it into:
      - `session_contract_health_trend_impl()` latest/oldest issue-type derivation.
      - `snapshot_issue_churn_count` and latest issue-type aliases in payload (`latest_issue_types_*` fields).
      - Snapshot persistence pipeline `_append_health_snapshot()` issue extraction from blocked sessions.
    - Result: malformed shapes (`None`, scalar strings, dicts) no longer produce character-level expansion.
  - `src/thegent/cli.py`
    - Reused `_coerce_issue_types` in trend markdown/csv/jsonl serializers for:
      - `latest_issue_types_*` computed fallbacks.
      - per-snapshot `issue_types` rendering.
    - Result: malformed `latest.issue_types` and `snapshots[*].issue_types` now stringify deterministically.
  - `src/thegent/mcp_server.py`
    - Reused `_coerce_issue_types` in MCP trend tool meta derivation for `latest_issue_types_*` fallbacks.
    - Result: MCP meta fields maintain deterministic behavior even with malformed trend payloads.
- Extended regressions:
  - `tests/test_unit_health_trend.py`
    - Added malformed-issue-types input fixture test covering trend computation with scalar `latest.issue_types` and dict `oldest.issue_types`.
    - Verified `snapshot_issue_churn_count` stability and normalized `latest_issue_types_*`.
  - `tests/test_unit_health_serializers.py`
    - Added trend serializer normalization test for scalar latest issues and dict snapshot issues across md/csv/jsonl.
  - `tests/test_unit_mcp.py`
    - Added trend tool meta normalization test when `latest.issue_types` is malformed.

## Chunk 306

### Completed

- Closed remaining regression gaps in trend serialization robustness:
  - `src/thegent/cli.py`
    - Added missing `_coerce_issue_types` import from `thegent.cli_impl` for trend serializer support.
    - Completed fallback normalization for `_serialize_health_trend_md(...)`:
      - `latest_issue_types_count` and `latest_issue_types_csv` now consistently use normalized issue-type vectors.
      - Removed raw `latest.issue_types` fallbacks from those fields.
    - Completed fallback normalization for `_serialize_health_trend_csv(...)` and
      `_serialize_health_trend_jsonl(...)`:
      - Added normalized `latest_issue_types` vector derivation once per call.
      - Used normalization for computed `latest_issue_types_*` fallbacks in summary and snapshot rows.
      - Kept snapshot-level issue-type rendering in CSV as normalized `", ".join(_coerce_issue_types(...))`.
    - Completed diagnostic print fallback in trend console path to use normalized latest issue type count.
  - `src/thegent/mcp_server.py`
    - Tightened `latest_issue_types_hash` fallback in trend MCP meta derivation to hash normalized issue-types, not raw nested values.
- This resolves remaining inconsistencies between implemented hardening intent and `cli.py`/`mcp_server.py` behavior for malformed `latest.issue_types` payloads in CLI, JSONL, CSV, and MCP meta output paths.

## Chunk 307

### Completed

- Continued hardening for issue-shape robustness in health trend/report aggregation:
  - `src/thegent/cli_impl.py`
    - Normalized `contract_issues` when building report issue counts and blocked row issues:
      - `session_contract_health_report_impl()` now uses `_coerce_issue_types(...)` for:
        - `issue_counts` accumulation.
        - blocked row `"issues"` emission.
    - Normalized blocker issues when computing `current_issue_types` in
      `session_contract_health_gate_impl()`, preventing character-level expansion on malformed issue strings.
  - `tests/test_unit_health_trend.py`
    - Added regression test `test_health_report_impl_normalizes_contract_issues_for_issues_counts_and_rows`:
      - verifies a scalar `contract_issues` value is treated as one issue token.
      - verifies blocked row issue rendering uses normalized lists.
    - Existing gate-trend regression still validates malformed `issue_types` + malformed blocked-session issue vectors and trend churn deltas.

## Chunk 308

### Completed

- Hardened CLI-facing session contract audit render path for malformed issue vectors:
  - `src/thegent/cli.py`
    - `session_contract_health_audit_cmd(...)` markdown and table renderers now normalize
      `contract_issues` via `_coerce_issue_types(...)` before formatting.
    - Prevents scalar string issue payloads from rendering as character-split lists in outputs.

## Chunk 309

### Completed

- Cleaned `session_contract_health_gate_impl()` blocker normalization path:
  - `src/thegent/cli_impl.py`
    - Gate blockers now store normalized `issues` vectors immediately via
      `_coerce_issue_types(row.get("contract_issues"))` at construction time,
      eliminating one possible normalization boundary before delta derivation.

## Chunk 310

### Completed

- Added persistence-layer regression guard for malformed blocked-session issues:
  - `tests/test_unit_health_trend.py`
    - Added `test_health_gate_impl_appends_normalized_issue_types_for_blocked_sessions`.
    - Simulates gate execution with scalar `contract_issues` on blocked sessions.
    - Verifies persisted snapshot `issue_types` is stored as `["missing_contract:provider"]`
      (not split characters), proving `_append_health_snapshot` and blocker normalization
      remain robust for scalar issue payloads.

## Chunk 311

### Completed

- Hardened remaining health output paths against scalar issue payloads:
  - `src/thegent/cli.py`
    - Normalized blocked-session/report `issues` joins across all report serializers:
      - `_serialize_health_report_md`
      - `_serialize_health_report_csv`
      - `_serialize_health_report_jsonl`
      - `_serialize_health_gate_csv`/`_serialize_health_gate_jsonl` blockers
  - `session_contract_health_report_cmd` console rendering
  - `_serialize_health_trend` console output (top blocked sessions view)

## Chunk 312

### Completed

- Expanded incremental parser regression coverage for stream truncation and partial-state safety (`XA3`):
  - `tests/test_unit_contracts.py`
    - Added `TestIncrementalXMLParser`.
    - Added regression for allowed-tag filtering and case-insensitive parse on mixed-case XML tags (`extract_tags` + `IncrementalXMLParser.parse`).
    - Added regression for partial-state capture with unclosed nested tags (`get_partial_state` returns stable `open_tag`, `partial_content`, and `is_truncated`).
    - Added regression for incomplete trailing tag prefixes (`incomplete_tag` path).
    - Added regression for fully closed markup (`is_truncated=False`, no open tags).
- Coverage now pins parser behavior for the common truncation modes seen in streamed LLM output:
  - open tag not closed by stream end,
  - raw trailing tag prefix,
  - fully closed balanced XML.
- This closes the immediate verification gap for XA3’s partial-state behavior; next hardening can now focus on explicit partial-commit policy/error-budget controls.

## Chunk 313

### Completed

- Extended contract adapter regression coverage for truncation handling (`XA3` + resilience):
  - `tests/test_unit_contracts.py`
    - Added `TestXMLOutputAdapter`.
    - Added regression for truncated XML input via `normalize_output("gemini", "<SUMMARY>running<DETAILS>work")`:
      - asserts `parse_truncated` is surfaced as a parse error,
      - asserts result status remains `CSMStatus.PENDING`,
      - asserts confidence is `0.0`.
  - Added regression for complete XML payload parse:
      - asserts parse errors are empty,
      - asserts status resolves to `CSMStatus.COMPLETED`,
      - asserts summary mapping is preserved.
  - This verifies `XMLOutputAdapter` does not treat truncated payloads as final and that complete tags are accepted with status-summary mapping.

## Chunk 314

### Completed

- Hardened `observe_summary` into a configurable operator cockpit signal (`FR-X08`):
  - `src/thegent/contracts/telemetry.py`
    - Extended `ContractTelemetry.get_fallback_kpis(...)` with optional provider filtering (`provider`) for focused KPI slices.
  - `src/thegent/cli_impl.py`
    - Expanded `observe_summary_impl(...)` with parameters:
      - `structural_budget_pct`, `semantic_budget_pct` (no hardcoded budgets)
      - `provider` (provider-scoped telemetry KPIs)
      - `top_escalations` (controlled escalation snapshot size)
    - Added robust past-SLA backlog shaping and timing projection:
      - `past_sla_count`, `backlog_count`, `top_escalations`
      - per-item `minutes_overdue` / `minutes_remaining`
      - blocked-run ordering by SLA urgency and priority
    - Added summary-level health fields: `status` (`healthy|critical`) and actionable `alerts`.
  - `src/thegent/cli.py`
    - `observe_summary_cmd(...)` now passes new budget/provider/escalation options.
    - Rich panel now prints explicit budget baselines, provider scope, actionable alerts, and top escalation rows.
  - `src/thegent/main.py`
    - `observe summary` command exposes config knobs for:
      - `--structural-budget`
      - `--semantic-budget`
      - `--provider`
      - `--top-escalations`

- Expanded test coverage for the observability path and CLI contract:
  - `tests/test_unit_cli.py`
    - Added `TestObserveSummaryImpl` with explicit verification of:
      - propagated budgets and provider filter into telemetry path,
      - backlog projection fields,
      - escalated-alert behavior.
  - `tests/test_e2e_cli.py`
    - Added `TestObserveSummaryCustom` for JSON-mode summary and custom budgets/provider options.

- This chunk closes a key gap between FR-X08 implementation and operator usability:
  `observe summary` is now actionable, budget-configurable, and provider-aware for handoff-ready cockpit reporting.

## Chunk 315

### Completed

- Exposed `observe summary` through MCP for direct agent/automation consumption (`FR-X08` completion loop):
  - `src/thegent/mcp_server.py`
    - Added `thegent_observe_summary` MCP tool wrapper over `observe_summary_impl` with configurable:
      - `limit`
      - `drift_window`
      - `structural_budget_pct`
      - `semantic_budget_pct`
      - `provider`
      - `top_escalations`
    - Added `thegent://observe/summary` MCP resource with matching params for URL-style retrieval.
    - Added `thegent_observe_summary` entry to `TOOL_ICONS` for discovery ergonomics.
  - `tests/test_unit_mcp.py`
    - Added `TestMCPObserveSummaryContract` covering:
      - tool payload parity + key metadata projections,
      - resource JSON payload structure.
- This chunk enables end-to-end consistency between CLI and MCP operator workflows: one canonical `observe_summary_impl` contract with both interactive and tool-based access paths.

## Chunk 316

### Completed

- Added discoverability and schema contract hardening for `observe summary` payloads:
  - `src/thegent/cli_impl.py`
    - Added observe-summary metadata constants:
      - `OBSERVE_SUMMARY_SCHEMA_VERSION = "observe-summary-schema-v1"`
      - `OBSERVE_SUMMARY_PAYLOAD_TYPES`
    - Extended `get_server_meta_impl()` to publish:
      - `observe_summary_payload_schema_version`
      - `observe_summary_payload_types`
    - Extended `observe_summary_impl()` return payload with:
      - `payload_type`
      - `payload_schema_version`
  - `src/thegent/mcp_server.py`
    - Augmented `thegent_observe_summary` MCP tool meta with:
      - `payload_type`
      - `payload_schema_version`
  - `tests/test_unit_mcp.py`
    - Expanded meta contract assertions for discoverability fields.
    - Added `thegent_observe_summary` meta assertions for `payload_type` + `payload_schema_version`.

- This chunk closes another important interoperability gap so MCP clients can feature-detect and normalize `observe summary` outputs via declared schema metadata.

## Chunk 317

### Completed

- Extended contract validation in CLI end-to-end tests for discoverability metadata:
  - `tests/test_e2e_cli.py`
    - `TestObserveSummaryCustom.test_observe_summary_format_json_exits_zero` now asserts:
      - `payload["payload_type"] == "observe_summary"`
      - `payload["payload_schema_version"] == "observe-summary-schema-v1"`
    - `TestObserveSummaryCustom.test_observe_summary_custom_budgets_provider_exits_zero` now asserts the same metadata fields in addition to budget/provider checks.

- This chunk ensures CLI JSON mode exposes the same schema-tagged payload contract that MCP now publishes, improving cross-channel parity checks in automation.

## Chunk 318

### Completed

- Added historical trend and delta context to `observe summary`:
  - `src/thegent/cli_impl.py`
    - Extended `observe_summary_impl(...)` with:
      - `trend_samples` parameter,
      - snapshot persistence for observe-summary snapshots via shared snapshot log (`record_type="observe_summary_snapshot"`),
      - scoped historical lookup via `_load_previous_observe_summary_snapshots`,
      - computed `trend_summary` deltas for totals, drift KPIs, confidence, and backlog counters.
    - Added `generated_query` and top-level `trend_summary` in payload for reproducible trend-context introspection.
    - Added `_append_observe_summary_snapshot` + generic snapshot lookup helpers.
  - `src/thegent/cli.py`
    - `observe_summary_cmd(...)` accepts `trend_samples`.
    - Rich summary panel now prints trend status and delta context when enabled.
  - `src/thegent/main.py`
    - `observe summary` command now exposes `--trend-samples` with safe defaults.
  - `src/thegent/mcp_server.py`
    - `thegent://observe/summary` resource and `thegent_observe_summary` tool now accept `trend_samples`.
    - MCP tool metadata now projects trend summary fields (`trend_enabled`, `trend_*_delta`, sample metadata) for orchestration-level reads.

- Added trend regression and parity tests:
  - `tests/test_unit_cli.py`
    - `TestObserveSummaryImpl::test_observe_summary_impl_with_trend_samples`.
  - `tests/test_unit_mcp.py`
    - Expanded `TestMCPObserveSummaryContract` for trend payload projection and `trend_samples` wiring.
    - Resource path now asserts trend pass-through in JSON payload.
  - `tests/test_e2e_cli.py`
    - `TestObserveSummaryCustom::test_observe_summary_trend_samples_json_exits_zero` with isolated snapshot path to validate JSON trend output shape.

- This chunk makes `observe summary` trend-aware while preserving existing alerting, schema, and MCP parity behavior.

## Chunk 319

### Completed

- Hardened `observe summary` trend semantics for deterministic replay and clearer operator UX:
  - `src/thegent/cli_impl.py`
    - Expanded trend baseline scope key to include trend-dependent query shape (`limit`, `top_escalations`).
    - Clamped `trend_samples` to non-negative values in `observe_summary_impl` so invalid/negative inputs do not trigger snapshots.
    - Ensured full-trend payload shape is stable when baseline is unavailable by emitting explicit `None` delta fields.
    - Added `trend_samples_requested` normalization and kept trend history disabled for `<=1`.
  - `src/thegent/cli.py`
    - Normalized negative `trend_samples` values in command dispatch.
    - Added signed trend delta rendering in rich output for faster directional read.
  - `src/thegent/mcp_server.py`
    - Extended `thegent_observe_summary` meta with full trend delta projection:
      `trend_structural_drift_pct_delta`, `trend_semantic_drift_pct_delta`,
      `trend_drift_structural_rate_pct_delta`, `trend_drift_semantic_rate_pct_delta`,
      `trend_backlog_count_delta`, `trend_past_sla_count_delta`.
  - `src/thegent/main.py`
    - Tightened `observe summary --trend-samples` option contract (`min=0`) and clarified help text for 0/1 disable semantics.

- Expanded regression coverage:
  - `tests/test_unit_cli.py`
    - Added tests for trend sample clamping, deterministic trend-scope capture (`limit` + `top_escalations`).
  - `tests/test_unit_mcp.py`
    - Extended MCP observe summary tool assertions for all projected trend delta metadata keys.

- This chunk increases resilience against noisy trend scopes and makes MCP/CLI trend projections feature-complete for operational dashboards and automation consumers.

## Chunk 320

### Completed

- Added explicit trend-effective-window semantics to make `1` and `<=1` behavior machine-actionable:
  - `src/thegent/cli_impl.py`
    - Added `trend_effective_samples` to `trend_summary` and derived it from request normalization:
      - `0` when trend disabled (`trend_samples <= 1`)
      - requested count otherwise
    - Kept loading gate at `trend_samples > 1` while preserving non-negative normalization.
  - `src/thegent/cli.py`
    - Added richer delta formatter controls (`scale`, `unit`) and switched trend output to explicit percent-formatted:
      - requested/effective sample fields
      - fallback and success deltas in `%`
      - structural drift as `%`
    - This makes trend direction and unit semantics clearer in rich output.
  - `src/thegent/mcp_server.py`
    - Added `trend_effective_samples` to `thegent_observe_summary` tool metadata.

- Extended trend robustness tests:
  - `tests/test_unit_cli.py`
    - Added assertions for `trend_effective_samples` on clamped and disabled (`trend_samples=1`) trend paths.
  - `tests/test_unit_mcp.py`
    - Added assertions for `trend_effective_samples` projection in tool metadata.
    - Added `test_observe_summary_tool_treats_trend_samples_one_as_disabled`.

- This chunk moves trend behavior from binary UX to explicitly modeled window intent across CLI and MCP surfaces.

## Chunk 321

### Completed

- Closed the parity gap for disabled trend mode (`trend_samples=1`) across tool and command surfaces:
  - `tests/test_unit_mcp.py`
    - Updated `test_observe_summary_resource_returns_json_payload` to mirror CLI contract:
      - expected `trend_samples_requested=1`, `trend_effective_samples=0`, and `history_sample_count=0`.
    - Kept metadata coverage for `trend_effective_samples` in tool path assertions.
  - `tests/test_e2e_cli.py`
    - Added `test_observe_summary_trend_samples_one_disables_trend` to validate interactive behavior:
      - JSON payload contains `trend_summary.enabled == False`
      - `trend_samples_requested == 1`
      - `trend_effective_samples == 0`
      - `history_sample_count == 0`.

- This chunk removes remaining ambiguity around the `1` edge case and ensures e2e parity with the new trend contract (`requested` vs `effective`) semantics.

## Chunk 322

### Completed

- Closed remaining consistency gap in trend test fixtures and extended edge-case e2e semantics:
  - `tests/test_unit_mcp.py`
    - Updated `test_observe_summary_tool_returns_payload_and_meta` trend stub to include `trend_effective_samples`,
      aligning fixture payload with asserted MCP metadata.
  - `tests/test_e2e_cli.py`
    - Added `test_observe_summary_trend_samples_two_reports_effective`:
      - confirms `trend_samples=2` enables trend mode and sets `trend_effective_samples=2`.
    - Added `test_observe_summary_trend_samples_zero_disables_trend`:
      - confirms `trend_samples=0` disables trend and sets `trend_effective_samples=0`.

- This chunk improves contract consistency and covers the full requested window semantics (`0`, `1`, `2`) across CLI JSON output.

## Chunk 323

### Completed

- Added malformed and boundary trend-sample hardening tests across implementation and CLI command surfaces:
  - `tests/test_unit_cli.py`
    - Added `test_observe_summary_impl_treats_non_integer_trend_samples_as_zero`:
      - verifies non-integer input to `observe_summary_impl` does not crash
      - normalizes to disabled trend (`trend_samples_requested=0`, `trend_effective_samples=0`)
      - avoids historical lookups.
  - `tests/test_e2e_cli.py`
    - Added `test_observe_summary_trend_samples_large_enables_and_tracks_effective_samples`:
      - asserts `trend_samples=9999` keeps trend enabled and `effective=9999`.
    - Added `test_observe_summary_invalid_trend_samples_is_rejected_by_cli`:
      - asserts CLI type validation rejects non-integer `--trend-samples`.

- This chunk finalizes explicit contract coverage for trend request boundaries (`0`, non-int, very large values), reducing drift risk in automation tooling and CLI UX error handling.

## Chunk 324

### Completed

- Added deterministic partial-history coverage for oversized trend window requests:
  - `tests/test_unit_cli.py`
    - Added `test_observe_summary_impl_partial_history_for_large_trend_request`:
      - verifies request `trend_samples=5` loads history with `max_items=4`
      - trend remains enabled with `trend_effective_samples=5`
      - deterministic `history_sample_count` reflects available snapshots (sparse-history behavior).
    - Confirms baseline selection remains valid when only one historical snapshot is available.

- This chunk closes the edge case where requested trend windows exceed snapshot availability by asserting the request/load contract (`max_items = trend_samples - 1`) remains stable.

## Chunk 325

### Completed

- Hardened the “enabled but missing baseline” path for trend output:
  - `tests/test_unit_cli.py`
    - Added `test_observe_summary_impl_enabled_without_baseline` to guarantee stable null-delta shape when no historical snapshot exists but trend is enabled (`trend_samples > 1`).
    - Asserts full `trend_summary` shape remains stable and all delta fields are explicit `None`.
  - `tests/test_e2e_cli.py`
    - Added `test_observe_summary_trend_enabled_without_baseline_keeps_stable_shape` with isolated snapshot path:
      - verifies `trend_samples=3` returns `enabled=True`, `trend_effective_samples=3`, `history_sample_count=0`.
      - verifies all delta fields remain `None` when baseline is unavailable.

- This chunk completes a subtle but high-impact robustness gap for first-run or sparse-history operators where trend is requested before enough snapshots exist.

## Chunk 326

### Completed

- Added MCP resource parity assertion for enabled trend semantics:
  - `tests/test_unit_mcp.py`
    - Added `test_observe_summary_resource_preserves_effective_samples_for_enabled_path`.
    - Verifies `thegent://observe/summary` resource preserves:
      - `trend_summary.enabled == True`
      - `trend_samples_requested`
      - `trend_effective_samples`
      - `baseline_available` when no baseline exists.

- This chunk extends resource-plane confidence for orchestrators that rely on MCP resources instead of tool metadata for stateful trend consumption.

## Chunk 327

### Completed

- Normalized trend-query metadata propagation across observe-summary output:
  - `src/thegent/cli_impl.py`
    - Normalized `trend_samples` persisted into `generated_query` so query metadata is always canonicalized (`int`/clamped form) even for malformed inputs (`0`, negative, non-integer).
    - This prevents downstream consumers from inferring conflicting “requested” values from CLI typing vs internal trend parsing.
  - `src/thegent/cli.py`
    - Added explicit trend-disabled line in rich output to make effective-vs-requested sample status visible when trend is disabled.
  - `src/thegent/mcp_server.py`
    - Added `trend_sampling_mode` metadata in `thegent_observe_summary` meta payload (`enabled|disabled`), making automation intent explicit without requiring field inference.
- Expanded regression coverage:
  - `tests/test_unit_cli.py`
    - Added assertions that `payload["generated_query"]["trend_samples"]` is canonical in enabled, clamped, and sanitized trend-input paths.
  - `tests/test_unit_mcp.py`
    - Added assertions for `trend_sampling_mode` in both enabled and disabled MCP observe-summary tool paths.
  - `tests/test_e2e_cli.py`
    - Added assertions in trend E2E cases that `generated_query.trend_samples` matches the normalized effective request for 0/1/2/3/9999.

This chunk closes a subtle but important contract gap where `generated_query.trend_samples` and internal trend request handling could diverge under malformed/edge inputs.

## Chunk 328

### Completed

- Added deterministic trend scope fingerprinting and trend history integrity metadata for observe-summary:
  - `src/thegent/cli_impl.py`
    - Added `_hash_observe_summary_payload()` for deterministic payload signature generation.
    - Added canonical trend scope materialization:
      - `trend_summary.scope_key`
      - `trend_summary.scope_key_json` (stable key order)
      - `trend_summary.scope_payload_type`
      - `trend_summary.scope_signature` (SHA-256 of scope JSON)
    - Added trend-history traceability fields:
      - `trend_summary.trend_snapshot_ids`
      - `trend_summary.trend_snapshot_ids_csv`
      - `trend_summary.trend_snapshot_ids_hash`
      - `trend_summary.trend_snapshot_window_seconds`
    - Added `generated_query.trend_scope_signature` for direct run-to-summary parity checks.
    - Added `payload_signature` on observe-summary payloads and persisted `scope_signature/scope_key_json` in snapshot records.
  - `src/thegent/mcp_server.py`
    - Extended `thegent_observe_summary` tool meta with scope/trend-history introspection:
      - `trend_signature` fields: `trend_scope_signature`, `trend_scope_key_json`, `trend_scope_payload_type`.
      - trend history exposure: `trend_snapshot_ids_count`, `trend_snapshot_ids_csv`, `trend_snapshot_ids_hash`, `trend_snapshot_window_seconds`.
      - Aliased `trend_requested_samples` to explicit `trend_samples_requested`.
      - Exposed `payload_signature` in tool meta.
  - `src/thegent/cli.py`
    - Added human-readable rich output lines for trend scope signature and trend snapshot window state in both enabled and disabled paths.
- Expanded regression coverage:
  - `tests/test_unit_cli.py`
    - `test_observe_summary_impl_tracks_query_scope_for_trend_baseline` now asserts:
      - deterministic scope key serialization/signature
      - scope signature propagation into `generated_query`
      - snapshot traceability defaults (`trend_snapshot_ids`, hash)
  - `tests/test_unit_mcp.py`
    - `TestMCPObserveSummaryContract::test_observe_summary_tool_returns_payload_and_meta`
      now validates scope/signature and trend snapshot meta fields in MCP result metadata.
    - Resource-path assertions now validate trend scope metadata pass-through in `trend_summary`.
  - `tests/test_e2e_cli.py`
- Added `test_observe_summary_trend_scope_signature_is_visible`:
  - verifies `scope_key_json` captures full trend scope
  - verifies deterministic scope signature parity through `generated_query`.

This chunk improves cross-agent replayability and avoids cross-surface drift by making trend scope and snapshot lineage first-class and machine-readable.

## Chunk 329

### Completed

- Extended observe-summary trend diagnostics into a production-usable timing and coverage plane:
  - `src/thegent/cli_impl.py`
    - Added `_parse_observe_summary_timestamp()` for robust snapshot timestamp parsing.
    - Added coverage/timing metrics into `trend_summary`:
      - `trend_snapshot_expected_count`
      - `trend_snapshot_deficit`
      - `trend_snapshot_interval_seconds_avg`
      - `trend_snapshot_freshness_seconds`
      - `trend_previous_samples_requested`
      - `trend_sampling_mode` (`enabled`, `enabled_partial`, `disabled`)
    - Added sampling metadata into snapshot records:
      - `trend_sampling_mode`
      - `trend_previous_samples_requested`
      - `trend_snapshot_expected_count`
      - `trend_snapshot_deficit`
      - `trend_snapshot_interval_seconds_avg`
      - `trend_snapshot_freshness_seconds`
  - `src/thegent/mcp_server.py`
    - Added meta-plane coverage for the new trend diagnostics:
      - `trend_snapshot_sampling_mode`
      - `trend_previous_samples_requested`
      - `trend_snapshot_expected_count`
      - `trend_snapshot_deficit`
      - `trend_snapshot_interval_seconds_avg`
      - `trend_snapshot_freshness_seconds`
  - `src/thegent/cli.py`
    - Added trend history telemetry lines to the rich summary panel:
      - expected/loaded/deficit coverage
      - interval average and freshness

- Expanded regression matrix:
  - `tests/test_unit_cli.py`
    - Added `test_observe_summary_impl_reports_snapshot_timing_and_coverage`:
      - asserts deterministic timestamp filtering behavior with mixed-valid snapshot inputs
      - asserts coverage/timing fields and enabled sampling mode.
  - `tests/test_unit_mcp.py`
    - Extended MCP observe-summary fixtures/assertions for new trend diagnostic keys in:
      - `test_observe_summary_tool_returns_payload_and_meta`
      - `test_observe_summary_resource_returns_json_payload`
    - Asserted meta-plane coverage keys and resource-pass-through coverage fields.
  - `tests/test_e2e_cli.py`
    - Added `test_observe_summary_trend_history_metadata_replayed_from_snapshots`:
      - seeds deterministic observe-summary snapshot records
      - validates window, interval, expected/loaded/deficit behavior and replayed freshness.

This chunk upgrades trend observability from just snapshot lineage to a robust operational signal for coverage quality, cadence, and timing freshness.

## Chunk 330

### Completed

- Hardened observe-summary trend quality and freshness semantics for scheduler decisions:
  - `src/thegent/cli_impl.py`
    - Added environment-tunable freshness classification:
      - `THGENT_OBSERVE_SUMMARY_FRESHNESS_BUCKET_FRESH_SECONDS` (default 600)
      - `THGENT_OBSERVE_SUMMARY_FRESHNESS_BUCKET_WARM_SECONDS` (default 3600)
      - `THGENT_OBSERVE_SUMMARY_FRESHNESS_BUCKET_STALE_SECONDS` (default 86400)
    - Added trend quality fields to `trend_summary`:
      - `trend_snapshot_invalid_timestamps` (timestamp parsing failures in history window)
      - `trend_snapshot_coverage_pct` (parsed snapshot coverage vs expected)
      - `trend_snapshot_gap_count` (gap count between valid snapshot timestamps)
      - `trend_snapshot_interval_seconds_min`
      - `trend_snapshot_interval_seconds_max`
      - `trend_snapshot_freshness_bucket` (`fresh|warm|stale|critical|future|unknown`)
    - Persisted new trend-quality counters/qualities in `observe_summary_snapshot` records.
- Extended MCP and CLI operator surface:
  - `src/thegent/mcp_server.py`
    - Added trend-quality meta:
      - `trend_snapshot_interval_seconds_min`
      - `trend_snapshot_interval_seconds_max`
      - `trend_snapshot_gap_count`
      - `trend_snapshot_invalid_timestamps`
      - `trend_snapshot_coverage_pct`
      - `trend_snapshot_freshness_bucket`
  - `src/thegent/cli.py`
    - Added rich output lines showing:
      - coverage percentage
      - invalid timestamp count
      - interval range + gap count
      - freshness bucket + freshness seconds
- Added regression coverage:
  - `tests/test_unit_cli.py`
    - Extended trend timing/coverage test to validate invalid timestamp accounting and coverage math.
  - `tests/test_unit_mcp.py`
    - Added trend-quality assertions in tool/resource payload-parity tests.
  - `tests/test_e2e_cli.py`
    - Extended replay-from-snapshot assertions with interval min/max, gap count, invalid timestamp count, coverage percent, and freshness bucket.

This chunk upgrades trend behavior from linearly counting samples to a richer quality scorecard suitable for adaptive trend scheduling and alerting.

## Chunk 331

### Completed

- Added deterministic trend-health scoring and recommendation signals:
  - `src/thegent/cli_impl.py`
    - Added `_classify_observe_summary_trend_health` to convert trend timing/coverage/freshness metrics into:
      - `trend_snapshot_health` (`good|warning|degraded|critical|disabled`)
      - `trend_snapshot_health_score` (`0..100`)
      - `trend_snapshot_recommendations` (actionable remediation hints)
    - Added environment tunables:
      - `THGENT_OBSERVE_SUMMARY_TREND_HEALTH_MIN_COVERAGE_PCT` (default `80.0`)
      - `THGENT_OBSERVE_SUMMARY_TREND_HEALTH_MAX_INVALID_TIMESTAMPS` (default `0`)
    - Appended health score/recommendations into:
      - trend payload (`trend_summary`)
      - persisted `observe_summary_snapshot` records
    - Appended adaptive quality alerts for degraded/critical trend states.
  - `src/thegent/mcp_server.py`
    - Added MCP meta keys for trend quality scoring:
      - `trend_snapshot_health`
      - `trend_snapshot_health_score`
      - `trend_snapshot_recommendation_count`
      - `trend_snapshot_recommendations_csv`
- Extended CLI operator display in `src/thegent/cli.py`:
  - Added trend history quality line fields for health/score.
  - Added trend recommendation summary lines when suggestions are available.
- Added regression coverage for the new signal:
  - `tests/test_unit_cli.py`
    - Extended trend timing/coverage assertions for:
      - `trend_snapshot_health`
      - `trend_snapshot_health_score`
      - `trend_snapshot_recommendations`
    - Added disabled-state assertion for trend quality fields.
  - `tests/test_unit_mcp.py`
    - Extended `test_observe_summary_tool_returns_payload_and_meta` to assert MCP meta for trend health/recommendation fields.
  - `tests/test_e2e_cli.py`
    - Extended `test_observe_summary_trend_history_metadata_replayed_from_snapshots` with health/score/recommendation checks.

This chunk introduces practical operational value: trend history now produces a deterministic quality rating and actionable remediation hints in addition to raw timing metrics, improving robustness and triage speed.

## Chunk 332

### Completed

- Added health-score explainability and tuning controls for `observe_summary` trend quality:
  - `src/thegent/cli_impl.py`
    - Extended `_classify_observe_summary_trend_health(...)` to return a detailed breakdown payload (`trend_snapshot_health_breakdown`) including:
      - per-dimension penalties (`coverage`, `deficit`, `invalid_timestamps`, `freshness`, `gap`)
      - threshold context (`good`, `warning`, `degraded` thresholds)
      - raw input counters and effective shortfall/coverage values.
    - Added environment tuning for score class boundaries:
      - `THGENT_OBSERVE_SUMMARY_TREND_HEALTH_GOOD_THRESHOLD` (default `95`)
      - `THGENT_OBSERVE_SUMMARY_TREND_HEALTH_WARNING_THRESHOLD` (default `80`)
      - `THGENT_OBSERVE_SUMMARY_TREND_HEALTH_DEGRADED_THRESHOLD` (default `50`)
    - Persisted breakdown details to `trend_summary` and `observe_summary_snapshot` records.
  - `src/thegent/mcp_server.py`
    - Added `trend_snapshot_health_breakdown` into `thegent_observe_summary` tool metadata.
- Expanded regression coverage:
  - `tests/test_unit_cli.py`
    - Extended coverage assertions in `test_observe_summary_impl_reports_snapshot_timing_and_coverage`:
      - breakdown shape + penalty dimension keys.
    - Added `test_classify_observe_summary_trend_health_respects_threshold_env` to validate env-based threshold controls and derived score.
  - `tests/test_unit_mcp.py`
    - Extended payload/meta assertions in `test_observe_summary_tool_returns_payload_and_meta` to include full breakdown parity.

This chunk makes trend health observable as an auditable signal instead of a scalar-only label, with explicit policy levers and machine-readable diagnostics.

## Chunk 333

### Completed

- Added operator-facing policy fingerprinting for trend-quality scoring and added penalty visibility in CLI summaries:
  - `src/thegent/cli_impl.py`
    - Added deterministic policy metadata to `trend_snapshot_health_breakdown`:
      - full policy thresholds in `policy` (`healthy`, `warning`, `degraded`, `min_coverage_pct`, `max_invalid_timestamps`)
      - deterministic `policy_signature` (`sha256` over policy surface + scoring constants)
    - Added policy metadata in disabled-state breakdown as well, so trend health diagnostics remain stable even when trend is disabled.
  - `src/thegent/cli.py`
    - Added compact penalty summary output lines (`coverage`, `deficit`, `invalid_ts`, `freshness`, `gap`) from `trend_snapshot_health_breakdown` to all trend-history modes.
- Expanded regression coverage:
  - `tests/test_unit_cli.py`
    - Extended disabled-state trend test to assert breakdown policy fields are present.
    - Extended trend coverage test to assert breakdown now includes policy metadata + policy signature.
    - Added threshold test for `_classify_observe_summary_trend_health()` remains tuned to verify score/penalty behavior.

This chunk closes the final “black-box gap” for disabled mode and makes quality scoring configuration detectable and comparable across runs.

## Chunk 334

### Completed

- Completed MCP parity for trend policy explainability:
  - `tests/test_unit_mcp.py`
    - Extended `test_observe_summary_tool_returns_payload_and_meta` to assert full `trend_snapshot_health_breakdown` includes:
      - `policy_signature` in tool meta payload.
      - deterministic `policy` block (`healthy`, `warning`, `degraded`, `min_coverage_pct`, `max_invalid_timestamps`).
      - consistency between CLI content payload and MCP meta payload for `policy_signature`.
    - Added structural sanity checks to ensure trend policy metadata is surfaced as first-class MCP fields rather than hidden nested-only data.

This chunk ensures trend health policy explainability is preserved at automation/tool contract boundaries, improving parity between CLI output, persisted snapshots, and MCP integration surfaces.

## Chunk 335

### Completed

- Extended MCP resource-layer parity for observe-summary trend policy metadata:
  - `tests/test_unit_mcp.py`
    - Added `test_observe_summary_resource_exposes_health_policy_breakdown` to verify `thegent://observe/summary` returns raw `trend_snapshot_health_breakdown.policy_signature` and policy block in JSON payloads.
    - Replaced brittle fixture hash literals with deterministic signature generation in MCP coverage assertions.
    - Added stricter policy metadata parity checks for `policy_signature` and policy threshold fields in both payload and tool meta paths.
  - `src/thegent/cli_impl.py`
    - Added `policy` block to enabled-path trend health breakdown so policy explainability is present in real emitted payloads, not just disabled-state data.

This chunk closes a remaining gap by validating that raw observe-summary MCP resources and tool-meta outputs both carry explicit trend-health policy explainability, not just the tool summary path.

## Chunk 336

### Completed

- Added end-to-end policy explainability assertions to real observe-summary CLI output:
  - `tests/test_e2e_cli.py`
    - Extended `test_observe_summary_trend_history_metadata_replayed_from_snapshots` to verify emitted trend breakdown includes:
      - deterministic `policy_signature`.
      - full `policy` threshold block (`healthy_threshold`, `warning_threshold`, `degraded_threshold`, `min_coverage_pct`, `max_invalid_timestamps`).
    - This verifies policy explainability in a fully executed command path, not just MCP mock payloads.

This chunk closes the final validation gap between unit-level MCP parity and real CLI execution behavior for trend health diagnostics.

## Chunk 337

### Completed

- Extended CLI unit-path policy-surface checks for real trend replay calculations:
  - `tests/test_unit_cli.py`
    - In `test_observe_summary_impl_partial_history_for_large_trend_request`, added deterministic policy signature + policy-threshold assertions for `trend_snapshot_health_breakdown`.
    - This aligns unit assertions for CLI trend quality with MCP/e2e parity and guards against silent policy-metadata drift.

This chunk tightens deterministic parity across all three observation layers: direct CLI logic, MCP tooling, and end-to-end CLI behavior.

## Chunk 338

### Completed

- Closed disabled-path parity gaps for trend health policy explainability:
  - `tests/test_unit_mcp.py`
    - Added `_expected_trend_health_policy_signature()` helper.
    - Extended `test_observe_summary_tool_treats_trend_samples_one_as_disabled` to assert tool meta includes policy signature + policy threshold block.
    - Added `test_observe_summary_resource_exposes_health_policy_for_disabled_path` to assert MCP resource JSON preserves disabled-path policy metadata.
  - `tests/test_e2e_cli.py`
    - Added deterministic policy-signature assertions for disabled trend modes (`--trend-samples 1` and `--trend-samples 0`) including disabled health state and policy fields.

This chunk ensures policy explainability is present even when trend history is effectively disabled, which prevents silent observability regressions in non-trending modes.
