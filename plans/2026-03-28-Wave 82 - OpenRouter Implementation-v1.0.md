# Wave 82 - OpenRouter Integration Execution Plan

## Status: Ready for Implementation

## Overview

Execute the OpenRouter integration backlog items (WL-001 through WL-005) to fix WebSocket authentication, add provider registration, configure LiteLLM, add model mappings, and fix SSE parsing.

---

## Task Checklist (Implementation)

- [ ] **WL-001: OpenRouter WebSocket Auth Fix**
  - [ ] Add `Authorization: Bearer <OPENROUTER_API_KEY>` header injection
  - [ ] Add `HTTP-Referer` and `X-Title` headers
  - [ ] Implement connection state management
  - [ ] Add error handling for auth failures
  - [ ] Add reconnection logic with backoff

- [ ] **WL-002: OpenRouter Provider Registration**
  - [ ] Add provider to `cliproxy_manager.py`
  - [ ] Configure base URL: `https://openrouter.ai/api/v1`
  - [ ] Register supported models
  - [ ] Add to routing configuration

- [ ] **WL-003: OpenRouter LiteLLM Config**
  - [ ] Configure LiteLLM proxy backend
  - [ ] Set up model aliases
  - [ ] Configure rate limiting
  - [ ] Add health check endpoint

- [ ] **WL-004: OpenRouter Model Mappings**
  - [ ] Map OpenAI models to OpenRouter equivalents
  - [ ] Add provider/model format conversion
  - [ ] Configure multi-model routing
  - [ ] Add model metadata enrichment

- [ ] **WL-005: OpenRouter SSE Parse Fix**
  - [ ] Implement proper SSE event parsing
  - [ ] Handle `data: [DONE]` termination
  - [ ] Add chunked transfer decoding
  - [ ] Handle error events gracefully

---

## Technical Details

### Authentication Headers Required

```python
headers = {
    "Authorization": f"Bearer {api_key}",
    "HTTP-Referer": "https://your-app-url.com",
    "X-Title": "Your App Name",
    "Content-Type": "application/json",
}
```

### Model ID Format

OpenRouter uses `provider/model-name` format:
- `openai/gpt-4o`
- `anthropic/claude-3.5-sonnet`
- `google/gemini-2.0-flash`

### SSE Parsing

```python
import sse_starlette

class OpenRouterSSIE:
    async def event_generator(self):
        async for line in response.content:
            if line.startswith("data: "):
                yield json.loads(line[6:])
```

---

## Verification Criteria

- [ ] Unit tests pass for auth flow
- [ ] Integration tests pass for WebSocket
- [ ] Manual streaming test succeeds
- [ ] Model routing test passes
- [ ] SSE parsing test passes

---

## Dependencies

- `httpx` for async HTTP
- `sse-starlette` for SSE handling
- `thegent.cliproxy_adapter` for base adapter
