# Merged Fragmented Markdown

## Source: changes/research-compute-offload/INDEX.md

# Consolidated Index

## Files

* `INDEX.md`
* `SYNTHESIS.md`
* `design.md`
* `proposal.md`
* `tasks.md`

## Subdirectories


---

## Source: changes/research-compute-offload/SYNTHESIS.md

# Synthesis: Mac ↔ PC Compute Offload Research Initiative\n\n**Document Version:** 1.0  \n**Change ID:** research-compute-offload  \n**Date:** 2026-02-18  \n**Status:** Synthesized Overview  \n\n---\n\n## Executive Summary\n\nThis research initiative proposes intelligent compute offloading between macOS (Mac) and Windows/Linux (PC) environments within the thegent orchestration framework. The research spans three coordinated documents:\n\n1. **proposal.md** — Problem statement, solution vision, research questions, success criteria\n2. **design.md** — Technical architecture, component specifications, integration patterns\n3. **tasks.md** — Implementation breakdown, phase structure, resource allocation\n\nTogether, these documents form a **complete research-to-prototype roadmap** with clear go/no-go decision points and handoff criteria.\n\n---\n\n## Document Relationships\n\n### Information Flow\n\n```\n┌──────────────────────────────────────────────────────────────┐\n│  proposal.md                                                 │\n│  • Problem & Opportunity                                    │\n│  • Solution Vision                                          │\n│  • 10 Research Questions                                    │\n│  • Success Criteria (prototype artifacts)                   │\n│  • Risks & Mitigations                                      │\n└────────────────────┬─────────────────────────────────────────┘\n                     │\n                     │ \"How to build?\" → design.md\n                     ▼\n┌──────────────────────────────────────────────────────────────┐\n│  design.md                                                   │\n│  • Architecture diagram & component roles                   │\n│  • 7 core components with code structure                    │\n│  • Data models (Pydantic)                                   │\n│  • Integration hooks with thegent                           │\n│  • Protocol specs (HTTP + JSON)                             │\n│  • Security & error handling                                │\n│  • Decision log (Why HTTP? Why JSON? etc.)                  │\n└────────────────────┬─────────────────────────────────────────┘\n                     │\n                     │ \"What to build first?\" → tasks.md\n                     ▼\n┌──────────────────────────────────────────────────────────────┐\n│  tasks.md                                                    │\n│  • 4 Phases with clear milestones                           │\n│  • 16 Tasks grouped by responsibility                       │\n│  • Task dependency graph (DAG)                              │\n│  • Effort estimates (person-days)                           │\n│  • Success metrics per task                                 │\n│  • Resource allocation suggestions                          │\n│  • Timeline: ~15 agent-days / 2-3 weeks                     │\n└──────────────────────────────────────────────────────────────┘\n```\n\n### Traceability\n\nEach proposal research question traces to design components and tasks:\n\n| Research Q | Design Component | Key Task | Success Metric |\n|---|---|---|---|\n| **Feasibility: Network reliability** | RemoteExecutor (timeout + retry) | T2.6 | E2E test: ≥90% success rate |\n| **Feasibility: Latency impact** | OffloadRouter, OffloadClient | T3.1 | Measure <5s per offload cycle |\n| **Feasibility: Auth & trust** | Bridge Protocol (bearer token) | T2.5 | Validate requests with auth |\n| **Feasibility: Isolation** | Remote Executor (OS-level) | T2.6 | No cross-task interference |\n| **Architecture: Protocol choice** | BridgeProtocol (HTTP + JSON) | T1.3, T2.5 | Protocol schema complete |\n| **Architecture: Registry model** | ComputeCatalog (file + sync) | T2.1 | Catalog loads/saves, query works |\n| **Architecture: Routing algorithm** | OffloadRouter (cost/latency/capability) | T2.4 | Route selection correct |\n| **Architecture: Failure modes** | Integration + Fallback logic | T2.8 | Offload error → local execution |\n| **Economics: Cost benefit** | Cost estimation, aggregation | T2.6 | Measure actual cost per task |\n| **Economics: SLA guarantees** | Perf measurements, logging | T3.1 | Latency baseline documented |\n\n---\n\n## Key Design Decisions\n\n### 1. HTTP + JSON Bridge Protocol\n\n**Rationale** (from design.md Decision Log):\n- ✅ Simplicity: No need for gRPC compilation or binary serialization\n- ✅ Debugging: curl/Postman can inspect messages; human-readable logs\n- ✅ Stateless: Easier to load balance or add multiple executors\n- ❌ Trade-off: Less efficient than gRPC (binary + streaming), but complexity not justified for prototype\n\n**Implication**: All offload messages use JSON; executors are simple HTTP servers (FastAPI)\n\n### 2. File-Based Compute Catalog with Periodic Sync\n\n**Rationale** (from design.md Decision Log):\n- ✅ Avoids external service dependency (no database, no gossip protocol)\n- ✅ Simple to prototype (single JSON file in `~/.thegent/`)\n- ✅ Works for LAN environments\n- ❌ Trade-off: Eventual consistency; requires manual registration (for prototype)\n\n**Implication**: Each environment publishes its capabilities; control plane reads catalog and routes accordingly\n\n### 3. OS-Level Isolation (No Containers)\n\n**Rationale**:\n- ✅ Simpler implementation: Use subprocess with timeout\n- ✅ Fast execution: No container overhead\n- ✅ Works for prototype in trusted environments\n- ❌ Trade-off: Less secure than Docker; prototype assumes LAN-only\n\n**Implication**: Remote executor runs offloaded agents as isolated OS processes; future work can add Docker sandboxing\n\n### 4. Heuristic-Based Workload Classification\n\n**Rationale**:\n- ✅ Accurate for common cases (Python, Node, Rust, Swift)\n- ✅ Simple to implement and debug\n- ❌ Trade-off: May misclassify edge cases; no ML-based optimization\n\n**Implication**: Classification uses regex patterns and keyword matching; confidence scores guide routing decisions\n\n---\n\n## Component Interaction Map\n\n```\nThegent Control Plane\n┌─────────────────────────────────────────────────┐\n│                                                   │\n│  Workload Classifier  ┌──→ Classification        │\n│  (propose.md: Q6,Q7)  │     {required_caps,      │\n│                       │      suitability_scores}  │\n│                       │                          │\n│  Offload Router ──────┘──→ Route                 │\n│  (design.md: 2.4)          {env_id,              │\n│                            base_url,              │\n│                            reason}               │\n│                                                   │\n│                            ↓                     │\n└─────────────────────────────────────────────────┘\n                            ↓\nOffload Client\n(design.md: 2.7)\n│\n├─→ Health Check → RemoteExecutor health_check\n│\n├─→ Execute Request ──────→ RemoteExecutor\n│   (ExecutionRequest)      (design.md: 2.6)\n│                           │\n│                           ├─→ Capability Resolver\n│                           │   (design.md: 2.2)\n│                           │   [Probe local env]\n│                           │\n│                           ├─→ Subprocess Exec\n│                           │   [Run task in sandbox]\n│                           │\n│                           └─→ Cost Compute\n│                               [Est. cost]\n│\n└─← Execute Response ──────← RemoteExecutor\n    (ExecutionResponse)\n    {exit_code,\n     stdout, stderr,\n     cost_usd}\n\nCompute Catalog\n(design.md: 2.1)\n• Registry of {env_id → Environment}\n• Environments = {os, arch, capabilities, cost_per_min, ...}\n• Read by: Classifier, Router\n• Written by: Capability Resolver + RemoteExecutor\n```\n\n---\n\n## Phased Execution Strategy\n\n### Phase 1: Research & Design (Week 1, ~3.5 agent-days)\n\n**Goals**:\n- Validate assumptions with stakeholders\n- Learn from competitor systems (K8s, Temporal, Nomad)\n- Lock down architecture & protocol before coding\n\n**Tasks**: T1.1 (Stakeholder), T1.2 (Competitive), T1.3 (Design)\n\n**Deliverables**:\n- design.md complete (all sections, protocol spec, decision log)\n- Stakeholder consensus on feasibility\n- Go/no-go decision made\n\n**Critical Decision Point**: After T1.3, decide to proceed with implementation or archive.\n\n---\n\n### Phase 2: Prototype Implementation (Week 2-3, ~9 agent-days)\n\n**Goals**:\n- Build all 7 core components\n- Integrate with thegent agent runner\n- Achieve ≥70% test coverage\n- Prepare for end-to-end validation\n\n**Tasks**: T2.1-T2.9 (Modules, Integration, Testing)\n\n**Parallel Tracks** (from tasks.md):\n- **Track A** (Infrastructure): T2.1 (Catalog) → T2.2 (Resolver) → T2.6 (Executor)\n- **Track B** (Logic): T2.3 (Classifier) → T2.4 (Router)\n- **Track C** (Protocol): T2.5 (Bridge) → T2.7 (Client) → T2.8 (Integration)\n- **Cross-cutting**: T2.9 (Tests)\n\n**Key Deliverables**:\n- `src/thegent/offload/` with 7 modules (2000+ LOC)\n- `tests/thegent/offload/` with unit tests (≥70% coverage)\n- Feature flag: `THGENT_OFFLOAD_ENABLED`\n- Fallback flow working (offload error → local execution)\n\n**Success Metric**: All tests passing, no lint/type errors\n\n---\n\n### Phase 3: Validation & Documentation (Week 3, ~4.5 agent-days)\n\n**Goals**:\n- Deploy prototype to 2+ real environments\n- Validate end-to-end offload workflow\n- Document findings and operations runbook\n- Answer all 10 research questions\n\n**Tasks**: T3.1-T3.4 (E2E Testing, Runbook, Findings, Code Quality)\n\n**Execution Steps** (from T3.1):\n1. Set up compute catalog with Mac + Linux environments\n2. Execute ≥3 real tasks (Python analysis, Node hello world, Rust compile check)\n3. Measure: latency, cost, success rate\n4. Log decisions and outcomes\n\n**Key Deliverables**:\n- T3.1: E2E test results (≥90% success, <5s latency)\n- T3.2: `runbook.md` (setup guide, troubleshooting)\n- T3.3: `design.md` findings section (all 10 research Qs answered)\n- T3.4: Code docs complete (docstrings, type hints, README)\n\n**Success Metric**: ≥3 tasks offloaded successfully, latency <5s per task\n\n---\n\n### Phase 4: Decision & Handoff (End Week 3, ~2 agent-days)\n\n**Goals**:\n- Present findings to stakeholders\n- Make go/no-go decision for production path\n- Archive prototype with clear handoff docs\n\n**Tasks**: T4.1-T4.3 (Presentation, Code Archival, Lessons Learned)\n\n**Decision Matrix** (from proposal.md):\n\n| Outcome | Next Step |\n|---|---|\n| **Go**: All research Qs answered \"yes\", prototype works | Refine for production (Phase 13+) |\n| **Conditional**: Some Qs answered \"maybe\", some gaps | Archive + detailed future roadmap |\n| **No-go**: Infeasible or lower ROI than expected | Archive + document blockers |\n\n**Key Deliverables**:\n- T4.1: Slide deck + demo (or recording)\n- T4.2: Feature branch `research/compute-offload` with PR summary\n- T4.3: `docs/research/CONVERSATION_DUMP_2026-02-18_OFFLOAD.md`\n\n---\n\n## Success Criteria by Phase\n\n### Phase 1: Design Completeness\n- [ ] Stakeholder interviews completed (≥3 conversations)\n- [ ] Competitive analysis (≥4 systems studied)\n- [ ] design.md complete with all 9 sections\n- [ ] All design decisions documented with rationale\n- [ ] Go/no-go decision made\n\n### Phase 2: Implementation Completeness\n- [ ] All 7 modules implemented (~2000 LOC)\n- [ ] Unit tests: ≥70% coverage\n- [ ] All tests passing (100%)\n- [ ] No lint errors (ruff check)\n- [ ] No type errors (mypy)\n- [ ] Feature flag works (enable/disable offload)\n- [ ] Fallback flow tested (offload error → local)\n\n### Phase 3: Validation & Documentation\n- [ ] E2E test: ≥3 tasks offloaded successfully (≥90% success)\n- [ ] Latency: <5s per offload cycle (measured)\n- [ ] runbook.md complete (setup + troubleshooting)\n- [ ] design.md findings section: all 10 research Qs answered\n- [ ] Code quality: docstrings, type hints, README\n- [ ] All artifacts in `docs/changes/research-compute-offload/`\n\n### Phase 4: Decision & Handoff\n- [ ] Presentation to stakeholders (go/no-go decision)\n- [ ] Code on feature branch with clean PR\n- [ ] All code marked `@experimental`\n- [ ] Handoff doc: lessons learned + future roadmap\n\n---\n\n## Resource & Timeline Estimate\n\n### Effort Breakdown\n\n| Phase | Tasks | Effort | Parallel Potential |\n|---|---|---|---|\n| **Phase 1** | T1.1-T1.3 | 3.5 agent-days | ~1 agent (sequential) |\n| **Phase 2** | T2.1-T2.9 | 9 agent-days | 2-3 agents (3 parallel tracks) |\n| **Phase 3** | T3.1-T3.4 | 4.5 agent-days | 2 agents (test + docs in parallel) |\n| **Phase 4** | T4.1-T4.3 | 2 agent-days | 1-2 agents |\n| **Total** | **16 tasks** | **~15 agent-days** | **2-3 agents concurrent** |\n\n### Timeline (Wall Clock)\n\n**Assumption**: 2-3 agents working concurrently on independent tracks\n\n| Milestone | Duration | Start | End |\n|---|---|---|---|\n| Phase 1 (Design) | ~3-4 days | Feb 18 | Feb 21 |\n| Phase 2 (Implementation) | ~5-7 days | Feb 21 | Feb 28 |\n| Phase 3 (Validation) | ~2-3 days | Feb 28 | Mar 2 |\n| Phase 4 (Handoff) | ~1-2 days | Mar 2 | Mar 3 |\n| **Total** | **~2-3 weeks** | Feb 18 | Mar 3 |\n\n---\n\n## Integration with thegent Ecosystem\n\n### Existing Dependencies\n\nThe offload system integrates with these existing thegent components:\n\n| Component | Usage | PR Impact |\n|---|---|---|\n| **AgentRunner** | Invoke offload decision in `run()` | Modify `src/thegent/agent_runner.py` |\n| **Policy Engine** | Evaluate offload against cost/trust gates | Integrate at route selection |\n| **Run Registry** | Log offload decisions and outcomes | Add offload event types |\n| **Settings** | Feature flag, timeout, routing policy config | Add `THGENT_OFFLOAD_*` env vars |\n| **Cost Estimator** | Compute cost for offloaded execution | Reuse existing logic |\n\n### New Modules\n\nAll new code lives in `src/thegent/offload/`:\n\n```\nsrc/thegent/offload/\n├── __init__.py\n├── compute_catalog.py        # T2.1\n├── capability_resolver.py    # T2.2\n├── workload_classifier.py    # T2.3\n├── offload_router.py         # T2.4\n├── bridge_protocol.py        # T2.5\n├── remote_executor.py        # T2.6\n├── offload_client.py         # T2.7\n└── __main__.py              # CLI entry: `thegent offload serve`\n```\n\n### Configuration (New Env Vars)\n\n```bash\n# Enable/disable offload feature\nexport THGENT_OFFLOAD_ENABLED=\"true\"\n\n# Compute catalog location\nexport THGENT_COMPUTE_CATALOG_PATH=\"~/.thegent/compute_catalog.json\"\n\n# Routing policy\nexport THGENT_OFFLOAD_POLICY=\"cost_optimal\"\n\n# Remote executor (on target hosts)\nexport THGENT_OFFLOAD_EXECUTOR_HOST=\"0.0.0.0\"\nexport THGENT_OFFLOAD_EXECUTOR_PORT=\"9000\"\nexport THGENT_OFFLOAD_EXECUTOR_AUTH_TOKEN=\"secret-token\"\n\n# Cost cap (prevent runaway cost)\nexport THGENT_OFFLOAD_MAX_COST_CAP_USD=\"10.0\"\n```\n\n---\n\n## Risk Mitigation Strategy\n\n### High-Probability Risks\n\n| Risk | Probability | Mitigation (from tasks.md) |\n|---|---|---|\n| **Integration complexity** | Medium | T1.3: Design integration points early; T2.8: Simplify policy integration; iterate later |\n| **Workload classification mismatches** | Medium | T2.3: Start with simple heuristics; T3.1: Collect misclassification logs; refine in Phase 13+ |\n| **Network unreliability** | Medium | T2.6: Add configurable timeouts; T2.8: Implement retry logic; T3.1: Test on LAN only |\n\n### Low-Probability Risks\n\n| Risk | Mitigation |\n|---|---|\n| **Prototype becomes tech debt** | Mark all code `@experimental`; clear handoff doc; no production guarantees |\n| **Stakeholder skepticism** | T1.1: Early stakeholder engagement; T4.1: Working prototype demo |\n\n---\n\n## Answering the 10 Research Questions\n\nThe prototype is designed to answer all 10 research questions from proposal.md:\n\n### Feasibility Tier\n\n1. **Network reliability**: Measured in T3.1 (E2E test success rate)\n2. **Latency impact**: Measured in T3.1 (offload cycle latency <5s?)\n3. **Auth & trust**: Prototyped with bearer tokens (T2.5)\n4. **Isolation**: OS-level process isolation (T2.6)\n\n### Architecture Tier\n\n5. **Protocol choice**: HTTP + JSON chosen in T1.3; trade-offs documented in design.md Decision Log\n6. **Registry model**: File-based sync chosen; tested in T2.1\n7. **Routing algorithm**: Cost/latency/capability implemented in T2.4\n8. **Failure modes**: Fallback tested in T2.8\n\n### Economics Tier\n\n9. **Cost benefit**: Measured during T3.1 (actual cost per task)\n10. **SLA guarantees**: Latency baseline documented in T3.3\n\n**Completion Target**: All 10 Qs answered (yes/no/maybe) in design.md findings section (T3.3)\n\n---\n\n## Document Cross-References\n\n### proposal.md → design.md\n\n| Proposal Section | Design Reference | Details |\n|---|---|---|\n| Problem Statement | design.md §1.2 | Component responsibilities |\n| Proposed Solution | design.md §1.1-§2.7 | 7 core components |\n| Research Questions | design.md §4-§7 | Config, error handling, security |\n| Success Criteria | design.md §2.1-§2.7 | Data models, interfaces |\n\n### proposal.md → tasks.md\n\n| Proposal Section | Task Reference | Details |\n|---|---|---|\n| Success Criteria | T2.1-T2.9 | Module implementation |\n| Proposed Phases | Phase 1-4 | Task structure |\n| Dependencies | tasks.md DAG | Task dependency graph |\n| Resources | tasks.md Resource Allocation | Effort + timeline |\n\n### design.md → tasks.md\n\n| Component | Implementation Task | Module File |\n|---|---|---|\n| Compute Catalog | T2.1 | `compute_catalog.py` |\n| Capability Resolver | T2.2 | `capability_resolver.py` |\n| Workload Classifier | T2.3 | `workload_classifier.py` |\n| Offload Router | T2.4 | `offload_router.py` |\n| Bridge Protocol | T2.5 | `bridge_protocol.py` |\n| Remote Executor | T2.6 | `remote_executor.py` |\n| Offload Client | T2.7 | `offload_client.py` |\n| Integration | T2.8 | Modify `agent_runner.py` |\n| Tests | T2.9 | `tests/thegent/offload/` |\n\n---\n\n## Next Steps\n\n### Immediate (Next 1-2 Days)\n\n1. **Share proposal.md with stakeholders**\n   - Goal: Get feedback on problem statement and solution vision\n   - Stakeholders: thegent team, key users\n   - Deliverable: Go/no-go decision to proceed with design\n\n2. **Begin Phase 1 (Research & Design)**\n   - Assign resources: 1 agent for T1.1-T1.3\n   - T1.1: Stakeholder interviews\n   - T1.2: Competitive analysis research\n   - T1.3: Finalize architecture & protocol\n\n### Week 2 (After Phase 1 Go-Ahead)\n\n3. **Begin Phase 2 (Implementation)**\n   - Assign resources: 2-3 agents for parallel tracks\n   - Launch T2.1-T2.9 in parallel\n   - Daily sync on integration points\n\n### Week 3 (After Phase 2)\n\n4. **Begin Phase 3 (Validation)**\n   - Deploy prototype to Mac + Linux environments\n   - Run E2E test suite\n   - Document findings\n\n### End of Week 3\n\n5. **Phase 4 (Decision & Handoff)**\n   - Present to stakeholders\n   - Make go/no-go for production\n   - Archive prototype or begin Phase 13+ work\n\n---\n\n## Key Takeaways\n\n1. **Comprehensive Roadmap**: Three complementary documents (proposal, design, tasks) provide a complete vision from problem → architecture → execution\n\n2. **Traceable**: Every research question, design decision, and success criterion has a corresponding task and artifact\n\n3. **Phased & Gated**: Go/no-go decision points after Phase 1 and Phase 3 prevent wasteful continuation\n\n4. **Prototype-Focused**: All code marked `@experimental`; no production guarantees; clear path for future production work\n\n5. **Multi-Dimensional**: Addresses feasibility (network, latency), architecture (protocol, registry, routing), and economics (cost, SLA)\n\n6. **2-3 Week Timeline**: With 2-3 agents working in parallel, prototype can be validated in realistic Phase 10-12 window\n\n---\n\n## Document Maintenance\n\nThese three documents are **living artifacts**:\n\n- **proposal.md**: Update with stakeholder feedback during Phase 1\n- **design.md**: Refine as implementation reveals new constraints; add findings section during Phase 3\n- **tasks.md**: Update effort estimates and timeline as work progresses; track task completion\n\n**Review Cadence**:\n- Daily: tasks.md (progress tracking)\n- Weekly: design.md (integration updates)\n- End-of-phase: All three (go/no-go decision)\n\n---\n\n**End of Synthesis Document**\n\n---\n\n## Appendix: File Locations\n\nAll three documents are located in:\n```\ndocs/changes/research-compute-offload/\n├── proposal.md       (Problem, vision, research questions)\n├── design.md         (Architecture, components, protocols)\n├── tasks.md          (Implementation breakdown, timeline)\n├── SYNTHESIS.md      (This document: integrating overview)\n└── README.md         (Quick navigation guide)\n```\n\nTo get started:\n1. Read **proposal.md** for the vision\n2. Read **design.md** for the technical approach\n3. Read **tasks.md** for the execution plan\n4. This **SYNTHESIS.md** ties them all together\n"

---

## Source: changes/research-compute-offload/design.md

# Design: Mac ↔ PC Compute Offload Architecture

**Document Version:** 1.0
**Change ID:** research-compute-offload
**Date:** 2026-02-18
**Status:** Design
**Phase:** Research & Prototype

---

## 1. Architecture Overview

### 1.1 System Diagram: Remote Shadow Workspace (RSW)

The Distributed Compute Offload architecture is designed as a **Remote Shadow Workspace (RSW)** system. It does not just share states; it creates true, isolated, concurrent execution environments on remote "Worker" nodes (e.g., your Desktop PC).

```text
[ LAPTOP (Client) ]                      [ DESKTOP PC (Worker Node) ]
        │                                            │
        │ 1. Workload Analysis                       │
        ├───────────────────┐                        │
        │                   ▼                        │
        │           [Offload Router]                 │
        │                   │                        │
        │ 2. State Sync (SSE)│ 3. Execution Request  │
        ├───────────────────┼───────────────────────▶│ [Remote Executor]
        │                   │ (JSON Bridge)          │        │
        │                   │                        │        │ 4. Spawn RSW
        │                   │                        │        ▼
        │                   │                        │ [Shadow Workspace]
        │                   │                        │ (git worktree)
        │                   │                        │        │
        │                   │                        │        │ 5. Execute Agent
        │                   │                        │        ▼
        │ 6. Stream Results │                        │ [ isolated process ]
        │◀──────────────────┼────────────────────────┤        │
        │                   │                        │        │
        │ 7. Reconcile      │                        │        │ 8. Cleanup
        │◀──────────────────┴────────────────────────┴────────┘
```

### 1.2 Core Logic: Remote Worktree vs. Shared State

*   **Option: Shared OS/States (NO)**: We avoid a simple shared filesystem because it leads to "Index Contention" and state-smashing when both your laptop and desktop try to write to the same `.git` index.
*   **Effectively Remote Worktree (YES)**: The `State Synchronization Engine (SSE)` ensures your desktop has the exact delta of your code. The `Remote Executor` then spawns a **True Concurrent Workspace** using `git worktree`.
*   **Result**: You can be coding on your laptop while 3 different agents are running heavy tests or builds on your Desktop PC, each in their own isolated filesystem slice.

## 2. Expanded Feature Set (Breadth & Depth)

To "maximally engineer" this system, we are adding the following dimensions:

### 2.1 State Synchronization Engine (SSE) [BREADTH]
*   **Git-Delta Sync**: Instead of sending full files, we send uncommitted diffs + current HEAD. Fast, even on high-latency links.
*   **Virtual Filesystem Fallback**: If the repo is not Git-managed, we use an `rsync`-like rolling hash sync.
*   **Artifact-Aware Sync**: Excludes `node_modules`, `.venv`, and `target/` to minimize network transit.

### 2.2 Remote Shadow Workspace Manager (RSWM) [DEPTH]
*   **Isolation Levels**:
    *   *Level 1 (Process)*: High speed, uses standard worktree isolation.
    *   *Level 2 (Containerized)*: Spawns a Docker container mapped to the worktree for OS-level parity (e.g., running Linux tests from a Mac client).
*   **Lifespan Management**: Auto-prunes worktrees after task completion or heartbeat loss.

### 2.3 Cross-Platform Context Bridging (XPCB) [POLISH]
*   **Path Translation**: Automatically maps `/Users/koosha/...` (Mac) to `C:\Users\koosha\...` (Windows) during context handoff.
*   **Tool Parity**: Leverages `mise` on the remote node to ensure the *exact* same version of Python/Rust/Node is used as on the client.

### 2.4 Distributed TUI Cockpit (QOL) [POLISH]
*   **Unified View**: A laptop dashboard showing:
    *   CPU/RAM load on Desktop PC.
    *   Active remote tasks and their "time-to-complete" estimates.
    *   One-click "Remote Attach" to view live logs.

## 3. Implementation Status (Updated)

| Feature | Engineering Depth | Status |
| :--- | :--- | :--- |
| **Bridge Protocol** | Pydantic V2 + JSON | Finalized |
| **SSE (Sync)** | Git Worktree Over SSH | **IN DEVELOPMENT** |
| **Remote Executor** | FastAPI + Streaming | **IN DEVELOPMENT** |
| **Workload Classifier** | Heuristic AST Analysis | Finalized |
| **TUI Cockpit** | Textual (Python) | Planned |

### 1.2 Component Responsibilities

| Component | Responsibility | Location |
|-----------|---|---|
| **Compute Catalog** | Registry of available environments + capabilities | `thegent/offload/compute_catalog.py` |
| **Capability Resolver** | Probe local env; publish fingerprint | `thegent/offload/capability_resolver.py` |
| **Workload Classifier** | Analyze task; infer platform requirements | `thegent/offload/workload_classifier.py` |
| **Offload Router** | Route to best target based on policy | `thegent/offload/offload_router.py` |
| **Bridge Protocol** | Serialize/deserialize execution context | `thegent/offload/bridge_protocol.py` |
| **Remote Executor** | Listen for offload requests; execute tasks | `thegent/offload/remote_executor.py` |
| **Offload Client** | Initiate remote execution; stream results | `thegent/offload/offload_client.py` |

---

## 2. Core Components

### 2.1 Compute Catalog

**Purpose**: Registry of available compute environments and their capabilities.

**Data Structure**:
```python
class Environment(BaseModel):
    """Represents a compute environment (Mac, Linux, Windows)"""
    env_id: str  # "mac-m1-mini", "linux-ubuntu-22.04", "windows-11"
    os: str  # "macos", "linux", "windows"
    arch: str  # "arm64", "x86_64"
    hostname: str  # FQDN or IP
    base_url: str  # "http://192.168.1.100:9000" for remote executor

    # Resource profile
    cpu_cores: int
    memory_gb: float
    storage_gb: float

    # Cost profile ($/minute)
    cost_per_minute: float

    # Capabilities
    capabilities: Set[str]  # {"git", "python-3.12", "node-20", "swift", ...}

    # Network
    network_latency_ms: float  # Approximate RTT
    bandwidth_mbps: float

    # Health
    is_online: bool
    last_health_check: datetime
    availability_percentage: float  # SLA %

    # Metadata
    region: str  # "local", "us-west", "eu-central"
    created_at: datetime
    expires_at: Optional[datetime]  # For temporary nodes

class CapabilityProfile(BaseModel):
    """Capabilities of an environment"""
    languages: Set[str]  # {"python", "node", "rust", "go", "swift"}
    package_managers: Set[str]  # {"pip", "npm", "cargo", "go"}
    runtimes: Set[str]  # {"python-3.12", "node-20", "jvm-21"}
    compilers: Set[str]  # {"gcc", "clang", "rustc", "swiftc"}
    build_tools: Set[str]  # {"make", "cmake", "cargo", "gradle"}
    vcs: Set[str]  # {"git", "hg"}
    container: Set[str]  # {"docker", "podman"}
    databases: Set[str]  # {"postgres", "mysql", "mongodb"}
    cloud_tools: Set[str]  # {"aws-cli", "gcloud", "az"}
    dev_frameworks: Set[str]  # {"xcode", "visual-studio", "vscode"}

class ComputeCatalog(BaseModel):
    """Registry of all available environments"""
    environments: Dict[str, Environment]  # env_id -> Environment

    @classmethod
    def load(cls, path: Path) -> "ComputeCatalog":
        """Load from JSON/YAML file"""
        pass

    def save(self, path: Path):
        """Save to JSON file"""
        pass

    def register_environment(self, env: Environment):
        """Register a new environment"""
        self.environments[env.env_id] = env

    def find_by_hostname(self, hostname: str) -> Optional[Environment]:
        """Find environment by hostname"""
        pass

    def get_online_environments(self) -> List[Environment]:
        """Filter to online environments"""
        return [e for e in self.environments.values() if e.is_online]
```

**File Format** (JSON):
```json
{
  "environments": {
    "mac-m1-mini": {
      "env_id": "mac-m1-mini",
      "os": "macos",
      "arch": "arm64",
      "hostname": "macs-mini.local",
      "base_url": "http://192.168.1.100:9000",
      "cpu_cores": 8,
      "memory_gb": 24.0,
      "storage_gb": 512.0,
      "cost_per_minute": 0.005,
      "capabilities": ["git", "python-3.12", "node-20", "swift", "rustc"],
      "network_latency_ms": 1.5,
      "bandwidth_mbps": 1000.0,
      "is_online": true,
      "last_health_check": "2026-02-18T10:15:32Z",
      "availability_percentage": 99.5,
      "region": "local",
      "created_at": "2026-02-01T00:00:00Z",
      "expires_at": null
    },
    "linux-ubuntu": {
      "env_id": "linux-ubuntu",
      "os": "linux",
      "arch": "x86_64",
      "hostname": "ubuntu-vm.local",
      "base_url": "http://192.168.1.101:9000",
      "cpu_cores": 16,
      "memory_gb": 32.0,
      "storage_gb": 1024.0,
      "cost_per_minute": 0.003,
      "capabilities": ["git", "python-3.12", "node-20", "rustc", "gcc"],
      "network_latency_ms": 2.0,
      "bandwidth_mbps": 1000.0,
      "is_online": true,
      "last_health_check": "2026-02-18T10:14:12Z",
      "availability_percentage": 98.9,
      "region": "local",
      "created_at": "2026-02-05T00:00:00Z",
      "expires_at": null
    }
  }
}
```

**Persistence**:
- Location: `~/.thegent/compute_catalog.json` (or `${THGENT_COMPUTE_CATALOG_PATH}`)
- Refresh: TTL 5 minutes (or on-demand via `health_check()`)
- Sync: Each environment's remote executor publishes its catalog entry; control plane aggregates

---

### 2.2 Capability Resolver

**Purpose**: Probe local environment; publish capabilities.

**Interface**:
```python
class CapabilityResolver:
    """Probe local machine for capabilities"""

    @staticmethod
    def probe() -> CapabilityProfile:
        """Detect installed tools, languages, runtimes in this environment"""
        profile = CapabilityProfile()

        # Detect languages
        profile.languages.add("python") if _has_python() else None
        profile.languages.add("node") if _has_node() else None
        # ... etc

        # Detect runtimes
        if _has_python():
            profile.runtimes.add(f"python-{_get_python_version()}")

        # Detect build tools
        profile.build_tools.add("make") if _has_make() else None

        return profile

    @staticmethod
    def _has_python() -> bool:
        """Check if Python is available"""
        return shutil.which("python3") is not None

    @staticmethod
    def _get_python_version() -> str:
        """Get Python version"""
        result = subprocess.run(["python3", "--version"], capture_output=True, text=True)
        return result.stdout.strip().split()[-1]  # "3.12.0"

class CapabilityCache:
    """Cache resolved capabilities with TTL"""
    def __init__(self, ttl_seconds: int = 600):  # 10 min default
        self.ttl = ttl_seconds
        self.profile: Optional[CapabilityProfile] = None
        self.cached_at: Optional[datetime] = None

    def get(self) -> CapabilityProfile:
        """Get cached or re-probe if expired"""
        now = datetime.utcnow()
        if self.profile and self.cached_at and (now - self.cached_at).total_seconds() < self.ttl:
            return self.profile

        self.profile = CapabilityResolver.probe()
        self.cached_at = now
        return self.profile
```

**Usage**:
```python
# During remote executor startup
cache = CapabilityCache(ttl_seconds=600)
profile = cache.get()

# Periodically publish to control plane
env_entry = Environment(
    env_id="mac-m1-mini",
    capabilities=profile.all_capabilities,
    # ... other fields
)
catalog.register_environment(env_entry)
```

---

### 2.3 Workload Classifier

**Purpose**: Analyze task/prompt; infer platform requirements.

**Heuristics**:
```python
class WorkloadClassifier:
    """Classify workload by platform suitability"""

    def classify(self, prompt: str, code: Optional[str] = None) -> "Classification":
        """Analyze prompt and code to infer requirements"""

        classification = Classification(
            required_capabilities=set(),
            preferred_os=None,  # None=flexible, "macos", "linux", "windows"
            suitable_environments=[],
            confidence=0.0,
        )

        # Heuristic 1: Language Detection
        for lang in ["python", "node", "rust", "go", "swift", "java", "c++"]:
            if self._mentions_language(prompt, lang) or self._detect_code_language(code) == lang:
                classification.required_capabilities.add(lang)

        # Heuristic 2: Framework Detection
        if "xcode" in prompt.lower() or "swift" in prompt.lower():
            classification.required_capabilities.add("xcode")
            classification.preferred_os = "macos"

        if "visual-studio" in prompt.lower() or ".net" in prompt.lower():
            classification.required_capabilities.add("visual-studio")
            classification.preferred_os = "windows"

        # Heuristic 3: Tool Detection
        if "docker" in prompt.lower():
            classification.required_capabilities.add("docker")

        if "cargo" in prompt.lower():
            classification.required_capabilities.add("cargo")

        # Heuristic 4: OS-Specific Commands
        if "brew install" in prompt.lower():
            classification.preferred_os = "macos"

        if "apt install" in prompt.lower() or "yum install" in prompt.lower():
            classification.preferred_os = "linux"

        if "choco install" in prompt.lower():
            classification.preferred_os = "windows"

        # Compute suitability for each environment in catalog
        catalog = ComputeCatalog.load(CATALOG_PATH)
        for env in catalog.environments.values():
            suitability = self._compute_suitability(env, classification)
            classification.suitable_environments.append((env.env_id, suitability))

        # Confidence: fraction of required capabilities available in best match
        if classification.suitable_environments:
            best_env_id, best_score = max(classification.suitable_environments, key=lambda x: x[1])
            classification.confidence = best_score

        return classification

    def _mentions_language(self, prompt: str, lang: str) -> bool:
        """Check if prompt mentions a language"""
        keywords = {
            "python": ["python", "py3", "django", "flask", "pandas"],
            "node": ["node", "npm", "javascript", "typescript", "express"],
            "rust": ["rust", "cargo", "tokio", "axum"],
            # ... etc
        }
        return any(kw in prompt.lower() for kw in keywords.get(lang, []))

    def _compute_suitability(self, env: Environment, classification: "Classification") -> float:
        """Score environment suitability (0.0-1.0)"""
        if not classification.required_capabilities:
            return 1.0  # Flexible workload; any env is fine

        matched = len(classification.required_capabilities & env.capabilities)
        total = len(classification.required_capabilities)
        base_score = matched / total if total > 0 else 1.0

        # Prefer matching OS if specified
        if classification.preferred_os:
            if env.os == classification.preferred_os:
                base_score *= 1.05  # 5% boost
            else:
                base_score *= 0.5  # 50% penalty

        return min(1.0, base_score)

class Classification(BaseModel):
    required_capabilities: Set[str]
    preferred_os: Optional[str]  # "macos", "linux", "windows", or None
    suitable_environments: List[Tuple[str, float]]  # [(env_id, score), ...]
    confidence: float  # 0.0-1.0
```

---

### 2.4 Offload Router

**Purpose**: Select best target environment; apply routing policies.

**Routing Policies**:
```python
from enum import Enum

class RoutingPolicy(Enum):
    COST_OPTIMAL = "cost_optimal"  # Cheapest
    LATENCY_OPTIMAL = "latency_optimal"  # Fastest
    CAPABILITY_OPTIMAL = "capability_optimal"  # Most capable
    AVAILABILITY_OPTIMAL = "availability_optimal"  # Highest SLA
    PARETO = "pareto"  # Pareto frontier (cost vs latency)

class OffloadRouter:
    """Route workload to best target environment"""

    def __init__(self, policy: RoutingPolicy = RoutingPolicy.COST_OPTIMAL):
        self.policy = policy
        self.catalog = ComputeCatalog.load(CATALOG_PATH)

    def route(self, classification: "Classification") -> Optional["Route"]:
        """Select target environment for this workload"""

        # Filter to suitable environments
        suitable = [
            (env_id, score)
            for env_id, score in classification.suitable_environments
            if score > 0.5  # Min 50% suitability
        ]

        if not suitable:
            return None  # No suitable environment

        # Apply routing policy
        if self.policy == RoutingPolicy.COST_OPTIMAL:
            return self._select_cost_optimal(suitable)
        elif self.policy == RoutingPolicy.LATENCY_OPTIMAL:
            return self._select_latency_optimal(suitable)
        elif self.policy == RoutingPolicy.CAPABILITY_OPTIMAL:
            return self._select_capability_optimal(suitable)
        elif self.policy == RoutingPolicy.AVAILABILITY_OPTIMAL:
            return self._select_availability_optimal(suitable)
        elif self.policy == RoutingPolicy.PARETO:
            return self._select_pareto_optimal(suitable)

        return None

    def _select_cost_optimal(self, suitable: List[Tuple[str, float]]) -> "Route":
        """Select cheapest suitable environment"""
        env_id, _ = min(suitable, key=lambda x: self._cost_score(x[0]))
        env = self.catalog.environments[env_id]
        return Route(
            env_id=env.env_id,
            hostname=env.hostname,
            base_url=env.base_url,
            reason=f"Cost optimal: ${env.cost_per_minute:.4f}/min",
        )

    def _select_latency_optimal(self, suitable: List[Tuple[str, float]]) -> "Route":
        """Select fastest suitable environment"""
        env_id, _ = min(suitable, key=lambda x: self._latency_score(x[0]))
        env = self.catalog.environments[env_id]
        return Route(
            env_id=env.env_id,
            hostname=env.hostname,
            base_url=env.base_url,
            reason=f"Latency optimal: {env.network_latency_ms:.1f}ms RTT",
        )

    def _cost_score(self, env_id: str) -> float:
        """Cost score (lower is better)"""
        env = self.catalog.environments[env_id]
        return env.cost_per_minute

    def _latency_score(self, env_id: str) -> float:
        """Latency score (lower is better)"""
        env = self.catalog.environments[env_id]
        return env.network_latency_ms

class Route(BaseModel):
    env_id: str
    hostname: str
    base_url: str
    reason: str  # Human-readable explanation for routing decision
```

---

### 2.5 Bridge Protocol

**Purpose**: Serialize/deserialize execution context for cross-platform communication.

**Message Format**:
```python
class ExecutionRequest(BaseModel):
    """Request to offload task execution"""
    request_id: str  # UUID
    timestamp: datetime

    # Execution context
    prompt: str
    cwd: str  # Working directory (relative to executor home)
    env_vars: Dict[str, str]  # Environment variables to inject
    timeout_seconds: int  # Execution timeout

    # Origin
    origin_hostname: str
    origin_agent: str  # e.g., "claude-sonnet"
    origin_mode: str  # e.g., "write", "read-only"

    # Policy
    cost_cap_usd: Optional[float] = None
    dry_run: bool = False  # Don't actually execute; validate only

    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "req-abc123",
                "timestamp": "2026-02-18T10:15:32Z",
                "prompt": "Analyze this Python codebase",
                "cwd": "~/myrepo",
                "env_vars": {"PYTHONPATH": "."},
                "timeout_seconds": 300,
                "origin_hostname": "mac-m1.local",
                "origin_agent": "claude-sonnet",
                "origin_mode": "write",
                "cost_cap_usd": 1.0,
                "dry_run": False,
            }
        }

class ExecutionResponse(BaseModel):
    """Response from remote executor"""
    request_id: str  # Echo request_id
    timestamp: datetime

    # Execution result
    exit_code: int
    stdout: str
    stderr: str

    # Metadata
    execution_time_seconds: float
    executor_hostname: str

    # Cost
    cost_usd: float
    tokens_used: Optional[int] = None

    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "req-abc123",
                "timestamp": "2026-02-18T10:15:45Z",
                "exit_code": 0,
                "stdout": "Analysis complete: 42 files, 3 major issues found",
                "stderr": "",
                "execution_time_seconds": 12.3,
                "executor_hostname": "linux-ubuntu.local",
                "cost_usd": 0.008,
                "tokens_used": 4200,
            }
        }
```

**HTTP API**:
```
POST /v1/offload/execute
Content-Type: application/json
Authorization: Bearer <token>

{
  "request_id": "req-abc123",
  ...
}

---

HTTP/1.1 200 OK
Content-Type: application/json

{
  "request_id": "req-abc123",
  ...
}
```

---

### 2.6 Remote Executor

**Purpose**: Listen for offload requests; execute tasks in sandbox; return results.

**Server Interface**:
```python
class RemoteExecutor:
    """HTTP server for executing offloaded tasks"""

    def __init__(self, host: str = "0.0.0.0", port: int = 9000):
        self.host = host
        self.port = port
        self.app = self._build_app()

    def _build_app(self) -> FastAPI:
        """Build FastAPI app"""
        app = FastAPI(title="RemoteExecutor")

        @app.post("/v1/offload/execute")
        async def execute(request: ExecutionRequest) -> ExecutionResponse:
            """Execute an offloaded task"""
            try:
                # Validate request
                if request.cost_cap_usd is not None:
                    cost = self._estimate_cost(request)
                    if cost > request.cost_cap_usd:
                        raise CostCapExceeded(f"Estimated {cost} > cap {request.cost_cap_usd}")

                # Dry run: validate only
                if request.dry_run:
                    return ExecutionResponse(
                        request_id=request.request_id,
                        timestamp=datetime.utcnow(),
                        exit_code=0,
                        stdout="Dry run OK",
                        stderr="",
                        execution_time_seconds=0.0,
                        executor_hostname=socket.gethostname(),
                        cost_usd=0.0,
                    )

                # Execute in sandbox
                result = await self._execute_in_sandbox(request)

                return ExecutionResponse(
                    request_id=request.request_id,
                    timestamp=datetime.utcnow(),
                    exit_code=result.exit_code,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    execution_time_seconds=result.execution_time_seconds,
                    executor_hostname=socket.gethostname(),
                    cost_usd=result.cost_usd,
                    tokens_used=result.tokens_used,
                )

            except Exception as e:
                return ExecutionResponse(
                    request_id=request.request_id,
                    timestamp=datetime.utcnow(),
                    exit_code=1,
                    stdout="",
                    stderr=str(e),
                    execution_time_seconds=0.0,
                    executor_hostname=socket.gethostname(),
                    cost_usd=0.0,
                )

        @app.get("/v1/health")
        async def health() -> dict:
            """Health check"""
            return {"status": "ok", "hostname": socket.gethostname()}

        return app

    async def _execute_in_sandbox(self, request: ExecutionRequest) -> "ExecutionResult":
        """Execute request in isolated sandbox"""
        # For prototype: OS-level process isolation (no containers)
        # Future: Docker/Podman container with security context

        import subprocess
        import time

        start_time = time.time()

        try:
            # Prepare environment
            env = os.environ.copy()
            env.update(request.env_vars)

            # Expand cwd
            cwd = os.path.expanduser(request.cwd)

            # Invoke agent (delegate to installed agent, e.g., "claude" CLI)
            result = subprocess.run(
                ["thegent", "run", request.prompt],
                cwd=cwd,
                env=env,
                capture_output=True,
                text=True,
                timeout=request.timeout_seconds,
            )

            execution_time = time.time() - start_time

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                execution_time_seconds=execution_time,
                cost_usd=self._compute_cost(execution_time),
                tokens_used=self._estimate_tokens(result.stdout, result.stderr),
            )

        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            return ExecutionResult(
                exit_code=124,  # Timeout exit code
                stdout="",
                stderr="Execution timed out",
                execution_time_seconds=execution_time,
                cost_usd=self._compute_cost(execution_time),
                tokens_used=None,
            )

    def _compute_cost(self, execution_time_seconds: float) -> float:
        """Compute execution cost based on time"""
        # Placeholder: $0.001 per minute
        return (execution_time_seconds / 60.0) * 0.001

    def _estimate_tokens(self, stdout: str, stderr: str) -> int:
        """Estimate token usage from output"""
        # Placeholder: ~4 chars per token
        output = stdout + stderr
        return len(output) // 4

    def run(self):
        """Start the server"""
        import uvicorn
        uvicorn.run(self.app, host=self.host, port=self.port)

class ExecutionResult(BaseModel):
    exit_code: int
    stdout: str
    stderr: str
    execution_time_seconds: float
    cost_usd: float
    tokens_used: Optional[int] = None
```

---

### 2.7 Offload Client

**Purpose**: Initiate remote execution from control plane.

**Interface**:
```python
class OffloadClient:
    """Client for invoking remote executor"""

    def __init__(self, base_url: str, auth_token: Optional[str] = None):
        self.base_url = base_url
        self.auth_token = auth_token
        self.http_client = httpx.AsyncClient()

    async def execute(self, request: ExecutionRequest) -> ExecutionResponse:
        """Send execution request to remote executor"""
        headers = {}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"

        response = await self.http_client.post(
            f"{self.base_url}/v1/offload/execute",
            json=request.dict(),
            headers=headers,
            timeout=60.0,
        )

        if response.status_code != 200:
            raise OffloadError(f"Execution failed: {response.status_code} {response.text}")

        return ExecutionResponse(**response.json())

    async def health_check(self) -> bool:
        """Check if remote executor is alive"""
        try:
            response = await self.http_client.get(
                f"{self.base_url}/v1/health",
                timeout=5.0,
            )
            return response.status_code == 200
        except Exception:
            return False
```

---

## 3. Integration with thegent

### 3.1 Execution Flow

```
User: thegent run "Analyze Python repo" free
    │
    ├─→ AgentRunner.run()
    │   ├─→ WorkloadClassifier.classify()  # Detect "python"
    │   │   └─→ Classification{required={"python"}, suitable=[...]}
    │   │
    │   ├─→ OffloadRouter.route()  # Select best env
    │   │   └─→ Route{env_id="linux-ubuntu", ...}
    │   │
    │   ├─→ OffloadClient.execute()  # Send to remote
    │   │   ├─→ ExecutionRequest{prompt, cwd, ...}
    │   │   └─→ ExecutionResponse{exit_code, stdout, stderr, ...}
    │   │
    │   └─→ Return normalized result
    │
    └─→ Display output
```

### 3.2 Policy Engine Integration

Offload decisions should respect governance policies:

```python
# In OffloadRouter.route()
def route(self, classification: "Classification") -> Optional["Route"]:
    # ... select candidate environments ...

    # Evaluate against policy
    policy_result = self.policy_engine.evaluate(
        operation_type="OFFLOAD",
        target_env=candidate_env,
        cost_estimate=self._estimate_cost(candidate_env),
        agent_name=self.origin_agent,
    )

    if not policy_result.allow:
        raise OffloadNotAllowed(f"Policy: {policy_result.reason}")

    return route
```

### 3.3 Telemetry & Cost Tracking

Log offload decisions and outcomes:

```python
# In run_registry
def register_offload_decision(self, run_id: str, offload_decision: OffloadDecision):
    """Record offload routing decision"""
    event = {
        "type": "offload_decision",
        "run_id": run_id,
        "timestamp": datetime.utcnow().isoformat(),
        "classification": offload_decision.classification.dict(),
        "selected_route": offload_decision.selected_route.dict(),
        "reason": offload_decision.reason,
    }
    self._append_to_registry(event)

def register_offload_completion(self, run_id: str, response: ExecutionResponse):
    """Record offload execution result"""
    event = {
        "type": "offload_completion",
        "run_id": run_id,
        "timestamp": datetime.utcnow().isoformat(),
        "exit_code": response.exit_code,
        "execution_time_seconds": response.execution_time_seconds,
        "cost_usd": response.cost_usd,
        "executor_hostname": response.executor_hostname,
    }
    self._append_to_registry(event)
```

---

## 4. Configuration & Deployment

### 4.1 Environment Variables

```bash
# Compute catalog path
export THGENT_COMPUTE_CATALOG_PATH="~/.thegent/compute_catalog.json"

# Offload routing policy
export THGENT_OFFLOAD_POLICY="cost_optimal"  # cost_optimal, latency_optimal, capability_optimal

# Remote executor settings
export THGENT_OFFLOAD_EXECUTOR_HOST="0.0.0.0"
export THGENT_OFFLOAD_EXECUTOR_PORT="9000"
export THGENT_OFFLOAD_EXECUTOR_AUTH_TOKEN="secret-token-here"

# Offload capabilities (enable/disable)
export THGENT_OFFLOAD_ENABLED="true"
export THGENT_OFFLOAD_MAX_COST_CAP_USD="10.0"
```

### 4.2 Setup Instructions

**On each target environment (Mac, Linux, Windows):**

1. Install thegent
2. Start remote executor:
   ```bash
   thegent offload serve --host 0.0.0.0 --port 9000
   ```
3. Publish to shared catalog (manual for prototype):
   ```bash
   # On control plane
   thegent offload register --env-id linux-ubuntu \
     --hostname ubuntu-vm.local \
     --base-url http://192.168.1.101:9000 \
     --cpu-cores 16 --memory-gb 32
   ```

---

## 5. Testing Strategy

### 5.1 Unit Tests

- `test_compute_catalog.py`: Load/save, register, query
- `test_capability_resolver.py`: Probe mock environment, cache TTL
- `test_workload_classifier.py`: Classify Python, Node, Rust, Swift workloads
- `test_offload_router.py`: Route with different policies (cost, latency)
- `test_bridge_protocol.py`: Serialize/deserialize execution requests/responses

### 5.2 Integration Tests

- `test_offload_end_to_end.py`: Full flow (classify → route → execute → return)
  - Test case 1: Python analysis on Linux
  - Test case 2: Swift build on Mac (should fail on Linux)
  - Test case 3: Cost routing selects cheapest

### 5.3 Mock Strategy

- Mock `ComputeCatalog` with 3 test environments
- Mock `OffloadClient` to return canned responses
- Real subprocess execution in integration tests

---

## 6. Security Considerations

### 6.1 Authentication

**Prototype**: Pre-shared bearer tokens (simple, not production-grade)

```bash
# Client sends token
curl -H "Authorization: Bearer secret-token" \
  http://executor:9000/v1/offload/execute
```

**Future**: mTLS certificates, OAuth, JWT

### 6.2 Isolation

**Prototype**: OS-level process isolation (separate user, working directory)

**Future**: Docker/Podman containers with restricted capabilities

### 6.3 Input Validation

- Validate `cwd` is within allowed directories (prevent path traversal)
- Validate `env_vars` keys/values (prevent injection)
- Reject overly long prompts (prevent DoS)

### 6.4 Network

- Assume LAN/VPN only (no internet-scale security)
- Implement timeout (5s) for health checks
- Log all requests (audit trail)

---

## 7. Error Handling & Fallback

### 7.1 Failure Modes

| Scenario | Handling |
|----------|----------|
| Remote executor offline | Fall back to local execution |
| Network timeout | Retry with backoff; fall back to local |
| Cost cap exceeded | Reject offload; run locally |
| Workload unsuitable for all envs | Run locally with warning |
| Executor policy rejects request | Fall back to local |

### 7.2 Fallback Flow

```python
def run_with_offload_fallback(self, prompt: str) -> RunResult:
    """Try offload; fall back to local execution"""
    try:
        classification = self.classifier.classify(prompt)
        route = self.router.route(classification)
        if not route:
            raise NoSuitableEnvironment("No suitable offload target")

        client = OffloadClient(route.base_url, self.auth_token)
        response = await client.execute(ExecutionRequest(...))

        return self._adapt_response(response)

    except (OffloadNotAllowed, OffloadError, NoSuitableEnvironment, TimeoutError) as e:
        logger.warning(f"Offload failed: {e}; falling back to local execution")
        return self._execute_locally(prompt)
```

---

## 8. Decision Log

### Decision 1: HTTP vs gRPC

**Chosen**: HTTP (prototype only)

**Rationale**:
- Simpler to implement and debug
- Built-in tooling (curl, Postman)
- Stateless; easier to load balance
- JSON serialization widely understood

**Trade-off**: gRPC would be more efficient (binary + streaming), but complexity not justified for prototype.

---

### Decision 2: JSON vs Protocol Buffers

**Chosen**: JSON + Pydantic

**Rationale**:
- Self-documenting
- Pydantic provides validation + serialization
- Human-readable logs

---

### Decision 3: Centralized vs Distributed Catalog

**Chosen**: File-based catalog with periodic sync (hybrid)

**Rationale**:
- Simple for prototype (single JSON file)
- Avoid external service dependency
- Future: Gossip protocol or git-based sync

---

### Decision 4: Local vs Container Isolation

**Chosen**: OS-level process isolation (local execution)

**Rationale**:
- Simpler to prototype
- Sufficient for LAN environments
- Future: Docker containers for stronger isolation

---

## 9. References & Appendices

### A. Example Workload Classifications

See proposal.md Appendix A

### B. Compute Catalog Example

See Section 2.1

### C. Bridge Protocol Schema

See Section 2.5

---

**End of Design Document**

---

## Source: changes/research-compute-offload/proposal.md

# Proposal: Mac ↔ PC Compute Offload Research

**Document Version:** 1.0
**Change ID:** research-compute-offload
**Date:** 2026-02-18
**Status:** Proposal
**Priority:** P2

---

## Executive Summary

This research initiative investigates intelligent compute offloading between macOS (Mac) and Windows/Linux (PC) environments within the thegent orchestration framework. The goal is to enable agents to transparently route workloads to the most suitable execution environment based on platform-specific capabilities, cost, and resource availability.

**Key Outcomes:**
- Feasibility analysis of cross-platform execution bridging
- Design patterns for environment-aware task routing
- Prototype implementation of Mac ↔ PC offload mechanism
- Integration architecture with thegent's existing multi-agent framework

---

## Problem Statement

### Current State
- thegent executes agents on a single machine (the host running the CLI)
- No mechanism exists to leverage compute resources across heterogeneous environments
- Mac-specific workloads (e.g., Xcode builds, iOS development) cannot run on Windows/Linux hosts
- Windows-specific workloads (e.g., .NET builds, DirectX development) cannot run on macOS
- Each environment pays for compute independently; no cost optimization across platforms

### Gaps
1. **Workload Awareness**: thegent has no notion of platform-specific tool requirements
2. **Environment Bridging**: No standardized protocol for remote execution between platforms
3. **Resource Orchestration**: Can't leverage idle or cost-effective compute in peer environments
4. **Cost Optimization**: No ability to route to cheapest/fastest platform per task
5. **Dependency Resolution**: No mechanism to detect or validate platform compatibility

---

## Proposed Solution

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│             Unified thegent Control Plane                │
│  (agent dispatch, policy eval, cost aggregation)         │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
   ┌─────────┐  ┌─────────┐  ┌─────────┐
   │ Host A  │  │ Host B  │  │ Host C  │
   │ (Mac)   │  │ (PC)    │  │ (Linux) │
   │         │  │         │  │         │
   │ Local   │  │ Local   │  │ Local   │
   │ Executor│  │ Executor│  │ Executor│
   └────┬────┘  └────┬────┘  └────┬────┘
        │            │            │
        └────────────┼────────────┘
             ▲       │       ▲
             │ Offload Bridge │
             └────────────────┘
```

### Key Components

1. **Compute Catalog** (`src/thegent/offload/compute_catalog.py`)
   - Registry of available compute environments (Mac, Windows, Linux)
   - Capabilities per environment (installed tools, SDKs, runtimes)
   - Resource profiles (CPU, memory, storage, network)
   - Cost profiles ($/minute per environment)

2. **Workload Classifier** (`src/thegent/offload/workload_classifier.py`)
   - Analyzes prompt and task to infer platform requirements
   - Detects language/framework/tool requirements from code snippets
   - Assigns compatibility matrix per target platform
   - Computes suitability scores (0.0-1.0) per environment

3. **Offload Router** (`src/thegent/offload/offload_router.py`)
   - Receives workload classification and available environments
   - Applies routing policies (cost-optimal, fastest, most capable)
   - Selects target environment and agent
   - Encodes execution context for remote agent

4. **Bridge Protocol** (`src/thegent/offload/bridge_protocol.py`)
   - Standardized message format for cross-platform execution
   - Encapsulates prompt, working directory, environment variables
   - Marshals/unmarshals execution context
   - Supports both synchronous (HTTP) and asynchronous (AMQP/gRPC) transport

5. **Remote Executor** (`src/thegent/offload/remote_executor.py`)
   - Listens on host for offload requests
   - Validates incoming requests against local policy
   - Prepares sandbox/container for execution
   - Executes task and returns normalized output

6. **Capability Resolver** (`src/thegent/offload/capability_resolver.py`)
   - Probes local environment for installed tools/SDKs
   - Generates capability fingerprint (git, docker, python, node, ruby, go, rust, etc.)
   - Caches fingerprint with TTL
   - Publishes to shared registry

---

## Research Questions

### Feasibility
1. **Network Reliability**: Can we maintain stable connections for long-running tasks (>10min)?
2. **Latency Impact**: What overhead does network roundtrip add vs. local execution? Acceptable threshold?
3. **Authentication & Trust**: How do we securely authenticate Mac ↔ PC without SSH keys per pair?
4. **Isolation**: Can we safely sandbox offloaded workloads without full VM/container overhead?

### Architecture
5. **Protocol Choice**: HTTP (simple, ubiquitous), gRPC (typed, streaming), AMQP (async), WebSocket (bidirectional)?
6. **Registry Model**: Centralized (shared server), Decentralized (gossip), Hybrid (local cache + sync)?
7. **Routing Algorithm**: Cost-based greedy, ML-based predictor, game-theoretic equilibrium?
8. **Failure Modes**: How do we handle network partition, task timeout, agent crash mid-execution?

### Economics
9. **Cost Benefit**: At what workload volume does offload cost < local cost?
10. **SLA Guarantees**: Can we maintain latency SLAs across heterogeneous networks?

---

## Scope & Constraints

### In Scope
- ✅ Feasibility analysis (theory + prototype)
- ✅ Workload classification heuristics
- ✅ Capability probing and registry
- ✅ Router logic and policy integration
- ✅ Synchronous HTTP bridge protocol
- ✅ Reference implementation for 2 platforms (Mac, Linux)

### Out of Scope
- ❌ Asynchronous protocols (AMQP, gRPC) — prototype only with HTTP
- ❌ Full multi-cloud federation (AWS, GCP, Azure) — research only
- ❌ ML-based routing optimization — heuristic-based only
- ❌ Automatic infrastructure provisioning — manual setup
- ❌ Container/VM orchestration — sandboxing via lightweight isolation (OS-level)

### Constraints
- **Timeline**: Fit within Phase 10-12 research window (2-3 weeks)
- **Code Debt**: Prototype code must be marked `@experimental`; no production guarantees
- **Network**: Assume LAN-only or VPN (no internet-scale)
- **Auth**: Use temporary tokens or pre-shared secrets; no PKI infrastructure
- **Latency**: Target <1s overhead for offload decision + handoff

---

## Success Criteria

### Research Validation
- [ ] **Complete Feasibility Matrix**: Document yes/no answers for all 10 research questions
- [ ] **Prototype Execution**: Offload a real agent task (e.g., git repo analysis) from Mac to Linux
- [ ] **Capability Detection**: Fingerprint ≥5 environments; match 90%+ accuracy against manual audit
- [ ] **Routing Logic**: Correctly select environment for ≥3 workload types (Python, Node, Rust)
- [ ] **Performance Baseline**: Measure latency overhead; document per task type

### Prototype Artifacts
- [ ] **Compute Catalog** populated with ≥3 environments and ≥10 capabilities per env
- [ ] **Workload Classifier** with ≥5 heuristics (language detection, tool inference, dependency scanning)
- [ ] **Offload Router** integrates with thegent policy engine; respects cost/trust gates
- [ ] **Bridge Protocol** message schema defined in Pydantic; examples for ≥3 workflows
- [ ] **Remote Executor** runs on 2+ platforms; passes smoke tests
- [ ] **Test Coverage**: ≥70% unit test coverage for core modules

### Documentation
- [ ] **Design Document**: Detailed architecture, protocol, integration points
- [ ] **Runbook**: Step-by-step setup for Mac + Linux + Windows environments
- [ ] **Decision Log**: Rationale for protocol, registry, routing choices
- [ ] **Next Phase Roadmap**: Clear path from prototype → production

---

## Proposed Phases

### Phase 1: Research & Design (Week 1)
- Stakeholder interviews (thegent team, users with multi-platform setups)
- Competitive analysis (Kubernetes federation, Terraform, Nomad, Temporal)
- Network architecture design
- Protocol spec in YAML/Pydantic
- **Deliverable**: design.md

### Phase 2: Prototype Implementation (Week 2-3)
- Implement compute catalog, workload classifier, router
- Implement HTTP bridge protocol + reference server
- Integrate with thegent policy engine
- Write unit tests for core modules
- **Deliverable**: src/thegent/offload/ + tests

### Phase 3: Validation & Runbook (Week 3)
- Deploy prototype to 2+ environments (Mac + Linux VM)
- Validate end-to-end offload workflow
- Write setup + operations runbook
- Document findings in design.md + decision log
- **Deliverable**: docs/changes/research-compute-offload/design.md, runbook.md

### Phase 4: Decision & Handoff (End of Week 3)
- Present findings to team
- Decide: Refine prototype, archive for future work, or pursue production path
- Handoff artifacts (code, docs, lessons learned)
- **Deliverable**: tasks.md (updated with outcomes)

---

## Dependencies & Integrations

### Internal
- thegent policy engine (for gate evaluation)
- thegent settings & configuration
- thegent run registry (for cost tracking)
- thegent contract telemetry (for audit trail)

### External
- No mandatory external dependencies beyond stdlib + existing thegent deps
- Optional: `docker` CLI for sandbox creation (if exploring container-based isolation)

---

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Network unreliability in production | High | Task hangs / timeouts | Prototype assumes LAN; add timeout + retry logic; doc as future work |
| Authentication/trust complexity | Medium | Security vulnerabilities | Use pre-shared tokens for prototype; recommend mTLS for production |
| Workload classification mismatches | Medium | Wrong platform selected | Start with simple heuristics; add manual override; collect misclassification logs |
| Integration complexity with policy engine | Medium | Schedule slip | Start with simplified policy; iterate based on feedback |
| Prototype code becomes "legacy" | Low | Maintenance burden | Mark all code `@experimental`; clear upgrade path in handoff |

---

## Success Stories & Related Work

### Kubernetes Federation
Inspired by Kubernetes multi-cluster support: declarative resource affinity, cluster-aware routing, federated control plane.

### Terraform
Uses provider-specific execution backends; each platform (AWS, GCP, local) has a provider. Our compute catalog is analogous.

### Temporal
Workflow engine with worker pools across regions/datacenters; workers register capabilities. Our capability resolver + registry is inspired by this.

---

## Open Questions for Stakeholders

1. **Priority**: Is Mac ↔ PC offload critical for Phase 10-12, or can it wait for Phase 13+?
2. **Network Assumption**: Do we assume LAN-only (VPN) or internet-scale?
3. **Auth Model**: Pre-shared secrets (simple), mTLS (secure), OAuth (enterprise)?
4. **Sandbox Strategy**: OS-level isolation (fast, less secure) or containers (slower, more secure)?
5. **Routing Policy**: Cost-optimal (cheapest) or quality-optimal (fastest + most capable)?

---

## Resources & References

### Existing Documentation
- `docs/reference/ARCHITECTURE_LAYERS.md` — thegent architecture
- `docs/plans/02-UNIFIED-WBS.md` — Phase 10-12 work breakdown
- `FUNCTIONAL_REQUIREMENTS.md` — FR-EXE-*, FR-MOD-*, FR-AGT-* (agent execution, models, routing)

### External References
- [Kubernetes Federation](https://kubernetes.io/docs/concepts/cluster-administration/federation/)
- [Terraform Providers](https://www.terraform.io/language/providers)
- [Temporal Worker Pools](https://docs.temporal.io/workers)
- [gRPC Load Balancing](https://grpc.io/docs/guides/performance-best-practices/)

---

## Timeline & Effort Estimate

| Phase | Duration | Effort | Owner |
|-------|----------|--------|-------|
| Research & Design | 3 days | 3 agent-days | TBD |
| Implementation | 5 days | 8 agent-days | TBD |
| Validation & Docs | 2 days | 4 agent-days | TBD |
| **Total** | **~2 weeks** | **~15 agent-days** | TBD |

---

## Approval & Sign-Off

| Role | Name | Date | Comments |
|------|------|------|----------|
| Proposer | (auto-generated) | 2026-02-18 | Initial proposal |
| Architecture Review | (pending) | (pending) | – |
| Product Manager | (pending) | (pending) | – |
| Security Review | (pending) | (pending) | – |

---

## Next Steps

1. **Stakeholder Review**: Share this proposal with thegent team (sync or async)
2. **Go/No-Go Decision**: Decide if research should proceed in this or next phase window
3. **Design Phase Start**: If approved, begin design.md immediately
4. **Resource Allocation**: Assign agent(s) to research + prototype tracks

---

## Appendix A: Workload Classification Examples

### Example 1: Python Project
```
Prompt: "Analyze this Python monorepo for dependency cycles"
Detected: python, pip, git
Suitable: [Mac (score 0.95), Linux (score 0.95), Windows (score 0.80)]
Reason: Python is cross-platform; Windows lacks git-bash by default
Recommended: Linux (lowest cost)
```

### Example 2: iOS Development
```
Prompt: "Build and test this iOS app with Xcode"
Detected: swift, xcodebuild, ios-simulator
Suitable: [Mac (score 1.0), Linux (score 0.0), Windows (score 0.0)]
Reason: Xcode only on Mac; iOS simulator requires Mac hardware
Recommended: Mac (only viable)
```

### Example 3: Node.js Service
```
Prompt: "Profile CPU usage of this Node.js service"
Detected: node, npm, perf-tools
Suitable: [Mac (score 0.90), Linux (score 0.95), Windows (score 0.80)]
Reason: All support Node; Linux perf tools more sophisticated
Recommended: Linux (fastest + most capable)
```

---

**End of Proposal Document**

---

## Source: changes/research-compute-offload/tasks.md

---
task_id: research-compute-offload
status: in_progress
---

# Implementation Tasks: Mac ↔ PC Compute Offload

**Document Version:** 1.0
**Change ID:** research-compute-offload
**Date:** 2026-02-18
**Status:** WIP
**Total Effort**: ~15 agent-days

---

## Phase 1: Research & Design (Week 1) — **Status: PLANNING**

### T1.1: Stakeholder Research & Requirements Gathering
- **Objective**: Interview thegent team and users; document use cases
- **Effort**: 1 agent-day
- **Owner**: (TBD)
- **Dependencies**: None
- **Deliverables**:
  - List of ≥3 real use cases (cross-platform workflows)
  - Network assumptions (LAN vs internet)
  - Security requirements (auth model, isolation level)
  - Integration preferences (when/where to offload)
- **Success Criteria**:
  - All stakeholders consulted
  - Requirements documented in design.md
  - Go/no-go decision made

### T1.2: Competitive Analysis
- **Objective**: Research similar systems (Kubernetes federation, Nomad, Temporal, Terraform)
- **Effort**: 1.5 agent-days
- **Owner**: (TBD)
- **Dependencies**: T1.1
- **Deliverables**:
  - Comparison matrix (protocol choice, registry model, routing)
  - Lessons learned doc
- **Success Criteria**:
  - ≥4 systems analyzed
  - Key patterns identified

### T1.3: Architecture & Protocol Design
- **Objective**: Design bridge protocol, compute catalog, routing logic
- **Effort**: 1.5 agent-days
- **Owner**: (TBD)
- **Dependencies**: T1.1, T1.2
- **Deliverables**:
  - Bridge protocol YAML spec (ExecutionRequest, ExecutionResponse)
  - Compute catalog JSON schema
  - Routing policy enumeration
  - Design decisions log (why HTTP vs gRPC, JSON vs Protobuf, etc.)
- **Success Criteria**:
  - Design.md complete with all sections
  - Protocol examples provided
  - All design decisions documented with rationale

---

## Phase 2: Prototype Implementation (Week 2-3) — **Status: PENDING**

### T2.1: Compute Catalog Module
- **Objective**: Implement `ComputeCatalog` + `CapabilityProfile` classes
- **Effort**: 1.5 agent-days
- **Owner**: (TBD)
- **Dependencies**: T1.3
- **Deliverables**:
  - `src/thegent/offload/compute_catalog.py` (400 LOC)
  - Unit tests (70% coverage)
  - Example catalog JSON file
- **Success Criteria**:
  - `ComputeCatalog` loads/saves JSON
  - Methods: `register_environment()`, `get_online_environments()`, `find_by_hostname()`
  - Tests: load, save, register, query
  - Example with ≥3 environments populated

### T2.2: Capability Resolver Module
- **Objective**: Implement `CapabilityResolver` for probing local environment
- **Effort**: 1.5 agent-days
- **Owner**: (TBD)
- **Dependencies**: T1.3, T2.1
- **Deliverables**:
  - `src/thegent/offload/capability_resolver.py` (300 LOC)
  - Tests for ≥10 capability types (python, node, rust, git, docker, etc.)
  - `CapabilityCache` with TTL
- **Success Criteria**:
  - Probes ≥15 tools/languages correctly
  - Cache TTL working (verified in unit tests)
  - Test pass rate ≥90%
  - Handles missing tools gracefully

### T2.3: Workload Classifier Module
- **Objective**: Implement `WorkloadClassifier` with ≥5 heuristics
- **Effort**: 2 agent-days
- **Owner**: (TBD)
- **Dependencies**: T1.3, T2.1
- **Deliverables**:
  - `src/thegent/offload/workload_classifier.py` (400 LOC)
  - Heuristics: language detect, framework detect, tool detect, OS-specific commands, dependency scanning
  - Tests for ≥5 workload types (Python, Swift, Node, Rust, .NET)
- **Success Criteria**:
  - Classify Python correctly in ≥3 example prompts
  - Detect Swift → prefer macOS
  - Detect xcodebuild → macOS only
  - Confidence scores 0.5-1.0 range
  - Edge case: empty prompt returns default classification

### T2.4: Offload Router Module
- **Objective**: Implement `OffloadRouter` with ≥3 routing policies
- **Effort**: 1.5 agent-days
- **Owner**: (TBD)
- **Dependencies**: T1.3, T2.1, T2.3
- **Deliverables**:
  - `src/thegent/offload/offload_router.py` (300 LOC)
  - Policies: `COST_OPTIMAL`, `LATENCY_OPTIMAL`, `CAPABILITY_OPTIMAL`
  - Tests: verify correct route selection per policy
- **Success Criteria**:
  - Route selection respects policy
  - Returns reason for routing decision
  - Handles "no suitable environment" gracefully
  - Cost scoring accurate (vs mock catalog)

### T2.5: Bridge Protocol Module
- **Objective**: Define `ExecutionRequest` + `ExecutionResponse` Pydantic models
- **Effort**: 1 agent-day
- **Owner**: (TBD)
- **Dependencies**: T1.3
- **Deliverables**:
  - `src/thegent/offload/bridge_protocol.py` (200 LOC)
  - Pydantic models with validators
  - JSON schema generation
  - Example payloads for ≥3 workflows
- **Success Criteria**:
  - Models validate correctly
  - JSON schema can be generated
  - Round-trip serialization works (dict → model → dict)
  - Examples provided in docstrings

### T2.6: Remote Executor Server
- **Objective**: Implement FastAPI-based remote executor
- **Effort**: 2.5 agent-days
- **Owner**: (TBD)
- **Dependencies**: T2.5, T2.2
- **Deliverables**:
  - `src/thegent/offload/remote_executor.py` (500 LOC)
  - Endpoints: POST `/v1/offload/execute`, GET `/v1/health`
  - Subprocess execution in sandbox
  - Cost estimation + token counting
  - Tests: mock subprocess, validate response
- **Success Criteria**:
  - Server starts and listens on 0.0.0.0:9000
  - Health check returns 200
  - Execute endpoint receives request, returns response
  - Timeout handling (subprocess.TimeoutExpired)
  - Cost computation plausible

### T2.7: Offload Client Module
- **Objective**: Implement `OffloadClient` for invoking remote executor
- **Effort**: 1 agent-day
- **Owner**: (TBD)
- **Dependencies**: T2.5, T2.6
- **Deliverables**:
  - `src/thegent/offload/offload_client.py` (150 LOC)
  - Async HTTP client using `httpx`
  - Methods: `execute()`, `health_check()`
  - Error handling + retry logic
- **Success Criteria**:
  - Sends valid ExecutionRequest
  - Parses ExecutionResponse
  - Handles 200/error responses
  - Health check returns bool

### T2.8: Integration with thegent Agent Runner
- **Objective**: Wire offload into `AgentRunner.run()` decision logic
- **Effort**: 2 agent-days
- **Owner**: (TBD)
- **Dependencies**: T2.1-T2.7
- **Deliverables**:
  - Modify `src/thegent/agent_runner.py` to support offload
  - Add offload settings to `ThegentSettings`
  - Feature flag: `THGENT_OFFLOAD_ENABLED`
  - Fallback flow (offload fails → run locally)
- **Success Criteria**:
  - Feature flag works (enabled/disabled)
  - Offload only attempted if enabled
  - Fallback to local execution on error
  - Logging for offload decisions
  - ≥80% test coverage for new code

### T2.9: Unit Tests & Coverage
- **Objective**: Achieve ≥70% coverage across all offload modules
- **Effort**: 2 agent-days
- **Owner**: (TBD)
- **Dependencies**: T2.1-T2.8
- **Deliverables**:
  - `tests/thegent/offload/` test suite
  - Mock catalog, mock executor, mock HTTP client
  - Positive + negative test cases
  - Coverage report (CI integration optional)
- **Success Criteria**:
  - Overall coverage ≥70%
  - All modules have unit tests
  - Test pass rate 100%
  - No lint violations (ruff, mypy)

---

## Phase 3: Validation & Documentation (Week 3) — **Status: PENDING**

### T3.1: End-to-End Offload Workflow Test
- **Objective**: Deploy prototype to 2+ environments (Mac + Linux VM); validate real offload
- **Effort**: 2 agent-days
- **Owner**: (TBD)
- **Dependencies**: T2.1-T2.9
- **Deliverables**:
  - Populate compute catalog with 2+ test environments
  - Execute ≥3 real tasks (Python repo analysis, Node hello world, Rust compilation check)
  - Measurement: latency, cost, success rate
  - Log real offload decisions + outcomes
- **Success Criteria**:
  - ≥3 tasks successfully offloaded and executed on remote
  - Success rate ≥90% (2 out of ≥3 tasks succeed)
  - Latency < 5s per task (classification + routing + execution)
  - Output from remote executor matches expected format

### T3.2: Runbook & Setup Documentation
- **Objective**: Write step-by-step guide for deploying offload infrastructure
- **Effort**: 1.5 agent-days
- **Owner**: (TBD)
- **Dependencies**: T3.1
- **Deliverables**:
  - `docs/changes/research-compute-offload/runbook.md` (2000+ words)
  - Sections:
    - Prerequisites (ports, network, auth)
    - Install thegent on each environment
    - Register environments in catalog
    - Start remote executor servers
    - Configure client (settings, feature flags)
    - Test offload workflow (manual step-by-step)
    - Troubleshooting common issues
- **Success Criteria**:
  - New user can follow runbook start-to-finish
  - Includes ≥5 troubleshooting scenarios
  - Commands copy-pastable

### T3.3: Findings & Decision Document
- **Objective**: Synthesize research findings; propose next steps
- **Effort**: 1 agent-day
- **Owner**: (TBD)
- **Dependencies**: T3.1, T3.2
- **Deliverables**:
  - Update `design.md` with findings section:
    - What worked well
    - Unexpected challenges
    - Performance characteristics
    - Answers to all 10 research questions
  - Production readiness assessment (yes/no/needs_work)
  - Recommendations for Phase 13+ (if pursuing production)
- **Success Criteria**:
  - All 10 research questions answered (yes/no/maybe)
  - Go/no-go recommendation clear
  - Next phase roadmap provided

### T3.4: Code Quality & Documentation
- **Objective**: Add docstrings, type hints, and comments to all code
- **Effort**: 1 agent-day
- **Owner**: (TBD)
- **Dependencies**: T2.1-T2.9
- **Deliverables**:
  - Docstrings for all public classes + methods
  - Type hints for all function parameters + returns
  - README.md in `src/thegent/offload/` explaining module purpose
  - Inline comments for non-obvious logic
- **Success Criteria**:
  - Sphinx can generate API docs without errors
  - Type coverage ≥90% (mypy check)
  - No linting violations (ruff, pylint)

---

## Phase 4: Decision & Handoff (End of Week 3) — **Status: PENDING**

### T4.1: Presentation & Stakeholder Review
- **Objective**: Present prototype and findings to thegent team
- **Effort**: 0.5 agent-day
- **Owner**: (TBD)
- **Dependencies**: T3.1-T3.4
- **Deliverables**:
  - Slide deck (≥10 slides): architecture, prototype results, findings, decision matrix
  - Live demo (if possible) or recorded walkthrough
  - Q&A response document
- **Success Criteria**:
  - Stakeholders understand design + tradeoffs
  - Go/no-go decision made
  - Path forward clear (produce, archive, extend)

### T4.2: Code Archival & Handoff
- **Objective**: Clean up prototype; mark as @experimental; prepare for handoff or merging
- **Effort**: 1 agent-day
- **Owner**: (TBD)
- **Dependencies**: T3.4
- **Deliverables**:
  - Mark all code `@experimental` (docstring decorator)
  - Add `OFFLOAD_README.md` with disclaimer (research-stage)
  - Commit to feature branch `research/compute-offload`
  - PR with summary: scope, what worked, what didn't, recommendations
- **Success Criteria**:
  - Code is clean, well-documented, and reviewable
  - PR has clear summary
  - All tests passing
  - No tech debt TODOs (document as future work)

### T4.3: Lessons Learned & Future Roadmap
- **Objective**: Update docs/research/CONVERSATION_DUMP_*.md with findings
- **Effort**: 0.5 agent-day
- **Owner**: (TBD)
- **Dependencies**: T3.3
- **Deliverables**:
  - `docs/research/CONVERSATION_DUMP_2026-02-18_OFFLOAD.md`:
    - Issues addressed
    - Findings (yes to all research questions? trade-offs?)
    - Prototype artifacts (code location, test results)
    - Open questions (for future research)
    - Recommendations (pursue production? archive?)
- **Success Criteria**:
  - Document provides clear context for future developer picking up this work

---

## Dependency Graph (DAG)

```
T1.1 (Stakeholder Research)
  ↓
T1.2 (Competitive Analysis)
  ↓
T1.3 (Design)
  ├─→ T2.1 (Catalog Module)
  │     ├─→ T2.3 (Classifier) ─→ T2.4 (Router)
  │     └─→ T2.8 (Integration)
  │
  ├─→ T2.2 (Capability Resolver) ─→ T2.6 (Remote Executor) ─→ T2.8
  │
  └─→ T2.5 (Bridge Protocol) ─→ T2.6 (Remote Executor) ─→ T2.7 (Client) ─→ T2.8

T2.1-T2.8 (all) ─→ T2.9 (Unit Tests) ─→ T3.1 (E2E Validation) ─→ T3.2 (Runbook)

T3.1, T3.2 ─→ T3.3 (Findings) ─→ T4.1 (Presentation)

T2.1-T2.9, T3.3 ─→ T3.4 (Code Quality) ─→ T4.2 (Handoff)

T4.1, T4.2 ─→ T4.3 (Lessons Learned)
```

**Critical Path**: T1.1 → T1.2 → T1.3 → T2.{1-8} → T2.9 → T3.1 → T3.2 → T3.3 → T4.1 (**~13 days**)

**Parallel Tracks**:
- T2.1, T2.2, T2.5 can start immediately after T1.3
- T2.3, T2.4 can start after T2.1
- T2.6, T2.7 can start after T2.5
- T3.4 (docs) can start after T2.9

---

## Success Metrics

| Metric | Target | Validation |
|--------|--------|------------|
| **Prototype Completeness** | All 7 modules implemented | Code review + tests passing |
| **Test Coverage** | ≥70% | `pytest --cov` report |
| **E2E Validation** | ≥3 tasks offloaded successfully | Manual testing + logs |
| **Performance** | <5s offload latency per task | Measured during T3.1 |
| **Documentation** | Design + runbook + lessons learned | Reader can follow from scratch |
| **Code Quality** | No lint/type errors; ≥8/10 readable | ruff + mypy + review |
| **Research Questions** | All 10 answered | Section in findings doc |

---

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Network unreliability | Medium | Task timeouts | Add configurable timeouts; test on LAN only |
| Integration complexity with policy engine | Medium | Schedule slip | Simplify policy integration; iterate later |
| Workload classification mismatches | Medium | Wrong platform selected | Start simple; add logging to collect misclassifications |
| Prototype becomes "tech debt" | Low | Maintenance burden | Mark @experimental; clear handoff doc; no promises |
| Stakeholder skepticism | Low | Scope reduction | Manage expectations early (research-stage); show working prototype |

---

## Resource Allocation

**Total Effort**: ~15 agent-days

**Suggested Allocation** (if 2 agents assigned):
- **Agent A** (Infrastructure): T1.1, T2.1, T2.2, T2.5, T2.6, T3.1 (8 days)
- **Agent B** (Logic): T1.2, T1.3, T2.3, T2.4, T2.7, T2.8, T2.9 (7 days)
- **Parallel**: T3.2, T3.3, T3.4, T4.1, T4.2, T4.3 (all agents)

**Estimated Timeline**: 2-3 weeks (sprint-based)

---

## Approval & Sign-Off

| Item | Owner | Date | Status |
|------|-------|------|--------|
| Task breakdown | (auto-generated) | 2026-02-18 | Draft |
| Phase 1 approval | (TBD) | (TBD) | Pending |
| Phase 2 approval | (TBD) | (TBD) | Pending |
| Phase 3 approval | (TBD) | (TBD) | Pending |
| **Final handoff** | (TBD) | (TBD) | Pending |

---

## Appendix: Task Template for Each Phase

### Phase 1 Task Template
```
[ ] T1.X: Task Name
    - Effort: X agent-days
    - Owner: (TBD)
    - Dependencies: [prior tasks]
    - Deliverables:
      - Artifact 1
      - Artifact 2
    - Success Criteria:
      - Criterion 1
      - Criterion 2
```

### Phase 2 Task Template
```
[ ] T2.X: Module Impl
    - Effort: X agent-days
    - Owner: (TBD)
    - Dependencies: [design, prior modules]
    - Code: src/thegent/offload/module_name.py (~N LOC)
    - Tests: tests/thegent/offload/test_module_name.py
    - Success Criteria:
      - Methods implemented: [list]
      - Coverage ≥70%
      - Tests pass 100%
```

---

**End of Task Breakdown Document**

---
