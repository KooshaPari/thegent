# Full Stack Architecture Spec (Long-Term, No LiteLLM Shim)

Date: 2026-02-23
Status: target architecture

## 1) Canonical Stack

Logical dependency stack:

```text
[Providers]
  -> [CLIProxyAPI (Bifrost-powered execution/routing fabric)]
  -> [AgentAPI (agent control-plane)]
  -> [Harnesses: Codex, Claude, Droid, Antigma, Codex-alt]
  -> [MCP + Skills + Env runtime context]
```

Runtime request path (actual direction):

```text
User/Automation
  -> Harness
  -> AgentAPI
  -> CLIProxyAPI+Bifrost
  -> Provider(s)
  -> back up the stack
```

## 2) Layered Topology

```text
+-------------------------------------------------------------+
| L5 Runtime Context                                          |
| MCP servers | Skills | Env vars | Sandboxes | File mounts  |
+---------------------------+---------------------------------+
                            ^
                            | tool calls / context injection
+---------------------------+---------------------------------+
| L4 Harness Plane                                            |
| codex-harness | claude-harness | droid-harness             |
| antigma-harness | codex-alt-harness                         |
+---------------------------+---------------------------------+
                            ^
                            | normalized harness request
+---------------------------+---------------------------------+
| L3 AgentAPI Plane (Control Plane)                           |
| sessions | auth/org/project | policy | prompt assembly      |
| tool permissions | model intent | run state                 |
+---------------------------+---------------------------------+
                            ^
                            | execution request
+---------------------------+---------------------------------+
| L2 CLIProxyAPI Plane (Execution Plane)                      |
| provider registry | translation | routing | fallback        |
| spend/limits | retries | stream mux                         |
| powered by Bifrost runtime primitives                       |
+---------------------------+---------------------------------+
                            ^
                            | provider-specific calls
+---------------------------+---------------------------------+
| L1 Provider Substrate                                        |
| mlx | vllm | llamacpp | ollama                              |
| openrouter | openai | claude | cursor/api providers         |
| account-based and key-based upstreams                       |
+-------------------------------------------------------------+
```

## 3) Layer Responsibilities

### L2: CLIProxyAPI + Bifrost (Execution Fabric)
Owns:
- provider registry and aliases
- route selection and fallback
- account/key lane resolution
- provider payload translation
- retries, timeout policy, stream normalization
- cost/rate enforcement in execution path

Does not own:
- user/session business context
- harness semantics
- MCP policy decisions

### L3: AgentAPI (Control Plane)
Owns:
- authn/authz + org/project/session state
- harness profile interpretation
- prompt/context assembly
- tool/skill/env policy envelope
- run lifecycle and state recording

Does not own:
- low-level provider translation
- route/fallback mechanics

### L4: Harnesses
Owns:
- UX and command surface
- run initiation and stream rendering

Does not own:
- provider direct calls
- provider route policy

### L5: MCP/Skills/Env
Owns:
- runtime capability injection
- tool execution context

Does not own:
- provider routing or retries

## 4) Provider Classes (for policy)

```text
local_inference: mlx, vllm, llamacpp, ollama
cloud_direct: openai, anthropic
cloud_aggregator: openrouter
account_api: cursor, other account-based providers
internal_custom: antigma_internal, codex_alt_internal
```

## 5) Execution Lifecycle

```text
1) Harness starts run
2) AgentAPI resolves harness_profile + org policy
3) AgentAPI composes MCP/skills/env envelope
4) AgentAPI sends normalized request to CLIProxyAPI
5) CLIProxyAPI selects route candidate(s)
6) CLIProxyAPI executes against provider
7) On failure: classify -> fallback route(s)
8) CLIProxyAPI emits normalized events/results
9) AgentAPI updates run/session state
10) Harness renders output and status
```

## 6) Failure and Fallback Model

```text
primary route fails
 -> error classifier
 -> if transient/policy-eligible: next candidate
 -> preserve same run_id, new attempt_id
 -> attach fallback lineage metadata
 -> return normalized envelope
```

Error classes:
- `transient_network`
- `provider_throttle`
- `provider_5xx`
- `policy_denied`
- `invalid_request`
- `tool_runtime_failure`

## 7) Observability Spine

Global IDs:
- `run_id` (AgentAPI run)
- `request_id` (bridge request)
- `attempt_id` (execution attempt)
- `route_id` (provider/account lane)
- `tool_call_id` (MCP/skill event)

Minimum telemetry fields:
- harness profile
- provider/subprovider used
- latency (first token + total)
- input/output tokens
- estimated cost
- fallback depth
- terminal outcome

## 8) Canonical AgentAPI <-> CLIProxyAPI Contract

## 8.1 `ExecutionRequest`

```json
{
  "bridge_schema_version": "v1.0.0",
  "request_id": "req_...",
  "run_id": "run_...",
  "session_id": "sess_...",
  "harness_profile": "codex",
  "actor": {
    "user_id": "u_...",
    "org_id": "org_...",
    "project_id": "proj_...",
    "roles": ["developer"]
  },
  "intent": {
    "capability": "chat_completion",
    "task_type": "codegen",
    "latency_tier": "interactive",
    "quality_tier": "high"
  },
  "model_preferences": {
    "provider_class_order": ["cloud_direct", "cloud_aggregator", "local_inference"],
    "allow_models": ["openai/gpt-5", "anthropic/claude-sonnet"],
    "deny_models": []
  },
  "routing_policy": {
    "budget_usd_max": 2.5,
    "max_fallbacks": 2,
    "retry_policy": "standard",
    "region_hint": "us-east"
  },
  "inputs": {
    "messages": [
      {"role": "system", "content": "..."},
      {"role": "user", "content": "..."}
    ],
    "tools": [
      {
        "name": "search_code",
        "description": "...",
        "schema": {"type": "object", "properties": {"query": {"type": "string"}}}
      }
    ],
    "tool_choice": "auto"
  },
  "context": {
    "env_scope": "project",
    "skills": ["refactor", "test-analysis"],
    "mcp_servers": ["repo-index", "issue-tracker"]
  },
  "stream": true
}
```

## 8.2 `ExecutionResponse` (terminal)

```json
{
  "bridge_schema_version": "v1.0.0",
  "request_id": "req_...",
  "run_id": "run_...",
  "status": "ok",
  "selected_route": {
    "provider_id": "openai",
    "subprovider_id": "acct_team_a",
    "model": "gpt-5"
  },
  "attempts": 1,
  "usage": {
    "input_tokens": 1234,
    "output_tokens": 456,
    "estimated_cost_usd": 0.021
  },
  "output": {
    "message": {"role": "assistant", "content": "..."},
    "tool_calls": []
  },
  "governance_outcome": {
    "budget_check": "pass",
    "rate_limit_check": "pass",
    "fallback_used": false
  }
}
```

## 8.3 Streaming event format

```json
{
  "event_type": "chunk|tool_call|tool_result|route_change|error|done",
  "request_id": "req_...",
  "run_id": "run_...",
  "attempt_id": "att_...",
  "ts": "2026-02-23T00:00:00Z",
  "payload": {}
}
```

## 9) Route Candidate Contract

```json
{
  "route_id": "route_...",
  "provider_id": "openai",
  "subprovider_id": "acct_team_a",
  "provider_class": "cloud_direct",
  "model": "gpt-5",
  "priority": 100,
  "constraints": {
    "requires_region": "us",
    "max_cost_per_1k_tokens": 0.05,
    "supports_tools": true,
    "supports_stream": true
  }
}
```

## 10) Harness Profile Contract

```json
{
  "harness_profile": "codex|claude|droid|antigma|codex_alt",
  "defaults": {
    "intent_capability": "chat_completion",
    "latency_tier": "interactive",
    "quality_tier": "high"
  },
  "policy_overrides": {
    "max_fallbacks": 2,
    "budget_usd_max": 2.5
  },
  "tool_policy": {
    "allowed_tool_sets": ["core", "repo"],
    "requires_confirmation_for": ["shell_write", "network_mutation"]
  }
}
```

## 11) Minimal Interfaces (Go)

```go
package bridge

type ProviderAdapter interface {
    Execute(req ExecutionRequest) (ExecutionResponse, error)
    Stream(req ExecutionRequest, sink EventSink) error
    Capabilities() CapabilityDescriptor
}

type MetaproviderAdapter interface {
    ProviderAdapter
    ResolveSubproviders(req ExecutionRequest) ([]RouteCandidate, error)
}

type Middleware interface {
    Name() string
    Handle(req ExecutionRequest, next Handler) (ExecutionResponse, error)
}

type Handler interface {
    Handle(req ExecutionRequest) (ExecutionResponse, error)
}

type Runtime interface {
    Register(providerID string, adapter MetaproviderAdapter) error
    Execute(req ExecutionRequest) (ExecutionResponse, error)
    Stream(req ExecutionRequest, sink EventSink) error
}
```

## 12) Minimal Interfaces (Python)

```python
from typing import Protocol, Iterable

class ProviderAdapter(Protocol):
    def execute(self, req: dict) -> dict: ...
    def stream(self, req: dict) -> Iterable[dict]: ...
    def capabilities(self) -> dict: ...

class MetaproviderAdapter(ProviderAdapter, Protocol):
    def resolve_subproviders(self, req: dict) -> list[dict]: ...

class Middleware(Protocol):
    def name(self) -> str: ...
    def handle(self, req: dict, next_handler) -> dict: ...

class Runtime(Protocol):
    def register(self, provider_id: str, adapter: MetaproviderAdapter) -> None: ...
    def execute(self, req: dict) -> dict: ...
    def stream(self, req: dict): ...
```

## 13) Integration with thegent and Harnesses

Required shape:
- `thegent` harnesses call one generated bridge client.
- No direct provider API clients in harness codepaths.
- Harness-to-profile mapping is static config + policy, not ad-hoc branches.

```text
thegent command
 -> harness runner
 -> AgentAPI /runs
 -> bridge execute/stream
 -> CLIProxyAPI+Bifrost
 -> providers
```

## 14) Security and Policy Placement

Enforce at AgentAPI + CLIProxyAPI boundaries:
- authn/authz and org scoping at AgentAPI
- budget/rate/quota at CLIProxyAPI middleware
- key/account isolation at route candidate selection
- audit log per run/request/attempt/tool_call id tuple

## 15) Non-Goals

- No LiteLLM short-term compatibility layer in target system.
- No harness-owned routing logic.
- No provider-specific branching in client SDKs/CLI.

## 16) Implementation Phases

Phase 1: Contract freeze
- finalize `ExecutionRequest`, `ExecutionResponse`, streaming events
- publish `v1.0.0` schema artifact

Phase 2: Adapter wiring
- implement `AgentApiMetaProviderAdapter`
- implement `CliproxyMetaProviderAdapter`
- route one harness profile end-to-end

Phase 3: Hardening
- middleware: budget/rate/fallback/telemetry
- fallback lineage and error normalization
- per-provider class policy tuning

Phase 4: Full cutover
- move all harness profiles to bridge
- deprecate direct provider pathways
- keep only bridge contract for API/SDK/CLI/MCP integration points
