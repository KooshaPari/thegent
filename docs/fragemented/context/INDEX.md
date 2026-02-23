# Context Documentation Index

Authoritative reference catalog for all technologies integrated with thegent.

Each context doc is a **standalone, technically authoritative reference** for implementing against that technology. See `GOVERNANCE.md` for standards and format requirements.

---

## Index by Technology

| Technology | File | Category | Priority | Last Updated | Status |
|-----------|------|----------|----------|--------------|--------|
| OpenRouter | `openrouter.md` | API Gateway | P0 | 2026-02-20 | ✅ Current |
| Claude Code | `claude-code.md` | Agent Harness | P0 | 2026-02-20 | ✅ Current |
| Ante | `ante.md` | Agent Harness | P0 | 2026-02-20 | ✅ Current |
| Ante Analysis | `ante-analysis.md` | Strategic Analysis | P1 | 2026-02-20 | ✅ Current |
| process-compose | `process-compose.md` | Infrastructure | P1 | 2026-02-20 | ✅ Current |
| WorkOS | `workos.md` | Auth Provider | P1 | 2026-02-20 | ✅ Current |
| WorkOS AuthKit | `workos-authkit.md` | Auth Provider | P1 | 2026-02-20 | ✅ Current |
| FastMCP | `fastmcp.md` | Core Protocol/SDK | P0 | 2026-02-20 | ✅ Current |
| Vercel AI SDK | `vercel-ai-sdk.md` | AI SDK | P1 | 2026-02-20 | ✅ Current |
| Temporal (temporalio) | `temporalio.md` | Workflow Orchestration | P1 | 2026-02-20 | ✅ Current |
| NATS (nats-py) | `nats.md` | Messaging | P1 | 2026-02-20 | ✅ Current |
| tRPC | `trpc.md` | API Layer | P1 | 2026-02-20 | ✅ Current |

---

## Index by Category

### Agent Harnesses (P0 - Critical)

These are the harnesses thegent integrates with for agent execution.

| Technology | File | Priority | Notes |
|-----------|------|----------|-------|
| Ante | `ante.md` | P0 | Rust terminal agent; provider-agnostic with skills system |
| Ante Analysis | `ante-analysis.md` | P1 | Strategic analysis of ANTE's differentiators vs Claude Code/Codex |
| Claude Code | `claude-code.md` | P0 | Anthropic's agentic CLI; conversational coding |
| Codex | `codex.md` | P0 | OpenAI's agent IDE (planned) |
| Gemini CLI | `gemini-cli.md` | P0 | Google's agent CLI (planned) |
| Copilot | `copilot.md` | P0 | Microsoft's agent harness (planned) |

**Coverage**: 3/6 docs exist (Ante, Ante Analysis, Claude Code). Codex, Gemini CLI, Copilot needed before support.

### API Gateways & Proxies (P0 - Critical)

These are routing, aggregation, and relay layers for model access.

| Technology | File | Priority | Notes |
|-----------|------|----------|-------|
| OpenRouter | `openrouter.md` | P0 | Unified gateway for 400+ models; cost routing |
| LiteLLM Router | `litellm.md` | P0 | Multi-provider routing library (planned) |
| CLIProxy | `cliproxy.md` | P0 | thegent's own routing proxy (planned) |

**Coverage**: 1/3 docs exist. LiteLLM and CLIProxy needed for routing layer.

### Core Protocols (P0 - Critical)

These are the fundamental protocols thegent implements or relies on.

| Technology | File | Priority | Notes |
|-----------|------|----------|-------|
| Model Context Protocol (MCP) | `mcp-protocol.md` | P0 | Tool system; tool calling, resource access |
| FastMCP | `fastmcp.md` | P0 | Python MCP framework — 3.0 GA (2026-02-18) ✅ |
| OpenAI Responses API | `openai-responses-api.md` | P0 | Native tool/response formats |

**Coverage**: 2/3 docs exist.

### Core SDKs & Libraries (P0 - Critical)

These are the SDKs and libraries thegent depends on.

| Technology | File | Priority | Notes |
|-----------|------|----------|-------|
| FastMCP | `fastmcp.md` | P0 | See Protocols section above |
| OpenAI Python SDK | `openai-python.md` | P0 | Python client for OpenAI API (planned) |
| Anthropic Python SDK | `anthropic-python.md` | P0 | Python client for Claude API (planned) |

**Coverage**: 0/3 docs exist. All needed for SDK integration.

### Auth Providers (P1 - High Priority)

Authentication and identity providers.

| Technology | File | Priority | Notes |
|-----------|------|----------|-------|
| WorkOS | `workos.md` | P1 | Enterprise auth (SSO, SAML, OIDC) |
| WorkOS AuthKit | `workos-authkit.md` | P1 | Python SDK + Next.js auth flows ✅ |
| Anthropic Console API | `anthropic-console.md` | P1 | API key management (planned) |

**Coverage**: 2/3 docs exist.

### Infrastructure (P1 - High Priority)

System tooling and service orchestration.

| Technology | File | Priority | Notes |
|-----------|------|----------|-------|
| process-compose | `process-compose.md` | P1 | YAML-based service orchestrator; process deps, health checks, REST API ✅ |
| Nix | `nix.md` | P1 | Package management and reproducible builds (planned) |
| Docker | `docker.md` | P1 | Container runtime (planned) |

**Coverage**: 1/3 docs exist (process-compose). Nix and Docker planned.

### Workflow & Messaging (P1 - High Priority)

Distributed workflow execution and messaging systems found in trace and thegent.

| Technology | File | Priority | Notes |
|-----------|------|----------|-------|
| Temporal (temporalio) | `temporalio.md` | P1 | Durable workflow orchestration; Python SDK 1.23.0 ✅ |
| NATS (nats-py) | `nats.md` | P1 | Cloud-native messaging; JetStream, KV store ✅ |

**Coverage**: 2/2 docs exist.

### TypeScript API Layer (P1 - High Priority)

TypeScript API tooling used in trace frontend.

| Technology | File | Priority | Notes |
|-----------|------|----------|-------|
| tRPC | `trpc.md` | P1 | End-to-end typesafe TypeScript API; v10.45.2 ✅ |
| Vercel AI SDK | `vercel-ai-sdk.md` | P1 | AI provider abstraction; SDK 6.0.94 ✅ |

**Coverage**: 2/2 docs exist.

### Communication & Data (P1 - High Priority)

Data serialization and communication protocols.

| Technology | File | Priority | Notes |
|-----------|------|----------|-------|
| JSON Schema | `json-schema.md` | P1 | Validation and type specification (planned) |
| Protocol Buffers | `protobuf.md` | P1 | Efficient serialization (planned) |

**Coverage**: 0/2 docs exist.

### Optional Integrations (P2 - Nice to Have)

Create as needed when implementing these integrations.

| Technology | File | Priority | Notes |
|-----------|------|----------|-------|
| Stripe | (not created) | P2 | Billing and payment processing |
| PostHog | (not created) | P2 | Product analytics |
| Grafana | (not created) | P2 | Metrics and monitoring visualization |
| GitHub API | (not created) | P2 | Repository and PR operations |
| GitLab API | (not created) | P2 | Repository and MR operations |

---

## Coverage Summary

### Current Coverage

```
P0 (Critical)    4/8 docs        50%    ⬆️ Improving (Ante + Claude Code + OpenRouter + FastMCP)
P1 (High)        9/12 docs       75%    ⬆️ Strong (WorkOS + AuthKit + process-compose + Temporal + NATS + tRPC + Vercel AI SDK + Ante Analysis)
P2 (Optional)    0/0 docs        N/A    ⏭️ On-demand
────────────────────────────────────
Total            13/20 planned    65%    ⬆️ Strong progress
```

### Priority Roadmap

**Phase 1 (Remaining P0)** - Complete critical coverage
1. [x] FastMCP (`fastmcp.md`) - Core protocol/SDK ✅
2. [ ] MCP (`mcp-protocol.md`) - Tool system foundation (exists, verify completeness)
3. [ ] Codex (`codex.md`) - Second harness (exists, verify completeness)
4. [ ] LiteLLM (`litellm.md`) - Routing layer (exists, verify completeness)

**Phase 2 (Remaining P1)** - Fill gaps
5. [ ] Anthropic Console API (`anthropic-console.md`)
6. [ ] Nix (`nix.md`) - Build reproducibility
7. [ ] Docker (`docker.md`) - Container runtime

**Phase 3 (On-demand P2)** - Add as integrations expand
8. [ ] Stripe, PostHog, Grafana, GitHub API

---

## Staleness Report

Generated: 2026-02-20

| Doc | Last Verified | Age | Status | Action |
|-----|---------------|-----|--------|--------|
| openrouter.md | 2026-02-20 | 0 days | ✅ Current | None |
| claude-code.md | 2026-02-20 | 0 days | ✅ Current | None |
| ante.md | 2026-02-20 | 0 days | ✅ Current | None |
| ante-analysis.md | 2026-02-20 | 0 days | ✅ Current | None |
| workos.md | 2026-02-20 | 0 days | ✅ Current | None |
| workos-authkit.md | 2026-02-20 | 0 days | ✅ Current | None (updated with Python SDK) |
| fastmcp.md | 2026-02-20 | 0 days | ✅ Current | Updated for FastMCP 3.0 GA |
| process-compose.md | 2026-02-20 | 0 days | ✅ Current | None |
| vercel-ai-sdk.md | 2026-02-20 | 0 days | ✅ Current | None (new) |
| temporalio.md | 2026-02-20 | 0 days | ✅ Current | None (new) |
| nats.md | 2026-02-20 | 0 days | ✅ Current | None (new) |
| trpc.md | 2026-02-20 | 0 days | ✅ Current | None (new) |

**Target**: All P0/P1 docs < 90 days old. Re-verify in May 2026.

---

## How to Use This Index

### For Implementers

**Before starting an integration:**
1. Find the technology in the index
2. Check if context doc exists
3. If not: Create it first (follow `CONTEXT_DOCS_PROCESS.md`)
4. If exists: Read it and follow the documented API/process
5. Add code comments linking to the doc

### For Tech Leads

**Monthly maintenance:**
1. Check Coverage Summary above
2. For any doc > 90 days stale: Trigger refresh
3. For any P0 technology without a doc: Create issue to create one
4. Update this index with latest status

### For Doc Authors

**When creating/updating a doc:**
1. Write following `GOVERNANCE.md` format
2. Test all code examples
3. Add entry to this index (or update existing entry)
4. Link from `docs/governance/CONTEXT_DOCS_PROCESS.md` if it's a new technology

---

## Archival

Technologies that are deprecated from thegent are moved to `archive/` and marked below.

| Technology | File | Deprecated | Reason |
|-----------|------|-----------|--------|
| (none yet) | | | |

---

## See Also

- `GOVERNANCE.md` - Context doc standards and format specification
- `docs/governance/CONTEXT_DOCS_PROCESS.md` - Step-by-step creation and update process
- `docs/governance/ARCHITECTURAL_GOVERNANCE.md` - Technology decisions and rationale

---

## Quick Links to Key Docs

### Essential Reading for Integration Work

- **Getting started**: `claude-code.md` (how the harness works)
- **Model access**: `openrouter.md` (unified API gateway)
- **Auth setup**: `workos.md` (enterprise authentication)
- **Tool system**: (MCP doc - planned)

### Cross-References

Most context docs reference each other. Common patterns:

- Harness docs link to SDK/protocol docs
- Protocol docs link to implementation examples
- Auth docs link to harness integration guides

Use Ctrl+F to search within this index and linked docs.
