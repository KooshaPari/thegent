# Model Context Protocol (MCP) Context

> Definitive reference for implementing and using Model Context Protocol in thegent.
> Sources: modelcontextprotocol.io specification, official documentation (fetched 2026-02-20).

---

## What is MCP

The Model Context Protocol (MCP) is a standardized protocol that enables AI models and applications to access tools, data, and capabilities from external systems. It defines how clients (AI applications like Claude, Gemini) connect to servers (tools, APIs, databases) and request execution of operations or retrieval of information.

Key characteristics:
- **Standardized**: JSON-RPC 2.0 message format, shared across providers
- **Bidirectional**: Both model-to-server and server-to-client communication
- **Extensible**: Tools, resources, prompts, sampling, and more
- **Transport-agnostic**: STDIO, SSE, Streamable HTTP, or custom transports
- **Multi-capability**: Tools (side effects), Resources (read-only data), Prompts (templates), Sampling (model control)
- **Recent**: Latest spec version 2025-11-25
- **Growing ecosystem**: Hugging Face, Vercel, local inference providers, many open-source servers

---

## Architecture

### Conceptual Model

```
┌─────────────────────────────────────┐
│  AI Host (Client)                   │
│  - Claude                           │
│  - Gemini CLI                       │
│  - thegent / LLM Application        │
└────────────────┬────────────────────┘
                 │ JSON-RPC 2.0
                 │
    ┌────────────┴────────────┐
    │                         │
┌───▼──────────────┐  ┌──────▼──────────┐
│ MCP Server 1     │  │ MCP Server 2    │
│ - Tools          │  │ - Resources     │
│ - Resources      │  │ - Tools         │
│ - Prompts        │  │ - Prompts       │
└──────────────────┘  └─────────────────┘
```

### Components

| Component | Role | Example |
|-----------|------|---------|
| **Host** | AI application, client | Claude, Gemini CLI, thegent |
| **Client** | Connects to servers | MCP client library |
| **Server** | Provides tools/resources | FastMCP server, local tool server |
| **Transport** | Message delivery mechanism | STDIO, SSE, HTTP |

---

## Message Format (JSON-RPC 2.0)

All MCP communication uses JSON-RPC 2.0, which defines three message types:

### Request

A message that requires a response:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list",
  "params": {}
}
```

### Response

Successful reply to a request:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {
        "name": "get_weather",
        "description": "Get weather for a location",
        "inputSchema": {...}
      }
    ]
  }
}
```

### Error Response

Failed request:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32600,
    "message": "Invalid Request"
  }
}
```

### Notification

One-way message, no response expected:

```json
{
  "jsonrpc": "2.0",
  "method": "notification/example",
  "params": {}
}
```

---

## Transport Protocols

### STDIO Transport

Direct communication via child process stdin/stdout.

**Setup**: Host spawns MCP server as subprocess:

```python
import subprocess
import json

process = subprocess.Popen(
    ["python", "mcp_server.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Send request
request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2025-11-25",
        "capabilities": {},
        "clientInfo": {"name": "thegent", "version": "1.0"}
    }
}

process.stdin.write(json.dumps(request) + "\n")
process.stdin.flush()

# Read response
response_line = process.stdout.readline()
response = json.loads(response_line)
```

**Advantages**:
- Simple, no network setup
- Built-in process isolation
- Direct stdout/stderr communication

**Disadvantages**:
- Local only
- Single connection per process

### SSE (Server-Sent Events) Transport

HTTP-based streaming for remote servers:

```bash
# Start SSE server on localhost:3000
curl -X POST http://localhost:3000/sse/initialize \
  -H "Content-Type: application/json" \
  -d '{
    "protocolVersion": "2025-11-25",
    "capabilities": {},
    "clientInfo": {"name": "thegent"}
  }'

# Server responds with stream of events
event: server.ready
data: {"status": "initialized"}

# Client sends requests
event: tools/list
data: {}
```

**Advantages**:
- Remote server access
- Browser-compatible
- Bi-directional streaming

**Disadvantages**:
- Network latency
- Requires HTTP server

### Streamable HTTP Transport

Modern HTTP with bi-directional streaming:

```
POST /mcp HTTP/1.1
Content-Type: application/octet-stream

[request frames as binary or JSON]
```

**Advantages**:
- Efficient, multiplexed
- Works with proxies
- Supports both directions

---

## Initialization Handshake

Every MCP connection begins with initialization:

### Client Sends Initialize Request

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-11-25",
    "capabilities": {
      "roots": {
        "listChanged": true
      },
      "sampling": {}
    },
    "clientInfo": {
      "name": "thegent",
      "version": "1.0.0"
    }
  }
}
```

### Server Responds with Capabilities

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2025-11-25",
    "capabilities": {
      "tools": {},
      "resources": {},
      "prompts": {},
      "logging": {}
    },
    "serverInfo": {
      "name": "my-mcp-server",
      "version": "1.0"
    },
    "instructions": "Server usage instructions..."
  }
}
```

### Client Acknowledges with Initialized Notification

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/initialized",
  "params": {}
}
```

---

## Core Capabilities

### Tools

Functions the model can call to perform actions (side effects).

#### Listing Tools

**Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list",
  "params": {}
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "tools": [
      {
        "name": "get_weather",
        "description": "Get current weather for a location",
        "inputSchema": {
          "type": "object",
          "properties": {
            "location": {
              "type": "string",
              "description": "City name or coordinates"
            },
            "unit": {
              "type": "string",
              "enum": ["celsius", "fahrenheit"],
              "default": "celsius"
            }
          },
          "required": ["location"]
        }
      },
      {
        "name": "send_email",
        "description": "Send an email message",
        "inputSchema": {
          "type": "object",
          "properties": {
            "to": { "type": "string" },
            "subject": { "type": "string" },
            "body": { "type": "string" }
          },
          "required": ["to", "subject", "body"]
        }
      }
    ]
  }
}
```

#### Calling a Tool

**Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "get_weather",
    "arguments": {
      "location": "San Francisco",
      "unit": "fahrenheit"
    }
  }
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Current weather in San Francisco: 65°F, partly cloudy"
      }
    ],
    "isError": false
  }
}
```

### Resources

Read-only data sources that the model can query.

#### Listing Resources

**Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "resources/list",
  "params": {}
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "result": {
    "resources": [
      {
        "uri": "file:///data/customer_db.csv",
        "name": "Customer Database",
        "description": "Customer records and preferences",
        "mimeType": "text/csv"
      },
      {
        "uri": "sqlite:///knowledge.db",
        "name": "Knowledge Base",
        "description": "Company policies and procedures",
        "mimeType": "application/json"
      }
    ]
  }
}
```

#### Reading a Resource

**Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "method": "resources/read",
  "params": {
    "uri": "file:///data/customer_db.csv"
  }
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "result": {
    "contents": [
      {
        "uri": "file:///data/customer_db.csv",
        "mimeType": "text/csv",
        "text": "id,name,email\n1,Alice,alice@example.com\n2,Bob,bob@example.com\n..."
      }
    ]
  }
}
```

### Prompts

Reusable prompt templates and workflows for standardizing interactions.

#### Listing Prompts

**Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 6,
  "method": "prompts/list",
  "params": {}
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 6,
  "result": {
    "prompts": [
      {
        "name": "code_review",
        "description": "Code review prompt template",
        "arguments": [
          {
            "name": "code",
            "description": "Code to review"
          },
          {
            "name": "language",
            "description": "Programming language"
          }
        ]
      }
    ]
  }
}
```

#### Getting a Prompt

**Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 7,
  "method": "prompts/get",
  "params": {
    "name": "code_review",
    "arguments": {
      "code": "def add(a, b):\n    return a + b",
      "language": "python"
    }
  }
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 7,
  "result": {
    "messages": [
      {
        "role": "user",
        "content": "Review the following Python code for best practices:\n\ndef add(a, b):\n    return a + b"
      }
    ]
  }
}
```

### Sampling (Reverse)

Server can request the AI model to generate text (model-in-the-loop):

**Request** (from server to host):
```json
{
  "jsonrpc": "2.0",
  "id": 8,
  "method": "sampling/createMessage",
  "params": {
    "messages": [
      {
        "role": "user",
        "content": "Generate a test case for this function"
      }
    ],
    "modelPreferences": {
      "costPriority": 1,
      "latencyPriority": 50,
      "intelligencePriority": 25
    },
    "systemPrompt": "You are a test engineer..."
  }
}
```

**Response** (from host to server):
```json
{
  "jsonrpc": "2.0",
  "id": 8,
  "result": {
    "content": {
      "type": "text",
      "text": "def test_add():\n    assert add(2, 3) == 5\n    assert add(-1, 1) == 0"
    },
    "model": "gpt-4o",
    "stopReason": "end_turn",
    "usage": {
      "inputTokens": 50,
      "outputTokens": 30
    }
  }
}
```

---

## Python SDK (Official)

### Server Implementation (FastMCP)

```python
from mcp.server.fastmcp import FastMCP

server = FastMCP("my-server")

# Define a tool
@server.tool()
def get_weather(location: str, unit: str = "celsius") -> str:
    """Get weather for a location."""
    # Implementation
    return f"Weather in {location}: 20°C"

# Define a resource
@server.resource("file:///knowledge.db")
def knowledge_db() -> str:
    """Read knowledge database."""
    with open("/path/to/knowledge.db") as f:
        return f.read()

# Define a prompt
@server.prompt()
def code_review(code: str, language: str) -> list:
    """Code review prompt template."""
    return [
        {
            "role": "user",
            "content": f"Review this {language} code:\n{code}"
        }
    ]

# Run server
if __name__ == "__main__":
    server.run()
```

### Client Usage

```python
import asyncio
from mcp.client import StdioClient

async def main():
    # Connect to STDIO-based server
    client = StdioClient(["python", "mcp_server.py"])

    # Initialize
    await client.initialize()

    # List tools
    tools = await client.list_tools()
    print(f"Available tools: {[t.name for t in tools]}")

    # Call a tool
    result = await client.call_tool("get_weather", {"location": "NYC"})
    print(f"Result: {result.text}")

    # List resources
    resources = await client.list_resources()
    for resource in resources:
        print(f"Resource: {resource.uri}")

    # Read a resource
    content = await client.read_resource("file:///knowledge.db")
    print(f"Content: {content.text}")
```

---

## Schema Definition

### Tool Input Schema

Tools use JSON Schema for input validation:

```json
{
  "name": "database_query",
  "description": "Execute SQL query",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "SQL SELECT query"
      },
      "timeout": {
        "type": "integer",
        "minimum": 1,
        "maximum": 300,
        "description": "Query timeout in seconds"
      }
    },
    "required": ["query"]
  }
}
```

### Accepted Types

```
- string
- number
- integer
- boolean
- array
- object
- null
```

---

## Thegent Integration

MCP servers integrate into thegent in three ways:

### 1. Direct Tool Registration

```python
# In thegent's MCPToolRegistry
class MCPToolRegistry:
    def register_server(self, server_config: dict):
        """Register MCP server and expose its tools."""
        transport = server_config.get("transport", "stdio")

        if transport == "stdio":
            client = StdioClient(server_config["command"])
        elif transport == "sse":
            client = SSEClient(server_config["url"])

        # Auto-register all tools from server
        tools = await client.list_tools()
        for tool in tools:
            self.register_tool(tool.name, client.call_tool)
```

### 2. Gemini CLI MCP Support

Configured in `~/.gemini/config`:

```yaml
mcp:
  servers:
    - name: custom-tools
      command: python /path/to/mcp_server.py
      transport: stdio
    - name: web-tools
      url: http://localhost:3000
      transport: sse
```

### 3. Responses API MCP Integration

```json
{
  "model": "gpt-4o",
  "input": {"type": "message", "content": "..."},
  "tools": [
    {
      "type": "mcp",
      "server": {
        "type": "stdio",
        "command": "python /path/to/mcp_server.py"
      }
    }
  ]
}
```

---

## Capability Negotiation

### Server Declares Capabilities

```json
{
  "result": {
    "capabilities": {
      "tools": {
        "listChanged": false
      },
      "resources": {
        "subscribe": true,
        "listChanged": true
      },
      "prompts": {
        "listChanged": false
      },
      "logging": {
        "level": "debug"
      },
      "sampling": {
        "supported": true
      }
    }
  }
}
```

### Client Declares Capabilities

```json
{
  "capabilities": {
    "roots": {
      "listChanged": true
    },
    "sampling": {
      "supported": true
    },
    "experimental": {
      "mcp_apps": true
    }
  }
}
```

---

## Error Handling

### Standard JSON-RPC Errors

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32600,
    "message": "Invalid Request",
    "data": { "details": "..." }
  }
}
```

### MCP-Specific Errors

| Code | Message | Meaning |
|------|---------|---------|
| -32700 | Parse error | JSON parse failure |
| -32600 | Invalid Request | Malformed request |
| -32601 | Method not found | Unknown method |
| -32602 | Invalid params | Parameter validation failed |
| -32603 | Internal error | Server error |

---

## MCP Apps (2026 Feature)

MCP Apps allow servers to return interactive UI components:

```json
{
  "result": {
    "content": [
      {
        "type": "app",
        "app": {
          "type": "dashboard",
          "title": "Sales Dashboard",
          "widgets": [
            {
              "type": "chart",
              "data": [...]
            }
          ]
        }
      }
    ]
  }
}
```

The app renders directly in the conversation, enabling:
- Interactive dashboards
- Multi-step workflows
- Forms and inputs
- Real-time visualizations

---

## Security Considerations

### Input Validation

Always validate tool inputs:

```python
@server.tool()
def execute_command(cmd: str) -> str:
    """Execute shell command (restricted)."""
    # Whitelist allowed commands
    allowed = ["ls", "pwd", "whoami"]
    if cmd.split()[0] not in allowed:
        raise ValueError(f"Command {cmd} not allowed")
    return os.popen(cmd).read()
```

### Approval Gates (Elicitation)

```python
@server.tool()
def delete_database() -> str:
    """Requires user approval."""
    # Server notifies host for approval
    return await request_user_approval(
        "Delete database?",
        details="This will erase all data"
    )
```

### Sandboxing

```python
@server.tool()
def run_code(code: str) -> str:
    """Execute code in sandbox."""
    # Use subprocess with restrictions
    result = subprocess.run(
        ["python", "-c", code],
        timeout=5,
        capture_output=True,
        cwd="/tmp/sandbox"  # Restricted directory
    )
    return result.stdout
```

---

## Comparison to Other Tool Protocols

| Feature | MCP | OpenAI Tools | Anthropic Tool Use |
|---------|-----|-------------|-------------------|
| **Standard** | Open standard | OpenAI proprietary | Anthropic proprietary |
| **Transport** | JSON-RPC + multiple | HTTP REST only | HTTP REST only |
| **Bi-directional** | Yes (sampling) | No | No |
| **Resources** | Yes (read-only data) | No | No |
| **Prompts** | Yes (templates) | No | No |
| **Multi-server** | Native | Proxy-only | Proxy-only |
| **Local support** | STDIO native | Requires wrapper | Requires wrapper |

---

## Sources

- [Model Context Protocol Specification (2025-11-25)](https://modelcontextprotocol.io/specification/2025-11-25)
- [MCP GitHub Repository](https://github.com/modelcontextprotocol/modelcontextprotocol)
- [MCP Transports Documentation](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports)
- [MCP Server Development Guide](https://github.com/cyanheads/model-context-protocol-resources/blob/main/guides/mcp-server-development-guide.md)
- [MCP Message Types Reference](https://portkey.ai/blog/mcp-message-types-complete-json-rpc-reference-guide/)
- [Model Context Protocol Complete Guide 2026](https://fast.io/resources/model-context-protocol/)
- [Python SDK Repository](https://github.com/modelcontextprotocol/python-sdk)
- [Roo Code MCP Documentation](https://docs.roocode.com/features/mcp/server-transports)
- [MCP Apps Blog Post](http://blog.modelcontextprotocol.io/posts/2026-01-26-mcp-apps/)
