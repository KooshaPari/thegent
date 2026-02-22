# Routing Domain Technical Specification

## Overview

The Routing domain handles LLM model selection, cost optimization, and request routing.

## Components

### Router Types

| Router | Purpose | Priority |
|--------|---------|----------|
| `TaskRouter` | Task-based routing | P0 |
| `CostAwareRouter` | Cost optimization | P0 |
| `SemanticRouter` | Semantic caching | P1 |
| `CircuitBreakerRouter` | Fault tolerance | P1 |
| `ParetoRouter` | Multi-objective | P2 |

### Routing Strategies

| Strategy | File | Use Case |
|----------|------|----------|
| Task routing | `task_router.py` | Default |
| Cost optimization | `cost_aware_router.py` | Budget-constrained |
| Semantic cache | `semantic_cache.py` | Repeated prompts |
| Rate limiting | `rate_limiter.py` | API limits |
| Preemption | `preemption.py` | Priority queues |

## API Reference

### Router Interface

```python
class Router(Protocol):
    async def route(self, request: Request) -> Model: ...
    def capabilities(self) -> list[ModelCapability]: ...
    def health_check(self) -> HealthStatus: ...
```

### Request Flow

```
Request → RateLimit → CostCheck → SemanticCache → Router → Provider
                              ↓
                        Cache Hit? → Return Cached
```

## Cost Optimization

| Mechanism | File | Target |
|-----------|------|---------|
| Cost tracking | `cost_tracker.py` | Budget monitoring |
| Cost calculation | `cost_calculator.py` | Per-token pricing |
| Budget limits | `budget.py` | Spending caps |

## Performance

| Metric | Target |
|--------|--------|
| Route decision | <10ms |
| Cache lookup | <5ms |
| Provider fallback | <100ms |

## Providers Supported

| Provider | Adapter | Status |
|----------|---------|--------|
| OpenAI | `openai_provider.py` | ✅ |
| Anthropic | `claude_provider.py` | ✅ |
| Gemini | `gemini_provider.py` | ✅ |
| Ollama | `ollama_provider.py` | ✅ |
| Local models | `local_provider.py` | ✅ |

## Configuration

```yaml
routing:
  default_model: gpt-4
  fallback_chain:
    - model: gpt-4
    - model: claude-3
    - model: gpt-3.5-turbo
  cost_limits:
    per_request: 0.50
    per_hour: 10.00
```
