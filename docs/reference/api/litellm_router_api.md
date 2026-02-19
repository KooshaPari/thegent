# litellm_router API Reference

> **Source**: `src/thegent/routing/litellm_router.py`

LiteLLM Router wrapper with full feature support.

Provides comprehensive LiteLLM integration including:
- Multi-provider routing (cheapest, fastest, latency-based, round_robin)
- Response caching (in-memory or Redis)
- Fallback chains with cooldown times
- Context window validation
- Cost tracking and budget alerts
- Webhook alerting for latency/errors/budget
- Streaming support
- Donut Architecture integration

---

## EnhancedRouter

Enhanced router with full feature support.

Wraps LiteLLM Router with:
- Cost tracking integration
- Alert management
- Donut Architecture integration
- Context window validation
- Streaming support

### Methods

#### EnhancedRouter.__init__

Initialize enhanced router.

Args:
    policy: Optional routing policy override

```python
__init__(self, policy)
```

#### EnhancedRouter.alert_manager

Get alert manager (lazy initialization).

```python
alert_manager(self)
```

#### EnhancedRouter.cost_tracker

Get cost tracker (lazy initialization).

```python
cost_tracker(self)
```

#### EnhancedRouter.donut_adapter

Get Donut adapter (lazy initialization).

```python
donut_adapter(self)
```

#### EnhancedRouter.route

Route a request through LiteLLM.

Args:
    prompt: The prompt to send
    model: Optional model override (otherwise router selects)
    stream: Whether to stream the response
    **kwargs: Additional LiteLLM parameters

Returns:
    RoutingResult with response and metadata

```python
route(self, prompt, model, stream)
```

#### EnhancedRouter.route_stream

Route with streaming response.

Args:
    prompt: The prompt to send
    model: Optional model override
    **kwargs: Additional LiteLLM parameters

Yields:
    Stream chunks from the model

```python
route_stream(self, prompt, model)
```

---

## RouterConfig

Configuration for LiteLLM Router.

---

## RoutingResult

Result from a routing operation.

---

## alert_manager

Get alert manager (lazy initialization).

```python
alert_manager(self)
```

---

## build_fallback_chains

Build fallback chains for models in LiteLLM format.

LiteLLM Router expects fallbacks as a list of dicts:
[{"primary_model": ["fallback1", "fallback2"]}, ...]

Returns:
    List of fallback chain dicts for LiteLLM Router

---

## build_litellm_model_list

Build LiteLLM model_list from catalog routes.

Excludes NATIVE_CLI_PROVIDERS (codex, claude).
Routes API_KEY_PROVIDERS directly.
Routes LOGIN_AUTH_PROVIDERS via CLIProxyAPIPlus.

Returns:
    List of LiteLLM model_list entries

---

## cost_tracker

Get cost tracker (lazy initialization).

```python
cost_tracker(self)
```

---

## donut_adapter

Get Donut adapter (lazy initialization).

```python
donut_adapter(self)
```

---

## get_context_window

Get context window size for a model.

Args:
    model: Model name (may be alias)

Returns:
    Context window in tokens

```python
get_context_window(model)
```

---

## get_enhanced_router

Get global enhanced router instance.

Args:
    policy: Optional routing policy override

Returns:
    EnhancedRouter instance

```python
get_enhanced_router(policy)
```

---

## get_litellm_router

Get configured LiteLLM Router instance.

Args:
    policy: Routing policy (cheapest, fastest, round_robin, latency-based-routing)

Returns:
    Configured LiteLLM Router

```python
get_litellm_router(policy)
```

---

## get_router_config

Get router configuration from settings.

Returns:
    RouterConfig with values from ThegentSettings

---

## reset_enhanced_router

Reset the global enhanced router (useful for testing).

---

## route

Route a request through LiteLLM.

Args:
    prompt: The prompt to send
    model: Optional model override (otherwise router selects)
    stream: Whether to stream the response
    **kwargs: Additional LiteLLM parameters

Returns:
    RoutingResult with response and metadata

```python
route(self, prompt, model, stream)
```

---

## route_stream

Route with streaming response.

Args:
    prompt: The prompt to send
    model: Optional model override
    **kwargs: Additional LiteLLM parameters

Yields:
    Stream chunks from the model

```python
route_stream(self, prompt, model)
```

---

## validate_context_window

Validate that prompt fits within model's context window.

Args:
    model: Model name
    prompt_tokens: Estimated prompt token count

Returns:
    True if prompt fits, False otherwise

```python
validate_context_window(model, prompt_tokens)
```

---

