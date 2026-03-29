# Track 4: Sub-Project Split + Ecosystem Consolidation — Summary

**Date:** 2026-02-22
**Status:** Design Complete | Ready for Implementation
**Duration Estimate:** 12–16 wall-clock hours (4 agents in parallel)

---

## What is Track 4?

Track 4 transforms the thegent monolith into a **modular polyglot workspace** with four independent sub-projects that communicate exclusively via the **MCP (Machine Context Protocol)**. Simultaneously, it consolidates the ecosystem by absorbing zen-mcp-server and deprecating adjacent tools.

### Current State (Monolith)

```
src/thegent/
├── cli/              (32K LOC — mixed concerns)
├── agents/           (scattered across modules)
├── orchestration/    (mixed with agents)
├── planning/         (mixed with agents)
├── memory/           (mixed with agents)
├── team/             (mixed with agents)
├── mcp/              (scattered integration)
└── ... 80+ other modules
```

### Target State (Modular)

```
thegent/ (workspace root)
├── sub-projects/
│   ├── thegent-cli/          (~8K LOC — thin wrapper)
│   │   └── MCP client to agents
│   ├── thegent-agents/       (~12K LOC — orchestration)
│   │   └── MCP server @ 3847
│   ├── thegent-mcp/          (~7.5K LOC → 500+ tools)
│   │   └── MCP server @ 3848
│   └── thegent-core/         (Rust/Zig)
│       └── FFI bridge to Python
├── crates/
│   ├── thegent-ffi/          (Python bridge)
│   └── ... 20+ others
└── docs/
    ├── guides/
    │   ├── SUBPROJECT_ARCHITECTURE.md
    │   └── SUBPROJECT_DEVELOPMENT.md
    └── reference/
        ├── IPC_PROTOCOL_SPEC.md
        ├── SUBPROJECT_INTERFACES.md
        └── SESSION_STATE_CONTRACT.md

# Ecosystem (Consolidated)
/kush/
├── thegent/              (primary, actively developed)
├── zen-mcp-server/       (absorbed → thegent-mcp)
├── task-tool/            (deprecated)
├── crun/                 (evaluate for DAG merge)
├── agentapi/             (archived)
└── agentapi++/           (archived)
```

---

## Four Sub-Projects

### 1. **thegent-core** (Rust/Zig) — Already in Progress (Tracks 2–3)

**Purpose:** Performance-critical primitives
- Caching (thegent-cache)
- Cryptography (thegent-crypto)
- Git operations (thegent-git)
- Memory store (thegent-memory)
- Discovery (thegent-discovery)
- File operations (thegent-fs)
- Hooks system (thegent-hooks)

**Interface:** Python FFI via `thegent-ffi` crate
**Process:** Compiled library (no server)

---

### 2. **thegent-cli** (Python, ~8K LOC)

**Purpose:** CLI command dispatch, output formatting
**Key Files:**
- `apps/main.py` — entry point (typer)
- `commands/` — command handlers (free, research, code, fix, etc.)
- `output/` — formatting (rich pretty-print, JSON)
- `mcp_client.py` — MCP wrapper (NEW)

**Responsibility:** Parse user input → call agents via MCP → format output

**Server Dependency:** Requires `thegent-agents` MCP server running @ 3847

**Auto-Start:** If agents server not running, CLI auto-starts it (configurable)

---

### 3. **thegent-agents** (Python, ~12K LOC)

**Purpose:** Agent orchestration, planning, memory, team management
**Key Modules:**
- `agents/` — agent runner strategies
- `orchestration/` — execution modes (sequential, parallel, loops)
- `planning/` — task decomposition, DAG execution
- `memory/` — persistent store (JSONL + SQLite)
- `team/` — multi-agent coordination

**Server:** FastMCP (http://127.0.0.1:3847)

**Tools Exposed (via MCP):**
- `run_agent(agent_id, prompt, context)` → stream
- `list_agents()` → list
- `get_agent_state(agent_id)` → dict
- `stop_agent(agent_id)` → bool
- `query_memory(agent_id, query)` → results
- `add_memory(agent_id, item)` → success

**Resources:**
- `agents://{id}/state` — read-only state
- `agents://{id}/memory` — agent memory

---

### 4. **thegent-mcp** (Python, ~7.5K → 500+ tools)

**Purpose:** Unified tool aggregator
**Contents:**
- MCP server (FastMCP)
- Tool handlers (GitHub, Slack, Stripe, OpenAI, Anthropic, Jira, Confluence, Salesforce, + 40+ more)
- Resource streaming
- Error normalization

**Integration:** Absorbs all 620 files from zen-mcp-server

**Server:** FastMCP (http://127.0.0.1:3848)

**Tools:** ~500 across all integrations
- `github/list_repos`, `github/create_issue`, etc.
- `slack/send_message`, `slack/list_channels`, etc.
- `stripe/create_charge`, etc.
- `openai/create_chat_completion`, etc.
- (+ 40+ more integrations)

---

## Communication Architecture

```
User Input
    ↓
thegent-cli (MCP Client)
    ↓
thegent-agents (MCP Server @ 3847)
    ├─ Agent Runner
    ├─ Memory Store
    ├─ Planning Engine
    ├─ Team Manager
    ↓
thegent-mcp (MCP Server @ 3848)
    ├─ GitHub Tools
    ├─ Slack Tools
    ├─ Stripe Tools
    ├─ OpenAI Tools
    ├─ Anthropic Tools
    └─ ... (500+ total)
    ↓
External APIs
```

### Key Features

1. **Decoupling:** Each sub-project is independent; can be developed, tested, deployed separately
2. **Scaling:** Sub-projects can run on separate machines (microservices)
3. **Language Flexibility:** Rust for performance, Python for orchestration
4. **Clear Interfaces:** MCP protocol is only communication method; no direct imports
5. **Backward Compatibility:** No breaking changes to CLI interface

---

## Ecosystem Consolidation

### Absorb: zen-mcp-server (620 files)

- All 50+ tool categories integrated into `thegent-mcp/tools/`
- Configuration unified via `~/.thegent/config.toml`
- Tests migrated and passing
- Original repo marked deprecated

### Deprecate: task-tool

- Functionality superseded by `thegent-agents` planning engine
- Migration guide provided
- Freeze date: 2026-03-15
- Archive date: 2026-04-30

### Archive: AgentAPI / AgentAPI++

- Superseded by thegent architecture
- Kept in `/kush/` for historical reference (read-only)
- No data loss

---

## Implementation Plan (4 Phases)

### Phase 1: Infrastructure (2–3 hours)
1. **P1.1:** Define IPC & MCP contracts → `docs/reference/IPC_PROTOCOL_SPEC.md`
2. **P1.2:** Create workspace config → `pyproject.toml`, `Cargo.toml`
3. **P1.3:** Update `tach.toml` → architecture boundaries

### Phase 2: Extract Sub-Projects (8–10 hours)
4. **P2.1:** Extract `thegent-cli` → 8K LOC, MCP client only
5. **P2.2:** Extract `thegent-agents` → 12K LOC, FastMCP server @ 3847
6. **P2.3:** Extract `thegent-mcp` + absorb zen-mcp-server → 500+ tools @ 3848
7. **P2.4:** Deprecate task-tool, archive AgentAPI/++

### Phase 3: Integration (4–5 hours)
8. **P3.1:** Full test suite (all sub-projects + integration tests)
9. **P3.2:** Update documentation (architecture, dev guide, deployment)
10. **P3.3:** Ecosystem consolidation report

### Phase 4: Completion (1–2 hours)
11. **P4.1:** CI/CD integration, final validation

**Total:** 21–33 hours | **Wall-clock (4 agents):** 8–10 hours

---

## Key Deliverables

### Documentation (3 major docs)

1. **`docs/plans/TRACK_4_TDD_IMPLEMENTATION_PLAN.md`**
   - Comprehensive 25K-word plan with all tasks, acceptance criteria, code examples
   - Every task has TDD structure: contract tests first, implementation second
   - Includes risk mitigation, commits strategy, success criteria

2. **`docs/reference/IPC_PROTOCOL_SPEC.md`**
   - Machine-readable MCP contracts
   - Error codes, request/response schemas
   - Pydantic models for type safety
   - Performance SLOs

3. **`docs/reference/SUBPROJECT_INTERFACE_SPEC.md`**
   - Interface between each sub-project
   - CLI ↔ Agents (6 tools, 2 resources)
   - Agents ↔ MCP (tool invocation contract)
   - Configuration and credentials
   - Error handling and back-pressure

4. **`docs/guides/SUBPROJECT_ARCHITECTURE.md`**
   - Overview of polyglot architecture
   - Communication patterns (diagram)
   - Development workflow (setup, testing, adding tools)
   - Deployment (local, Docker, Kubernetes)
   - Troubleshooting

5. **`docs/guides/SUBPROJECT_DEVELOPMENT.md`**
   - Step-by-step: "How to add a new tool to thegent-mcp"
   - Code templates for each sub-project
   - Testing patterns
   - CI/CD integration

6. **`docs/reports/ECOSYSTEM_CONSOLIDATION_2026-02-22.md`**
   - What was absorbed (zen-mcp-server: 620 files)
   - What was deprecated (task-tool: migration path)
   - What was archived (AgentAPI/++: historical reference)
   - Impact analysis (performance, breaking changes)
   - Data preservation verification

### Code (Sub-Projects)

- `sub-projects/thegent-cli/` — thin CLI wrapper
- `sub-projects/thegent-agents/` — orchestration + FastMCP server
- `sub-projects/thegent-mcp/` — tool aggregator + FastMCP server
- `crates/thegent-ffi/` — Python bridge for Rust code

### Configuration

- Root `pyproject.toml` (workspace aggregator)
- Each sub-project `pyproject.toml`
- Updated `crates/Cargo.toml` (add thegent-ffi)
- Updated `tach.toml` (architecture boundaries)

### Tests

- Contract tests for MCP protocol compliance
- Integration tests (CLI → agents → MCP)
- Full sub-project test suite
- CI/CD GitHub Actions workflow

---

## Success Criteria (Definition of Done)

✅ **Modular Architecture:**
- 4 independent sub-projects
- No cross-project imports (only MCP)
- tach DAG acyclic

✅ **Ecosystem Consolidated:**
- zen-mcp-server (620 files) integrated → 500+ tools
- task-tool deprecated with migration guide
- AgentAPI/++ archived

✅ **Zero Breaking Changes:**
- Existing CLI interface unchanged
- Session files still work
- All user workflows preserved

✅ **Fully Documented:**
- Architecture guide (overview, patterns, examples)
- Development guide (setup, testing, adding features)
- Interface spec (machine-readable contracts)
- Consolidation report (impact analysis)

✅ **Tested:**
- 100% test pass rate
- ≥80% coverage (agents, mcp)
- ≥95% coverage (cli)
- Integration tests passing

✅ **CI/CD Ready:**
- GitHub Actions workflow testing all sub-projects
- Coverage thresholds enforced
- No regressions vs. monolith

---

## Risk Mitigation

| Risk | Likelihood | Mitigation |
|------|-----------|-----------|
| **MCP protocol overhead** | Medium | Benchmark CLI startup; target <250ms (was ~800ms) |
| **Async/await complexity** | Medium | pytest-asyncio strict fixtures, retry flaky tests |
| **Credential conflicts** | Low | Unified config system, never hardcode secrets |
| **Tool conflicts** (500+ tools) | Low | Namespace by service (github/list_repos) |
| **Import cycles** | Low | tach check before every commit |
| **Data migration** | Very Low | Session files unchanged, backward-compat verified |

---

## Performance Impact

| Metric | Before | After | Target |
|--------|--------|-------|--------|
| **CLI startup** | ~800ms | TBD | <250ms (-75%) |
| **Agent init** | ~1.2s | TBD | <400ms (-67%) |
| **Tool lookup** | O(n) search | O(1) hash | <10ms |
| **Memory/process** | ~150MB monolith | ~80–120MB distributed | Similar |

---

## Execution Strategy

### Recommended Parallelization (4 Agents)

```
Agent 1: P1.1 + P1.2 (Contracts & Workspace)
Agent 2: P2.1 (CLI Extraction)
Agent 3: P2.2 (Agents Extraction + MCP Service)
Agent 4: P2.3 (MCP Extraction + zen-mcp absorption)

Dependencies:
  P1.1 ──┐
  P1.2 ──┼→ P1.3 ──┬→ P2.1, P2.2, P2.3 ──→ P2.4 ──┬→ P3.1, P3.2, P3.3 ──→ P4.1
         └→ ────────┘                              └────────────────────────┘
```

**Wall-clock time:** 8–10 hours (parallelized)
**Sequential time:** 24–30 hours (single agent)

---

## Files Created

This TDD plan includes three comprehensive documents:

1. **`docs/plans/TRACK_4_TDD_IMPLEMENTATION_PLAN.md`** (25K words)
   - 4 phases, 11 tasks, detailed acceptance criteria
   - Code examples for all sub-projects
   - Test-first approach with contract tests
   - Risk mitigation, commits, success criteria

2. **`docs/reference/TRACK_4_QUICK_CHECKLIST.md`** (5K words)
   - Quick reference for implementation
   - Phase-by-phase checklist
   - Time allocations
   - Execution strategy

3. **`docs/reference/SUBPROJECT_INTERFACE_SPEC.md`** (8K words)
   - Machine-readable MCP contracts
   - CLI ↔ Agents tool definitions
   - Agents ↔ MCP tool invocation pattern
   - Shared module access rules
   - Error codes, back-pressure, SLOs

---

## Next Steps

1. **Review** this summary and linked documents
2. **Approve** the TDD plan (no code changes yet)
3. **Spawn agents** to execute Phase 1 (infrastructure)
   ```bash
   thegent free --do-next --repeat 4
   ```
4. **Monitor** progress via task list
5. **Merge** each completed phase before starting next

---

## Contact & Questions

All questions about Track 4 design are answered in:
- `docs/plans/TRACK_4_TDD_IMPLEMENTATION_PLAN.md` (primary reference)
- `docs/reference/SUBPROJECT_INTERFACE_SPEC.md` (protocol details)
- `docs/reference/TRACK_4_QUICK_CHECKLIST.md` (execution guide)

---

**Track 4 TDD Implementation Plan is READY FOR EXECUTION**

**Status:** ✅ Design Complete
**Review Date:** 2026-02-22
**Owner:** Claude Code
