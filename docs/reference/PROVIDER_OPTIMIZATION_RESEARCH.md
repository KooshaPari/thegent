# Provider-Specific Optimization Research

## MiniMax M2.5 Best Practices

### Context & Intent
- Tell "why" not just "what" - explains reasoning for better results
- Use templates with good/bad examples to avoid mistakes
- 200k token context - use efficiently

### Multi-Window Workflow
- Phased processing: first window sets framework, second iterates
- Create tests.json for long-term tracking
- Use init.sh for server/test startup

### Error Handling
- Check Retry-After headers from responses
- Exponential backoff with jitter
- Circuit breaker pattern for failing providers

## GLM-5 Optimization

### Context Handling
- 200k input, 128k output tokens
- Monitor quota before requests
- Use caching to reduce redundant calls

### Rate Limits
- Implement sliding window rate limiting
- Key-level granularity
- Dynamic adjustment based on server load

## GPT-5 / OpenAI Models

### Rate Limits
- Tier-based limits (RPM/TPM/RPD)
- Check rate limit headers in responses
- Token bucket algorithm

### Best Practices
- Exponential backoff with max_retries
- Use max_completion_tokens to limit output
- Concurrency: use async pools

## Claude Code Optimization

### Context Management
- 200k context window
- Use compression for single tasks
- Restart for new tasks
- Token budget awareness

### Tool Calling
- Proper tool definitions with schemas
- Retry with tenacity
- Circuit breaker for provider failures

## Codex CLI

### Known Issues
- Version 0.57.0 recommended (latest has compatibility issues)
- Retry headers handling needed
- Provider-specific backoff

### Parallelization
- Profile-based execution
- Environment variable configuration
- JSON config for model selection

## Droid (Factory)

### Retry Patterns
- tenacity for all API calls
- Exponential backoff
- Circuit breaker for provider failures

## General Patterns

### Retry Strategy (All Providers)

```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=60),
    retry=retry_if_exception_type((RateLimitError, TimeoutError))
async def call_provider(provider: str, prompt: str) -> str:
    ...
```

### Circuit Breaker

```python
import pybreaker

breaker = pybreaker.CircuitBreaker(
    fail_max=5,
    reset_timeout=60,
)

@breaker
async def call_api():
    ...
```

### Async Pool for Parallelization

```python
import asyncio
from concurrent.futures import AsyncIOExecutor

pool = AsyncIOExecutor(max_workers=10)
results = await pool.map(call_provider, prompts)
```

### Provider-Specific Configuration

| Provider | Retry Strategy | Circuit Breaker | Async Pool |
|----------|----------------|----------------|-------------|
| MiniMax | tenacity | pybreaker | asyncio.gather |
| GLM | tenacity | pybreaker | asyncio.gather |
| GPT-5 | tenacity | pybreaker | asyncio.gather |
| Claude | tenacity | pybreaker | asyncio.gather |
| Codex | tenacity | pybreaker | asyncio.gather |
| Droid | tenacity | pybreaker | asyncio.gather |

## Implementation Status

| Component | Location | Status |
|----------|-----------|--------|
| **tenacity retry** | `infra/fast_http_client.py` | ✅ Implemented |
| **pybreaker circuit breaker** | `utils/routing_impl/circuit_breaker.py` | ✅ Implemented |
| **Circuit breaker registry** | `ProviderCircuitBreakerRegistry` | ✅ Implemented |
| **Async pools** | Need audit | ⚠️ Check asyncio usage |
| **Provider-specific configs** | Need audit | ⚠️ Check |

### Already Implemented

1. **tenacity retry** in `infra/fast_http_client.py`:
   - Exponential backoff with jitter
   - Max attempts configuration
   - Logging on retry

2. **Circuit breaker** in `utils/routing_impl/circuit_breaker.py`:
   - ProviderCircuitBreaker per-provider config
   - State machine: CLOSED → OPEN → HALF_OPEN → CLOSED
   - Thread-safe registry

3. **Provider routing** in `utils/routing_impl/route_executor.py`:
   - Multiple routing policies
   - Cost-aware routing
   - Fallback providers

### Implementation Complete (Feb 2026)

1. **Provider-specific retry configs** in `agents/codex_proxy.py`:
   - Added `_PROVIDER_RETRY_CONFIG` dict with MiniMax, GLM, NIM, Kilo settings
   - MiniMax: 5 attempts, 2-120s backoff (highspeed plan optimized)
   - GLM: 4 attempts, 2-60s backoff
   - NIM/Kilo: 3 attempts, 1-30s backoff

2. **Circuit breaker integration** in `agents/codex_proxy.py`:
   - Integrated `ProviderCircuitBreakerRegistry` into `_execute_litellm_api`
   - Records success/failure for each provider
   - Fast-fail when circuit is OPEN

3. **tenacity retry integration** in `agents/codex_proxy.py`:
   - Added `@retry` decorator with provider-specific settings
   - Exponential backoff with multiplier from config
   - Logs retry attempts for debugging

### Needs Implementation

1. **Async pools** for parallel execution
2. **Rate limit header parsing** - Extract Retry-After from provider responses

## Implementation Checklist

- [x] Add tenacity to all LLM API calls (infra/http layer)
- [x] Add pybreaker circuit breaker (utils/routing_impl/circuit_breaker.py)
- [x] Add provider-specific retry configs to codex_proxy.py
- [x] Integrate circuit breaker with LiteLLM API calls
- [x] Add tenacity retry with provider-specific backoff to _execute_litellm_api
- [ ] Add async pools for parallelization
- [ ] Rate limit header parsing (Retry-After)
