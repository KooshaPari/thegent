# ADR-008: API Design and Protocol Strategy

**Date**: 2026-04-05  
**Status**: Accepted  
**Deciders**: Agent  

## Context

thegent needs to expose its functionality to multiple consumers:
1. CLI tool for local users
2. TUI for interactive sessions
3. MCP (Model Context Protocol) server for AI integration
4. REST API for programmatic access
5. WebSocket for real-time updates

We need a unified API design that supports all these use cases while maintaining consistency and type safety.

## Decision Drivers

- **Type Safety**: Compile-time verification of API contracts
- **Discoverability**: Clear schema for tooling
- **Flexibility**: Support multiple protocols (HTTP, WebSocket, stdio)
- **Performance**: Low latency for local operations
- **Extensibility**: Easy to add new endpoints

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         API Layer                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐│
│   │   CLI       │  │   TUI       │  │   MCP Server           ││
│   │  (stdio)    │  │ (Crossterm) │  │  (JSON-RPC 2.0)        ││
│   └──────┬──────┘  └──────┬──────┘  └───────────┬─────────────┘│
│          │                 │                      │               │
│          └─────────────────┴──────────────────────┘               │
│                            │                                      │
│   ┌────────────────────────▼────────────────────────────────────┐│
│   │                    Service Layer                              ││
│   │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ││
│   │  │  Agent   │  │   Task   │  │ Sandbox  │  │ Tenant   │  ││
│   │  │ Service  │  │ Service  │  │ Service  │  │ Service  │  ││
│   │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  ││
│   └────────────────────────────────────────────────────────────┘│
│                            │                                      │
│   ┌────────────────────────▼────────────────────────────────────┐│
│   │                 Infrastructure Layer                         ││
│   │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ││
│   │  │ Database │  │ EventBus │  │ Sandbox  │  │   LLM    │  ││
│   │  │(SQLite)  │  │  (NATS)  │  │Adapters │  │ Adapters │  ││
│   │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  ││
│   └────────────────────────────────────────────────────────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Protocol Support

### MCP (Model Context Protocol) - Primary

```json
// MCP request/response format
{
  "jsonrpc": "2.0",
  "id": "unique-id",
  "method": "tools/call",
  "params": {
    "name": "agent_execute",
    "arguments": {
      "agent_id": "installer",
      "task": "install neovim",
      "tier": "bubblewrap"
    }
  }
}
```

```json
// MCP response
{
  "jsonrpc": "2.0",
  "id": "unique-id",
  "result": {
    "success": true,
    "output": "Neovim installed successfully",
    "duration_ms": 234,
    "tier_used": "bubblewrap"
  }
}
```

### REST API - Secondary

```yaml
openapi: 3.0.0
info:
  title: thegent API
  version: 1.0.0
paths:
  /api/v1/agents:
    get:
      summary: List all agents
      responses:
        '200':
          description: List of agents
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Agent'
    post:
      summary: Create new agent
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateAgent'
      responses:
        '201':
          description: Agent created

  /api/v1/tasks:
    post:
      summary: Execute task
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ExecuteTask'
      responses:
        '202':
          description: Task queued
```

### WebSocket - Real-time

```typescript
// WebSocket messages
interface WSMessage {
  type: 'event' | 'request' | 'response';
  channel: string;
  payload: unknown;
}

// Subscribe to agent events
{ type: 'subscribe', channel: 'agent.*' }

// Receive events
{ type: 'event', channel: 'agent.started', payload: { agent_id: '...', task_id: '...' } }
```

## Core API Models

```rust
// Agent operations
#[derive(Debug, Serialize, Deserialize)]
pub struct Agent {
    pub id: AgentId,
    pub name: String,
    pub role: Role,
    pub goal: String,
    pub status: AgentStatus,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Serialize, Deserialize)]
pub enum AgentStatus {
    Idle,
    Planning { task_id: TaskId },
    Executing { task_id: TaskId },
    AwaitingInput { prompt: String },
    Completed { output: String },
    Failed { error: String },
}

// Task operations
#[derive(Debug, Serialize, Deserialize)]
pub struct Task {
    pub id: TaskId,
    pub description: String,
    pub expected_output: String,
    pub agent_id: Option<AgentId>,
    pub status: TaskStatus,
    pub sandbox_tier: SandboxTier,
    pub priority: u8,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ExecuteTaskRequest {
    pub description: String,
    pub expected_output: Option<String>,
    pub agent_id: Option<AgentId>,
    pub tier: Option<SandboxTier>,
    pub timeout_seconds: Option<u64>,
}

// Sandbox operations
#[derive(Debug, Serialize, Deserialize)]
pub struct Sandbox {
    pub id: SandboxId,
    pub tier: SandboxTier,
    pub status: SandboxStatus,
    pub tenant_id: Option<u64>,
}

#[derive(Debug, Serialize, Deserialize)]
pub enum SandboxStatus {
    Creating,
    Ready,
    Executing,
    Destroying,
    Destroyed,
    Error { message: String },
}
```

## API Endpoints

```rust
// MCP tool definitions
pub fn register_mcp_tools(mcp: &mut McpServer) {
    
    // Agent tools
    mcp.register_tool("agent_create", |params: CreateAgentParams| async move {
        let agent = agent_service::create(params.name, params.role, params.goal)
            .await?;
        Ok(serde_json::to_value(agent)?)
    });
    
    mcp.register_tool("agent_list", |_params: Empty| async move {
        let agents = agent_service::list().await?;
        Ok(serde_json::to_value(agents)?)
    });
    
    mcp.register_tool("agent_execute", |params: ExecuteTaskParams| async move {
        let result = agent_service::execute(params.agent_id, params.task, params.tier)
            .await?;
        Ok(serde_json::to_value(result)?)
    });
    
    // Sandbox tools
    mcp.register_tool("sandbox_create", |params: CreateSandboxParams| async move {
        let sandbox = sandbox_service::create(params.tier, params.config)
            .await?;
        Ok(serde_json::to_value(sandbox)?)
    });
    
    mcp.register_tool("sandbox_execute", |params: ExecuteInSandboxParams| async move {
        let result = sandbox_service::execute(params.sandbox_id, params.command)
            .await?;
        Ok(serde_json::to_value(result)?)
    });
    
    // Tenant tools
    mcp.register_tool("tenant_create", |params: CreateTenantParams| async move {
        let tenant = tenant_service::create(params.name, params.quota)
            .await?;
        Ok(serde_json::to_value(tenant)?)
    });
}
```

## Error Handling

```rust
#[derive(Debug, Serialize, Deserialize)]
pub struct ApiError {
    pub code: ErrorCode,
    pub message: String,
    pub details: Option<Value>,
    pub request_id: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub enum ErrorCode {
    // 4xx Client errors
    ValidationError,
    NotFound,
    AlreadyExists,
    PermissionDenied,
    RateLimited,
    
    // 5xx Server errors
    InternalError,
    SandboxError,
    AgentError,
    Timeout,
    Unavailable,
}

impl ApiError {
    pub fn new(code: ErrorCode, message: &str) -> Self {
        Self {
            code,
            message: message.to_string(),
            details: None,
            request_id: Uuid::new_v4().to_string(),
        }
    }
    
    pub fn with_details(mut self, details: Value) -> Self {
        self.details = Some(details);
        self
    }
}
```

## Consequences

### Positive
- **Unified**: Single API surface for all protocols
- **Type-safe**: Rust types compile-verified
- **Discoverable**: MCP schema for AI tooling
- **Extensible**: Easy to add new endpoints

### Negative
- **Complexity**: Multiple protocols to maintain
- **Versioning**: API changes require migration
- **Documentation**: Must keep docs in sync

## References

- MCP specification: https://modelcontextprotocol.io/
- OpenAPI 3.0: https://spec.openapis.org/oas/v3.0.3
- JSON-RPC 2.0: https://www.jsonrpc.org/specification
- REST maturity model: https://martinfowler.com/articles/richardsonMaturityModel.html

---

*This ADR will be updated as implementation progresses*
