# LiteLLM Context

> Definitive reference for integrating LiteLLM as the routing and proxy layer in thegent's CLIProxyAPIPlus.
> Sources: litellm.ai, BerriAI/litellm on GitHub (fetched 2026-02-20).

---

## What is LiteLLM

LiteLLM is a unified Python SDK and OpenAI-compatible proxy server (AI Gateway) that provides programmatic access to 100+ LLM providers. It abstracts provider differences, enables load balancing, cost tracking, fallback routing, and guardrails—all through a single OpenAI-compatible API.

Key characteristics:
- **100+ provider support**: OpenAI, Anthropic, Google, Meta, Cohere, Bedrock, VertexAI, Groq, DeepSeek, Mistral, and many others
- **OpenAI-compatible**: Drop-in replacement for OpenAI SDK
- **Proxy server**: Standalone AI Gateway with HTTP interface
- **Load balancing**: Multiple routing strategies (least-busy, latency-based, usage-based)
- **Cost tracking**: Automatic spend aggregation across providers
- **Fallback routing**: Model fallbacks when primary provider fails
- **MIT licensed**: Open source, actively maintained (latest release: Feb 17, 2026)
- **Observability**: Callbacks for Langfuse, Prometheus, MLflow, custom logging

---

## Installation

### Python SDK

```bash
pip install litellm
```

### Proxy Server

```bash
pip install litellm[proxy]
# or
pipx install litellm
```

### Verification

```bash
python -c "import litellm; print(litellm.__version__)"
litellm --version
```

---

## Python SDK Usage

### Basic Completion

```python
import litellm

# Simple call with model name mapping
response = litellm.completion(
    model="gpt-3.5-turbo",  # Mapped to OpenAI
    messages=[{"role": "user", "content": "Hello!"}],
)
print(response.choices[0].message.content)
```

### Unified Signature Across Providers

```python
# Works with ANY provider
response = litellm.completion(
    model="claude-3-5-sonnet",      # Anthropic
    messages=[{"role": "user", "content": "Hello"}]
)

response = litellm.completion(
    model="gemini-pro",              # Google
    messages=[{"role": "user", "content": "Hello"}]
)

response = litellm.completion(
    model="command-r",               # Cohere
    messages=[{"role": "user", "content": "Hello"}]
)
```

### Async Completion

```python
import asyncio

async def main():
    response = await litellm.acompletion(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Hello"}],
    )
    print(response.choices[0].message.content)

asyncio.run(main())
```

### Model Provider Mapping

LiteLLM automatically maps model names to provider endpoints:

```python
# Format: provider/model or provider.model
litellm.completion(model="openai/gpt-4o", messages=[...])
litellm.completion(model="anthropic/claude-3-sonnet", messages=[...])
litellm.completion(model="google/gemini-pro", messages=[...])
litellm.completion(model="bedrock/anthropic.claude-3-sonnet", messages=[...])
```

### Token Counting

```python
tokens = litellm.token_counter(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello"}]
)
print(f"Tokens: {tokens}")
```

### Cost Calculation

```python
from litellm import completion_cost

response = litellm.completion(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello"}]
)

cost = completion_cost(completion_response=response)
print(f"Cost: ${cost}")
```

---

## Proxy Server

### Quick Start

```bash
# With default config
litellm --config config.yaml

# Starts server at http://localhost:8000
# OpenAI-compatible: POST /v1/chat/completions
```

### Configuration File (config.yaml)

```yaml
# Model definitions
model_list:
  - model_name: gpt-4o
    litellm_params:
      model: openai/gpt-4o
      api_key: $OPENAI_API_KEY

  - model_name: claude-sonnet
    litellm_params:
      model: anthropic/claude-3-5-sonnet-20241022
      api_key: $ANTHROPIC_API_KEY

  - model_name: gemini
    litellm_params:
      model: google/gemini-pro
      api_key: $GOOGLE_API_KEY

# Router settings (load balancing, fallbacks)
router_settings:
  routing_strategy: "usage-based-routing-v2"  # or "least-busy", "latency-based", "simple-shuffle"
  redis_host: localhost
  redis_port: 6379
  redis_password: null
  enable_pre_call_checks: true

# General proxy settings
general_settings:
  master_key: "sk-1234567890abcdef"  # For auth to proxy
  database_url: null  # For request logging
  logging: true
  debug: false
```

### Deployment Models

A **deployment** is a single model configuration in `model_list`, representing:

```yaml
model_list:
  - model_name: "gpt-4-deployment-1"
    litellm_params:
      model: "openai/gpt-4o"
      api_key: $OPENAI_KEY_1
      api_base: "https://api.openai.com/v1"

  - model_name: "gpt-4-deployment-2"
    litellm_params:
      model: "openai/gpt-4o"
      api_key: $OPENAI_KEY_2
      api_base: "https://alternative-openai.com/v1"

  - model_name: "claude-deployment-1"
    litellm_params:
      model: "anthropic/claude-3-5-sonnet"
      api_key: $ANTHROPIC_KEY
```

Router selects deployments based on routing strategy.

---

## Routing Strategies

### Routing Strategy Options

| Strategy | Behavior | Use Case |
|----------|----------|----------|
| `simple-shuffle` | Random selection from healthy endpoints | Load spreading |
| `least-busy` | Selects deployment with fewest in-flight requests | Balanced throughput |
| `usage-based-routing-v2` | Routes based on historical usage and cost | Cost optimization |
| `latency-based-routing` | Prefers deployments with lower latency | Performance |

### Configuration

```yaml
router_settings:
  routing_strategy: "usage-based-routing-v2"
  redis_host: localhost           # Required for distributed state
  redis_port: 6379
  redis_password: null
  enable_pre_call_checks: true
```

### Fallback Routing

```yaml
model_list:
  - model_name: "gpt-4-with-fallback"
    litellm_params:
      model: "openai/gpt-4o"
      api_key: $OPENAI_KEY
    fallbacks:
      - model_name: "gpt-3.5-turbo"
      - model_name: "claude-3-sonnet"
```

When primary model fails, router automatically tries fallbacks in order.

---

## Cost Tracking

### Automatic Cost Calculation

LiteLLM automatically calculates cost for all known models:

```python
response = litellm.completion(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello"}]
)

# Access usage info
print(f"Prompt tokens: {response.usage.prompt_tokens}")
print(f"Completion tokens: {response.usage.completion_tokens}")

# Calculate cost
from litellm import completion_cost
cost = completion_cost(response)
print(f"Cost: ${cost}")
```

### Proxy-Level Cost Tracking

The proxy server tracks spend for all API keys:

```yaml
# Enable cost tracking in proxy
general_settings:
  database_url: "postgresql://user:pass@localhost/litellm"
  logging: true
```

Spend tracking via virtual keys:

```bash
# Create a virtual key with budget
curl -X POST http://localhost:8000/key/new \
  -H "Authorization: Bearer $MASTER_KEY" \
  -d '{"budget_limit": 100, "budget_duration": "1mo"}'

# Returns: {"key": "sk-abc123", "budget": 100}
```

### Budget Management

```yaml
model_list:
  - model_name: gpt-4o
    litellm_params:
      model: openai/gpt-4o
      api_key: $OPENAI_KEY
    budget_limit: 50
    budget_duration: 1d  # Reset daily
```

When a deployment reaches budget limit, router moves to next deployment or fails gracefully.

---

## Provider Support

LiteLLM supports 100+ providers across multiple categories:

### Major Cloud Providers

```yaml
model_list:
  # OpenAI
  - model_name: gpt-4o
    litellm_params:
      model: openai/gpt-4o

  # Anthropic
  - model_name: claude
    litellm_params:
      model: anthropic/claude-3-5-sonnet

  # Google
  - model_name: gemini
    litellm_params:
      model: google/gemini-pro

  # AWS Bedrock
  - model_name: bedrock-claude
    litellm_params:
      model: bedrock/anthropic.claude-3-sonnet-20240229-v1:0
      aws_region_name: us-east-1

  # Azure OpenAI
  - model_name: azure-gpt4
    litellm_params:
      model: azure/gpt-4o
      api_base: https://{resource}.openai.azure.com/
      api_version: 2024-02-15-preview

  # Cohere
  - model_name: cohere-command
    litellm_params:
      model: cohere/command-r
```

### Open-Source / Self-Hosted

```yaml
  # vLLM server
  - model_name: vllm-model
    litellm_params:
      model: openai/llama-2-7b
      api_base: http://localhost:8000/v1

  # GGML / Ollama
  - model_name: ollama-mistral
    litellm_params:
      model: openai/mistral
      api_base: http://localhost:11434/v1

  # HuggingFace Inference
  - model_name: hf-model
    litellm_params:
      model: huggingface/meta-llama/Llama-2-7b
      api_key: $HUGGINGFACE_KEY

  # NVIDIA NIM
  - model_name: nim-llama
    litellm_params:
      model: openai/meta-llama2-70b
      api_base: http://localhost:8000/v1
```

---

## Streaming

### Python SDK Streaming

```python
response = litellm.completion(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Write a poem"}],
    stream=True
)

for chunk in response:
    print(chunk.choices[0].delta.content, end="", flush=True)
```

### Proxy Server Streaming

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-1234567890" \
  -d '{
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": "Hello"}],
    "stream": true
  }' \
  | jq -r '.choices[0].delta.content'
```

---

## Caching

### Redis Caching

```yaml
router_settings:
  redis_host: localhost
  redis_port: 6379
  redis_password: null

general_settings:
  cache:
    type: "redis"  # or "in_memory", "disk"
    cache_responses: true
```

### In-Memory Cache

```python
import litellm

litellm.cache.set_cache(type="in_memory")

# First call: hits API
response = litellm.completion(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hi"}]
)

# Second call: returns cached response (same messages)
response = litellm.completion(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hi"}]
)
```

### S3 Cache

```python
litellm.cache.set_cache(
    type="s3",
    s3_bucket_name="my-cache-bucket",
    s3_region_name="us-east-1"
)
```

---

## Observability and Logging

### Callbacks

```python
import litellm
from litellm.integrations.langfuse import langfuse

# Enable Langfuse observability
litellm.success_callback = [langfuse.log_event]

response = litellm.completion(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hi"}]
)
# Automatically logged to Langfuse
```

### Supported Integrations

| Platform | Status | Setup |
|----------|--------|-------|
| Langfuse | Supported | `litellm.success_callback = [langfuse.log_event]` |
| MLflow | Supported | Enable in config |
| Lunary | Supported | API key in config |
| Prometheus | Supported | Expose /metrics endpoint |
| DataDog | Supported | Via callbacks |
| Custom | Supported | Implement callback interface |

### Prometheus Metrics

```bash
# Expose metrics from proxy
curl http://localhost:8000/metrics
```

Returns Prometheus-format metrics:
- `litellm_requests_total`
- `litellm_request_duration_seconds`
- `litellm_cost_total`
- `litellm_prompt_tokens_total`
- `litellm_completion_tokens_total`

---

## Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `OPENAI_API_KEY` | OpenAI auth | `sk-...` |
| `ANTHROPIC_API_KEY` | Anthropic auth | `sk-ant-...` |
| `GOOGLE_API_KEY` | Google auth | `AIzaS...` |
| `LITELLM_LOG` | Debug logging | `1` |
| `LITELLM_LOCAL_MODEL_COST_MAP` | Custom pricing | `{"my-model": {"prompt": 0.001, "completion": 0.002}}` |
| `LITELLM_PROXY_MASTER_KEY` | Proxy auth | `sk-1234567890` |
| `LITELLM_REDIS_HOST` | Redis host | `localhost` |
| `LITELLM_REDIS_PORT` | Redis port | `6379` |

---

## Thegent Integration

LiteLLM serves as the routing layer in thegent's CLIProxyAPIPlus:

### Architecture

```
User Request (OpenAI SDK)
        ↓
thegent CLIProxyAPIPlus (localhost:8317)
        ↓
LiteLLM Router (routing_strategy, fallbacks)
        ↓
Provider Selection (OpenAI, Anthropic, Google, etc.)
        ↓
Provider API
```

### Configuration

```yaml
# In thegent's proxy config
litellm:
  enabled: true
  proxy_port: 8317
  config_file: "/path/to/config.yaml"
  routing_strategy: "usage-based-routing-v2"
  redis_url: "redis://localhost:6379"
```

### Model Routing in Proxy

```bash
# Request via proxy
curl -X POST http://localhost:8317/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $THEGENT_KEY" \
  -d '{
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": "Hello"}]
  }'

# Router picks deployment based on:
# - routing_strategy (usage-based, least-busy, etc.)
# - fallback_model if primary fails
# - budget constraints
# - provider availability
```

### Features via LiteLLM

- **Multi-provider routing**: Model request routed intelligently
- **Cost aggregation**: Unified cost tracking across providers
- **Fallback logic**: Automatic failover when provider down
- **Load balancing**: Distribute across multiple deployments
- **Budget management**: Per-model budget limits
- **Observability**: Prometheus metrics, structured logging

---

## Comparison to Other Proxies

| Feature | LiteLLM | OpenRouter | Anthropic Proxy |
|---------|---------|-----------|-----------------|
| **Providers** | 100+ | 400+ | Anthropic only |
| **Cost Tracking** | Built-in | Per-generation | Not exposed |
| **Routing Strategies** | Multiple | Price/throughput/latency | N/A |
| **Redis/Caching** | Yes | Internal | N/A |
| **Self-hostable** | Yes | No | Yes |
| **Open Source** | Yes (MIT) | Closed | Closed |
| **Fallbacks** | Native support | models[] array | Not applicable |
| **Multi-region** | Via deployments | Native | N/A |

---

## Sources

- [LiteLLM Official Docs](https://docs.litellm.ai/docs/)
- [LiteLLM GitHub Repository](https://github.com/BerriAI/litellm)
- [LiteLLM Router - Load Balancing](https://docs.litellm.ai/docs/routing)
- [LiteLLM Proxy Configuration](https://docs.litellm.ai/docs/proxy/configs)
- [LiteLLM Cost Tracking](https://docs.litellm.ai/docs/proxy/cost_tracking)
- [LiteLLM Budget Routing](https://docs.litellm.ai/docs/proxy/provider_budget_routing)
- [LiteLLM on PyPI](https://pypi.org/project/litellm/)
- [LiteLLM Quick Start - Proxy CLI](https://docs.litellm.ai/docs/proxy/quick_start)
