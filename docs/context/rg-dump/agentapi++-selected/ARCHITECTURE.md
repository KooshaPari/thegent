# atomsAgent Architecture

## System Overview

atomsAgent is a FastAPI-based service that provides an OpenAI-compatible interface to Claude models on Vertex AI, with multi-level prompt orchestration and MCP server integration.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Applications                      │
│  (OpenAI SDK, curl, custom clients, etc.)                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Server                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ API Routes Layer                                     │  │
│  │ ├─ /v1/chat/completions (OpenAI-compatible)        │  │
│  │ ├─ /atoms/mcp/* (MCP management)                   │  │
│  │ └─ /atoms/platform/* (Admin)                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                   │
│  ┌──────────────────────▼──────────────────────────────┐  │
│  │ Services Layer                                       │  │
│  │ ├─ Claude Client (Vertex AI wrapper)               │  │
│  │ ├─ Prompt Orchestrator (hierarchy resolution)      │  │
│  │ ├─ MCP Integration (server composition)            │  │
│  │ └─ Chat History Manager (session tracking)         │  │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                   │
│  ┌──────────────────────▼──────────────────────────────┐  │
│  │ Data Layer                                           │  │
│  │ ├─ Supabase Database (models, sessions, prompts)   │  │
│  │ └─ Repositories (CRUD operations)                  │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Vertex AI    │  │ Supabase     │  │ MCP Servers  │
│ (Claude)     │  │ (Database)   │  │ (HTTP-based) │
└──────────────┘  └──────────────┘  └──────────────┘
```

## Component Responsibilities

### API Routes Layer
**Location:** `src/atomsAgent/api/routes/`

**Responsibilities:**
- Handle HTTP requests
- Validate input
- Call appropriate services
- Format responses
- Stream responses (SSE)

**Key Routes:**
- `openai.py` - OpenAI-compatible chat completion endpoints
- `mcp.py` - MCP server registration and management
- `platform.py` - Platform admin endpoints

### Services Layer
**Location:** `src/atomsAgent/services/`

**Responsibilities:**
- Business logic
- Orchestration
- Integration with external services
- Caching and optimization

**Key Services:**
- `claude_client.py` - Wrapper around Vertex AI Claude API
- `prompts.py` - Multi-level prompt resolution
- `mcp_registry.py` - MCP server registry and composition
- `chat_history.py` - Session and message management

### Data Layer
**Location:** `src/atomsAgent/db/`

**Responsibilities:**
- Database access
- Model definitions
- CRUD operations
- Query optimization

**Key Components:**
- `models.py` - Pydantic models wrapping Supabase tables
- `repositories/` - Repository pattern for CRUD operations

### MCP Integration
**Location:** `src/atomsAgent/mcp/`

**Responsibilities:**
- MCP server composition
- Tool discovery and execution
- OAuth handling
- Error handling

## Data Flow

### Chat Completion Request Flow

```
1. Client sends POST /v1/chat/completions
   ├─ Headers: Authorization, Content-Type
   └─ Body: model, messages, stream, etc.

2. API Route Handler (openai.py)
   ├─ Validate request
   ├─ Extract user from JWT
   └─ Call ChatCompletionService

3. Services Layer
   ├─ Resolve multi-level prompt
   │  └─ Platform → Org → User → Workflow
   ├─ Compose MCP servers (if configured)
   ├─ Call Claude via Vertex AI
   └─ Stream or return response

4. Claude Response
   ├─ Tool calls (if any)
   ├─ Execute tools via MCP
   ├─ Continue conversation
   └─ Return final response

5. Response to Client
   ├─ Stream: Server-Sent Events (SSE)
   └─ Non-stream: JSON response
```

### Prompt Resolution Flow

```
Request for prompt:
  platform_id=plat_123
  org_id=org_456
  user_id=user_789
  workflow_id=wf_abc

Resolution order:
  1. Check cache (5 min TTL)
  2. Query workflow-level prompt
     └─ If found, return (most specific)
  3. Query user-level prompt
     └─ If found, return
  4. Query org-level prompt
     └─ If found, return
  5. Query platform-level prompt
     └─ If found, return (fallback)
  6. Cache result
  7. Return resolved prompt
```

### MCP Server Composition Flow

```
1. Client registers MCP servers
   ├─ Server URL
   ├─ OAuth credentials (if needed)
   └─ Tool approval settings

2. MCP Integration discovers tools
   ├─ Call /mcp/tools endpoint
   ├─ Parse tool definitions
   └─ Cache tool list

3. During chat completion
   ├─ Claude decides to use tool
   ├─ MCP Integration executes tool
   │  ├─ Call /mcp/call endpoint
   │  ├─ Pass tool name and arguments
   │  └─ Get result
   ├─ Return result to Claude
   └─ Continue conversation

4. Final response sent to client
```

## Key Design Decisions

### 1. OpenAI-Compatible API
**Decision:** Implement OpenAI API specification
**Rationale:**
- Drop-in replacement for existing OpenAI integrations
- Familiar to developers
- Reduces migration effort
- Enables use of OpenAI SDKs

### 2. Multi-Level Prompt Orchestration
**Decision:** Implement hierarchy: Platform → Org → User → Workflow
**Rationale:**
- Flexible prompt management
- Supports different use cases
- Allows customization at multiple levels
- Fallback mechanism ensures always have a prompt

### 3. MCP Server Integration
**Decision:** Support HTTP-based MCP servers
**Rationale:**
- Flexible tool integration
- Supports multiple tool providers
- OAuth support for security
- Composable architecture

### 4. Supabase for Database
**Decision:** Use Supabase (PostgreSQL + Auth)
**Rationale:**
- Managed PostgreSQL
- Built-in authentication
- Real-time capabilities
- Easy to scale

### 5. Vertex AI for Claude
**Decision:** Use Google Vertex AI for Claude access
**Rationale:**
- Managed service
- Integrated with Google Cloud
- Reliable and scalable
- Cost-effective

## Scalability Considerations

### Horizontal Scaling
- Stateless API servers (can run multiple instances)
- Load balancer distributes requests
- Database connection pooling
- Cache layer for prompt resolution

### Vertical Scaling
- Async/await for I/O operations
- Connection pooling
- Caching strategies
- Efficient database queries

### Performance Optimization
- Prompt caching (5 min TTL)
- MCP tool list caching
- Database query optimization
- Connection pooling

## Security Architecture

### Authentication
- JWT tokens from WorkOS
- Token validation on every request
- User and organization isolation

### Authorization
- User can only access their own data
- Organization isolation
- Admin endpoints require special permissions

### Data Protection
- Secrets stored in environment variables
- OAuth tokens encrypted in database
- HTTPS for all external communication
- Input validation on all endpoints

## Error Handling

### API Errors
- Validation errors (400)
- Authentication errors (401)
- Authorization errors (403)
- Rate limit errors (429)
- Server errors (500)

### Service Errors
- Claude API errors (retry with backoff)
- MCP server errors (graceful degradation)
- Database errors (transaction rollback)

### Logging
- Request/response logging
- Error logging with stack traces
- Performance metrics
- Audit logging for sensitive operations

## Deployment Architecture

```
┌─────────────────────────────────────────┐
│         Load Balancer                   │
│         (Cloud Load Balancer)           │
└────────────────┬────────────────────────┘
                 │
    ┌────────────┼────────────┐
    ▼            ▼            ▼
┌────────┐  ┌────────┐  ┌────────┐
│ Server │  │ Server │  │ Server │
│ Pod 1  │  │ Pod 2  │  │ Pod 3  │
└────────┘  └────────┘  └────────┘
    │            │            │
    └────────────┼────────────┘
                 │
         ┌───────▼────────┐
         │  Supabase      │
         │  (PostgreSQL)  │
         └────────────────┘
```

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **API** | FastAPI | Web framework |
| **Async** | asyncio | Async I/O |
| **Database** | Supabase/PostgreSQL | Data storage |
| **ORM** | SQLAlchemy | Database access |
| **Auth** | WorkOS | Authentication |
| **Claude** | Vertex AI | LLM access |
| **MCP** | HTTP | Tool integration |
| **Validation** | Pydantic | Input validation |
| **Testing** | pytest | Unit testing |
| **Linting** | ruff | Code quality |
| **Type Checking** | mypy | Type safety |

## Related Documentation

- **[README.md](./README.md)** - Project overview
- **[DEVELOPMENT.md](./DEVELOPMENT.md)** - Development setup
- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Deployment procedures
- **[API_REFERENCE.md](./API_REFERENCE.md)** - API documentation

---

**Last Updated:** 2025-11-23
**Version:** 1.0

