# Thegent Gaps and Discovery Report

**Date:** 2026-02-14  
**Scope:** All plan files, research files, docset artifacts. Identifies gaps to fill, optional→required items, optimizations/polishes not done, and discovery tasks.

---

## Executive Summary

| Category | Count | Priority |
|----------|-------|----------|
| **Required gaps** | 23 | P0–P1 |
| **Optional→required** | 12 | P1 |
| **Optimizations/polishes** | 18 | P1–P2 |
| **Discovery tasks** | 8 | P2 |

---

## 1. CLIPROXY API & Thegent Unified Plan

**Source:** `docs/plans/CLIPROXY_API_AND_THGENT_UNIFIED_PLAN.md`

### Gaps (Required)

| ID | Item | Status | Notes |
|----|------|--------|-------|
| C1 | **Phase 2: Cursor dedicated block** | ✓ Done | cliproxyapi-plusplus: CursorKey, synthesizeCursorKeys, cursorAddToken, config.example, PROVIDER_SETUP_GUIDE |
| C2 | **Phase 1: Fix Cursor config** | Done | config.example has cursor block; note: "Do NOT use api-key-entries" |
| C3 | **Phase 1: Regenerate patch** | N/A | Fork has cursor; patch for upstream PR if needed |

### Parity Matrix

- Cursor: Phase 2 (not Phase 2 done); cliproxy: Phase 4 done.
- All other providers (MiniMax, Roo, Kilo) done.

---

## 2. FastMCP Implementation Plan

**Source:** `docs/plans/THGENT_FASTMCP_IMPLEMENTATION_PLAN.md`

### Verification Gaps (Required)

| ID | Item | Section | Status |
|----|------|---------|--------|
| F1 | Cursor MCP config: add thegent server; tools visible | §9 | ✓ 2026-02-14 |
| F2 | `thegent_run` with gemini/cursor-agent returns output | §9 | [ ] (requires API key) |
| F3 | `thegent_bg` returns session_id; `thegent_ps` lists it | §9 | [ ] (requires API key) |
| F4 | Progress updates during long `thegent_run` (Phase 3) | §9 | [ ] |
| F5 | Resources `thegent://session/{id}/logs` return log content (Phase 2) | §9 | ✓ 2026-02-14 |
| F6 | Prompts render correctly (Phase 2) | §9 | ✓ 2026-02-14 |

### Phase 2–5 Gaps (Optional→Required)

| ID | Item | Phase | Notes |
|----|------|-------|-------|
| F7 | Resources: sessions, session/meta, session/logs, dag, agents, models | Phase 2 | ✓ 2026-02-14: 6/6 readable |
| F8 | Prompts: thegent_run_agent, thegent_create_wbs, thegent_bg_task | Phase 2 | ✓ 2026-02-14 (F6) |
| F9 | Background Tasks: `task=True` for `thegent_run` | Phase 3 | ✓ TaskConfig(mode="optional") on thegent_run |
| F10 | Elicitation: cd/owner ambiguous → ctx.elicit() | Phase 4 | ✓ ctx.elicit in thegent_run, thegent_bg, thegent_dag_list |
| F11 | Health Route: `@mcp.custom_route("/health")` | Phase 4 | ✓ 2026-02-14 |
| F12 | Production: Auth, stateless, Redis, session state store | Phase 5 | Deferred; document as future |

### Optimizations/Polishes (Design Excellence §14)

| ID | Item | Section | Status |
|----|------|---------|--------|
| F13 | ResponseCachingMiddleware for ps, list_agents, list_models (TTL 30s) | §12, §14.1 | ✓ Verified: mcp_server.py CallToolSettings ttl=30 |
| F14 | RateLimitingMiddleware (max 10/s, burst 20) | §12 | ✓ Verified: max_requests_per_second=10, burst_capacity=20 |
| F15 | ResponseLimitingMiddleware (max 500K) for thegent_logs | §12 | ✓ Verified: ResponseLimitingMiddleware(max_size=500_000) |
| F16 | Tool annotations: read_only, destructive, idempotent | §14.2 | ✓ Verified: readOnlyHint, destructiveHint, idempotentHint per tool |
| F17 | ToolResult with structured_content + meta.execution_time_ms | §14.2 | ✓ Verified: ToolResult used with structured_content, meta.execution_time_ms |
| F18 | thegent_inspect tool | §3.1 | ✓ Verified: thegent_inspect exists |
| F19 | Icons/UX hints for tools (optional) | §14.8 | Not implemented |
| F20 | Phase 6–7 checklist (§14.11) | ✓ Done | FASTMCP_PHASE_CHECKLIST_VERIFICATION.md |

### Discovery / Prerequisite

| ID | Item | Notes |
|----|------|-------|
| F21 | **CLI Single Source of Truth audit** | ✓ Done 2026-02-14. See `thegent-cli-single-source-of-truth-audit-2026-02-14.md` |
| F22 | **Research tasks (§11)** | ✓ Done 2026-02-14. Created FASTMCP_STORAGE_EVENTSTORE.md, FASTMCP_MIDDLEWARE.md, FASTMCP_SAMPLING_TELEMETRY.md |

---

## 3. Distributed Model Routing Plan

**Source:** `docs/plans/DISTRIBUTED_MODEL_ROUTING_PLAN.md`

### Pillar 1: Dynamic Scraping — Gaps

| ID | Task | Status | Notes |
|----|------|--------|-------|
| R1 | S1.4: gemini_adapter, claude_adapter (--help or API) | ✓ Done | scrape_gemini/claude try models list, --help; fallback static |
| R2 | S1.3: proxy_adapter for antigravity/minimax/glm | ✓ Done | scrape_proxy GET /v1/models; fallback when proxy down |
| R3 | S1.7: list_models_impl uses scraped catalog; fallback on failure | ✓ Verified | get_scraped_catalog; try/except fallback to static |
| R4 | S1.8: `thegent list-models --by-model` | ✓ Verified | ModelCatalog.to_catalog_view(use_scraped=True).by_model |
| R5 | S1.9: MCP thegent_list_models returns scraped catalog | ✓ Done | by_model param; list_models_impl returns by_model dict |

### Scraping Adapters Status (from §9.1)

| Provider | Scraping | Source |
|----------|----------|--------|
| cursor-agent | ✓ | cursor agent --list-models |
| copilot | ✓ | copilot --help |
| codex | ✓ | cursor --list-models filtered |
| gemini | ✓ | gemini models list / --help; fallback static |
| claude | ✓ | claude models list / --help; fallback static |
| antigravity | ✓ | proxy GET /v1/models; fallback static |
| minimax | ✓ | proxy; fallback minimax-m2.5 |
| glm | ✓ | proxy; fallback glm-5 |

### Optimizations

| ID | Item | Notes |
|----|------|-------|
| R6 | SA2–SA4: gemini_adapter, claude_adapter (--help subprocess) | Plan §12.5 |
| R7 | SA1: proxy_adapter GET /v1/models | Verify for cliproxy/antigravity |
| R8 | Cost-based routing (cheapest policy) | ✓ Documented: COST_ROUTING_DEFERRED.md; cheapest policy + cost_weight exist; per-run tracking deferred |

---

## 4. Research Validation Addendum (XML/Contract Deltas)

**Source:** `docs/docset/thegent-research-validation-2026-02-14.md`

### Required Architecture Deltas (All P0–P1)

| ID | Delta | WBS | Status |
|----|-------|-----|--------|
| V1 | XML Contract Registry (versioned, capability negotiation) | WBS-X1 | ✓ Done: contracts/registry.py, migration_window_end added |
| V2 | Canonical Structured Message (CSM) model | WBS-X2 | ✓ Done: contracts/csm.py, CONTRACT_AUTHORITY.md |
| V3 | Incremental XML Parser Engine | WBS-X3 | ✓ Done: contracts/parser.py IncrementalXMLParser, get_partial_state |
| V4 | Semantic Validation Layer | WBS-X4 | ✓ Done: contracts/validation.py validate_csm, phase-aware invariants |
| V5 | Provider Adapter Conformance Suite | WBS-X5 | ✓ Done: conformance suite, drift alarm (--check-drift), cursor-agent XML adapter |
| V6 | Fallback Reliability Policy | WBS-X6 | ✓ Done: FallbackStateMachine, FallbackPolicy, evaluate_fallback, FALLBACK_POLICY.md |
| V7 | Contract Migration Controller | WBS-X7 | ✓ Partial: MigrationController, evaluate_version, get_preferred_version, govern migration; dual-read/dual-write pipeline not wired |
| V8 | Contract Telemetry and Drift Detection | WBS-X7 | ✓ Done: ContractTelemetry.record_normalization, get_stats, analyze_drift |

### Functional Requirements (FR-X01–FR-X08)

- FR-X01: contract version negotiation — not implemented  
- FR-X02: canonical normalization pipeline — ✓ Done: normalize_output, adapters, XMLOutputAdapter→CSM  
- FR-X03: incremental parser with recoverable partial-state — ✓ Done: IncrementalXMLParser, get_partial_state  
- FR-X04: semantic validation with cross-tag invariants — ✓ Done: validate_csm, status/progress/phase invariants    
- FR-X05: provider adapter conformance tests and drift alarms — ✓ run_conformance_suite, govern conformance --check-drift, ContractTelemetry.detect_drift  
- FR-X06: policy-governed fallback routing with SLO budgets — ✓ FallbackPolicy, max_fallback_rate, evaluate_fallback
- FR-X07: dual-read/dual-write migration support — Partial: MigrationController + govern migration; pipeline dual-read/write not wired  
- FR-X08: observability for parse quality, semantic quality, fallback — ✓ Done: ContractTelemetry in closure_pack (parse quality, fallback rate, adapter confidence, drift vs budget, drift issues)  

### Prioritized Sequence (from §9)

- **P0:** contract registry + canonical schema + adapter scaffolding  
- **P1:** incremental parser and structural validation migration  
- **P2:** semantic validation and fallback control plane  
- **P3:** conformance test suite and drift alarms  
- **P4:** migration controller, canary rollout, deprecation  

---

## 5. Governance Policy Audit Research

**Source:** `docs/research/GOVERNANCE_POLICY_AUDIT_RESEARCH.md`

### Implementation Status vs WBS

| WP | Description | Implementation | Gap |
|----|-------------|----------------|-----|
| WP-3001 | Policy pre-check and gate evaluator | PolicyEngine in execution.py | OPA/NeMo integration optional |
| WP-3002 | Signed action artifacts | SHA-256 signatures on runs | MAIF artifact structure optional |
| WP-3003 | Override path with TTL | OverrideRegistry, override_ttl_seconds | ✓ Done: revalidation on expiry |
| WP-3004 | Immutable audit trail | history verify | Hash chain, WORM storage |
| WP-3005 | Policy drift detection | policy show, govern sweep | ✓ Done: govern sweep (drift + past-SLA) |
| WP-3006 | Compliance evidence retention | retention_days_*, archive --domain | ✓ Done: tiered retention, domain filter |
| WP-3007 | Trust boundary checks | TrustBoundaryValidator | ✓ Done: env transition validation, skip-level block |
| WP-3008 | Escalation SLA | EscalationQueue, govern escalate list/add/resolve | ✓ Done: queue, SLA tracking, auto-add on deny |

### Technology Stack (from §11)

- OPA, OPAL, Oso, NeMo Guardrails, Guardrails AI, Portkey, WORM storage, OpenTelemetry — verify integration status.

---

## 6. Cross-Analysis Matrix & Kush Docs Deep Dive

**Sources:** `thegent-cross-analysis-matrix-2026-02-14.md`, `thegent-kush-docs-deep-dive-2026-02-14.md`

### Delta Set A: Contract and Parser Engineering

| ID | Item | Priority |
|----|------|----------|
| XA1 | Canonical schema package `contracts/csm/v1` | P0 |
| XA2 | Adapter interface per provider with conformance suite | P0 | ✓ Done |
| XA3 | Streaming parser with partial-commit safety | P1 |
| XA4 | Contract version negotiation in task metadata | P1 | ✓ Done: dag add/update/run --contract-version, task-level override |

### Delta Set B: Runtime and Fallback Policy

| ID | Item | Priority |
|----|------|----------|
| XB1 | Fallback state machine with bounded retries | P1 | ✓ Done |
| XB2 | Parser-quality and adapter-confidence in routing | P1 | ✓ Done: rank_providers_by_parser_quality, routing_parser_quality_enabled |
| XB3 | Fallback observability KPIs | P2 | ✓ Done: thegent observe kpis, get_fallback_kpis |

### Delta Set C: Governance and Quality Gates

| ID | Item | Priority | Status |
|----|------|----------|--------|
| XC1 | Semantic validation gate before promotion | P1 | ✓ Done: state_machine validate_csm blocks promotion |
| XC2 | Contract drift alarms; blocked promotion on critical drift | P1 | ✓ Done: Policy 2b blocks critical lane when drift exceeds budget; observe drift; dag run --check-drift, govern conformance --check-drift |
| XC3 | No critical lane action with unknown contract version | P1 | ✓ Done: migrator.evaluate_version rejects unknown before run |

### Delta Set D: Planning and Simulation

| ID | Item | Priority |
|----|------|----------|
| XD1 | PERT uncertainty overlays to WBS milestone confidence | P2 | ✓ Partial: plan analyze --pert, pert_forward_pass |
| XD2 | Resource contention simulation for parallel DAG waves | P2 | ✓ Partial: plan analyze --resources, simulate_resource_contention (stub) |
| XD3 | Continuity risk scoring for shift handoff | P2 | ✓ Partial: plan analyze --continuity, score_continuity_risk |

### Kush Docs: Universal Operation Interfaces (D-B)

| ID | Item | Notes |
|----|------|-------|
| XK1 | thegent.orchestrate, thegent.govern, thegent.recover, thegent.observe, thegent.plan | ✓ Done: orchestrate/govern/recover/observe/plan apps, Operation enum, thegent operations, thegent_list_operations, thegent://operations |
| XK2 | Multi-agent mode catalog: sequential_delegation, parallel_consensus, review_loop | ✓ Done: orchestration_modes.py, thegent modes, thegent_list_modes, suggest_mode |
| XK3 | Contract authority publication | task-tool docs vs impl mismatch resolution |
| XK4 | CI architecture boundary checks | tach/grimp/deply style |

---

## 7. Orchestration WBS/DAG/PRD — Completion Verification

**Sources:** `thegent-wbs-final.md`, `thegent-dag-final.md`, `thegent-prd-final.md`, `thegent-implementation-log-2026-02-14.md`

### Phase 0: Foundation

| WP | Description | Status |
|----|-------------|--------|
| WP-0001 | Baseline telemetry contracts and run IDs | Done (Chunk 219) |
| WP-0002 | Canonical schemas for chunk/evidence/policy events | Partial |
| WP-0003 | Planner dependency graph normalization | Done |
| WP-0004 | Initial risk and confidence scoring framework | Done |
| WP-0005 | Program operating model and ownership map | ✓ Done: docs/enterprise/OPERATING_MODEL.md (RACI, escalation paths) |

### Phase 6: Enterprise Readiness — Gaps

| WP | Description | Status |
|----|-------------|--------|
| WP-6002 | Security and compliance signoff package | ✓ Done: closure-pack with audit trail, architecture refs, risk/oversight refs |
| WP-6004 | Runbook finalization and on-call readiness | ✓ Done: RUNBOOK.md with escalation, recovery, decommission links |
| WP-6006 | Decommission/sunset plan for temporary controls | ✓ Done: DECOMMISSIONING_PLAN.md with targets, migration path, rollback |
| WP-6007 | Post-launch observation and rollback reserve | ✓ Done: POST_LAUNCH_OBSERVATION_PLAYBOOK.md (severity→SLA, rollback checklist) |

### Plan Index Completion Definition

- WBS phase exits satisfied and signed off — verify  
- DAG invariants pass in canary and production — verify  
- PRD acceptance criteria met — verify  
- Auditability, rollback, continuity SLAs for two release cycles — verify  
- Remaining open risks accepted or closed — verify  

### Next Artifacts (from plan index)

- WBS-to-issue import matrix — ✓ `WBS_TO_ISSUE_IMPORT_MATRIX.md`  
- DAG node-to-service contract checklist — ✓ `DAG_NODE_SERVICE_CONTRACT_CHECKLIST.md`  
- PRD test plan matrix — ✓ `PRD_TEST_PLAN_MATRIX.md`  

---

## 8. Discovery Tasks (Explicit)

### FastMCP Research (§11 of THGENT_FASTMCP_IMPLEMENTATION_PLAN.md)

```bash
# 1. Storage + EventStore
thegent bg cursor-agent -d <cwd> "Read gofastmcp.com/servers/storage-backends and fastmcp/server/event_store.py. Extract: (a) RedisStore, DiskStore usage, (b) EventStore(storage=), (c) FernetEncryptionWrapper for OAuth. Output to docs/research/FASTMCP_STORAGE_EVENTSTORE.md"

# 2. Middleware pipeline
thegent bg cursor-agent -d <cwd> "Read gofastmcp.com/servers/middleware. Extract: (a) add_middleware order, (b) ResponseCachingMiddleware with CallToolSettings, (c) RateLimitingMiddleware params, (d) on_call_tool hook for thegent_run. Output to docs/research/FASTMCP_MIDDLEWARE.md"

# 3. Sampling + Telemetry
thegent bg cursor-agent -d <cwd> "Read gofastmcp.com/servers/sampling and servers/telemetry. Extract: (a) ctx.sample with result_type, (b) get_tracer(), (c) opentelemetry-instrument. Output to docs/research/FASTMCP_SAMPLING_TELEMETRY.md"
```

### Verification Runbook (FastMCP §9.1)

| Item | How to verify |
|------|---------------|
| Cursor MCP config | Settings → MCP → Add server; URL: http://127.0.0.1:3847/mcp |
| thegent_run | Call with agent=gemini, prompt="Hello"; expect stdout |
| thegent_bg / thegent_ps | bg → session_id; ps → session appears |
| Progress updates | Long run; check MCP stream for progress |
| Resources | thegent://session/{id}/logs returns content |
| Prompts | List prompts; render with args; verify output |

---

## 9. Consolidated Action List

### P0 (Immediate)

1. ~~**Cursor Phase 2**~~ ✓ Done (CLIPROXY fork has cursor: block, synthesizeCursorKeys, PROVIDER_SETUP_GUIDE).
2. ~~**Contract Registry + Canonical Schema**~~ ✓ Done (contracts/registry.py, csm.py, adapters.py, CONTRACT_AUTHORITY.md).
3. ~~**Contract authority**~~ ✓ Done: task-tool docs/xml_contract.md aligned with impl (task_graph, snake_case); CONTRACT_AUTHORITY.md references it.  
4. ~~**CLI Single Source of Truth audit**~~ ✓ Done (thegent-cli-single-source-of-truth-audit-2026-02-14.md).

### P1 (Short-term)

5. **FastMCP verification** (F1–F6): F1, F5, F6, F11 done. F2, F3 require API keys (run `scripts/verify-fastmcp.py --no-skip-api`). F4 manual.  
6. ~~**FastMCP Phase 2–4 polish** (F7–F12)~~ ✓ F7–F11 verified. F12 deferred.  
7. ~~**Model scraping adapters** (R1–R2)~~ ✓ gemini/claude/proxy adapters with multi-cmd fallback.  
8. ~~**Incremental parser + semantic validation** (V3, V4, XA3, XC1)~~ ✓ V3/V4 implemented; XC1 semantic gate blocks promotion.  
9. ~~**Fallback state machine** (V6, XB1)~~ ✓ FallbackStateMachine, policy, telemetry, bounded retries.  
10. ~~**Provider adapter conformance** (V5, XA2)~~ ✓ Done: conformance suite, drift alarm, cursor-agent.  
11. ~~**Universal operation interfaces** (XK1)~~ ✓ Done: orchestrate/govern/recover/observe/plan CLI apps, Operation enum, thegent operations, thegent_list_operations.  
12. ~~**Phase 6 enterprise** (WP-6002, WP-6004, WP-6006)~~ ✓ Done: closure-pack signoff, RUNBOOK.md, DECOMMISSIONING_PLAN.md.

### P2 (Medium-term)

13. ~~**FastMCP research tasks** (F22)~~ ✓ Done: FASTMCP_STORAGE_EVENTSTORE.md, FASTMCP_MIDDLEWARE.md, FASTMCP_SAMPLING_TELEMETRY.md.  
14. ~~**PERT/simulation overlays** (XD1–XD3)~~ ✓ Partial: thegent plan analyze --pert/--resources/--continuity.  
15. ~~**Fallback observability KPIs** (XB3)~~ ✓ Done: thegent observe kpis.  
16. ~~**Contract migration controller** (V7)~~ ✓ Partial: MigrationController, govern migration; dual-read/write pipeline deferred.  
17. ~~**Next artifacts** (plan index)~~ ✓ WBS matrix, DAG contract checklist created; PRD test matrix pending.  
18. ~~**Multi-agent mode catalog** (XK2)~~ ✓ Done: orchestration_modes.py, thegent modes, thegent_list_modes.

### Optional→Required (Treat as P1)

- All FastMCP Phase 2–4 items (resources, prompts, elicitation, health).  
- All design excellence items (§14) where not yet verified.  
- Governance WP-3003 revalidation, WP-3006 retention, WP-3008 escalation — see GOVERNANCE_WP_GAPS.md.  
- ~~Cost-based routing documentation (even if deferred)~~ ✓ COST_ROUTING_DEFERRED.md.

---

## 10. Summary Table

| Plan/Research | Total Gaps | P0 | P1 | P2 |
|---------------|------------|----|----|-----|
| CLIPROXY API | 3 | 1 | 2 | 0 |
| FastMCP | 22 | 1 | 15 | 6 |
| Distributed Routing | 8 | 0 | 5 | 3 |
| Research Validation | 8 | 2 | 4 | 2 |
| Governance Research | 8 | 0 | 4 | 4 |
| Cross-Analysis / Kush | 14 | 2 | 8 | 4 |
| Orchestration WBS | 7 | 0 | 4 | 3 |
| **Total** | **70** | **6** | **42** | **22** |

---

## References

- `docs/docset/REMAINING_GAPS_DEEP_DIVE.md` — Full-depth analysis of remaining gaps
- `docs/research/GOVERNANCE_WP_GAPS.md` — WP-3003, WP-3006, WP-3008 implementation notes
- `docs/plans/CLIPROXY_API_AND_THGENT_UNIFIED_PLAN.md`
- `docs/plans/THGENT_FASTMCP_IMPLEMENTATION_PLAN.md`
- `docs/plans/DISTRIBUTED_MODEL_ROUTING_PLAN.md`
- `docs/plans/NEW_PROVIDERS_AUTH_RESEARCH.md`
- `docs/plans/CURSOR_API_INTEGRATION_RESEARCH.md`
- `docs/research/GOVERNANCE_POLICY_AUDIT_RESEARCH.md`
- `docs/docset/thegent-research-validation-2026-02-14.md`
- `docs/docset/thegent-cross-analysis-matrix-2026-02-14.md`
- `docs/docset/thegent-kush-docs-deep-dive-2026-02-14.md`
- `docs/docset/thegent-plan-final-index.md`
- `docs/docset/thegent-wbs-final.md`
- `docs/docset/thegent-dag-final.md`
- `docs/docset/thegent-prd-final.md`
- `docs/docset/thegent-implementation-log-2026-02-14.md`
- `docs/research/FASTMCP_PROGRESS_TASKS.md`
- `docs/research/FASTMCP_TRANSFORMS_DEPLOYMENT.md`
- `docs/research/FASTMCP_ELICITATION_CONTEXT.md`
