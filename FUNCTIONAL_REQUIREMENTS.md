# Functional Requirements: thegent

Unified agent orchestration CLI for Factory skills and droids.

**Document version:** 1.0
**Schema:** FR-{DOMAIN}-{NNN}
**Domains:** AGT (agents), CTR (contracts), GOV (governance), EXE (execution), MOD (models), PLN (planning), CLI (cli), MCP (mcp), CFG (config), OPS (operations), INS (install), OUT (output parser)

---

## FR-AGT: Agents

### FR-AGT-001: Base Runner Interface

The system SHALL define an `AgentRunner` base class with a `run()` method accepting prompt, cwd, mode, timeout, streaming flags, and stdout/stderr callbacks, returning a `RunResult` with exit_code, stdout, stderr, and timed_out fields.

**Traces to:** E1.1
**Priority:** P1

### FR-AGT-002: Direct Agent Invocation via Native CLIs

The system SHALL invoke cursor-agent, gemini, codex, copilot, and claude agents directly through their native CLI binaries, resolving binary paths via environment variables (`THGENT_{AGENT}_CMD`), `shutil.which`, or `~/.local/bin` fallback locations.

**Traces to:** E1.2
**Priority:** P1

### FR-AGT-003: Noisy Stderr Filtering for Direct Agents

The system SHALL filter known noisy stderr patterns (node deprecation warnings, hook registry messages, usage stats, copilot info lines) from direct agent output before returning results, preserving only meaningful error content.

**Traces to:** E1.2
**Priority:** P2

### FR-AGT-004: Codex Proxy Runner via CLIProxyAPIPlus

The system SHALL support running agents (claude, codex, gemini, copilot, antigravity, minimax, glm, cliproxy, roo, kilo) through CLIProxyAPIPlus by configuring the proxy base URL as `OPENAI_BASE_URL` and mapping each agent to its default model ID from the `_PROXY_MODEL` dictionary.

**Traces to:** E1.3
**Priority:** P1

### FR-AGT-005: Cursor API Runner via OpenAI-Compatible HTTP Backend

The system SHALL support running cursor-api agents through the wisdgod cursor-api backend by verifying reachability via `GET /v1/models`, configuring `OPENAI_BASE_URL` and `OPENAI_API_KEY` from settings, and executing codex CLI with the proxy model.

**Traces to:** E1.4
**Priority:** P1

### FR-AGT-006: CLIProxyAPIPlus Lifecycle Management

The system SHALL manage the CLIProxyAPIPlus proxy lifecycle including binary resolution, config YAML generation with provider blocks (minimax, glm, antigravity via iFlow), proxy process startup with health-check polling, and ready-timeout enforcement of 5 seconds.

**Traces to:** E1.5
**Priority:** P1

### FR-AGT-007: Agent Registry and Name Resolution

The system SHALL maintain a canonical registry of agent names (gemini, codex, copilot, cursor-agent, cursor-api, claude, antigravity, minimax, glm, cliproxy, roo, kilo), resolve aliases (e.g. "cursor" to "cursor-agent"), and return the appropriate runner type (DirectAgentRunner, CodexProxyRunner, or CursorApiRunner) for each agent via `get_runner()`.

**Traces to:** E1.6
**Priority:** P1

### FR-AGT-008: Provider Fallback Chain

The system SHALL define ordered fallback chains per provider so that when an agent hits a usage limit, `get_fallback_agents()` returns the next providers to attempt, excluding the current agent from the chain.

**Traces to:** E1.7
**Priority:** P1

### FR-AGT-009: Retry with Exponential Backoff for Transient Failures

The system SHALL retry agent subprocess executions using tenacity with configurable max_attempts (default 4), exponential wait (min 2s, max 60s), retrying only on `TransientAgentError` exceptions classified as rate_limit or transient failures.

**Traces to:** E1.8
**Priority:** P1

### FR-AGT-010: Failure Classification (Rate Limit, Transient, Usage Limit)

The system SHALL classify agent run failures into FailureKind categories (RATE_LIMIT for 429/too-many-requests, TRANSIENT for 502/503/504/reconnecting, USAGE_LIMIT for quota/subscription/billing exhaustion, UNKNOWN otherwise) by matching stderr and stdout against defined regex patterns.

**Traces to:** E1.8
**Priority:** P1

### FR-AGT-011: Fallback State Machine Orchestration

The system SHALL implement a `FallbackStateMachine` that iterates through a provider list, executing each with retry (up to max_retries_per_provider with exponential backoff), falling back to the next provider on usage limits, normalizing output via adapters, running semantic validation, evaluating fallback policies, and recording telemetry including drift events.

**Traces to:** E1.9
**Priority:** P1

### FR-AGT-012: Droid Runner for Factory Droids

The system SHALL invoke Factory droids via `droid exec` subprocess with frontmatter-parsed config, resolving the droid binary from `~/.local/bin/droid` or `~/.factory/bin/droid`, supporting prompt injection, working directory, timeout, and streaming output.

**Traces to:** E1.10
**Priority:** P2

### FR-AGT-013: Multi-Agent Execution Modes

The system SHALL define execution modes (SEQUENTIAL_DELEGATION, PARALLEL_CONSENSUS, REVIEW_LOOP, ARBITRATION_QUORUM, SOLO) with metadata including min_agents, streaming support, and coordination logic descriptions, and provide lookup via `get_mode_capability()` and enumeration via `list_modes()`.

**Traces to:** E1.11
**Priority:** P2

---

## FR-CTR: Contracts

### FR-CTR-001: Canonical Structured Message (CSM) Schema

The system SHALL define a `CanonicalStructuredMessage` dataclass with fields for identifiers (task_id, run_id, chunk_id), lifecycle (status as CSMStatus enum, phase as CSMPhase enum, progress 0.0-1.0), content (objective, summary, actions_completed, issues, next_steps), governance (evidence_set_hash, policy_gate_id, decision_reason_code), and metadata (schema_version "csm-v1", source_contract, raw_payload), with `to_dict()` and `from_dict()` serialization.

**Traces to:** E2.1
**Priority:** P1

### FR-CTR-002: Incremental XML Parser for Agent Outputs

The system SHALL parse streaming/partial XML from agent outputs using regex-based tag extraction (`<TAG>content</TAG>`), supporting allowed tag filtering, case-insensitive matching, partial state detection for unclosed tags, and error classification (PARSE_OK, PARSE_TRUNCATED, PARSE_INVALID_TAG, PARSE_MALFORMED).

**Traces to:** E2.2
**Priority:** P1

### FR-CTR-003: XML Output Adapter Normalization

The system SHALL normalize XML-tagged agent outputs into CSM by mapping XML tags (STATUS, SUMMARY, PROGRESS, OBJECTIVE, ISSUES, NEXT_STEPS, ACTIONS_COMPLETED) to CSM fields, handling tag aliases and case variations, computing confidence scores, and falling back to PENDING status when tags cannot be parsed.

**Traces to:** E2.3
**Priority:** P1

### FR-CTR-004: Generic Output Adapter via Plain Text Extraction

The system SHALL provide a `GenericOutputAdapter` that normalizes any provider output by extracting condensed text via `output_parser.extract_condensed`, returning a CSM with COMPLETED status, confidence 0.7, and source_contract "plain".

**Traces to:** E2.3
**Priority:** P2

### FR-CTR-005: Provider Adapter Registry and Fallback Normalization

The system SHALL maintain an `ADAPTER_REGISTRY` mapping provider names to OutputAdapter instances, register default XML adapters for common providers (copilot, gemini, claude, codex, cursor, antigravity), and provide a `normalize_output()` function that attempts the registered adapter first, falls back to plain text extraction with reduced confidence (0.3-0.5), or raises SemanticValidationError when fallback is disabled.

**Traces to:** E2.4
**Priority:** P1

### FR-CTR-006: Contract Telemetry and Drift Detection

The system SHALL record normalization events to a JSONL file (`contract_telemetry.jsonl`) with timestamp, event_type, run_id, provider, contract, confidence, and success fields, emit structural and semantic drift events per G-RV-07, and provide `get_drift_budget_status()` to check drift rates against configurable budgets (default 5% structural, 10% semantic).

**Traces to:** E2.5
**Priority:** P1

### FR-CTR-007: Telemetry Statistics and KPI Aggregation

The system SHALL compute telemetry statistics from recent normalization events including total count, success_rate, fallback_rate, avg_confidence, and per-provider breakdowns via `get_stats()`, with configurable event limit and provider filter.

**Traces to:** E2.5
**Priority:** P2

### FR-CTR-008: Normalization Fallback Policy Evaluation

The system SHALL evaluate normalization results against a `FallbackPolicy` with configurable thresholds (min_confidence_threshold default 0.4, max_fallback_rate default 0.3), strict provider enforcement, and allow_plain_fallback toggle, returning a list of policy violation strings.

**Traces to:** E2.6
**Priority:** P1

### FR-CTR-009: Contract Version Registry and Compatibility

The system SHALL maintain a `ContractRegistry` with registered contract versions (csm-v1, task-tool-18, zen-rich-v1), compatibility matrix, deprecation status, and migration window dates, providing `get()` for version lookup, `is_compatible()` for normalization compatibility checks, and `list_versions()` for discovery.

**Traces to:** E2.7
**Priority:** P1

### FR-CTR-010: Contract Migration Controller

The system SHALL evaluate contract version suitability via `MigrationController.evaluate_version()`, returning allowed/status/reason/migration_days_left, blocking expired deprecated versions, warning on active deprecations, and providing `get_preferred_version()` for the latest non-deprecated version.

**Traces to:** E2.8
**Priority:** P2

### FR-CTR-011: Semantic Validation of CSM Invariants

The system SHALL validate CSM invariants including: COMPLETED status requires progress >= 1.0 and non-empty summary; PENDING status requires progress == 0.0; FAILED status requires non-empty issues or decision_reason_code; REVIEWER phase requires decision_reason_code; PLANNER COMPLETED requires objective; OPERATOR COMPLETED requires actions_completed or summary.

**Traces to:** E2.9
**Priority:** P1

### FR-CTR-012: Conformance Test Suite for Provider Adapters

The system SHALL define a conformance test suite with test cases covering XML basic parsing, partial XML, plain text fallback, malformed XML, and edge cases, verifying that adapters produce correct CSMStatus, meet minimum confidence thresholds, and generate appropriate summaries.

**Traces to:** E2.10
**Priority:** P2

### FR-CTR-013: Canonical Event Schemas for Audit Trail

The system SHALL define Pydantic models for orchestration events: `ChunkEvent` (streaming output chunks with run_id, task_id, chunk_id, sequence, payload), `EvidenceEvent` (evidence artifacts with evidence_id, evidence_type, hash_value), and `PolicyEvent` (policy decisions with decision allow/deny/warn, reason, policy_id, override_applied).

**Traces to:** E2.11
**Priority:** P2

---

## FR-GOV: Governance

### FR-GOV-001: Cost Estimation per Run

The system SHALL estimate per-run cost in USD via `CostEstimator.estimate()` using a pricing table ($/1k tokens for input and output by model), falling back to a heuristic based on prompt length when the model is not in the pricing table.

**Traces to:** E3.1
**Priority:** P2

### FR-GOV-002: Daily Cost Aggregation by Owner

The system SHALL aggregate daily cost totals per owner by reading finish events with `cost_usd` from `run_registry.jsonl`, filtering to the current UTC date, and summing costs via `CostAggregator.daily_total()`.

**Traces to:** E3.2
**Priority:** P2

### FR-GOV-003: Input Guardrail - Prompt Length Validation

The system SHALL reject prompts exceeding `prompt_max_chars` (default 65536) via `InputGuardrails.check()`, returning a `GuardrailResult` with `rail_id="prompt_length"`, the violation reason, and remediation instructions.

**Traces to:** E3.3
**Priority:** P1

### FR-GOV-004: Input Guardrail - Prompt Blocklist Patterns

The system SHALL reject prompts matching any regex pattern in `prompt_blocklist_patterns` via `InputGuardrails.check()`, returning `rail_id="prompt_blocklist"` with remediation guidance.

**Traces to:** E3.3
**Priority:** P1

### FR-GOV-005: Input Guardrail - Agent and Model Allowlists

The system SHALL reject agents not in `agent_allowlist` and models not in `model_allowlist` (when these lists are non-empty), returning appropriate `rail_id` values ("agent_allowlist" or "model_allowlist") with the list of allowed values as remediation.

**Traces to:** E3.3
**Priority:** P1

### FR-GOV-006: Input Guardrail - CWD Restriction

The system SHALL reject execution from working directories not under any `cwd_allowed_prefixes` path (when configured), returning `rail_id="cwd_restriction"` with allowed prefix paths as remediation.

**Traces to:** E3.3
**Priority:** P2

### FR-GOV-007: Guardrails Configuration from Environment Variables

The system SHALL construct `InputGuardrails` from environment variables: `THGENT_PROMPT_MAX_CHARS`, `THGENT_PROMPT_BLOCKLIST_PATTERNS` (comma-separated), `THGENT_AGENT_ALLOWLIST` (comma-separated), and `THGENT_CWD_ALLOWED_PREFIXES` (comma-separated).

**Traces to:** E3.4
**Priority:** P2

---

## FR-EXE: Execution

### FR-EXE-001: Run Metadata Model

The system SHALL define a `RunMeta` Pydantic model capturing run_id, correlation_id, agent, model, mode, prompt, cwd, owner, timestamps, exit_code, status, error_class, signature, policy_result/reason, override_reason/by, rationale, feedback_score/note, host, pid, is_background, lane (standard/critical/recovery), idempotency_token, confidence, arbitration, audit trail hashing (prev_hash, hash), route_contract, domain_tag, and contract_version.

**Traces to:** E4.1
**Priority:** P1

### FR-EXE-002: Run Registry with Hash-Chained Audit Trail

The system SHALL persist run events to `run_registry.jsonl` with SHA-256 hash chaining (each record includes prev_hash of the preceding record and its own hash), supporting register_start, register_end (with cost_usd), register_feedback, register_pause, and register_resume operations.

**Traces to:** E4.2
**Priority:** P1

### FR-EXE-003: Run Registry Schema Versioning

The system SHALL write a schema_version marker as the first record in new registry files and maintain `SCHEMA_VERSION = 1` for forward compatibility.

**Traces to:** E4.2
**Priority:** P2

### FR-EXE-004: Run State Tracking (Running/Paused/Completed/Failed)

The system SHALL derive current run state from registry events via `get_run_state()`: start -> RUNNING, finish -> COMPLETED or FAILED, pause -> PAUSED, resume -> RUNNING, with state transitions following the event stream chronologically.

**Traces to:** E4.3
**Priority:** P1

### FR-EXE-005: Idempotency Token Lookup

The system SHALL support finding the most recent run by idempotency token via `find_by_token()`, merging start and finish events for the matched run.

**Traces to:** E4.4
**Priority:** P2

### FR-EXE-006: Trust Score Calibration from Feedback History

The system SHALL compute a calibration factor per agent via `get_calibration_factor()` as the ratio of average feedback_score to average confidence across historical runs, clamped to [0.5, 2.0], defaulting to 1.0 when no feedback data exists.

**Traces to:** E4.5
**Priority:** P2

### FR-EXE-007: Checkpoint Registry for DAG State

The system SHALL persist state checkpoints to `checkpoint_registry.jsonl` with checkpoint_id, created_at_utc, reason, dag_content, session_dir, and owner, supporting create, list (most recent first), and get-by-id operations.

**Traces to:** E4.6
**Priority:** P2

### FR-EXE-008: PolicyEngine Evaluation with OPA Integration

The system SHALL evaluate runs against governance policies via `PolicyEngine.evaluate()`, delegating to OPA when `THGENT_OPA_URL` is configured (POST to `/v1/data/thegent/allow` with run_meta and context), falling back to Python policy logic based on `opa_fallback_allow` setting when OPA is unreachable.

**Traces to:** E4.7
**Priority:** P1

### FR-EXE-009: PolicyEngine - Critical Lane and Production Trust Gates

The system SHALL deny critical-lane runs with confidence below 0.9, deny unknown agents in critical/production, block critical lane when contract drift exceeds budget, warn recovery/critical runs without confidence scores, and deny production runs below the trust_score_threshold (default 0.8).

**Traces to:** E4.7
**Priority:** P1

### FR-EXE-010: Trust Boundary Validation for Environment Transitions

The system SHALL validate environment transitions via `TrustBoundaryValidator`, allowing same-level or downgrade transitions, requiring explicit audit for skip-level promotions (e.g. development directly to production), and recording the last environment after successful runs.

**Traces to:** E4.8
**Priority:** P2

---

## FR-MOD: Models

### FR-MOD-001: Static Model Catalog with Route Resolution

The system SHALL maintain a static catalog mapping canonical model IDs to ordered lists of `Route` objects (provider, backend_type direct/proxy, model_alias, priority, cost_weight), covering Anthropic 4.5/4.6, Gemini flash variants, Codex 5.3, cursor-api models, proxy providers (antigravity, minimax, glm, roo, kilo), sorted by priority.

**Traces to:** E5.1
**Priority:** P1

### FR-MOD-002: Model Alias Normalization

The system SHALL normalize model aliases ("haiku" -> "claude-haiku-4.5", "sonnet" -> "claude-sonnet-4.5", "opus" -> "claude-opus-4.6") via `normalize_model_id()` and validate routing policies via `normalize_route_policy()` against the set (prefer_direct, prefer_proxy, failover, round_robin, cheapest).

**Traces to:** E5.2
**Priority:** P1

### FR-MOD-003: Model Blacklist Enforcement

The system SHALL filter out blacklisted model versions via `_is_model_blacklisted()`, rejecting Claude 3.x and pre-4.5/4.6, Gemini 1.x and pro variants, GPT-4, and Codex/copilot GPT-5 without 5.3, allowing unparseable models by default.

**Traces to:** E5.3
**Priority:** P1

### FR-MOD-004: Dynamic Model Scraping with Cache

The system SHALL scrape available models from provider APIs (cursor `--list-models`, proxy `GET /v1/models`) with a JSON file cache (`~/.cache/thegent/models-cache.json`) using configurable TTL (default 300s), supporting forced refresh and cache invalidation via `invalidate_models_cache()`.

**Traces to:** E5.4
**Priority:** P2

### FR-MOD-005: Proxy Model Classification by Provider

The system SHALL classify proxy-scraped models into provider buckets (antigravity, minimax, glm, roo, kilo, gemini, claude) by matching model ID substrings, defaulting unmatched models to antigravity, and providing static fallbacks (minimax-m2.5, glm-5) when scraping returns empty results.

**Traces to:** E5.5
**Priority:** P2

### FR-MOD-006: Route Contract Metadata for Auditing

The system SHALL expose `route_contract()` returning schema_version, backend_types, and policy_names for auditing and compatibility checks by downstream consumers.

**Traces to:** E5.6
**Priority:** P3

---

## FR-PLN: Planning

### FR-PLN-001: PERT Forward Pass Analysis

The system SHALL compute PERT (Program Evaluation and Review Technique) expected duration and variance for task nodes using the formula `(optimistic + 4*most_likely + pessimistic) / 6` and `((pessimistic - optimistic) / 6)^2`, returning `PERTResult` with expected_duration, variance, critical_path flag, total_float, and confidence levels (p50, p90).

**Traces to:** E6.1
**Priority:** P2

### FR-PLN-002: Resource Contention Simulation

The system SHALL identify resource contention windows by comparing task resource demands against resource capacity profiles, returning `ContentionResult` with resource_id, time_window, peak_demand, capacity, contention_ratio, and affected_tasks.

**Traces to:** E6.2
**Priority:** P3

### FR-PLN-003: Continuity Risk Scoring for Shift Handoff

The system SHALL compute a continuity risk score (0.0-1.0) based on open tasks, snapshot freshness (tasks with snapshots older than 24 hours increase risk by 0.2 each), handoff windows, and owner coverage, returning risk factors, high-risk tasks, and recommendations (e.g. "Refresh snapshots before handoff").

**Traces to:** E6.3
**Priority:** P3

---

## FR-CLI: CLI

### FR-CLI-001: CLI Command Framework via Typer

The system SHALL implement a CLI using Typer with Rich console output, exposing commands for agent orchestration (run, bg), session management (ps, status, stop, wait, logs), DAG operations (dag list, dag run, dag add, dag update, dag remove, dag cancel, dag recover, dag rollback, dag reconcile), model discovery (models list, models refresh), governance (policy show, session-contracts, history verify), and installation (install, cliproxy login).

**Traces to:** E7.1
**Priority:** P1

### FR-CLI-002: Working Directory Resolution with Caching

The system SHALL resolve the working directory via `_resolve_cwd()` with a stat-based cache (10s TTL), returning None for ambiguous paths that require elicitation by MCP callers.

**Traces to:** E7.2
**Priority:** P2

### FR-CLI-003: Agent and Model Resolution for Runs

The system SHALL resolve agent aliases to canonical names, determine agent-specific default models from settings (cursor_agent_cmd, default_gemini_model, default_copilot_model, default_claude_model, default_codex_model), and support explicit model overrides via `--model` flag.

**Traces to:** E7.3
**Priority:** P1

### FR-CLI-004: Time Constraint Budget Injection

The system SHALL inject a time-constraint preamble into prompts calculating approximate tool-call budget from timeout (`timeout / SECONDS_PER_TOOL_CALL` where SECONDS_PER_TOOL_CALL = 2.3), instructing agents to complete within the budget.

**Traces to:** E7.4
**Priority:** P2

### FR-CLI-005: Session Continuation with Multi-Hop Context

The system SHALL build continuation prompts by tailing prior session stdout (last 8000 chars) and stderr (last 2000 chars), capping multi-hop total at 12000 chars, enabling agents to resume from where a prior session left off.

**Traces to:** E7.5
**Priority:** P2

---

## FR-MCP: MCP Server

### FR-MCP-001: FastMCP Server with Tool Registration

The system SHALL expose thegent capabilities as MCP tools via FastMCP (HTTP transport at configurable host:port, default 127.0.0.1:3847), registering tools for run, bg, ps, status, stop, wait, logs, inspect, list_agents, list_droids, list_models, dag_list, session_contracts, session_contract_health_report, session_contract_health_gate, session_contract_health_trend, and observe_summary.

**Traces to:** E8.1
**Priority:** P1

### FR-MCP-002: MCP Server Middleware Stack

The system SHALL configure the MCP server with error handling, logging, timing, rate limiting, response limiting, and response caching middleware.

**Traces to:** E8.2
**Priority:** P2

### FR-MCP-003: MCP Client Configuration Management

The system SHALL manage MCP client configuration for multiple consumers (cursor, claude-code, codex, claude-desktop, droid) by reading/writing their respective config files, ensuring `mcpServers` keys exist, and registering the thegent MCP server URL as a RemoteMCPServer entry.

**Traces to:** E8.3
**Priority:** P2

### FR-MCP-004: MCP Server CWD and Owner Elicitation

The system SHALL elicit working directory and owner from MCP callers when values cannot be inferred, using defined elicitation messages (`ELICIT_CWD_MSG`, `ELICIT_OWNER_MSG`) before returning errors.

**Traces to:** E8.4
**Priority:** P2

---

## FR-CFG: Configuration

### FR-CFG-001: Pydantic Settings with Environment Variable Binding

The system SHALL define `ThegentSettings` as a Pydantic BaseSettings model with `THGENT_` environment variable prefix, `.env` file support, and typed fields for all configuration including factory directories, agent commands, default models, timeouts, routing policy, session directory, MCP host/port, proxy settings, and OPA integration.

**Traces to:** E9.1
**Priority:** P1

### FR-CFG-002: Agent-Specific Default Model Configuration

The system SHALL provide per-agent default model settings: cursor_agent_cmd (gemini-3-flash), default_gemini_model (gemini-2.0-flash), default_copilot_model (claude-haiku-4.5), default_claude_model (haiku), default_codex_model (gpt-5.3-codex), default_codex_model_high (gpt-5.3-codex-high), default_antigravity_model (gemini-3-flash), each overridable via `THGENT_` prefixed environment variables.

**Traces to:** E9.2
**Priority:** P1

### FR-CFG-003: Timeout Configuration with Agent-Specific Overrides

The system SHALL enforce default_timeout (90s, range 10-3600) and default_timeout_claude (300s, range 60-3600) with per-agent timeout overrides via environment variables.

**Traces to:** E9.3
**Priority:** P1

### FR-CFG-004: Retention Policy Configuration (Tiered)

The system SHALL configure tiered retention policies: retention_days_sessions (default 30, range 7-365), retention_days_registry (default 90, range 30-730), retention_days_health (default 90), and per-domain retention via `THGENT_RETENTION_BY_DOMAIN` JSON (e.g. `{"gdpr":365,"soc2":2555}`).

**Traces to:** E9.4
**Priority:** P2

### FR-CFG-005: Normalization and Contract Policy Settings

The system SHALL configure normalization behavior: allow_fallback (default true), min_confidence (default 0.4), max_fallback_rate (default 0.3), strict_providers (comma-separated), contract_schema_version_minimum ("csm-v1"), canary_percent (0-100), and canary_providers (comma-separated).

**Traces to:** E9.5
**Priority:** P2

### FR-CFG-006: Startup Configuration Validation (Fail-Fast)

The system SHALL validate configuration on startup via `validate_setup()`, ensuring the session directory exists and is writable, raising RuntimeError on failure for fail-fast behavior.

**Traces to:** E9.6
**Priority:** P1

---

## FR-OPS: Operations

### FR-OPS-001: Operation Taxonomy Mapping

The system SHALL define a canonical operation taxonomy with five categories (ORCHESTRATE, GOVERN, RECOVER, OBSERVE, PLAN) and map each CLI command to its operation type via `OPERATION_MAP`, including MCP tool names and constraint metadata for each entry.

**Traces to:** E10.1
**Priority:** P2

### FR-OPS-002: Multi-Agent Orchestration Mode Catalog

The system SHALL define multi-agent orchestration modes (SEQUENTIAL_DELEGATION, PARALLEL_CONSENSUS, REVIEW_LOOP) with descriptions, phase lists, use cases, risk profiles, and selection hints, accessible via `get_mode()` and `list_modes()`.

**Traces to:** E10.2
**Priority:** P2

### FR-OPS-003: Mode Selection Policy Based on Risk/Urgency/Confidence

The system SHALL suggest an orchestration mode via `suggest_mode()` based on risk level, urgency, and confidence: PARALLEL_CONSENSUS when confidence < 0.5, REVIEW_LOOP for high risk with non-critical urgency, and SEQUENTIAL_DELEGATION as the default.

**Traces to:** E10.3
**Priority:** P2

---

## FR-INS: Install

### FR-INS-001: Source-to-Destination Mapping for Claude and Factory Targets

The system SHALL compute source-to-destination file mappings for "claude" (skills/agent-orchestra, hooks, templates, agents, commands, contracts to `~/.claude/`) and "factory" (.factory/hooks, skills, commands, droids, plugins, mcp.json, config.json, settings.json to `~/.factory/`) targets, with a "both" mode that combines both mappings.

**Traces to:** E11.1
**Priority:** P1

### FR-INS-002: Smart Copy with Modification Time Comparison

The system SHALL perform smart file copying via `smart_copy_file()` that copies only when the destination does not exist or the source modification time is newer, skipping up-to-date files, with optional verbose output.

**Traces to:** E11.2
**Priority:** P2

### FR-INS-003: Exclusion of Cache and Transient Directories

The system SHALL exclude directories matching `EXCLUDE_DIRS` (\_\_pycache\_\_, .pytest_cache, .ruff_cache, .mypy_cache, history.jsonl, session-env, debug, todos, tasks, teams, shell-snapshots, file-history, paste-cache) from install sync operations by checking all path components.

**Traces to:** E11.3
**Priority:** P2

### FR-INS-004: Symlink Mode for Editable Installs

The system SHALL support creating symlinks from source to destination via `create_symlink()` as an alternative to copying, enabling editable development workflows.

**Traces to:** E11.4
**Priority:** P3

---

## FR-OUT: Output Parser

### FR-OUT-001: JSONL Stream Extraction for Agent Output

The system SHALL extract the last assistant message from JSONL/streaming JSON agent output by parsing each line, filtering noise patterns (turn.completed, turn.started, thread.started, error items), and extracting content from nested envelopes (item.content, message.content, content, text, result fields).

**Traces to:** E12.1
**Priority:** P1

### FR-OUT-002: Plain Text Noise Stripping

The system SHALL strip leading noise lines (TIME CONSTRAINT echoes, usage headers, model headers, OK markers) and trailing noise lines (usage stats, token counts, copilot/cursor/claude verbosity) from plain text agent output, preserving meaningful content.

**Traces to:** E12.2
**Priority:** P1

### FR-OUT-003: Think Tag Removal

The system SHALL remove `<think>...</think>` tags and their content from agent output using DOTALL regex matching, cleaning reasoning traces that should not appear in final extracted output.

**Traces to:** E12.3
**Priority:** P2

### FR-OUT-004: ParseResult with Error Classification

The system SHALL return a `ParseResult` from extraction with error_class codes (PARSE_OK, PARSE_TRUNCATED, PARSE_MALFORMED, PARSE_EMPTY) and schema_version ("output-parser-v1") for downstream routing and fallback decisions.

**Traces to:** E12.4
**Priority:** P1

### FR-OUT-005: Condensed Output Extraction (extract_condensed)

The system SHALL provide `extract_condensed()` as the primary extraction entry point that attempts JSONL extraction first, falls back to plain text extraction with noise stripping, and returns the most meaningful content block from agent output regardless of provider format.

**Traces to:** E12.5
**Priority:** P1

---

## FR-FED: Policy Federation

### FR-FED-001: Hierarchical Policy Namespace Model

The system SHALL support a three-level hierarchical namespace (`org.project.environment`) for policy isolation and inheritance, where policies at higher levels (e.g., org) apply to lower levels (e.g., project, environment) unless explicitly overridden.

**Traces to:** WP-13001
**Priority:** P1

### FR-FED-002: Federated Policy Resolution

The system SHALL resolve policies by traversing the namespace hierarchy from most specific to most general (org.project.env -> org.project.default -> org.default.default), loading the first matching JSON policy file found in the designated policy directory structure.

**Traces to:** WP-13001
**Priority:** P1

### FR-FED-003: Jurisdiction Profile Mapping and Overlay

The system SHALL map geographical regions to legal/audit jurisdiction profiles (e.g., EU-AI-ACT, US-SEC) and overlay profile-specific constraints (e.g., human-in-loop requirements, retention periods) onto resolved policies.

**Traces to:** WP-13002
**Priority:** P1

### FR-FED-004: Cross-Namespace Consent Relay

The system SHALL support relaying approval consent between namespaces for multi-tenant workflows, generating a traceable relay artifact with provenance signatures.

**Traces to:** WP-13003
**Priority P2

### FR-FED-005: Policy Conflict Arbitration

The system SHALL arbitrate conflicts between multiple federated policies using a "most restrictive wins" strategy for critical constraints like risk thresholds and human-in-loop requirements.

**Traces to:** WP-13004
**Priority:** P1

### FR-FED-006: Federation Health and Drift Observability

The system SHALL provide observability into the state of the policy federation, including namespace discovery, sync status, and drift detection across the mesh.

**Traces to:** WP-13005
**Priority:** P2

---

## FR-EXIT: Exit Codes

### FR-EXIT-001: Standardized Exit Codes with Human-Readable Messages

The system SHALL define standardized exit codes (EXIT_TIMEOUT=124 for timeouts, EXIT_HEALTH_GATE_FAILED=2 for governance gate failures) with human-readable message descriptions accessible via `get_exit_message()`, returning None for unknown codes.

**Traces to:** E7.6
**Priority:** P2

---

## FR-HAX: Harmonious Agent Experience (Unified)

### FR-HAX-001: Unified Prompt Queue (UPQ)

The system SHALL maintain a single, project-aware prompt queue in `.thegent/prompt_queue.jsonl` (fallback to `~/.thegent/` if not in project), storing tasks with timestamp, prompt, project path, and status (pending/claimed/done).

**Traces to:** HAX-01
**Priority:** P1

### FR-HAX-002: Cross-Platform Rules Synchronization

The system SHALL provide a `thegent rules sync` command that reads canonical rules from `.thegent/rules/` and synchronizes them to `.cursor/rules/` (.mdc), `CLAUDE.md`, and `.codex/skills/` (SKILL.md).

**Traces to:** HAX-02
**Priority:** P1

### FR-HAX-003: Pareto-Optimal Model Routing via LiteLLM

The system SHALL integrate `litellm` as the routing backend, selecting models from the catalog based on a `TaskRouter` that maps task category (FAST, COMPLEX, etc.) to the Pareto-optimal route (cheapest/fastest/highest quality).

**Traces to:** HAX-03
**Priority:** P1

### FR-HAX-004: Universal Memory Provider (Supermemory.ai)

The system SHALL implement a `SupermemoryProvider` that integrates with Supermemory.ai for L3 (Long-term Graph) and L4 (Archival Document) memory, replacing local file-based context stores.

**Traces to:** HAX-04
**Priority:** P1

### FR-HAX-005: Automated Documentation Gardening (Gardener)

The system SHALL provide a `Gardener` agent that synthesizes recent audit logs and memory fragments into updates for `CLAUDE.md`, `ADR.md`, `PRD.md`, and `PLAN.md`.

**Traces to:** HAX-05
**Priority:** P2
