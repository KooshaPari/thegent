# AI Gateway Landscape (2026)

> Reference doc for AI agents. Last updated: 2026-02-20.
> Full research: `docs/research/AI_GATEWAY_LANDSCAPE_2026-02-20.md`

---

## Market Map

| Product | Type | Deployment | OpenAI Compat | Key Differentiator |
|---------|------|------------|--------------|-------------------|
| **Bifrost** (Maxim AI) | Infrastructure | Cloud/Edge/On-prem/OSS | Yes | 11µs overhead; OTel+MCP+semantic cache; enterprise governance |
| **LiteLLM** | Infrastructure | Self-hosted (OSS) | Yes | 100+ providers; Python SDK; open-source community |
| **Portkey** | Infrastructure | Both (OSS core) | Yes | 60+ guardrails; virtual keys; 1600+ LLMs; config-driven routing |
| **Helicone** | Observability-first | Both (OSS) | Yes | Async mode (no hot path); edge cache; session tracing; SOC2+HIPAA |
| **Cloudflare AI Gateway** | Infrastructure | SaaS only | Yes | Edge-native; 350+ models; Cloudflare ecosystem integration |
| **Kong AI Gateway** | Infrastructure | Both | Yes | Enterprise API management + AI; plugin ecosystem; MCP plugin |
| **Vercel AI Gateway** | Infrastructure | SaaS only | Yes | Sub-20ms; developer experience; Next.js/React integration |
| **OpenRouter** | Infrastructure | SaaS only | Yes | 300+ models; community; pay-per-use |
| **Not Diamond** | ML Routing | SaaS + VPC | Yes | ML meta-model routing; auto prompt rewriting; agent optimization |
| **Martian** | ML Routing | SaaS + VPC | Yes | Mechanistic interpretability routing; auto model indexing; compliance routing |
| **Unify** | Benchmark Routing | SaaS only | Yes | Provider-level routing; live 10-min benchmarks; quality/cost/latency sliders |
| **Requesty** | Infrastructure | SaaS only | Yes | 500+ models; 8ms P50 (Rust); 40+ metrics; 5% flat markup |
| **Braintrust** | Eval-first | Both (OSS proxy) | Yes | Async online eval; unified reasoning API; eval-native logging |
| **Langfuse** | Observability | Both (OSS) | Via LiteLLM | OTel-native; 50+ integrations; prompt management; scoring |
| **Azure APIM AI Gateway** | Enterprise | Azure cloud/hybrid | Yes | Native Azure auth (MSI); TPM rate limits; semantic cache; Content Safety; MCP |
| **AWS Bedrock + AgentCore** | Enterprise | AWS cloud/VPC | Yes | No-egress VPC; prompt caching (90% cost); AgentCore MCP gateway |
| **Google Vertex AI** | Enterprise | GCP cloud | Yes | Grounding with Google Search; Model Garden; TPU-backed |
| **Fireworks AI** | Inference | SaaS + BYOC | Yes | 250+ tok/s; BYOC inference inside customer VPC; fine-tuning + serving |
| **ZenMux** | Infrastructure | SaaS only | Yes | LLM Insurance (auto-compensation); HLE quality benchmarks |
| **Envoy AI Gateway** | Infrastructure/K8s | Self-hosted K8s (OSS) | Yes | Envoy-native; Gateway API Inference Ext; MCP first-class; OTel+OI |
| **TrueFoundry** | MLOps Platform | Both | Yes | Unified LLM + MCP gateway; MLOps-native; sub-3ms MCP latency |
| **AgentGateway** | Agentic | Self-hosted (OSS) | No (MCP/A2A) | A2A + MCP dual protocol; REST-to-MCP bridge; federated tool registry |
| **Operant AI** | Security | SaaS + Enterprise | No (MCP focus) | Shadow Escape detection; MCP inline redaction; 3D Runtime Defense |
| **IBM API Connect AI** | Enterprise | Multi-deployment | Yes | IBM ecosystem; audit trails; compliance; Watson integration |
| **GitLab AI Gateway** | Bundled | SaaS (GitLab) | Internal | Unified across all GitLab deployment modes for Duo |
| **Tyk AI Gateway** | Infrastructure | OSS + cloud | Yes | AI-assisted API design; traditional API mgmt + LLM routing |
| **Gloo Gateway** (Solo.io) | K8s Infrastructure | Self-hosted K8s | Yes | Envoy-based; Istio integration; function-level routing |

---

## Table Stakes Features (Must-Have for Any Competitive Gateway)

Every serious AI gateway must have all of these. Absence of any is a disqualifier for production use:

1. **OpenAI-compatible API** — drop-in replacement for `openai` SDK; no code changes for end users
2. **Multi-provider support** — minimum: OpenAI, Anthropic, Google, AWS Bedrock, Azure OpenAI
3. **Automatic failover** — detect provider failures and route to backup within milliseconds
4. **Request/response logging** — capture all traffic; content, tokens, latency, cost per request
5. **Per-request cost tracking** — token counting × model pricing = exact cost attribution
6. **Rate limiting** — enforce limits per API key / user / team / model
7. **Load balancing** — distribute across multiple provider endpoints (round-robin, weighted, priority)
8. **Exact-match caching** — avoid re-sending identical requests to providers
9. **Health checks + circuit breakers** — detect unresponsive backends and stop routing to them
10. **Per-key budget enforcement** — hard stop when budget exceeded

---

## Differentiating Features (Competitive Advantages)

Features that fewer than 3 products have; these are current moats or emerging advantages:

### Routing Intelligence
| Feature | Products |
|---------|---------|
| ML meta-model routing (trained, not rule-based) | Not Diamond, Martian |
| Automatic prompt rewriting per model family | Not Diamond only |
| Mechanistic interpretability as routing signal | Martian only |
| Provider-level routing (same model, cheapest host) | Unify only |
| Live benchmark routing signal (10-min refresh) | Unify only |
| Agent workflow / multi-step optimization | Not Diamond |
| Compliance-based model routing | Martian |

### Caching
| Feature | Products |
|---------|---------|
| Semantic caching (embedding-based similarity) | Bifrost, Portkey, Azure APIM, Cloudflare |
| Edge-distributed caching | Helicone, Cloudflare |
| Provider prompt caching integration (Claude/Nova) | AWS Bedrock |
| Eval-result caching | Braintrust |

### Guardrails and Security
| Feature | Products |
|---------|---------|
| 50+ pre-built guardrails (open-source) | Portkey |
| PII detection + auto-redaction | Portkey, Requesty, Operant AI, Azure APIM |
| Prompt injection detection | Portkey, Requesty, Operant AI |
| Jailbreak detection | Portkey, Operant AI |
| Output format validation (JSON, RegEx) | Portkey |
| MCP-specific security (tool poisoning, Shadow Escape) | Operant AI only |
| 3D Runtime Defense for agent traffic | Operant AI only |

### Observability and Evaluation
| Feature | Products |
|---------|---------|
| Async observability (no proxy required) | Helicone only |
| Async online evaluation of production traffic | Braintrust only |
| OTel-native (not adapter) | Langfuse, Envoy, AgentGateway |
| Session/trace tracking for agent flows | Helicone, Langfuse, Braintrust |
| Unified reasoning API abstraction | Braintrust only |
| 40+ observable metrics with custom dimensions | Requesty |

### Cost Governance
| Feature | Products |
|---------|---------|
| Virtual keys with per-project spend limits | Portkey, Bifrost |
| Tag-based cost attribution for chargebacks | LiteLLM, TrueFoundry, Azure APIM |
| LLM Insurance (auto-compensation for quality failures) | ZenMux only |
| Transparent flat-markup pricing | Requesty (5%) |

### Agent and MCP Support
| Feature | Products |
|---------|---------|
| MCP tool routing (agent → tools) | Envoy, TrueFoundry, AgentGateway, Kong, Azure APIM, Bifrost |
| A2A (Agent-to-Agent) protocol support | AgentGateway only |
| REST-to-MCP automatic bridge | AgentGateway only |
| Federated tool registry + discovery | AgentGateway, TrueFoundry |
| Unified LLM + MCP gateway (same control plane) | TrueFoundry, AWS AgentCore |

### Deployment
| Feature | Products |
|---------|---------|
| BYOC (customer's cloud/VPCs) | Fireworks AI, AWS Bedrock |
| Kubernetes Gateway API Inference Extension | Envoy AI Gateway |
| xDS dynamic config (zero-downtime reconfig) | Envoy, AgentGateway |
| Multi-tenancy with resource isolation | AgentGateway, TrueFoundry |
| HIPAA + SOC2 + ISO 27001 | Helicone, Not Diamond |

### Ecosystem / Unique
| Feature | Products |
|---------|---------|
| Grounding with live Google Search | Vertex AI only |
| Native Azure Managed Identity auth | Azure APIM only |
| WebSocket Realtime API + token tracking | Azure APIM only |
| Fine-tuning + gateway (same platform) | TrueFoundry, Fireworks AI |
| AI-assisted API design (LLM generates API specs) | Tyk only |
| Bundled with developer platform | Vercel, GitLab |

---

## Feature Matrix

> Rows = products. Columns = key features. Y = has it, P = partial/plugin, N = no, * = unique.

| Product | Semantic Cache | Guardrails | ML Routing | Prompt Mgmt | MCP/A2A | Eval Integration | Virtual Keys | Budget Mgmt | OTel-Native | Self-Host |
|---------|--------------|------------|-----------|-------------|---------|-----------------|-------------|-------------|------------|-----------|
| Bifrost | Y | P | N | N | MCP | N | Y | Y (hierarchical) | Y | Y |
| LiteLLM | N | P | N | N | N | Via plugins | Y | Y (per-key/team) | Via plugins | Y |
| Portkey | Y | Y (60+) | N | Y | N | N | Y (virtual)* | Y | N | Y (OSS) |
| Helicone | Y (edge) | P | N | Y | N | N | N | N | Y | Y |
| Cloudflare | Y | P | N | N | N | N | N | N | N | N |
| Kong | Y (plugin) | P (plugin) | N | P (plugin) | P (plugin) | N | P | P | N | Y |
| Vercel | Y | P | N | N | N | N | N | N | N | N |
| OpenRouter | N | N | P | N | N | N | N | N | N | N |
| Not Diamond | N | N | Y* (ML) | Y* (auto-rewrite) | N | N | N | N | N | VPC |
| Martian | N | P (compliance) | Y* (interp) | N | N | N | N | N | N | VPC |
| Unify | N | N | Y* (live BM) | N | N | N | N | N | N | N |
| Requesty | Y | Y (PII+inj) | P (latency) | N | N | N | N | Y (caps) | N | N |
| Braintrust | Y | N | N | N | N | Y* (async) | N | N | N | Y (OSS) |
| Langfuse | N | N | N | Y | N | Y (scoring) | N | N | Y* | Y |
| Azure APIM | Y (semantic) | Y (Content Safety) | N | P | Y (MCP) | N | N | Y (TPM) | N | Hybrid |
| AWS Bedrock | Y* (prompt) | P | N | N | Y* (AgentCore) | N | N | Y (IAM) | CloudWatch | VPC |
| Vertex AI | N | Y (Safety) | N | N | N | N | N | Y (quotas) | N | N |
| Fireworks | N | N | N | N | N | N | N | N | N | BYOC |
| ZenMux | N | N | P (task) | N | N | Y* (HLE) | N | N | N | N |
| Envoy AI GW | N | N | N | N | Y (MCP) | N | N | Y (token RL) | Y | Y |
| TrueFoundry | N | Y | N | N | Y* (LLM+MCP) | N | N | Y | Y | Y |
| AgentGateway | N | N | N | N | Y* (A2A+MCP) | N | N | N | Y | Y |
| Operant AI | N | Y* (MCP sec) | N | N | Y* (MCP security) | N | N | N | Y (traffic) | N |

---

## Emerging Trends 2026

1. **MCP is winning agent-tool connectivity** — nearly every gateway is adding MCP support or already has it. The Linux Foundation accepted MCP under open governance. MCP-native gateways (AgentGateway, TrueFoundry, Operant, Envoy) are a fast-growing sub-category.

2. **A2A emerging alongside MCP** — Google's Agent-to-Agent protocol is the second standard. AgentGateway is first open-source implementation. Expect rapid adoption in H1 2026.

3. **Agentic routing = multi-step optimization** — routing for agents means optimizing entire task sequences, not individual LLM calls. Not Diamond and TrueFoundry are first movers. This will be standard by late 2026.

4. **ML routing > rule-based routing** — Not Diamond (ML meta-model) and Martian (mechanistic interpretability) demonstrate that learned routing outperforms static benchmark lookup for production tasks. Routing intelligence is increasingly a product differentiator.

5. **Unified LLM + tool gateway** — the next architecture standard: one gateway for both LLM routing and agent-tool (MCP) routing. TrueFoundry and AWS AgentCore are first; this will become expected.

6. **Security specialization** — general guardrails (PII, injection) are table stakes. MCP-specific security (tool poisoning, Shadow Escape) is a new category. Operant AI is the specialist; general gateways are catching up.

7. **Hyperscaler pressure** — AWS/Azure/GCP all have compelling native gateway stories. Independent gateways must win on cross-cloud portability, routing intelligence, and developer experience.

8. **Performance in microseconds** — Rust/Go implementations push overhead below 1ms. Python gateways (LiteLLM) are losing high-throughput scenarios. Performance differentiation is now at 11µs (Bifrost) vs 8ms P50 (Requesty) vs higher.

9. **Eval-native routing** — gateways that score production traffic asynchronously (Braintrust) enable routing based on actual quality metrics. Expect eval-driven routing as a feature in 2026.

10. **Multimodal as table stakes** — vision/audio/video routing must be handled transparently. Gateways that are text-only are becoming incomplete.

---

## thegent's Position and Gap Summary

### Where thegent currently competes
thegent is building an LLM routing proxy/gateway with routing, observability, and cost governance. Based on codebase analysis, thegent has:
- Multi-provider routing (LiteLLM integration)
- Cost-aware router (`crates/thegent-router/`, `src/thegent/routing/`)
- Observability hooks
- Cache management (`crates/thegent-cache/`)
- Shared memory for performance (`crates/thegent-shm/`)
- Quality governance (hook pipeline)

### Gaps vs market leaders

**Critical gaps (table stakes missing or weak):**
- Exact-match + semantic caching needs validation against production workloads
- Guardrails (PII redaction, prompt injection) — not yet a first-class feature
- Virtual key management with per-key budget enforcement
- Health check / circuit breaker reliability pipeline

**High-value gaps (differentiators to build):**
1. **Semantic caching** with embedding-based similarity — reduce costs 70-95% for chatbot-style workloads
2. **ML routing layer** — integrate Not Diamond or build task-classification routing (cheap → expensive model selection)
3. **MCP gateway** — first-class agent-tool routing; this is the growth vector for 2026
4. **Guardrails** — even 10 guardrails (PII, injection, jailbreak, JSON validation) beats most competitors except Portkey
5. **Prompt management** — versioned templates with A/B testing; prevents prompt drift in production
6. **Online eval integration** — score production traffic asynchronously; enables eval-driven routing
7. **A2A protocol** — position thegent for the agentic routing future

**Strategic positioning options:**
- **Option A: Developer-first open-source** — compete with LiteLLM/Portkey on features; win on Rust performance + developer experience
- **Option B: Routing intelligence** — integrate Not Diamond/Martian for ML routing; differentiate on intelligence vs infrastructure
- **Option C: Agentic-native gateway** — lead on MCP+A2A; become the routing layer for multi-agent systems
- **Option D: Observability-integrated** — tight coupling between routing decisions and eval results; Braintrust model at the gateway layer

thegent's Rust/native crate architecture positions it well for Option A (performance) and Option C (agentic), with Option D as a natural synergy given the existing hook/quality pipeline.
