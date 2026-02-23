# Merged Fragmented Markdown

## Source: changes/research-cross-platform-coordination/INDEX.md

# Consolidated Index

## Files

* `INDEX.md`
* `design.md`
* `proposal.md`
* `tasks.md`

## Subdirectories


---

## Source: changes/research-cross-platform-coordination/design.md

# Cross-Platform Coordination Through Unified Work Stream — Design

**Status**: Design
**Date**: 2026-02-18
**Baseline**: proposal.md

## 1. Architecture Overview

```
┌────────────────────────────────────────────────────────────────┐
│                    Unified Work Stream                        │
│              (docs/reference/WORK_STREAM.md)                  │
│  ┌─────────────┬──────────────┬─────────────────────────────┐ │
│  │   BACKLOG   │   CLAIMED    │      COMPLETED              │ │
│  │  (pending)  │ (in-flight)  │      (done)                 │ │
│  └─────────────┴──────────────┴─────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
                            ▲
                ┌───────────┼───────────┐
                │           │           │
    ┌───────────────┐ ┌────────────┐ ┌──────────────┐
    │  File Locking │ │   Agent    │ │ Session      │
    │  + Git Merge  │ │  Registry  │ │  Bridge      │
    └───────────────┘ └────────────┘ └──────────────┘
         (atomic)      (capability)   (continuity)
```

## 2. Core Components

### 1. Platform Registry

**Location**: `thegent/platform/registry.py`

**Data Model**:
```python
@dataclass
class PlatformCapabilities:
    os_type: OSType  # darwin, linux, win32
    arch: str  # x86_64, arm64, aarch64
    python_version: str  # 3.11.2
    tools: Dict[str, ToolCapability]  # {rg: present, version: 14.0}
    env_vars: Dict[str, str]  # PATH, SHELL, etc.
    max_concurrent_processes: int
    available_memory_mb: int
    disk_free_mb: int
    container_runtime: Optional[str]  # docker, podman
    capabilities: Set[str]  # gpu, ssl, network
    last_updated: datetime
    hash: str  # for cache validation
```

**Tool Capability**:
```python
@dataclass
class ToolCapability:
    name: str
    available: bool
    version: Optional[str]
    path: Optional[str]
    fallback: Optional[str]  # alternative tool if unavailable
    min_version: Optional[str]  # minimum required version
```

### 2. Capability Detector

**Location**: `thegent/platform/detector.py`

**Responsibilities**:
- Detect OS, architecture, Python version
- Probe for tools (rg, fd, jq, docker, etc.) via which/where
- Check environment variables, paths
- Measure available memory, disk space
- Detect hardware (GPU, special features)
- Cache results with TTL (default: 1 hour)

**Detection Strategy**:
```python
class CapabilityDetector:
    def detect_platform(self) -> PlatformCapabilities:
        """Comprehensive detection with fallbacks"""
        platform_caps = PlatformCapabilities(
            os_type=self._detect_os(),
            arch=platform.machine(),
            python_version=platform.python_version(),
            tools=self._detect_tools(),  # runs in parallel
            env_vars=self._safe_env_vars(),
            max_concurrent_processes=os.cpu_count() or 4,
            available_memory_mb=self._detect_memory(),
            disk_free_mb=self._detect_disk(),
            container_runtime=self._detect_container(),
            capabilities=self._detect_capabilities(),
            last_updated=datetime.now(),
        )
        platform_caps.hash = hashlib.sha256(
            json.dumps(asdict(platform_caps), default=str).encode()
        ).hexdigest()
        return platform_caps
```

**Tool Detection**:
- Fast path: Check PATH (avoid spawning subprocess if possible)
- Fallback: Use `which` (Unix) or `where` (Windows)
- Version extraction: Run tool with `--version` flag
- Timeout: 1s per tool (fail gracefully if slow)
- Parallelization: Detect tools concurrently to minimize total time

### 3. Platform Constraints

**Location**: `thegent/platform/constraints.py`

**Agent/Task Declaration**:
```yaml
# In agent definition or task prompt
platforms:
  supported: [darwin, linux]  # exclude windows
  required_tools: [rg, fd, jq]
  min_memory_mb: 512
  requires_container: false
  requires_gpu: false
  requires_network: true

fallback_strategy:
  unavailable_tools:
    rg: grep  # if rg unavailable, use grep instead
    fd: find
    jq: python json module
  degraded_mode: reduced_parallelism  # if memory < threshold
```

**Constraint Matching**:
```python
def matches_constraints(
    caps: PlatformCapabilities,
    constraints: PlatformConstraints
) -> MatchResult:
    """Check if platform satisfies task constraints"""
    errors = []
    warnings = []

    # Check OS
    if caps.os_type not in constraints.supported:
        errors.append(f"OS {caps.os_type} not supported")

    # Check tools
    for tool in constraints.required_tools:
        if tool not in caps.tools or not caps.tools[tool].available:
            if tool in constraints.fallback_strategy.unavailable_tools:
                warnings.append(f"Tool {tool} unavailable, using fallback")
            else:
                errors.append(f"Required tool {tool} not found")

    # Check memory
    if caps.available_memory_mb < constraints.min_memory_mb:
        if constraints.degraded_mode:
            warnings.append(f"Memory low, degrading to {constraints.degraded_mode}")
        else:
            errors.append(f"Insufficient memory: {caps.available_memory_mb}MB < {constraints.min_memory_mb}MB")

    return MatchResult(
        matches=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        fallback_applied=constraints.fallback_strategy if warnings else None
    )
```

### 4. Dispatch Logic

**Location**: `thegent/platform/dispatcher.py`

**Dispatch Algorithm**:
```python
class PlatformDispatcher:
    def dispatch(
        self,
        task: Task,
        available_executors: List[ExecutorInfo]
    ) -> DispatchDecision:
        """Select best-fit executor for task"""

        candidates = []

        for executor in available_executors:
            caps = self.registry.get_capabilities(executor.platform_id)
            match = matches_constraints(caps, task.platform_constraints)

            if not match.errors:
                score = self._score_executor(executor, caps, task)
                candidates.append((executor, score, match.warnings))

        if not candidates:
            return DispatchDecision(
                success=False,
                reason="No compatible executor found",
                diagnostics=self._suggest_fixes(task, available_executors)
            )

        # Sort by score: full match > fallback available > degraded
        best_executor, score, warnings = max(candidates, key=lambda x: x[1])

        return DispatchDecision(
            success=True,
            executor=best_executor,
            warnings=warnings,
            fallback_strategy=match.fallback_applied
        )

    def _score_executor(self, executor, caps, task) -> float:
        """Score: 100 = perfect, 50 = fallback, 0 = degraded"""
        score = 100.0

        # Penalize fallbacks
        if executor.has_fallbacks:
            score -= 30

        # Penalize degraded mode
        if executor.in_degraded_mode:
            score -= 40

        # Bonus for excess capacity
        excess_memory = caps.available_memory_mb - task.platform_constraints.min_memory_mb
        if excess_memory > 1024:
            score += 10

        return score
```

### 5. Fallback Strategies

**Unavailable Tool Substitution**:
| Tool | Priority 1 | Priority 2 | Note |
|------|-----------|-----------|------|
| `rg` (ripgrep) | `grep` | N/A | Always available on Unix |
| `fd` | `find` | N/A | Always available on Unix |
| `jq` | `python -m json.tool` | custom parser | JSON manipulation |
| `docker` | `podman` | None | Container management |
| `git` | Fail loudly | N/A | Required; no substitute |

**Degraded Modes**:
- **`reduced_parallelism`**: Reduce concurrent processes if memory < threshold
- **`single_threaded`**: Run serially if CPU-bound constraints tight
- **`readonly`**: Disable write operations in read-only mode
- **`network_offline`**: Disable external calls if network unavailable

**Graceful Handling**:
```python
def execute_with_fallback(
    task: Task,
    executor: ExecutorInfo,
    fallback_strategy: FallbackStrategy
) -> ExecutionResult:
    """Execute task with fallback handling"""

    try:
        # Attempt execution with requested tools
        return executor.execute(task)

    except ToolNotFoundError as e:
        tool_name = e.tool
        if tool_name in fallback_strategy.unavailable_tools:
            substitute = fallback_strategy.unavailable_tools[tool_name]
            logging.warning(f"Tool {tool_name} not found, using {substitute}")

            # Inject substitute and retry
            modified_task = task.replace_tool(tool_name, substitute)
            return executor.execute(modified_task)
        else:
            raise

    except InsufficientResourceError as e:
        if fallback_strategy.degraded_mode:
            logging.warning(f"Degrading to {fallback_strategy.degraded_mode}")
            task.degraded_mode = fallback_strategy.degraded_mode
            return executor.execute(task)
        else:
            raise
```

---

## Data Structures

### PlatformConstraints (YAML/JSON)
```json
{
  "platforms": {
    "supported": ["darwin", "linux"],
    "required_tools": ["rg", "fd"],
    "min_memory_mb": 512,
    "requires_container": false,
    "requires_gpu": false,
    "requires_network": false,
    "architecture": ["x86_64", "arm64"]
  },
  "fallback_strategy": {
    "unavailable_tools": {
      "rg": "grep",
      "fd": "find"
    },
    "degraded_mode": "reduced_parallelism"
  },
  "execution_hints": {
    "prefer_local": true,
    "max_retries": 3
  }
}
```

---

## Integration Points

### 1. CLI Commands
```bash
# Show platform capabilities
thegent platform detect

# Show registry (cached)
thegent platform registry

# Refresh capabilities
thegent platform detect --refresh

# Validate task constraints
thegent platform validate-task <task-id>

# Dispatch simulation (dry-run)
thegent platform dispatch-sim <task> --executors <executor-list>
```

### 2. MCP Tools
- `thegent://platform/detect` — Get current platform capabilities
- `thegent://platform/registry` — Access capability cache
- `thegent://platform/constraints` — Declare task constraints

### 3. Agent Declarative API
```python
# In agent skill or task
from thegent.platform import PlatformConstraint, fallback

@PlatformConstraint(
    supported_platforms=["darwin", "linux"],
    required_tools=["rg", "fd"],
    min_memory_mb=512,
    fallbacks={"rg": "grep", "fd": "find"}
)
def my_agent_task():
    pass
```

---

## Error Handling & Diagnostics

**Diagnostic Output**:
```
DISPATCH FAILED: Cannot find compatible executor for task "audit-security"

Constraints:
  • Supported platforms: darwin, linux
  • Required tools: semgrep, gosec
  • Min memory: 2048 MB

Available executors:
  1. macOS (darwin/x86_64) – MATCH, but semgrep not found (fallback available)
  2. Linux (linux/x86_64) – FAILED: gosec not found (no fallback)
  3. Windows (win32/x86_64) – FAILED: platform not supported

Suggestions:
  • Install semgrep on macOS (brew install semgrep)
  • Install gosec on Linux (apt-get install gosec)
  • Remove Windows from execution pool, or declare windows support
```

---

## Testing Strategy

### Unit Tests
- Platform detection on mocked environments
- Constraint matching algorithm with edge cases
- Dispatch scoring and selection logic
- Fallback strategy application

### Integration Tests
- Multi-platform CI matrix (macOS, Linux, Windows)
- Real tool detection (rg, fd, docker, etc.)
- End-to-end dispatch with actual executors

### Scenario Tests
- All tools available → perfect dispatch
- One tool missing → fallback applied, task succeeds
- Multiple tools missing → degraded mode or failure
- Memory exhausted → degraded or failure
- Network unavailable → offline mode or failure

---

## Rollout Plan

### Phase 1: Core (Week 1)
- [ ] Implement capability detector
- [ ] Build platform registry (in-memory + disk cache)
- [ ] Add constraint matching and fallback logic

### Phase 2: Integration (Week 2)
- [ ] Wire dispatch into `thegent run` and `thegent bg`
- [ ] Add CLI commands (`thegent platform *`)
- [ ] Expose MCP tools

### Phase 3: Verification (Week 3)
- [ ] Multi-platform CI matrix setup
- [ ] Documentation and agent guide
- [ ] Knowledge transfer and backlog closure

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Detection overhead (slow startup) | Medium | Low | Cache with TTL; lazy detection on first use |
| False negatives (tool detected but broken) | Low | Medium | Version validation; smoke tests on dispatch |
| Platform-specific quirks | Medium | Medium | Comprehensive test matrix; community feedback |
| Configuration complexity | Medium | Low | Sensible defaults; decorator API |

---

## Success Metrics

- [ ] Dispatch decision made in <100ms (p95)
- [ ] Zero manual platform workarounds in CI/CD
- [ ] 100% of agents declare platform constraints
- [ ] 95%+ dispatch success rate on multi-platform matrix
- [ ] Fallback strategies cover 80%+ of common tool unavailability scenarios

---

## Source: changes/research-cross-platform-coordination/proposal.md

# Cross-Platform Coordination Through Unified Work Stream — Proposal

**Status**: Proposal
**Date**: 2026-02-18
**Priority**: P1
**Depends On**: research-cross-platform-isolation

## 1. Problem Statement

Multi-agent orchestration across heterogeneous platforms (macOS/Linux/Windows, bash/PowerShell, multiple shells) requires a **single source of truth** that all agents can access, coordinate through, and update atomically. Current approaches have three critical gaps:

### Gap 1: Work Attribution and Isolation
- Agents on different platforms cannot safely claim work without race conditions
- No clear assignment model for tracking which agent owns which task
- File-based coordination prone to concurrent-write corruption

### Gap 2: Platform-Specific Command Execution
- Agents running bash cannot coordinate with PowerShell agents
- Platform-specific hooks/scripts create isolated silos
- No cross-platform abstraction for common operations (claiming, completing, status)

### Gap 3: Session Continuity Across Platforms
- Sessions started on macOS cannot be resumed on Windows
- State lives in process memory or platform-specific locations (registry, ~/.)
- Workstreams disconnected from session lifecycle

## 2. Vision

**Goal**: Enable seamless multi-agent coordination across OS/shell boundaries through a **unified, atomic work stream** with:

1. **Platform-agnostic serialization** (JSON + Markdown for human readability, machine parsability)
2. **Atomic claim/complete operations** (file-locked CLAIMED/COMPLETED sections)
3. **Cross-platform session bridges** (Unix socket + HTTP fallback; platform-neutral session state)
4. **Standardized agent metadata** (agent_id, shell, platform, capabilities, constraints)

## 3. Scope

### In Scope
- Unified work stream format (enhanced WORK_STREAM.md design)
- Atomic claim/complete/release operations (file locking + Git-based conflict resolution)
- Cross-platform session store (JSON ledger per project)
- Agent registration and capability discovery
- Dependency resolution (DAG validation)
- Handoff protocols (session transfer, resume, rollback)

### Out of Scope
- Desktop automation (covered by research-cross-platform-desktop)
- Shell abstraction layer (covered by research-cross-platform-shell)
- Remote compute (covered by research-cross-platform-remote)
- Performance optimization (covered by research-cross-platform-performance)

## 4. Design Principles

| Principle | Rationale |
|-----------|-----------|
| **Single Source of Truth** | All agents read from one canonical file (WORK_STREAM.md) |
| **Atomic Operations** | Claim/complete are transactions; no partial state |
| **Human-Readable** | Markdown format remains editable; machine sections clearly marked |
| **Git-Native Conflict Resolution** | Use Git's merge strategy; no custom conflict resolution |
| **No Polling** | Use file system events and blocking wait, not busy loops |
| **Platform-Agnostic** | Works on macOS, Linux, Windows; bash, PowerShell, zsh |
| **Session-Aware** | Links to session registry for continuity |
| **Fail-Fast** | Explicit errors, no silent degradation |

## 5. Core Components

### 5.1 Enhanced Work Stream Format

**File**: `docs/reference/WORK_STREAM.md`

- BACKLOG section: Unclaimed work items
- CLAIMED section: Items currently owned by agents (with agent_id, started time)
- COMPLETED section: Finished work (with duration, result)
- Machine sections: YAML frontmatter for metadata, lock state, conflict markers

### 5.2 Atomic Operations

**Claim**: Acquire lock → verify dependencies → append to CLAIMED → release lock
**Complete**: Remove from CLAIMED → append to COMPLETED → update source file
**Release**: Move from CLAIMED back to BACKLOG (on timeout/error)

### 5.3 Cross-Platform Session Bridge

**Session Store**: `~/.thegent/sessions/registry.jsonl`
**Bridge Protocol**: Unix socket (primary) + HTTP fallback (secondary)
**Heartbeat**: Every 30s; timeout after 5 min
**Hand-off**: Session owner can pause; another agent resumes

### 5.4 Agent Registry

**File**: `.thegent/agents/registry.json`

Declares per-agent:
- ID, type (researcher/coder/reviewer)
- Platform (macOS/Linux/Windows)
- Shell (bash/zsh/PowerShell)
- Capabilities (grep, read, web-search)
- Constraints (no-shell-edit, read-only)

## 6. Benefits

| Benefit | Impact |
|---------|--------|
| **Atomic claims** | No race conditions; work never duplicated or lost |
| **Cross-platform** | macOS + Windows + Linux agents coordinate via same WORK_STREAM |
| **Session continuity** | Agent on Platform A can pause; Agent on Platform B resumes seamlessly |
| **Git-native** | Conflicts resolved via `git merge` logic; no custom resolution |
| **Human-readable** | Managers can read WORK_STREAM.md directly |
| **Fail-fast** | Errors are explicit; no silent claims |
| **Scalable** | Handles 50+ concurrent agents; linear O(n) claim time |

## 7. Success Criteria

- [ ] WORK_STREAM.md format finalized and validated
- [ ] File locking implementation passes race condition tests
- [ ] Cross-platform session bridge works (Unix socket + HTTP)
- [ ] Claim/complete operations atomic and idempotent
- [ ] Agent registry auto-discovery working
- [ ] DAG dependency validation prevents circular claims
- [ ] Git conflict resolution tested with concurrent writes
- [ ] CLI commands (`thegent work claim`, `thegent work complete`) working
- [ ] Tests pass on macOS, Linux, Windows
- [ ] Performance: <100ms claim time (p95)

## 8. Deliverables

1. **proposal.md** (this file) — Problem, vision, scope
2. **design.md** — Technical architecture, APIs, protocols
3. **tasks.md** — Implementation checklist, phases, dependencies

## 9. References

- [WORK_STREAM.md](../reference/WORK_STREAM.md) (current format)
- [CROSS_PLATFORM_RESEARCH_CONSOLIDATED.md](../docset/CROSS_PLATFORM_RESEARCH_CONSOLIDATED.md)
- [thegent-cross-analysis-matrix-2026-02-14.md](../docset/thegent-cross-analysis-matrix-2026-02-14.md)

---

## Source: changes/research-cross-platform-coordination/tasks.md

# Cross-Platform Coordination Through Unified Work Stream — Tasks

**Status**: Task Planning
**Date**: 2026-02-18
**Baseline**: proposal.md, design.md

## Implementation Phases

### Phase 1: Work Stream Format & File Locking (Days 1-2)

#### T1.1: Enhance WORK_STREAM.md Format
**Estimate**: 4 tool calls | 20 min
**Owner**: Agent A
**Depends on**: None
**Status**: Pending

**Tasks**:
- [ ] Add YAML frontmatter to WORK_STREAM.md (version, metadata, lock state)
- [ ] Add Platform and Shell columns to BACKLOG table
- [ ] Document machine-readable sections (clear boundaries for parsing)
- [ ] Create examples of valid/invalid entries

**Acceptance Criteria**:
- Format supports all three sections (BACKLOG, CLAIMED, COMPLETED)
- Platform/shell constraints are optional (default: "any")
- YAML frontmatter is parseable and versioned
- Markdown is human-editable without tools

---

#### T1.2: File Locking Implementation
**Estimate**: 6 tool calls | 30 min
**Owner**: Agent A
**Depends on**: None
**Status**: Pending

**Tasks**:
- [ ] Implement `FileLock` class (Unix: fcntl, Windows: msvcrt, fallback: filelock)
- [ ] Add timeout handling (default: 10s, configurable)
- [ ] Implement lock recovery (stale lock cleanup)
- [ ] Add tests for race conditions (10+ concurrent agents)
- [ ] Test on macOS, Linux, Windows

**Acceptance Criteria**:
- Lock acquisition <10ms typical case
- Timeout works correctly on all platforms
- Stale locks cleaned up after 5 min
- Race condition tests pass (no duplicates, no lost claims)

---

### Phase 2: Session Bridge & Agent Registry (Days 3-4)

#### T2.1: Session Store & Registry
**Estimate**: 5 tool calls | 25 min
**Owner**: Agent B
**Depends on**: None
**Status**: Pending

**Tasks**:
- [ ] Create session store: `~/.thegent/sessions/registry.jsonl`
- [ ] Implement session registration (UUID-based session IDs)
- [ ] Add session state tracking (in_progress, paused, completed)
- [ ] Implement heartbeat mechanism (30s interval, 300s timeout)
- [ ] Add session rollback on timeout (move work back to BACKLOG)

**Acceptance Criteria**:
- Sessions persist across process restarts
- Heartbeat correctly detects stale sessions
- Timeout correctly releases locks
- Session state machine is correct

---

#### T2.2: Agent Registry
**Estimate**: 4 tool calls | 20 min
**Owner**: Agent B
**Depends on**: None
**Status**: Pending

**Tasks**:
- [ ] Create agent registry: `.thegent/agents/registry.json`
- [ ] Add agent metadata (id, type, platform, shell, capabilities)
- [ ] Implement capability discovery (from agent definitions)
- [ ] Add constraint validation per agent
- [ ] Implement registry lookup by agent_id

**Acceptance Criteria**:
- Registry auto-discovers agents from definitions
- Constraints are enforced at claim time
- Clear error messages for unsupported platforms/shells

---

#### T2.3: Cross-Platform Session Bridge
**Estimate**: 6 tool calls | 30 min
**Owner**: Agent B
**Depends on**: T2.1
**Status**: Pending

**Tasks**:
- [ ] Implement Unix socket bridge (primary): `~/.thegent/sessions/bridge.sock`
- [ ] Implement HTTP fallback (secondary): `http://localhost:37847/sessions`
- [ ] Add session registration protocol (JSON messages)
- [ ] Implement heartbeat/ping protocol
- [ ] Test bridge on macOS (Unix socket), Windows (HTTP fallback)

**Acceptance Criteria**:
- Unix socket works on macOS/Linux
- HTTP fallback works when socket unavailable
- Heartbeat keeps sessions alive
- Cross-platform hand-offs work (session survives platform change)

---

### Phase 3: Atomic Operations (Days 5-6)

#### T3.1: Claim Operation
**Estimate**: 7 tool calls | 35 min
**Owner**: Agent C
**Depends on**: T1.2, T2.1, T2.2
**Status**: Pending

**Tasks**:
- [ ] Implement `claim_work()` function (acquires lock, validates deps, appends to CLAIMED)
- [ ] Add dependency validation (DAG check, circular detection)
- [ ] Add platform/shell constraint matching
- [ ] Implement session registration on claim
- [ ] Add comprehensive error handling and diagnostics

**Acceptance Criteria**:
- Claim succeeds for valid work
- Claim fails clearly for already-claimed work
- Dependency validation prevents invalid claims
- Session registration creates heartbeat task
- Error messages are actionable

---

#### T3.2: Complete Operation
**Estimate**: 5 tool calls | 25 min
**Owner**: Agent C
**Depends on**: T1.2, T3.1
**Status**: Pending

**Tasks**:
- [ ] Implement `complete_work()` function (moves from CLAIMED to COMPLETED)
- [ ] Calculate duration (started → completed)
- [ ] Update source file (e.g., 02-UNIFIED-WBS.md) to DONE status
- [ ] Update session state (idle)
- [ ] Add result tracking (commit SHA, duration, metadata)

**Acceptance Criteria**:
- Complete succeeds for claimed work
- Complete fails clearly if work not claimed by agent
- Source files are updated atomically
- Duration is calculated correctly
- Session state reflects completion

---

#### T3.3: Hand-off Protocol
**Estimate**: 5 tool calls | 25 min
**Owner**: Agent C
**Depends on**: T2.1, T3.1
**Status**: Pending

**Tasks**:
- [ ] Implement `hand_off_work()` for cross-platform transfer
- [ ] Create checkpoint (git SHA, files modified)
- [ ] Register new session for target agent
- [ ] Update CLAIMED (agent field changes)
- [ ] Pause source session

**Acceptance Criteria**:
- Hand-off creates clean handover point (git checkpoint)
- Target agent can resume from checkpoint
- Source session paused but work retained
- Both agents can track work ownership history

---

### Phase 4: DAG Validation & CLI (Days 7-8)

#### T4.1: DAG Validator
**Estimate**: 5 tool calls | 25 min
**Owner**: Agent D
**Depends on**: T1.1, T3.1
**Status**: Pending

**Tasks**:
- [ ] Implement topological sort for work stream
- [ ] Detect circular dependencies (Tarjan's algorithm)
- [ ] Validate all CLAIMED deps are satisfied
- [ ] Check platform/shell compatibility at claim time
- [ ] Add detailed error reporting

**Acceptance Criteria**:
- Circular dependencies detected and reported
- Unsatisfied deps prevent claiming
- Platform constraints validated
- Error messages list exact issues

---

#### T4.2: CLI Commands
**Estimate**: 6 tool calls | 30 min
**Owner**: Agent D
**Depends on**: T3.1, T3.2, T3.3, T4.1
**Status**: Pending

**Tasks**:
- [ ] Implement `thegent work claim <id> --agent <agent_id>`
- [ ] Implement `thegent work complete <id> --agent <agent_id> --result <result>`
- [ ] Implement `thegent work status <id>`
- [ ] Implement `thegent work claimed --agent <agent_id>`
- [ ] Implement `thegent work handoff <id> --from <agent_a> --to <agent_b>`
- [ ] Implement `thegent work show` (display full stream)

**Acceptance Criteria**:
- All commands work end-to-end
- Output is clear (table format for lists)
- Help text is comprehensive
- Commands complete in <1s

---

### Phase 5: Testing (Days 9-10)

#### T5.1: Unit Tests
**Estimate**: 8 tool calls | 40 min
**Owner**: Agent E
**Depends on**: All core implementation
**Status**: Pending

**Tasks**:
- [ ] Test file locking (no race conditions)
- [ ] Test claim/complete workflows
- [ ] Test hand-off protocol
- [ ] Test DAG validation
- [ ] Test platform/shell constraint matching
- [ ] Test error handling

**Test Coverage Target**: ≥85%

**Acceptance Criteria**:
- All tests pass
- Coverage ≥85%
- Race condition tests pass with 10+ concurrent agents

---

#### T5.2: Cross-Platform Integration Tests
**Estimate**: 6 tool calls | 30 min
**Owner**: Agent E
**Depends on**: T5.1
**Status**: Pending

**Tasks**:
- [ ] Test claim/complete on macOS (darwin/zsh)
- [ ] Test claim/complete on Linux (linux/bash)
- [ ] Test hand-off from macOS → Linux
- [ ] Test hand-off from Linux → Windows
- [ ] Test session bridge (Unix socket + HTTP)
- [ ] Test concurrent claims from multiple agents

**Acceptance Criteria**:
- All workflows work on ≥3 platforms
- Hand-offs preserve state correctly
- Session bridge handles fallback correctly
- Concurrent operations produce no duplicates

---

### Phase 6: Documentation & Handoff (Day 11)

#### T6.1: API Documentation
**Estimate**: 4 tool calls | 20 min
**Owner**: Agent F
**Depends on**: All implementation
**Status**: Pending

**Location**: `docs/reference/WORK_STREAM_API.md`

**Tasks**:
- [ ] Document claim/complete/handoff APIs
- [ ] Document error codes and messages
- [ ] Document platform/shell constraint format
- [ ] Provide Python examples for agents

**Acceptance Criteria**:
- API is clearly documented
- Examples are runnable
- Error handling is clear

---

#### T6.2: Developer Guide
**Estimate**: 3 tool calls | 15 min
**Owner**: Agent F
**Depends on**: T6.1
**Status**: Pending

**Location**: `docs/guides/UNIFIED_WORK_STREAM_GUIDE.md`

**Tasks**:
- [ ] Document how agents claim work
- [ ] Document how to declare platform constraints
- [ ] Document hand-off workflow
- [ ] Provide troubleshooting tips

**Acceptance Criteria**:
- Guide is clear and actionable
- Examples cover basic and advanced scenarios

---

## Dependency Graph

```
T1.1 (Format) → T1.2 (File Locking)
  ├─→ T2.1 (Session Store)
  ├─→ T2.2 (Agent Registry)
  │    └─→ T2.3 (Session Bridge) → T3.1 (Claim) → T3.2 (Complete)
  │                                    └─→ T3.3 (Hand-off)
  └─→ T4.1 (DAG Validator) → T4.2 (CLI)

T5.1 (Unit Tests) → T5.2 (Integration Tests)
T6.1 (API Docs) → T6.2 (Guide)
```

## Timeline

| Phase | Tasks | Est. Time | Days |
|-------|-------|-----------|------|
| 1: Format & Locking | T1.1, T1.2 | 50 min | 1 |
| 2: Session & Registry | T2.1, T2.2, T2.3 | 75 min | 1 |
| 3: Atomic Ops | T3.1, T3.2, T3.3 | 65 min | 1 |
| 4: Validation & CLI | T4.1, T4.2 | 55 min | 1 |
| 5: Testing | T5.1, T5.2 | 70 min | 2 |
| 6: Docs | T6.1, T6.2 | 35 min | 1 |
| **Total** | **11 tasks** | **~350 min** | **~7 days** (serial) |
| **Parallel** | Groups by phase | **~2 hrs/phase** | **~3-4 days** |

## Definition of Done

- [ ] All code passes linting (ruff, mypy)
- [ ] Unit test coverage ≥85%
- [ ] Integration tests pass on macOS, Linux, Windows
- [ ] All CLI commands working and documented
- [ ] Documentation complete and reviewed
- [ ] Feature merged to main
- [ ] WORK_STREAM.md incorporator updated
- [ ] Agent developers trained

---

## Dependency Graph (DAG)

```
T1.1 (Detect OS/Arch)
  ├─→ T1.2 (Tool Detection)
  ├─→ T1.3 (Memory/Disk/GPU)
  └─→ T1.4 (Data Model) ──→ T2.1 (Constraint Matching) ──→ T3.1 (Dispatch)
        └─→ T2.3 (Registry) ──→ T3.1
                  ├─→ T3.2 (Integration)
                  ├─→ T3.3 (CLI)
                  ├─→ T4.1 (MCP)
                  └─→ T4.2 (Decorators)

T5.1 (Unit Tests) ──→ T5.2 (Integration Tests) ──→ T5.3 (Multi-Platform CI)
T6.1 (Agent Guide), T6.2 (Registry Docs), T6.3 (Architecture)
T7.1 (Review & Merge) ──→ T7.2 (Handoff)
```

---

## Timeline

| Phase | Days | Start | End | Status |
|-------|------|-------|-----|--------|
| 1: Detection | 2 | Day 1 | Day 2 | Pending |
| 2: Constraint & Registry | 2 | Day 3 | Day 4 | Pending |
| 3: Dispatch | 2 | Day 5 | Day 6 | Pending |
| 4: MCP Integration | 1 | Day 7 | Day 7 | Pending |
| 5: Testing | 2 | Day 8 | Day 9 | Pending |
| 6: Documentation | 1 | Day 10 | Day 10 | Pending |
| 7: Integration | 1 | Day 11 | Day 11 | Pending |
| **Total** | **11** | **Day 1** | **Day 11** | **Pending** |

**Wall-clock with parallel agents**: ~6-7 days (agents A-E working in parallel)

---

## Definition of Done

- [ ] All code passes linting (ruff, mypy, type checks)
- [ ] Unit test coverage ≥80%
- [ ] Integration tests pass on ≥2 platforms
- [ ] Multi-platform CI matrix green
- [ ] Documentation complete and reviewed
- [ ] No outstanding review comments
- [ ] Feature merged to main branch
- [ ] Agent developers notified and trained
- [ ] Capability discovered in real agent usage (post-launch)

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Tool detection too slow | Parallel detection, cache TTL, lazy detection |
| False positives in tool detection | Version validation, smoke tests |
| Cross-platform quirks | Comprehensive test matrix, community feedback |
| Agent adoption friction | Simple decorator, clear docs, examples |

---

## Success Metrics

- [ ] Dispatch decisions made in <100ms p95
- [ ] 100% of new agents declare platform constraints
- [ ] 95%+ dispatch success rate on multi-platform matrix
- [ ] Zero manual platform workarounds in CI/CD
- [ ] Fallback strategies cover 80%+ of tool unavailability scenarios

---

## Rollback Plan

If issues arise:
1. Disable dispatch for tasks without constraints (use all executors)
2. Keep fallback registry but skip constraint validation
3. Disable multi-platform CI temporarily
4. Root cause analysis and patch
5. Re-enable features incrementally

---

## Notes for Agents

- **Parallel execution**: T1.x and T2.x can run in parallel (dependencies only at phase boundaries)
- **Code review**: Each phase should have code review before next phase starts
- **Testing as you go**: Unit tests alongside implementation, not after
- **Documentation**: Docs should be written during implementation, not as afterthought
- **Communication**: Log progress to CONVERSATION_DUMP daily

---

## Contact & Escalation

- **Technical Lead**: thegent core team
- **Blockers**: File issue in escalation queue (`docs/reference/ESCALATION_QUEUE.md`)
- **Questions**: Post to `docs/research/CONVERSATION_DUMP_YYYY-MM-DD.md`

---
