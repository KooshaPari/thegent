# ADR-006: Event-Driven Architecture

**Date**: 2026-04-05  
**Status**: Accepted  
**Deciders**: Agent  

## Context

thegent needs to coordinate multiple agents, track task execution, and provide real-time feedback to users. Traditional request-response patterns don't scale well for multi-agent workflows. We need an event-driven architecture to handle:

1. Agent-to-agent communication
2. Task state transitions
3. Sandbox lifecycle events
4. Audit logging for compliance
5. Real-time UI updates

## Decision Drivers

- **Scalability**: Support 100+ concurrent agents
- **Latency**: Event propagation <50ms
- **Reliability**: No lost events (at-least-once delivery)
- **Debuggability**: Full event tracing for troubleshooting
- **Integration**: Connect to external systems (webhooks, etc.)

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Event Bus (NATS)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Publishers:                     Subscribers:                   │
│   ┌──────────────┐               ┌──────────────┐               │
│   │ Agent Core  │───────────────│ Orchestrator │               │
│   └──────────────┘               └──────────────┘               │
│   ┌──────────────┐               ┌──────────────┐               │
│   │Task Service │───────────────│  UI/TUI     │               │
│   └──────────────┘               └──────────────┘               │
│   ┌──────────────┐               ┌──────────────┐               │
│   │  Sandbox    │───────────────│  Audit Log  │               │
│   └──────────────┘               └──────────────┘               │
│   ┌──────────────┐               ┌──────────────┐               │
│   │ Tenant Svc  │───────────────│ Metrics     │               │
│   └──────────────┘               └──────────────┘               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Event Schema

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "type", content = "data")]
pub enum DomainEvent {
    // Agent events
    AgentCreated {
        agent_id: String,
        role: String,
        timestamp: DateTime<Utc>,
    },
    AgentStarted {
        agent_id: String,
        task_id: String,
    },
    AgentCompleted {
        agent_id: String,
        task_id: String,
        duration_ms: u64,
    },
    AgentFailed {
        agent_id: String,
        task_id: String,
        error: String,
    },
    
    // Task events
    TaskCreated {
        task_id: String,
        description: String,
        priority: u8,
    },
    TaskAssigned {
        task_id: String,
        agent_id: String,
    },
    TaskStarted {
        task_id: String,
        sandbox_id: String,
    },
    TaskProgress {
        task_id: String,
        step: usize,
        total: usize,
    },
    TaskCompleted {
        task_id: String,
        output: Value,
    },
    TaskFailed {
        task_id: String,
        error: String,
    },
    
    // Sandbox events
    SandboxCreated {
        sandbox_id: String,
        tier: SandboxTier,
        tenant_id: Option<u64>,
    },
    SandboxDestroyed {
        sandbox_id: String,
        reason: String,
        duration_ms: u64,
    },
    SandboxError {
        sandbox_id: String,
        error: String,
    },
    
    // Tenant events
    TenantCreated {
        tenant_id: u64,
        name: String,
    },
    TenantDeleted {
        tenant_id: u64,
    },
    TenantQuotaExceeded {
        tenant_id: u64,
        resource: String,
    },
    
    // Trust events
    TrustEvaluation {
        source: String,
        level: TrustLevel,
        tier: SandboxTier,
    },
    TrustOverride {
        source: String,
        overridden_by: String,
        original_tier: SandboxTier,
        new_tier: SandboxTier,
    },
}
```

## Event Bus Configuration

```toml
[event_bus]
# NATS configuration
url = "nats://localhost:4222"
name = "thegent"
description = "thegent event bus"

# JetStream for persistence
enable_jetstream = true
stream_name = "thegent"
storage = "file"  # or "memory"
retention = "limits"  # or "interest" or "workqueue"

# Consumer groups
[event_bus.consumers.orchestrator]
durable = true
deliver_policy = "all"  # or "last", "new"
max_ack_pending = 100

[event_bus.consumers.audit]
durable = true
deliver_policy = "all"
max_ack_pending = 1000

[event_bus.consumers.ui]
durable = false  # Ephemeral for real-time updates
deliver_policy = "new"
```

## Event Flow Examples

### Task Execution Flow

```
1. User submits task
   → TaskService publishes: TaskCreated { task_id, description }

2. Orchestrator receives task
   → Orchestrator publishes: TaskAssigned { task_id, agent_id }

3. Agent starts execution
   → Agent publishes: AgentStarted { agent_id, task_id }
   → Sandbox publishes: SandboxCreated { sandbox_id, tier }

4. Task progresses
   → Agent publishes: TaskProgress { task_id, step, total }

5. Task completes
   → Agent publishes: AgentCompleted { agent_id, task_id, duration_ms }
   → Sandbox publishes: SandboxDestroyed { sandbox_id, reason }
   → TaskService publishes: TaskCompleted { task_id, output }
```

### Trust Override Flow

```
1. User executes with override
   → TrustEvaluator publishes: TrustOverride { source, overridden_by, ... }

2. Script executes
   → All normal events follow...

3. Audit consumer records override
   → AuditLog appends: { event: "trust_override", ... }
```

## Subscribers and Filters

```rust
pub struct EventSubscriber {
    pub name: String,
    pub topics: Vec<String>,  // e.g., "task.*", "agent.created"
    pub filter: Option<Box<dyn Filter>>,
    pub handler: Box<dyn EventHandler>,
}

impl EventSubscriber {
    pub fn new(name: &str) -> Self {
        Self {
            name: name.to_string(),
            topics: Vec::new(),
            filter: None,
            handler: Box::new(DefaultHandler),
        }
    }
    
    pub fn subscribe_to(&mut self, topic: &str) -> &mut Self {
        self.topics.push(topic.to_string());
        self
    }
    
    pub fn with_filter<F: Filter + 'static>(&mut self, filter: F) -> &mut Self {
        self.filter = Some(Box::new(filter));
        self
    }
}

// Pre-configured subscribers
pub fn standard_subscribers() -> Vec<EventSubscriber> {
    vec![
        // Orchestrator handles all task/agent events
        EventSubscriber::new("orchestrator")
            .subscribe_to("task.*")
            .subscribe_to("agent.*"),
        
        // UI gets real-time updates (no persistence)
        EventSubscriber::new("ui")
            .subscribe_to("task.progress")
            .subscribe_to("agent.*")
            .subscribe_to("sandbox.error"),
        
        // Audit logs everything
        EventSubscriber::new("audit")
            .subscribe_to("*"),  // Wildcard for full audit
        
        // Metrics collects for monitoring
        EventSubscriber::new("metrics")
            .subscribe_to("task.completed")
            .subscribe_to("task.failed")
            .subscribe_to("sandbox.*"),
    ]
}
```

## Consequences

### Positive
- **Decoupling**: Agents don't need to know about each other
- **Scalability**: Add subscribers without modifying publishers
- **Debuggability**: Full event log for tracing issues
- **Real-time**: UI updates without polling
- **Integration**: Easy to add webhooks/external consumers

### Negative
- **Complexity**: More moving parts than direct calls
- **Ordering**: Events may arrive out of order
- **Debugging**: Tracing across services requires tooling
- **Latency**: Event propagation adds ~5ms

## Implementation Notes

### Phase 1: Core Event Bus
- Deploy NATS locally for development
- Implement basic publish/subscribe
- Add structured logging fallback

### Phase 2: Event Persistence
- Enable JetStream for durability
- Implement dead letter queue
- Add event replay capability

### Phase 3: Production Features
- Multi-region replication
- Event sourcing for aggregates
- Correlation ID propagation

## References

- NATS: https://nats.io/
- JetStream: https://docs.nats.io/nats-concepts/jetstream
- Event Sourcing: https://martinfowler.com/eaaDev/EventSourcing.html
- CQRS: https://martinfowler.com/articles/cqrs.html

---

*This ADR will be updated as implementation progresses*
