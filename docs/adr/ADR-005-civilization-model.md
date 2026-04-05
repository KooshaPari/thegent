# ADR-005: Civilization Model for Multi-Agent Coordination

**Date**: 2026-04-04  
**Status**: Proposed  
**Deciders**: Architecture Team  
**Supersedes**: ADR-001 (basic agent framework)

---

## Context

### Problem Statement

thegent needs to coordinate multiple specialized agents (installer, configurator, verifier, auditor) to work together on complex dotfiles management tasks. Single-agent approaches fail when:
- Tasks have interdependent subtasks requiring different expertise
- Multiple agents need to access shared resources safely
- Results from one agent must feed into another's workflow
- Parallel execution opportunities are missed due to coordination overhead

### Background

Current thegent architecture supports single-agent execution with tiered sandboxing (ADR-002). However, dotfiles management inherently requires multiple coordinated operations:

1. **Installation agents** must prepare the environment (install packages)
2. **Configuration agents** must set up dotfiles based on detected environment
3. **Verification agents** must validate correctness of installed items
4. **Auditor agents** must ensure security and policy compliance

These agents have data dependencies (installer output feeds configurator input) and resource dependencies (can't configure before install is complete).

### Requirements

**Functional Requirements**:
- Support 2-10 concurrent agents per task
- Enable structured data passing between agents
- Support parallel execution where dependencies allow
- Maintain sandbox isolation between agents
- Provide unified audit trail across all agent executions

**Non-Functional Requirements**:
- Agent coordination overhead < 50ms
- Support 100+ concurrent civilizations per host
- Graceful degradation when agents fail
- Deterministic replay of agent workflows

**Constraints**:
- Must work within existing sandbox tier architecture (ADR-002)
- Must support thegent's Rust-first implementation
- Must integrate with existing role-based agent model

---

## Decision

### Chosen Alternative

**Adopt the Civilization Model**: A role-based multi-agent coordination pattern where specialized agents form "civilizations" with shared goals, communication protocols, and resource management.

> We have decided to implement the Civilization Model for multi-agent coordination because it provides structured parallelism, clear role boundaries, and natural extensibility while building on CrewAI-inspired role patterns already in the architecture.

### Key Design Principles

1. **Civilization**: A scoped execution context containing 2-10 agents working toward a shared goal
2. **Roles**: Specialized agent types (Installer, Configurator, Verifier, Auditor) with defined capabilities
3. **Protocols**: Standard communication patterns between agents (request, respond, delegate, broadcast)
4. **Artifacts**: Shared data structures passed between agents (environment metadata, config diffs, verification results)

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Civilization                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Civilization Coordinator                   │  │
│  │  • Goal decomposition                                 │  │
│  │  • Dependency graph management                        │  │
│  │  • Resource allocation                                │  │
│  │  • Result aggregation                                  │  │
│  └───────────────────────────────────────────────────────┘  │
│                            │                                  │
│  ┌─────────────┬───────────┴───────────┬─────────────┐       │
│  │             │                       │             │       │
│  ▼             ▼                       ▼             ▼       │
│ ┌────────┐ ┌────────┐           ┌────────┐ ┌────────┐       │
│ │Agent:  │ │Agent:  │           │Agent:  │ │Agent:  │       │
│ │Installer│ │Config- │           │Verifier│ │Auditor │       │
│ │         │ │urator  │           │        │ │        │       │
│ └────────┘ └────────┘           └────────┘ └────────┘       │
│      │            │                 │             │         │
│      └────────────┴─────────────────┴─────────────┘         │
│                        │                                     │
│              ┌─────────▼─────────┐                          │
│              │  Shared Artifact   │                          │
│              │      Store         │                          │
│              │  • env_metadata    │                          │
│              │  • config_delta    │                          │
│              │  • verify_results  │                          │
│              └───────────────────┘                          │
└─────────────────────────────────────────────────────────────┘
```

---

## Alternatives Considered

### Alternative 1: Flat Multi-Agent (All Agents Equal)

**Description**: All agents are peers with no explicit roles, communicate via broadcast messaging.

**Pros**:
- Simple implementation
- Maximum flexibility
- No role hierarchy overhead

**Cons**:
- No clear specialization
- Coordination becomes chaotic with >3 agents
- Difficult to reason about execution order
- No natural extension points

**Effort**: Small  
**Risk**: Medium (coordination complexity grows exponentially)

---

### Alternative 2: Hierarchical Pipeline (Master-Agent)

**Description**: One master agent orchestrates worker agents in a strict pipeline.

```
Master Agent
    │
    ├──► Installer ─► Master ─► Configurator ─► Master ─► Verifier
    │                     │                         │
    └─────────────────────┴─────────────────────────┘
                    (Results passed up hierarchy)
```

**Pros**:
- Clear execution order
- Master has full visibility
- Simple to reason about

**Cons**:
- Master becomes bottleneck
- No parallelism (strict pipeline)
- Master failure cascades
- Doesn't match real-world coordination patterns

**Effort**: Medium  
**Risk**: Low (but limits parallelism)

---

### Alternative 3: Blackboard System (Shared State Space)

**Description**: All agents communicate via a shared "blackboard" - a centralized knowledge store.

```
┌─────────────────────────────────────────┐
│              Blackboard                  │
│  ┌───────────────────────────────────┐  │
│  │ Knowledge:                         │  │
│  │ • env_detection: {os: macos}      │  │
│  │ • package_list: [brew, cargo]     │  │
│  │ • config_needs: {zsh: true}       │  │
│  └───────────────────────────────────┘  │
│         ▲    ▲    ▲    ▲                 │
│         │    │    │    │                 │
│    ┌────┐ ┌────┐ ┌────┐ ┌────┐          │
│    │Inst│ │Conf│ │Verif│ │Audt│          │
│    └────┘ └────┘ └────┘ └────┘          │
└─────────────────────────────────────────┘
```

**Pros**:
- Decoupled agents
- Natural parallelism
- Easy to add new agents
- Well-studied pattern (Hearsay II)

**Cons**:
- Centralized state becomes contention point
- No clear data flow
- Difficult to enforce ordering
- Blackboard can become unwieldy

**Effort**: Large  
**Risk**: Medium (complexity in consistency management)

---

### Alternative 4: Civilization Model (Chosen)

**Description**: Role-based agents with structured communication, shared artifacts, and a coordinator managing execution.

**Pros**:
- Clear roles and responsibilities
- Structured parallelism (agents within role work in parallel)
- Natural extension (add new roles)
- Coordinator handles complexity
- Matches CrewAI patterns (proven)
- Supports hierarchy when needed

**Cons**:
- More complex than flat model
- Coordinator is critical path
- Role definitions must be precise

**Effort**: Medium  
**Risk**: Low (builds on proven patterns)

---

## Rationale

### Comparison Matrix

| Criteria | Weight | Flat | Hierarchical | Blackboard | Civilization |
|----------|--------|------|--------------|------------|--------------|
| Parallelism | 25% | 9 | 4 | 8 | 8 |
| Coordination overhead | 20% | 6 | 7 | 5 | 7 |
| Role clarity | 15% | 3 | 6 | 4 | 9 |
| Extensibility | 15% | 7 | 5 | 8 | 9 |
| Fault isolation | 10% | 5 | 3 | 6 | 8 |
| Implementation complexity | 15% | 9 | 6 | 4 | 6 |
| **Total** | **100%** | **6.5** | **5.1** | **6.0** | **7.8** |

### Key Decision Factors

1. **Parallelism**: Civilization enables agents within roles to work in parallel (e.g., multiple installers for different package managers) while maintaining coordination between roles.

2. **Role Clarity**: The role-based approach maps directly to the agent types already defined (Installer, Configurator, Verifier, Auditor), reducing conceptual overhead.

3. **Extensibility**: Adding new agent types is straightforward - define the role, implement the agent, register with coordinator.

4. **Fault Isolation**: When one agent fails, the civilization can (optionally) continue with remaining agents, and the coordinator can route around failures.

---

## Consequences

### Positive Consequences (Benefits)

- **Structured Parallelism**: Agents within the same role can execute in parallel while respecting inter-role dependencies
- **Clear Data Flow**: Artifacts provide explicit data passing, making execution traceable
- **Scalable Coordination**: Coordinator overhead is O(agents) not O(agents^2)
- **Natural Testing**: Each role has defined inputs/outputs, enabling unit testing in isolation
- **Role Reuse**: Same roles can be composed into different civilizations for different tasks

### Negative Consequences (Drawbacks)

- **Coordinator Dependency**: The civilization coordinator is a single point of failure
- **Role Rigidity**: Predefined roles may not fit all use cases
- **Artifact Overhead**: Passing data via artifacts adds latency vs. direct communication
- **Learning Curve**: Users must understand the civilization concept

### Neutral Consequences

- **Coordination Protocol Complexity**: More complex than simple pipelining but enables better parallelism
- **Sandbox Requirements**: Each agent still runs in its sandbox tier (ADR-002), requiring inter-sandbox communication

---

## Implementation Plan

### Phase 1: Core Civilization Infrastructure

**Timeline**: 2026-04-07 - 2026-04-14  
**Effort**: 5 person-days

**Tasks**:
- [ ] Define `Civilization` struct with coordinator reference
- [ ] Implement `CivilizationCoordinator` trait
- [ ] Create artifact store (in-memory for Phase 1)
- [ ] Define role registry (Installer, Configurator, Verifier, Auditor)
- [ ] Implement basic coordination protocol (request-response)

**Deliverables**:
- `crates/civilization/src/coordinator.rs` - Core coordinator logic
- `crates/civilization/src/artifact.rs` - Artifact store
- `crates/civilization/src/roles.rs` - Role definitions

**Success Criteria**:
- [ ] Two agents can communicate via civilization
- [ ] Coordinator can decompose a goal into tasks
- [ ] Artifact store correctly passes data between agents

---

### Phase 2: Parallel Execution Support

**Timeline**: 2026-04-14 - 2026-04-21  
**Effort**: 4 person-days

**Tasks**:
- [ ] Implement dependency graph for agent tasks
- [ ] Add parallel task executor using existing async runtime
- [ ] Implement fan-out/fan-in patterns for role groups
- [ ] Add cancellation support for civilizations

**Deliverables**:
- `crates/civilization/src/executor.rs` - Parallel task executor
- `crates/civilization/src/dependency.rs` - Dependency graph

**Success Criteria**:
- [ ] 4 agents can execute in parallel when dependencies allow
- [ ] Dependency violations are detected and reported
- [ ] Civilization can be cancelled mid-execution

---

### Phase 3: Fault Tolerance and Observability

**Timeline**: 2026-04-21 - 2026-04-28  
**Effort**: 3 person-days

**Tasks**:
- [ ] Implement agent failure handling (continue, abort, retry)
- [ ] Add structured logging for civilization execution
- [ ] Create execution audit trail
- [ ] Add metrics (duration, resource usage per agent)

**Deliverables**:
- `crates/civilization/src/fault.rs` - Fault handling
- `crates/civilization/src/audit.rs` - Audit trail

**Success Criteria**:
- [ ] Agent failure doesn't crash civilization
- [ ] Full execution trace is available post-run
- [ ] Metrics are exposed for monitoring

---

## Rollback Plan

**Rollback Trigger**: 
- Civilization coordination overhead exceeds 100ms (10x target)
- Agent communication failures > 10% of executions
- Unrecoverable deadlocks occurring > 1% of runs

**Rollback Steps**:
1. Feature flag `civilization_enabled = false` in config
2. Revert to single-agent execution path
3. Deprecate civilization CLI flags
4. Keep civilization crate but don't use it

**Rollback Timeline**: 1 day (code already feature-flagged)

**Rollback Cost**: Low - single-agent mode remains available

---

## Related Decisions

### Previous Decisions

- **ADR-001**: Agent framework (establishes base agent model that civilization extends)
- **ADR-002**: Sandboxing strategy (civilization agents run within sandbox tiers)
- **ADR-003**: Multi-tenant architecture (civilizations can be tenant-isolated)

### Supersedes

- N/A - this is a new capability

### Superseded By

- Future ADR may supersede if we adopt a different coordination model

---

## Design Details

### Core Data Structures

```rust
/// A civilization is a coordinated group of agents working toward a shared goal
pub struct Civilization {
    pub id: Uuid,
    pub goal: String,
    pub coordinator: Arc<dyn CivilizationCoordinator>,
    pub roles: RoleRegistry,
    pub artifacts: Arc<dyn ArtifactStore>,
    pub config: CivilizationConfig,
}

/// The coordinator manages execution order and agent lifecycle
pub trait CivilizationCoordinator: Send + Sync {
    /// Decompose goal into ordered tasks
    fn decompose(&self, goal: &str) -> Vec<AgentTask>;
    
    /// Select agent for a given role
    fn select_agent(&self, role: &Role) -> Option<Arc<dyn Agent>>;
    
    /// Handle agent result
    fn on_result(&self, task_id: &str, result: AgentResult) -> CoordinationAction;
    
    /// Handle agent failure
    fn on_failure(&self, task_id: &str, error: &Error) -> CoordinationAction;
}

/// Roles define agent capabilities and communication patterns
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum Role {
    Installer,
    Configurator,
    Verifier,
    Auditor,
}

impl Role {
    pub fn default_tools(&self) -> Vec<Box<dyn Tool>> {
        match self {
            Role::Installer => vec![
                Box::new(InstallPackage),
                Box::new(DetectPackageManager),
            ],
            Role::Configurator => vec![
                Box::new(CreateSymlink),
                Box::new(WriteConfig),
            ],
            Role::Verifier => vec![
                Box::new(CheckSymlink),
                Box::new(ValidateConfig),
            ],
            Role::Auditor => vec![
                Box::new(ScanSecurityPatterns),
                Box::new(VerifyPolicyCompliance),
            ],
        }
    }
}

/// Artifacts are shared data structures passed between agents
pub trait Artifact: Send + Sync + Debug {
    fn artifact_type(&self) -> &str;
    fn artifact_id(&self) -> Uuid;
}

#[derive(Debug)]
pub struct EnvironmentMetadata {
    pub id: Uuid,
    pub os: OperatingSystem,
    pub package_managers: Vec<PackageManager>,
    pub shell: Shell,
    pub home_dir: PathBuf,
}
```

### Communication Protocol

```rust
/// Agents communicate via structured messages
#[derive(Debug, Message)]
pub enum AgentMessage {
    /// Request action from another agent
    Request {
        id: Uuid,
        to_role: Role,
        task: String,
        artifacts: Vec<Uuid>,
        reply_to: Uuid,
    },
    
    /// Response to a request
    Response {
        id: Uuid,
        in_reply_to: Uuid,
        result: Result<Artifact>,
    },
    
    /// Broadcast to all agents
    Broadcast {
        id: Uuid,
        content: String,
        artifacts: Vec<Uuid>,
    },
    
    /// Delegate task to subordinate
    Delegate {
        id: Uuid,
        to_agent: Uuid,
        subtask: String,
        constraints: ExecutionConstraints,
    },
}
```

### Example Civilization Execution

```rust
/// Example: Installing and configuring development environment
async fn setup_development_environment() -> Result<CivilizationResult> {
    let civilization = Civilization::builder()
        .goal("Set up complete development environment")
        .role(Role::Installer, installer_agent.clone())
        .role(Role::Configurator, configurator_agent.clone())
        .role(Role::Verifier, verifier_agent.clone())
        .role(Role::Auditor, auditor_agent.clone())
        .build()?;
    
    // Execute with automatic parallelization
    let result = civilization.execute().await?;
    
    // Result includes:
    // - All artifacts produced
    // - Execution timeline
    // - Any failures and how they were handled
    // - Audit trail
    
    Ok(result)
}
```

---

## Approval and Sign-Off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Tech Lead | [TBD] | [ ] | 2026-04-04 |
| Architecture Review | [TBD] | [ ] | 2026-04-04 |
| Product Owner | [TBD] | [ ] | 2026-04-04 |

---

## Monitoring and Review

### Success Metrics

| Metric | Target | Measurement | Frequency |
|--------|--------|-------------|-----------|
| Coordination overhead | <50ms | P50 per civilization | Per execution |
| Parallelism efficiency | >70% | (parallel time / total time) | Per execution |
| Agent communication failures | <1% | Failed messages / total | Daily |
| Civilization completion rate | >95% | Successful / total | Weekly |

### Review Schedule

- **1-week review**: Check coordination overhead metrics
- **2-week review**: Full execution analysis
- **1-month review**: Determine if civilization model should be default

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-04-04 | Research Agent | Initial version |

---

## Appendix

### A. Comparison with CrewAI

thegent's Civilization Model is inspired by CrewAI but differs in key ways:

| Aspect | CrewAI | thegent Civilization |
|--------|--------|---------------------|
| Agent communication | handoff-based | artifact-based |
| Execution model | Sequential handoffs | Parallel with dependency graph |
| Sandbox isolation | No | Yes (ADR-002) |
| Role definition | Loose | Strict with registry |
| Extensibility | Via custom agents | Via role registry + SKILL.md |

### B. Future Considerations

- **Hierarchical civilizations**: Civilizations of civilizations for complex workflows
- **Cross-civilization communication**: Agents from different civilizations sharing artifacts
- **Persistent civilizations**: Long-running civilizations for ongoing management tasks

---

*This ADR will be updated as implementation progresses*
