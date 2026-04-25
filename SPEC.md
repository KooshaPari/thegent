# thegent Specification

> Meta-Agent Framework for Autonomous System Orchestration

## Overview

`thegent` (The Agent) is a sophisticated meta-agent framework that enables:
- **Autonomous System Orchestration**: Self-directed execution with minimal human intervention
- **Multi-Agent Collaboration**: Seamless coordination between multiple agents
- **Intelligent Task Decomposition**: Break complex tasks into manageable sub-tasks
- **Continuous Self-Improvement**: Learn from execution feedback

## Philosophy

**"The agent that manages agents"**

| Principle | Description |
|-----------|-------------|
| **Autonomy** | Self-directed execution with minimal human intervention |
| **Reflection** | Continuous self-improvement through execution feedback |
| **Collaboration** | Seamless multi-agent coordination |
| **Adaptation** | Dynamic reconfiguration based on context |

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          TheGent Architecture                                  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        Meta-Controller                                 │   │
│  │                   (High-level orchestration)                           │   │
│  │                                                                      │   │
│  │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐               │   │
│  │   │   Planner   │  │  Reflector  │  │   Learner   │               │   │
│  │   │ (Planning)  │  │  (Analysis) │  │ (Adaptation)│               │   │
│  │   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘               │   │
│  │          │                │                │                       │   │
│  │          └────────────────┼────────────────┘                       │   │
│  │                           │                                       │   │
│  │                           ▼                                       │   │
│  │                  ┌─────────────┐                                  │   │
│  │                  │  Executor   │                                  │   │
│  │                  │ (Execution) │                                  │   │
│  │                  └──────┬──────┘                                  │   │
│  └─────────────────────────┼─────────────────────────────────────────┘   │
│                            │                                               │
│  ┌─────────────────────────┼─────────────────────────────────────────┐   │
│  │                    Agent Ecosystem                                     │   │
│  │                                                                      │   │
│  │   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐         │   │
│  │   │Orchest-  │  │Executor  │  │ Advisor  │  │  Memory  │         │   │
│  │   │  rator   │  │          │  │          │  │          │         │   │
│  │   └──────────┘  └──────────┘  └──────────┘  └──────────┘         │   │
│  │                                                                      │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Core Components

| Component | Role | Key Features |
|-----------|------|--------------|
| **Meta-Controller** | High-level orchestration | Goal management, strategy selection |
| **Planner** | Task decomposition | Hierarchical planning, dependency resolution |
| **Executor** | Plan execution | Action execution, monitoring, rollback |
| **Reflector** | Post-execution analysis | Outcome analysis, error diagnosis |
| **Learner** | Pattern extraction | Behavior adaptation, skill acquisition |
| **Communicator** | Inter-agent messaging | Pub/sub, direct messaging, broadcast |

## Agent Model

```go
type Agent struct {
    ID       string
    Name     string
    Type     AgentType
    Group    *AgentGroup
    State    AgentState
    Skills   []Skill
    Inbox    chan *Message
    Outbox   chan *Message
    Handlers map[string]MessageHandler
}

type AgentType string

const (
    AgentTypeOrchestrator AgentType = "orchestrator"
    AgentTypeExecutor     AgentType = "executor"
    AgentTypeAdvisor      AgentType = "advisor"
    AgentTypeMemory       AgentType = "memory"
)

type AgentState struct {
    Data   map[string]interface{}
    Status AgentStatus
    Voted  bool
    Leader bool
}

type AgentStatus string

const (
    StatusIdle      AgentStatus = "idle"
    StatusBusy      AgentStatus = "busy"
    StatusError     AgentStatus = "error"
    StatusCompleted AgentStatus = "completed"
)
```

## Messaging System

```go
type Message struct {
    ID        string
    From      string
    To        string  // empty for broadcast
    Type      MessageType
    Subject   string
    Payload   []byte
    ReplyTo   string
    Timestamp time.Time
}

type MessageType string

const (
    MessageTypeDirect    MessageType = "direct"
    MessageTypeBroadcast MessageType = "broadcast"
    MessageTypeReply     MessageType = "reply"
    MessageTypeVote      MessageType = "vote"
    MessageTypeTask      MessageType = "task"
)
```

## Agent Group

```go
type AgentGroup struct {
    ID        string
    Name      string
    Agents    map[string]*Agent
    State     *GroupState
    Transport MessageTransport
    Election  LeaderElection
}

type GroupState struct {
    CRDT      *CRDTState
    Version   int64
    Timestamp time.Time
}

type MessageTransport interface {
    Send(msg *Message) error
    Subscribe(subject string, handler MessageHandler) error
    Broadcast(msg *Message) error
}

type LeaderElection interface {
    Elect() (*Agent, error)
    Vote(agentID string) error
    GetLeader() (*Agent, error)
}
```

## Task Decomposition

```go
type Task struct {
    ID          string
    Description string
    ParentID    string
    Subtasks    []*Task
    AssignedTo  string
    Status      TaskStatus
    Priority    int
    Deadline    *time.Time
}

type TaskStatus string

const (
    TaskPending    TaskStatus = "pending"
    TaskInProgress TaskStatus = "in_progress"
    TaskCompleted  TaskStatus = "completed"
    TaskFailed     TaskStatus = "failed"
    TaskCancelled  TaskStatus = "cancelled"
)

type TaskPlanner interface {
    Decompose(task *Task) ([]*Task, error)
    Schedule(tasks []*Task) ([]*Task, error)
    Assign(tasks []*Task, agents []*Agent) error
}
```

## Agent Capabilities

| Type | Role | Capabilities | Use Case |
|------|------|--------------|----------|
| **orchestrator** | Meta-agent coordination | Planning, delegation, monitoring | Multi-agent workflows |
| **executor** | Task execution | Tools, API calls, code execution | Action-oriented tasks |
| **advisor** | Consultation and review | Analysis, recommendations | Review and guidance |
| **memory** | Context and knowledge | Retrieval, summarization | Knowledge management |

## Consensus Protocol

```go
type Consensus interface {
    Propose(value interface{}) error
    Vote(proposalID string, vote Vote) error
    Decide(proposalID string) (interface{}, error)
}

type Vote struct {
    AgentID  string
    ProposalID string
    Value    bool
    Reason   string
}
```

## Usage Examples

### Creating an Agent

```python
from thegent import Agent, AgentGroup

# Create agent group
group = AgentGroup(name="development-team")

# Create orchestrator agent
orchestrator = Agent(
    name="lead-dev",
    type="orchestrator",
    skills=["planning", "delegation", "code-review"]
)

# Create executor agent
executor = Agent(
    name="coder-1",
    type="executor",
    skills=["python", "rust", "typescript"]
)

# Add to group
group.add(orchestrator)
group.add(executor)
```

### Task Execution

```python
# Create complex task
task = Task(
    description="Implement user authentication",
    priority=1,
    deadline="2026-06-01"
)

# Decompose into subtasks
subtasks = orchestrator.plan(task)
# ["Design auth schema", "Implement login API", "Add JWT tokens", "Write tests"]

# Execute with monitoring
for subtask in subtasks:
    result = executor.execute(subtask)
    if result.status == "failed":
        orchestrator.replan(subtask)
```

### Inter-Agent Communication

```python
# Direct message
orchestrator.send_to(
    to="coder-1",
    message="Please review the auth implementation"
)

# Broadcast to group
orchestrator.broadcast(
    message="Sprint planning starting in 5 minutes"
)

# Pub/sub pattern
executor.subscribe("code-review-requests", handler)
```

## Integration Points

| System | Integration | Status |
|--------|-------------|--------|
| **phenotype-agent-core** | LLM provider abstraction | Stable |
| **phenotype-skills** | Skill marketplace | Stable |
| **phenotype-task-engine** | Task execution backend | Stable |
| **pheno-cli** | Command interface | In Progress |
| **phenotype-hub** | Team coordination | Planned |

## References

- [Multi-Agent Systems](https://en.wikipedia.org/wiki/Multi-agent_system) - Academic background
- [Actor Model](https://en.wikipedia.org/wiki/Actor_model) - Concurrency foundation
- [CRDTs](https://en.wikipedia.org/wiki/Conflict-free_replicated_data_type) - Distributed state
- [Paxos/Raft](https://raft.github.io/) - Consensus algorithms
