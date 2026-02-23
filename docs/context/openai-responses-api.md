# OpenAI Responses API Context

> Reference for OpenAI's Responses API in thegent.
> Sources: platform.openai.com API documentation, migration guides (fetched 2026-02-20).

---

## What is the Responses API

The Responses API is OpenAI's stateful endpoint for agent-based workflows, intended to replace Chat Completions. Unlike Chat Completions (stateless, array of messages), the Responses API uses Items, native tools, and persistent reasoning state.

Key characteristics:
- **Stateful** (with optional persistence): Reasoning tokens persist via `previous_response_id`
- **Agentic**: Native multi-tool execution in single request
- **Reasoning-first**: Full integration with reasoning models (o3, o4-mini, o1)
- **Native tools**: Web search, code interpreter, file search, custom functions, MCP servers
- **Better cache utilization**: 40-80% improvement vs Chat Completions
- **Item-based**: Messages are just one type of Item; also function_call, function_call_output
- **Open Specification**: Standardized across providers (Hugging Face, Vercel, local inference)

---

## Endpoint

```
POST https://api.openai.com/v1/responses
Authorization: Bearer $OPENAI_API_KEY
Content-Type: application/json
```

---

## Request Schema

### Basic Request

```json
{
  "model": "o4-mini",
  "input": {
    "type": "message",
    "content": "Write a Python function that calculates Fibonacci numbers"
  }
}
```

### Full Request Schema

```typescript
{
  // --- Required ---
  model: string;                // "o4-mini", "o3", "gpt-4o", etc.

  // --- Input (Required) ---
  input: Input;                 // See Input schema below

  // --- Agentic Configuration ---
  tools?: Tool[];               // Available tools for the model
  modalities?: string[];        // ["text", "audio", "image"] (default: text)

  // --- State Management ---
  previous_response_id?: string; // Use reasoning/tools from prior response
  store?: boolean;              // Persist state for future requests (default: false)

  // --- Sampling Parameters ---
  temperature?: number;         // 0.0–2.0 (default: 1)
  top_p?: number;              // 0.0–1.0 (default: 1)
  max_tokens?: number;         // Max output tokens

  // --- Observability ---
  metadata?: Record<string, unknown>;  // Custom key-value metadata
  user?: string;               // End-user ID for tracking

  // --- Response Format ---
  response_format?: "json_schema" | "text";

  // --- Streaming ---
  stream?: boolean;            // Enable SSE streaming (default: false)
}
```

### Input Types

```typescript
type Input =
  | { type: "message"; content: string | ContentPart[] }
  | { type: "text"; text: string }
  | { type: "image"; image: string | ImageObject[] }
  | { type: "audio"; audio: string | AudioObject[] }
  | { type: "document"; document: DocumentObject };
```

### ContentPart Types

```typescript
type ContentPart =
  | { type: "text"; text: string }
  | { type: "image_url"; image_url: { url: string } }
  | { type: "image_base64"; media_type: string; data: string }
  | { type: "audio_url"; audio_url: { url: string } }
  | { type: "audio_base64"; media_type: string; data: string }
  | { type: "document_url"; document_url: { url: string; document_type: string } };
```

---

## Tools

### Tool Definition

```json
{
  "type": "function",
  "function": {
    "name": "get_weather",
    "description": "Get the weather for a location",
    "parameters": {
      "type": "object",
      "properties": {
        "location": {
          "type": "string",
          "description": "City name"
        },
        "unit": {
          "type": "string",
          "enum": ["celsius", "fahrenheit"]
        }
      },
      "required": ["location"]
    }
  }
}
```

**Note**: Tool schema differs from Chat Completions. In Responses API, the `function` wrapper is the only required top-level structure.

### Built-in Tools

OpenAI provides native tools without custom definition:

| Tool | ID | Purpose |
|------|----|---------|
| Web Search | `web_search` | Real-time web search via Bing |
| Code Interpreter | `code_interpreter` | Execute Python code in sandbox |
| File Search | `file_search` | Search uploaded documents |
| Computer Use | `computer_use` | Control desktop (future) |

#### Enable Web Search

```json
{
  "tools": [
    {
      "type": "builtin",
      "name": "web_search"
    }
  ],
  "input": {
    "type": "message",
    "content": "What are the latest AI breakthroughs in February 2026?"
  }
}
```

#### Enable Code Interpreter

```json
{
  "tools": [
    {
      "type": "builtin",
      "name": "code_interpreter"
    }
  ],
  "input": {
    "type": "message",
    "content": "Calculate the Fibonacci sequence up to 100"
  }
}
```

### Custom Functions

Define custom tools for the model to call:

```json
{
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "create_task",
        "description": "Create a task in the task manager",
        "parameters": {
          "type": "object",
          "properties": {
            "title": { "type": "string" },
            "priority": { "enum": ["low", "medium", "high"] }
          },
          "required": ["title"]
        }
      }
    }
  ]
}
```

### MCP Servers

Connect to Model Context Protocol servers for extensible tools:

```json
{
  "tools": [
    {
      "type": "mcp",
      "server": {
        "type": "stdio",
        "command": "python",
        "args": ["/path/to/mcp_server.py"]
      }
    },
    {
      "type": "mcp",
      "server": {
        "type": "sse",
        "url": "http://localhost:3000"
      }
    }
  ]
}
```

---

## Response Schema

### Non-Streaming Response

```json
{
  "id": "resp-abc123",
  "type": "response",
  "model": "o4-mini",
  "status": "completed",
  "input": { ... },
  "output": {
    "type": "message",
    "content": [
      {
        "type": "text",
        "text": "Here's a Fibonacci function in Python:\n\ndef fibonacci(n):\n    ..."
      }
    ]
  },
  "usage": {
    "input_tokens": 42,
    "output_tokens": 156
  },
  "stop_reason": "end_turn",
  "created_at": "2026-02-20T15:30:45Z"
}
```

### With Tool Calls

```json
{
  "id": "resp-def456",
  "status": "completed",
  "output": {
    "type": "message",
    "content": [
      {
        "type": "tool_call",
        "tool_name": "web_search",
        "tool_use_id": "call_abc123",
        "arguments": {
          "query": "AI breakthroughs February 2026"
        }
      }
    ]
  },
  "stop_reason": "tool_calls"
}
```

### With Reasoning

```json
{
  "id": "resp-ghi789",
  "status": "completed",
  "output": {
    "type": "message",
    "content": [
      {
        "type": "thinking",
        "thinking": "Let me break down this problem... The user wants to know..."
      },
      {
        "type": "text",
        "text": "Based on my analysis, the answer is..."
      }
    ]
  },
  "stop_reason": "end_turn"
}
```

### Response Types

| Stop Reason | Meaning |
|-------------|---------|
| `end_turn` | Model finished generation normally |
| `tool_calls` | Model invoked tools; awaits execution results |
| `max_tokens` | Reached token limit |
| `content_filtered` | Safety policy triggered |
| `error` | Underlying error occurred |

---

## Stateful Requests with Reasoning

### Persistent Reasoning via `previous_response_id`

```json
{
  "model": "o4-mini",
  "input": {
    "type": "message",
    "content": "Now refactor that code for performance"
  },
  "previous_response_id": "resp-abc123",
  "store": true
}
```

**Benefit**: The model automatically has access to the reasoning from `resp-abc123` without re-sending the original request. This:
- Saves tokens (40-80% better cache utilization)
- Preserves reasoning context across turns
- Enables multi-turn agentic loops

### Multi-Turn Agent Loop

```python
import openai

client = openai.OpenAI(api_key="...")

# Turn 1: Initial reasoning
response1 = client.beta.responses.create(
    model="o4-mini",
    input={"type": "message", "content": "Design a web app for task management"},
    store=True  # Persist for future turns
)

response_id = response1.id
print(f"Design: {response1.output.content[0].text}")

# Turn 2: Refine (reuses previous reasoning)
response2 = client.beta.responses.create(
    model="o4-mini",
    input={"type": "message", "content": "Add authentication to the design"},
    previous_response_id=response_id,
    store=True
)
print(f"With Auth: {response2.output.content[0].text}")

# Turn 3: Further refinement (reuses both priors)
response3 = client.beta.responses.create(
    model="o4-mini",
    input={"type": "message", "content": "Include deployment strategy"},
    previous_response_id=response2.id  # Use most recent
)
print(f"Full Design: {response3.output.content[0].text}")
```

---

## Streaming (SSE)

Enable with `stream: true`.

### Stream Event Format

```
event: response.created
data: {"id": "resp-abc123", "type": "response", "created_at": "..."}

event: content_block.start
data: {"type": "content_block", "index": 0, "content_block": {"type": "text"}}

event: content_block.delta
data: {"type": "content_block_delta", "delta": {"type": "text_delta", "text": "Here"}}

event: content_block.delta
data: {"type": "content_block_delta", "delta": {"type": "text_delta", "text": " is"}}

event: content_block.done
data: {"type": "content_block", "index": 0, "content_block": {...}}

event: message.delta
data: {"type": "message_delta", "delta": {"stop_reason": "end_turn"}}

event: response.done
data: {"id": "resp-abc123", "status": "completed", "output": {...}, "usage": {...}}
```

### Streaming Tool Calls

```
event: content_block.start
data: {"type": "content_block", "index": 0, "content_block": {"type": "tool_call", "tool_name": "web_search"}}

event: content_block.delta
data: {"type": "content_block_delta", "delta": {"type": "tool_call_delta", "arguments": "{\"query\": "}}

event: content_block.delta
data: {"type": "content_block_delta", "delta": {"type": "tool_call_delta", "arguments": "February 2026"}}

event: content_block.done
data: {"type": "content_block", "index": 0, "content_block": {...}}
```

### Python Streaming Example

```python
import openai

client = openai.OpenAI()

with client.beta.responses.stream(
    model="gpt-4o",
    input={"type": "message", "content": "Explain quantum computing"}
) as stream:
    for event in stream:
        if event.type == "content_block.delta":
            if hasattr(event.delta, "text"):
                print(event.delta.text, end="", flush=True)
```

---

## Reasoning Models

### Supported Reasoning Models

| Model | Capability | Context | Cost |
|-------|-----------|---------|------|
| `o4-mini` | Advanced reasoning, fastest | 32K | ~$0.10/M input tokens |
| `o3` | Extended reasoning, most capable | 200K | Higher |
| `o1` | Basic reasoning (legacy) | 128K | Legacy pricing |
| `gpt-4o` | No reasoning, fast | 128K | Low |

### Reasoning Configuration

```json
{
  "model": "o4-mini",
  "input": { "type": "message", "content": "Solve this complex math problem: ..." },
  "reasoning": {
    "type": "enabled",
    "effort": "high"  // or "low", "medium"
  }
}
```

### Accessing Reasoning Output

```python
response = client.beta.responses.create(
    model="o4-mini",
    input={"type": "message", "content": "..."},
    reasoning={"type": "enabled", "effort": "high"}
)

# Extract reasoning
for block in response.output.content:
    if block.type == "thinking":
        print(f"Reasoning: {block.thinking}")
    elif block.type == "text":
        print(f"Answer: {block.text}")
```

---

## Comparison: Responses API vs Chat Completions

| Feature | Responses API | Chat Completions |
|---------|--------------|-----------------|
| **Endpoint** | `POST /v1/responses` | `POST /v1/chat/completions` |
| **Input Format** | Items (message, thinking, tool_call) | Array of Messages |
| **State Management** | Stateful (previous_response_id) | Manual (messages array) |
| **Native Tools** | web_search, code_interpreter, file_search | Requires custom handling |
| **Tool Execution** | Multi-tool in single request | Must loop manually |
| **Reasoning** | Full integration (o3, o4-mini) | Extended thinking only |
| **Cache Utilization** | 40-80% better | Baseline |
| **Tool Schema** | Simplified | Requires "function" wrapper |
| **Streaming** | SSE with detailed events | SSE, less granular |
| **Stop Reason** | Normalized (end_turn, tool_calls) | Provider-specific |
| **OpenAI Recommendation** | Use for new projects | Maintain for existing production |

---

## Thegent Integration

The Responses API serves as an alternative protocol for Codex harness in thegent:

### Routing Layer

```python
# In CLIProxyAPIPlus
class ResponsesAPIHandler(ProviderHandler):
    def call_responses(self, request: ResponsesRequest) -> ResponsesResponse:
        """Route via Responses API instead of Chat Completions."""
        response = openai.beta.responses.create(**request.dict())
        return self._transform_to_proxy_response(response)

    def call_chat_completions(self, request: ChatCompletionRequest):
        """Legacy Chat Completions path."""
        response = openai.chat.completions.create(**request.dict())
        return response
```

### Configuration

```yaml
# thegent proxy config
openai:
  api_key: $OPENAI_API_KEY
  default_endpoint: "responses"  # or "chat.completions"
  models:
    reasoning:
      - o4-mini
      - o3
    standard:
      - gpt-4o
      - gpt-4-turbo
```

### Benefits in thegent

- **Agentic loops**: Multi-tool execution in single request
- **Persistent reasoning**: Reuse reasoning across agent steps
- **Native tool support**: web_search, code_interpreter without custom setup
- **MCP integration**: Connect to custom MCP servers
- **Better caching**: 40-80% token savings on multi-turn conversations

---

## Migration from Chat Completions

### Step 1: Update Tool Definitions

**Chat Completions** (old):
```json
{
  "type": "function",
  "function": { "name": "...", "parameters": {...} }
}
```

**Responses API** (new):
```json
{
  "type": "function",
  "function": { "name": "...", "parameters": {...} }
}
```

Note: Schema is similar; main difference is Items vs Messages.

### Step 2: Update Request Format

**Chat Completions**:
```python
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "..."}],
    tools=[...]
)
```

**Responses API**:
```python
response = client.beta.responses.create(
    model="gpt-4o",
    input={"type": "message", "content": "..."},
    tools=[...]
)
```

### Step 3: Update Response Handling

**Chat Completions**:
```python
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        execute_tool(tool_call.function.name, tool_call.function.arguments)
```

**Responses API**:
```python
for block in response.output.content:
    if block.type == "tool_call":
        execute_tool(block.tool_name, block.arguments)
```

---

## Deprecation Timeline

- **2026 H1**: Assistants API retired (migrate to Responses API)
- **2026 H2+**: Chat Completions remains, but Responses API recommended for new projects
- **Timeline**: OpenAI maintains both for backward compatibility

---

## API Limits

| Limit | Value |
|-------|-------|
| Max input tokens | 200K (varies by model) |
| Max output tokens | 16K–131K (model dependent) |
| Rate limits | 10K requests/min (pro), 500/min (free) |
| Concurrent requests | 500 (pro) |
| Timeout | 10 minutes |

---

## Error Handling

### Common Error Codes

| Code | Meaning | Remedy |
|------|---------|--------|
| 400 | Bad request (invalid tool schema) | Review tool definitions |
| 401 | Unauthorized (invalid API key) | Check OPENAI_API_KEY |
| 429 | Rate limited | Implement backoff; upgrade tier |
| 500 | Server error | Retry with exponential backoff |
| 503 | Service unavailable | Wait and retry |

### Example Error Response

```json
{
  "error": {
    "type": "invalid_request_error",
    "message": "Tool 'get_weather' is not defined",
    "param": "tools"
  }
}
```

---

## Performance Characteristics

### Latency

- **First-token latency**: 1-3 seconds (reasoning adds overhead)
- **Token generation rate**: 50-100 tokens/sec
- **Tool execution**: 500ms-2s per tool call

### Cost Example

```
Request: "Analyze sentiment of 100 customer reviews"
Input tokens: 50K (reviews) + 200 (prompt)
Output tokens: 1K (analysis + reasoning)
Model: o4-mini

Cost = (50,200 * $0.10/M) + (1,000 * $0.40/M) ≈ $5.05
```

---

## Sources

- [OpenAI Responses API Reference](https://platform.openai.com/docs/api-reference/responses)
- [Migrate to the Responses API](https://platform.openai.com/docs/guides/migrate-to-responses)
- [Responses vs Chat Completions](https://platform.openai.com/docs/guides/responses-vs-chat-completions)
- [Better Performance from Reasoning Models using Responses API](https://developers.openai.com/cookbook/examples/responses_api/reasoning_items/)
- [Why We Built the Responses API](https://developers.openai.com/blog/responses-api/)
- [OpenAI Reasoning Models Documentation](https://platform.openai.com/docs/guides/reasoning)
- [Open Responses Specification](https://www.infoq.com/news/2026/02/openai-open-responses/)
