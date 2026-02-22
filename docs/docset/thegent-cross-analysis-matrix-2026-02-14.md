# Thegent Cross-Analysis Matrix (Deep)

Date: 2026-02-14
Status: Addendum for breadth/depth expansion
Scope: Cross-system synthesis across `thegent`, `task-tool`, `zen-mcp-server`, `crun`, `pheno-sdk`.

## 1. Why this exists

Your final split docset is strong, but this matrix captures cross-project design transfers so thegent can absorb proven patterns and avoid known failure modes.

## 2. Systems compared

- `thegent`: MCP-native orchestrator, provider multiplexing (`gemini`, `copilot`, `codex`, `claude`, etc.), DAG/session operations.
- `task-tool`: strict Planner/Operator/Reviewer lifecycle with canonical 18-tag XML contract.
- `zen-mcp-server`: rich XML communication protocol, streaming parser/fallback path, smart-contract validation patterns.
- `crun`: WBS/PERT/resource modeling and business-rule consistency validation.
- `pheno-sdk`: fallback execution adapters, deployment rollback strategies, observability primitives.

## 3. Source anchors

- `../thegent/src/thegent/mcp_server.py`
- `../thegent/src/thegent/main.py`
- `../thegent/src/thegent/agents/direct_agents.py`
- `../task-tool/task_tool/server/config.py`
- `../task-tool/task_tool/server/task_graph.py`
- `../task-tool/task_tool/server/orchestrator.py`
- `../task-tool/task_tool/executors/cli.py`
- `../zen-mcp-server/src/shared/agents/agent_prompts.py`
- `../zen-mcp-server/src/shared/utilities/agent/fastmcp_agent_client.py`
- `../zen-mcp-server/src/shared/utilities/agent/agent_xml_enhancer.py`
- `../crun/crun/core/planning_advanced.py`
- `../crun/crun/core/validation.py`
- `../pheno-sdk/src/pheno/adapters/execution/fallback_executor.py`
- `../pheno-sdk/src/pheno_sdk/deployment_strategies.py`

## 4. Comparative matrix

### 4.1 Orchestration model

- `thegent`: strong MCP middleware and runtime tools; needs deeper typed event normalization across provider outputs.
- `task-tool`: strict phase sequencing (Planner -> Operator -> Reviewer), explicit phase gating.
- `zen`: rich workflow orchestration and progress tags, with XML+MCP hybrid transport behavior.
- `crun`: planning-heavy models (PERT/resources) but less agent transport specialization.
- `pheno`: execution adapter fallback chains and deployment orchestrators with rollback control.

Cross transfer:
- bring task-tool phase strictness into thegent workflow lanes.
- bring pheno fallback policy primitives into thegent provider routing.

### 4.2 Structured output contracts

- `task-tool`: fixed 18-tag exact-once contract and structural validator.
- `zen`: broad XML vocabulary for status/progress/actions/resources, richer telemetry semantics.
- `thegent`: currently no single canonical structured-output schema across all providers.

Cross transfer:
- unify strictness + richness into a versioned canonical schema with adapters.

### 4.3 Parsing and streaming

- `task-tool`: root-bounded extraction + strict validation.
- `zen`: stream parsing and final parsing with regex-heavy extraction in places.
- `thegent`: execution integration exists; parser standardization is the largest gap.

Cross transfer:
- use incremental parser with explicit partial-state validity and final-state commitment rules.

### 4.4 Governance and safety

- `thegent`: middleware-level rate/size/error/timing/caching controls are strong.
- `task-tool`: phase-order correctness and XML contract gating are strong.
- `zen`: contract validation concepts and schema-first tool patterns are strong.
- `pheno`: production rollback policies and canary/blue-green execution are strong.

Cross transfer:
- formal policy gates should include parser-quality and adapter-confidence criteria.

### 4.5 Recovery and fallback

- `thegent`: supports provider orchestration and sessions; recovery policy can be more formalized.
- `pheno`: explicit fallback chains with retries and provider failover logic.
- `zen`: MCP fallback to XML path during streaming/execution interruptions.

Cross transfer:
- adopt unified fallback state machine with hard SLO budgets and drift events.

### 4.6 Planning depth

- `crun`: advanced PERT/resource/Monte Carlo and business-rule consistency checks.
- `thegent` docs: broad WBS/DAG/PRD coverage.

Cross transfer:
- add probabilistic schedule-risk overlays and resource contention simulation to final WBS governance gates.

## 5. High-confidence synthesis patterns

- Pattern P-01: `Strict Core + Rich Extension`
- Keep a strict minimal canonical schema required for all providers, plus optional extension blocks.

- Pattern P-02: `Dual validator`
- Structural validator first, semantic validator second.

- Pattern P-03: `Fallback state machine`
- Explicit transitions: `primary -> degraded -> fallback -> recovered` with policy gates.

- Pattern P-04: `Phase-gated multi-agent rounds`
- Planner/Operator/Reviewer semantics reduce chaotic execution and improve auditability.

- Pattern P-05: `Canary + rollback policy`
- Apply pheno-style deployment safeguards to contract and parser migrations.

## 6. New deltas to apply (beyond prior addendum)

### 6.1 Delta set A: Contract and parser engineering

- A1: Add canonical schema package `contracts/csm/v1`.
- A2: Add adapter interface per provider with conformance suite.
- A3: Add streaming parser with partial-commit safety.
- A4: Add contract version negotiation in task metadata.

### 6.2 Delta set B: Runtime and fallback policy

- B1: Add fallback state machine with bounded retries and provider scoring.
- B2: Add parser-quality and adapter-confidence to routing decisions.
- B3: Add fallback observability KPIs (`fallback_rate`, `fallback_success`, `recovery_time`).

### 6.3 Delta set C: Governance and quality gates

- C1: Add semantic validation gate before promotion.
- C2: Add contract drift alarms and blocked promotion on critical drift.
- C3: Add policy rule: no critical lane action with unknown contract version.

### 6.4 Delta set D: Planning and simulation depth

- D1: Add PERT uncertainty overlays to WBS milestone confidence.
- D2: Add resource contention simulation for heavy parallel DAG waves.
- D3: Add continuity risk scoring for shift handoff reliability.

## 7. WBS/DAG/PRD impact mapping

- WBS impact:
- Add `Phase-X Contract/Adapter Hardening` and `Phase-Y Simulation Governance`.

- DAG impact:
- Insert nodes for `contract-detect`, `adapter-normalize`, `semantic-validate`, `fallback-policy-eval`.

- PRD impact:
- Add FR/NFR for contract negotiation, parser resilience, adapter conformance, fallback SLO.

## 8. Priority and execution order

- P0 (immediate): canonical schema + adapters + structural validator.
- P1: streaming parser and semantic validator.
- P2: fallback state machine + policy gating.
- P3: simulation overlays (PERT/resource/continuity risk).
- P4: full migration and deprecation of legacy parsing branches.

## 9. What to enforce in CI

- Contract conformance tests per provider.
- Structural + semantic validation corpus tests.
- Fallback state-machine replay tests.
- Drift alarms treated as release blockers for critical lanes.
- Probabilistic schedule confidence report for major releases.

## 10. Final assessment

- Current plan quality: high.
- Cross-analysis verdict: strong foundation with clear next leverage.
- Most valuable remaining investment: structured-output unification + parser/fallback formalization + simulation-backed planning confidence.


---
## See also

- [WORK_STREAM.md](../reference/WORK_STREAM.md) — canonical backlog
- [00-MASTER-INDEX.md](../plans/00-MASTER-INDEX.md) — plan index
