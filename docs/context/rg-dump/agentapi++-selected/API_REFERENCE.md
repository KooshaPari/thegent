# API Reference

## Overview

Complete reference for atomsAgent API endpoints. All endpoints require authentication via JWT token in the `Authorization` header.

## Authentication

All endpoints (except health checks) require:
```
Authorization: Bearer <JWT_TOKEN>
```

## OpenAI-Compatible Endpoints

### POST /v1/chat/completions

Create a chat completion using Claude.

**Request:**
```json
{
  "model": "claude-4.5-sonnet",
  "messages": [
    {"role": "user", "content": "Hello"}
  ],
  "stream": false,
  "temperature": 0.7,
  "max_tokens": 1024
}
```

**Response (Non-streaming):**
```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "claude-4.5-sonnet",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! How can I help?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 5,
    "total_tokens": 15
  }
}
```

**Response (Streaming):**
```
data: {"choices":[{"delta":{"content":"Hello"}}]}
data: {"choices":[{"delta":{"content":" world"}}]}
data: [DONE]
```

**Parameters:**
- `model` (string, required) - Model name
- `messages` (array, required) - Message history
- `stream` (boolean) - Stream response (default: false)
- `temperature` (number) - Sampling temperature (0-1)
- `max_tokens` (number) - Max tokens to generate
- `tools` (array) - Tools for Claude to use

**Status Codes:**
- 200 - Success
- 400 - Invalid request
- 401 - Unauthorized
- 429 - Rate limited
- 500 - Server error

---

### GET /v1/models

List available models.

**Response:**
```json
{
  "object": "list",
  "data": [
    {
      "id": "claude-4.5-sonnet",
      "object": "model",
      "owned_by": "anthropic"
    }
  ]
}
```

---

## MCP Management Endpoints

### POST /atoms/mcp/register

Register an MCP server.

**Request:**
```json
{
  "name": "search",
  "url": "https://mcp-server.example.com",
  "oauth_enabled": false
}
```

**Response:**
```json
{
  "id": "mcp_123",
  "name": "search",
  "url": "https://mcp-server.example.com",
  "created_at": "2025-11-23T10:00:00Z"
}
```

---

### GET /atoms/mcp/servers

List registered MCP servers.

**Response:**
```json
{
  "servers": [
    {
      "id": "mcp_123",
      "name": "search",
      "url": "https://mcp-server.example.com"
    }
  ]
}
```

---

### DELETE /atoms/mcp/servers/{server_id}

Unregister an MCP server.

**Response:**
```json
{
  "success": true
}
```

---

### POST /atoms/mcp/tools

Discover tools from registered servers.

**Response:**
```json
{
  "tools": [
    {
      "name": "search",
      "description": "Search the web",
      "inputSchema": {
        "type": "object",
        "properties": {
          "query": {"type": "string"}
        }
      }
    }
  ]
}
```

---

## Platform Admin Endpoints

### POST /atoms/platform/prompts

Create a platform prompt.

**Request:**
```json
{
  "name": "default",
  "content": "You are a helpful assistant."
}
```

**Response:**
```json
{
  "id": "prompt_123",
  "name": "default",
  "content": "You are a helpful assistant.",
  "created_at": "2025-11-23T10:00:00Z"
}
```

---

### GET /atoms/platform/prompts

List platform prompts.

**Response:**
```json
{
  "prompts": [
    {
      "id": "prompt_123",
      "name": "default",
      "content": "You are a helpful assistant."
    }
  ]
}
```

---

### PUT /atoms/platform/prompts/{prompt_id}

Update a prompt.

**Request:**
```json
{
  "content": "You are a helpful assistant v2."
}
```

**Response:**
```json
{
  "id": "prompt_123",
  "name": "default",
  "content": "You are a helpful assistant v2.",
  "updated_at": "2025-11-23T10:00:00Z"
}
```

---

### DELETE /atoms/platform/prompts/{prompt_id}

Delete a prompt.

**Response:**
```json
{
  "success": true
}
```

---

## Health Check Endpoints

### GET /health/live

Liveness probe.

**Response:**
```json
{
  "status": "ok"
}
```

---

### GET /health/ready

Readiness probe.

**Response:**
```json
{
  "status": "ready"
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "error": {
    "message": "Error description",
    "code": "error_code",
    "details": {}
  }
}
```

**Common Error Codes:**
- `invalid_request` - Invalid request format
- `unauthorized` - Missing or invalid JWT
- `forbidden` - Insufficient permissions
- `not_found` - Resource not found
- `rate_limited` - Rate limit exceeded
- `server_error` - Internal server error

---

## Rate Limiting

- **Limit:** 1000 requests per minute per user
- **Header:** `Retry-After` (seconds to wait)
- **Status:** 429 Too Many Requests

---

## Pagination

List endpoints support pagination:

```
GET /atoms/platform/prompts?skip=0&limit=10
```

**Parameters:**
- `skip` - Number of items to skip (default: 0)
- `limit` - Maximum items to return (default: 100)

---

## See Also

- [README.md](./README.md) - Project overview
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture
- [DEVELOPMENT.md](./DEVELOPMENT.md) - Development setup

---

**Last Updated:** 2025-11-23
**Version:** 1.0

