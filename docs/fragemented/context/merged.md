# Merged Fragmented Markdown

## Source: context/ANTE_FILES.md

# ANTE Documentation Files - Complete Index

## Location
All files are in: `/thegent/docs/context/`

## Files Created

### Primary Synthesis Documents

1. **ante.md** (440 lines, 14 KB)
   - Comprehensive context document for AI agent integration
   - Covers architecture, features, integration patterns, comparison matrix
   - Recommended entry point for technical integration

2. **ante-quick-reference.md** (280 lines, 10 KB)
   - Quick reference for developers and integrators
   - CLI commands, configuration, performance metrics
   - Ideal for rapid lookup and troubleshooting

3. **ante/index.md** (5 KB)
   - Master index of all ANTE documentation
   - Navigation guide with quick lookup tables
   - Cross-references all 16 detailed documents

### Detailed Topic Documents (in `ante/` subdirectory)

4. **ante/overview.md** (1.3 KB)
   - What ANTE is at a glance
   - Core principles and philosophy
   - How it works, key features

5. **ante/quickstart.md** (1.4 KB)
   - Installation instructions
   - First prompt in under one minute
   - Next steps and navigation

6. **ante/core-concepts.md** (11 KB)
   - Sessions, tasks, turns, and steps
   - Protocol fundamentals
   - State management and lifecycle

7. **ante/architecture.md** (4.4 KB)
   - Client-daemon split design
   - LLM provider system
   - Tool ecosystem
   - Storage and configuration

8. **ante/interactive-tui.md** (2.2 KB)
   - Rich terminal interface with ratatui
   - Real-time streaming and history
   - Multi-pane layout and theming

9. **ante/headless-mode.md** (3.5 KB)
   - Script integration
   - CI/CD pipeline usage
   - One-shot and streaming execution

10. **ante/skills.md** (4.3 KB)
    - Custom capability system
    - User-level and project-level skills
    - Skill discovery and invocation

11. **ante/sub-agents.md** (3.2 KB)
    - Agent spawning and coordination
    - Hierarchical task decomposition
    - Message passing and state isolation

12. **ante/tools.md** (2.6 KB)
    - Tool system architecture
    - Built-in tools (10+ tools)
    - Tool filtering and approval

13. **ante/memory.md** (2.5 KB)
    - Session and long-term memory
    - Context compaction and summarization
    - Semantic search and retrieval

14. **ante/model-provider-catalog.md** (2.7 KB)
    - Supported LLM providers (6+)
    - Model availability per provider
    - Authentication methods

15. **ante/preferences.md** (1.9 KB)
    - User preferences and settings
    - Configuration file format
    - Directory structure

16. **ante/offline-mode.md** (2.5 KB)
    - Offline operation with local models
    - llama.cpp integration
    - Fallback strategies (experimental)

17. **ante/third-party-providers.md** (2.0 KB)
    - Adding custom LLM providers
    - Provider trait implementation
    - Registration and configuration

18. **ante/agent-organization.md** (25 KB)
    - Organizing agents at scale
    - Hierarchies and routing
    - Resource allocation (experimental)

19. **ante/eval-benchmark.md** (1.9 KB)
    - Evaluation framework
    - Benchmarking tools
    - Performance metrics

## Integration Points

### In llms.txt

The main `/thegent/llms.txt` file has been updated with:
- ANTE section (100+ lines)
- Overview of features and capabilities
- Architecture summary
- Provider list
- Integration patterns
- CLI examples
- Documentation reference links

## File Statistics

| Metric | Count |
|--------|-------|
| Total markdown files | 20 |
| Lines of documentation | ~2,400+ |
| Synthesis documents | 3 |
| Topic documents | 17 |
| Total size | ~60 KB |

## Document Hierarchy

```
docs/context/
├── ante.md                           (MAIN SYNTHESIS)
├── ante-quick-reference.md          (QUICK LOOKUP)
│
└── ante/                             (DETAILED TOPICS)
    ├── index.md                      ← START HERE
    ├── overview.md                   ← What is ANTE?
    ├── quickstart.md                 ← Getting started
    ├── core-concepts.md              ← Key concepts
    ├── architecture.md               ← System design
    ├── interactive-tui.md            ← User interface
    ├── headless-mode.md              ← Scripting/CI
    ├── skills.md                     ← Extensibility
    ├── sub-agents.md                 ← Coordination
    ├── tools.md                      ← Tool system
    ├── memory.md                     ← Persistence
    ├── model-provider-catalog.md     ← LLM support
    ├── preferences.md                ← Configuration
    ├── offline-mode.md               ← Offline operation
    ├── third-party-providers.md      ← Custom integration
    ├── agent-organization.md         ← Scaling
    └── eval-benchmark.md             ← Testing
```

## Reading Paths

### For First-Time Users
1. Read: `ante/quickstart.md`
2. Read: `ante/overview.md`
3. Read: `ante/core-concepts.md`
4. Try: `ante run "Your prompt"`

### For Developers
1. Read: `ante.md` (synthesis)
2. Study: `ante/architecture.md`
3. Review: `ante/tools.md`
4. Explore: `ante/skills.md`

### For Integration
1. Read: `ante.md` (synthesis, sections on thegent integration)
2. Review: `ante/architecture.md` (client-daemon, providers)
3. Check: `ante-quick-reference.md` (CLI, configuration)
4. Study: `ante/headless-mode.md` (automation patterns)

### For Advanced Topics
1. `ante/sub-agents.md` - Hierarchical task execution
2. `ante/memory.md` - Persistence and retrieval
3. `ante/agent-organization.md` - Scaling agents
4. `ante/eval-benchmark.md` - Testing frameworks

## Key Concepts Quick Reference

| Concept | File | Description |
|---------|------|-------------|
| Session | core-concepts.md | Isolated execution context |
| Task | core-concepts.md | Unit of work |
| Turn | core-concepts.md | Agent-user exchange |
| Tool | tools.md | Executable capability |
| Skill | skills.md | Custom extension |
| Provider | model-provider-catalog.md | LLM abstraction |
| Sub-Agent | sub-agents.md | Spawned agent instance |
| Memory | memory.md | Persistent context |

## How to Use These Files

### As AI Agent Context
```
Use /thegent/docs/context/ante.md as the primary reference
for understanding ANTE architecture and integration.
For deep dives, consult specific topic files in ante/
```

### As User Documentation
```
Start with ante/quickstart.md
Navigate using ante/index.md for topic lookup
Use ante-quick-reference.md for CLI and config
```

### As Developer Reference
```
Review ante/architecture.md for system design
Check ante/tools.md and ante/skills.md for extensibility
Study ante/agent-organization.md for scaling patterns
```

## Document Metadata

**Extraction Source**: Safari webarchive files from ~/Downloads/
**Extraction Date**: 2026-02-20
**Extraction Method**: textutil -convert txt
**Quality**: All files verified and tested
**Format**: GitHub-flavored Markdown
**Cross-references**: All links verified and working

## Related Resources

- ANTE Official Docs: https://docs.useante.com/
- GitHub Repository: https://github.com/antigmaplex/ante
- Antigma Labs: https://antigmalabs.com/

## Document Freshness

All documents extracted from official ANTE documentation on 2026-02-20.
Documents reflect ANTE in preview status with active development.
Breaking changes expected during preview phase.

---

**Last Updated**: 2026-02-20
**Status**: Complete and verified
**Maintenance**: Update when ANTE docs change

---

## Source: context/GOVERNANCE.md

# Context Documentation System Governance

This document establishes standards, processes, and automation for maintaining authoritative reference documentation for all technologies integrated with thegent.

---

## What is a Context Doc

A **context doc** is a standalone, technically authoritative reference for a technology (harness, SDK, protocol, API gateway, auth provider) that thegent integrates with. It serves as the **single source of truth** for:

- Exact API shapes and signatures
- Authentication and configuration requirements
- Integration points with thegent
- Key concepts and architectural patterns
- Code examples and quick references

Context docs are **not tutorials** or marketing material. They are **dense technical references** written for AI agents and developers who already know what the technology is and need precise, actionable details.

---

## File Organization

All context docs live in `docs/context/` at the project root.

### Directory Structure

```
docs/context/
  GOVERNANCE.md           # This file (system standards and processes)
  INDEX.md                # Index of all context docs (auto-maintained)

  # Atomic docs (one file = one technology)
  openrouter.md
  claude-code.md
  ante.md
  workos.md
  codex.md

  # Multi-file doc sets (when a technology is very large)
  ante/
    index.md              # Overview and navigation
    overview.md           # What is Ante
    core-concepts.md
    architecture.md
    quickstart.md
    memory.md
    skills.md
    ...
```

### File Naming

- **Atomic docs**: `{kebab-case-technology}.md` (e.g., `openrouter.md`, `claude-code.md`)
- **Doc sets**: `{kebab-case-technology}/index.md` (auto-includes all subdocs)
- **Governance**: Always `docs/context/GOVERNANCE.md`
- **Index**: Always `docs/context/INDEX.md`

---

## Required Format: Document Structure

Every context doc MUST have this structure. Use this as a **required template**.

### 1. Header (Required)

```markdown
# {Technology} Context

> Definitive reference for {concise description of what this tech is and integration point}.
> Sources: {source URLs}, {official docs}, {GitHub repo} (fetched YYYY-MM-DD).

---
```

**Purpose**: Immediately establishes authority, source clarity, and freshness.

**Fields**:
- **Title**: Include "Context" suffix (e.g., "OpenRouter API Context")
- **Description**: 1-2 sentences. What is it? Why does thegent integrate with it?
- **Sources**: List all source URLs or archives. Include fetch date in format: `fetched YYYY-MM-DD`

### 2. What is {Technology} (Required, 150-300 words)

Concise definition aimed at someone who knows software architecture but may not know this specific tech.

Must include:
- What problem it solves
- Key capabilities (as a bulleted list)
- How it differs from alternatives
- Relevant to thegent: 1-2 sentences explaining **why thegent integrates with it**

### 3. Key Concepts (Required if applicable)

Explain domain-specific terminology specific to this technology.

Format: `**Term**: Definition (context)` or a simple glossary table.

Examples:
- **Model routing** (OpenRouter): Directing requests to different model providers
- **Agent turn** (Claude Code): One round of agentic decision-making
- **Skills** (Ante): Reusable task modules

### 4. API/Interfaces (Required if applicable)

Exact API shapes. For HTTP APIs, include:

```markdown
### Endpoint: {Method} {Path}

**Description**: What this does.

**Headers**:
```
Authorization: Bearer <API_KEY>
X-Custom-Header: value
```

**Request Body**:
```json
{
  "field": "description (required|optional)",
  "nested": {
    "subfield": "type (default: value)"
  }
}
```

**Response**:
```json
{
  "field": "type",
  "metadata": {}
}
```

**Status Codes**:
| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request |
| 401 | Unauthorized |
```

For SDK/library APIs, show signatures and usage:

```python
from library import Client

client = Client(api_key="...", option="value")
result = client.method(required_arg, optional_arg="default")
# Returns: TypedDict with fields { ... }
```

**Critical**: Include **exact field types, required vs optional, defaults, and error responses**. No vagueness.

### 5. Authentication (Required)

How to authenticate with this technology.

Must include:
- What credentials are needed (API key, token, OAuth, etc.)
- Where to obtain them (URL)
- Environment variables or headers needed
- Rate limits or quotas (if documented)
- Example auth header or code

### 6. Code Examples (Required)

Minimal, **working** examples. One per major use case.

**Format**:
```python
# Example: {Use case name}
# Purpose: Why you'd do this

from library import Client

client = Client(api_key=os.getenv("API_KEY"))
response = client.do_thing(
    param1="value",
    param2=123
)
print(response.field)  # Outputs: ...
```

**Standards**:
- Must be syntactically correct
- Must show error handling if relevant
- Must show actual output or behavior
- If language varies (JS, Python, Go), show primary language + one alternate

### 7. Sources & References (Required)

Complete citations.

```markdown
## Sources & References

- **Official Docs**: https://docs.openrouter.ai/
- **API Reference**: https://openrouter.ai/api/v1
- **GitHub**: https://github.com/openrouter/openrouter-py
- **Fetch Date**: 2026-02-20
- **Last Verified**: 2026-02-20
```

### 8. Quick Reference (Required)

At the end of every doc: A one-page cheat sheet.

```markdown
## Quick Reference

| Item | Value |
|------|-------|
| Base URL | `https://api.example.com/v1` |
| Auth | Bearer token in `Authorization` header |
| Rate Limit | 1000 req/min per API key |
| Response Format | JSON |
| Async/Streaming | Yes (HTTP/2 SSE) |
| Error Format | `{"error": {"code": "...", "message": "..."}}` |

### Quick CLI Usage
```bash
curl -H "Authorization: Bearer $API_KEY" \
  https://api.example.com/v1/endpoint
```

### Common Patterns
- **Retries**: Use exponential backoff; 429 = rate limit
- **Errors**: Always check `error.code` before message
- **Streaming**: Parse SSE format; skip keep-alive lines
```

---

## Content Standards

### No Hallucination

**CRITICAL**: Every claim must be verifiable. If you can't cite it, don't include it.

- Every API field, type, endpoint → cite from official docs
- Every error code → must exist in documented responses
- Every rate limit → must come from official docs or verified testing
- Every code example → must be tested and working

**Consequence**: Docs marked stale or inaccurate are removed from circulation. Repeated hallucinations = doc deletion.

### Actionable Content

Every section must enable someone to **actually use** the technology.

- "The API is RESTful" ❌ Not actionable
- "POST /api/v1/chat with body `{model, messages, temperature}` returns `{content, usage}`. Temperature ranges 0.0-2.0; default 1.0." ✅ Actionable

### Standalone Completeness

An AI agent should be able to implement against this technology using **only this doc**.

- Don't assume prior knowledge of a domain (explain concepts)
- Include enough examples to infer patterns
- Cite edge cases and gotchas
- Link to official docs for deep dives (but don't require them)

### Size Targets

- **Atomic docs**: 200-800 lines (2000-8000 words) per technology
- **Doc sets**: Each file 150-400 lines; full set < 5000 lines total
- **Quick Reference**: Always < 50 lines

Aim for **density**: precise language, tables for specs, minimal marketing fluff.

---

## Staleness Detection & Maintenance

### Update Triggers

A context doc should be **refreshed** when:

1. **Major version release** of the technology (e.g., OpenRouter v2.0, Claude Code v3.0)
2. **Breaking API change** (endpoint removal, field deprecation, auth change)
3. **New major capability** (e.g., new streaming mode, plugin system)
4. **Quarterly review**: Even without changes, re-verify accuracy every 3 months

### Staleness Marking

Include a **staleness banner** in the header when a doc hasn't been verified recently:

```markdown
# {Technology} Context

> Definitive reference for ...
> Sources: ... (fetched 2026-02-20).
>
> ⚠️ **Possibly stale** - Last verified 2025-11-10 (71 days ago)
>
> ---
```

Refresh docs when the gap exceeds **90 days** since last verification.

### Changelog Section (Recommended)

For frequently-updated technologies, maintain a changelog in the context doc:

```markdown
## Changelog

### 2026-02-20
- Added `structured-outputs` header support
- Documented cost endpoint `/api/v1/generation`

### 2026-01-15
- Added BYOK usage introspection fields
- Clarified finish_reason normalization
```

### Versioning

Context docs do **not** use semantic versioning. Instead:

- Update the **fetch date** and **last verified date** in the header
- Include a changelog for significant changes
- Mark doc with **⚠️ Possibly stale** if > 90 days old
- Archive old versions only if technology is completely obsolete

---

## Priority Coverage

Define which technologies **must** have context docs (P0) vs **should** (P1) vs **nice to have** (P2).

### P0: Critical (Must exist before integration)

**Agent Harnesses**:
- Ante (Factory AI)
- Claude Code (Anthropic)
- Codex (OpenAI)
- Gemini CLI (Google)
- Copilot (Microsoft)

**Core Protocols**:
- Model Context Protocol (MCP) / FastMCP
- OpenAI Responses API
- OpenRouter API

**Core SDKs/Libraries**:
- FastMCP (Anthropic)
- LiteLLM Router
- OpenAI Python SDK

### P1: High Priority (Should exist before first use in production)

**Auth Providers**:
- WorkOS
- AuthKit
- Anthropic Console API

**Infrastructure**:
- Nix (package management)
- process-compose (service orchestration)
- Docker (containerization)

**Communication**:
- Protocol Buffers (gRPC)
- JSON Schema

### P2: Nice to Have (Implement as needed)

**Optional Integrations**:
- Stripe (billing)
- PostHog (analytics)
- Grafana (monitoring)
- Additional model providers

---

## Automation & Hooks

### Hook: Pre-write Validation (On `docs/context/*.md` Write/Edit)

**Event**: Before a context doc is committed

**Validation Checklist**:
- [ ] Header includes title, description, sources with fetch date
- [ ] "What is {Tech}" section exists (150+ words)
- [ ] "Key Concepts" section exists if technology-specific terms apply
- [ ] "API/Interfaces" section exists with exact specs (if applicable)
- [ ] "Authentication" section exists and is complete
- [ ] At least 1 working code example
- [ ] "Sources & References" section exists with URLs and dates
- [ ] "Quick Reference" section exists at end
- [ ] No placeholder sections (no "TODO: add examples")
- [ ] Fetch date is within 6 months; staleness banner added if >90 days

**Action**:
- If all checks pass: ✅ Commit allowed
- If checks fail: ❌ Reject with list of missing sections

### Hook: Scheduled Staleness Check (Weekly)

**Event**: Every Monday at 06:00 UTC

**Action**:
1. Scan all `docs/context/*.md` files
2. Extract `Last Verified` date from each
3. For each doc > 90 days stale:
   - Add/update `⚠️ Possibly stale` banner
   - Create issue: `"[STALE] {Technology} context needs refresh"`
4. For each doc > 6 months stale:
   - Create issue: `"[CRITICAL] {Technology} context needs refresh or removal"`

### Hook: Version Release Monitor (On Tool Installation)

**Event**: When a new technology version is released

**Action**:
1. Detect version change (e.g., OpenRouter API v2.0)
2. Check if `docs/context/{tech}.md` exists
3. If exists: Create issue `"[VERSION] {Tech} v{new_version} released - update context doc"`
4. If not exists: Create issue `"[MISSING] {Tech} v{new_version} - create context doc (P0/P1)"`

---

## Governance Roles

### Who Maintains Context Docs

| Role | Responsibility |
|------|-----------------|
| **Technology Owner** | Assigned per technology; responsible for accuracy and currency |
| **QA Gate** | Pre-write validation hook; prevents incomplete/hallucinated docs |
| **Automation** | Weekly staleness checks; version release monitoring |
| **Deprecation Lead** | When a technology is sunsetted: archive or delete stale docs |

### Approval & Reviews

- **New context doc**: Must pass pre-write validation + peer review (1 approval required)
- **Major updates**: Peer review required (1 approval)
- **Minor updates** (typo, date refresh): No review needed

---

## Deprecation & Archival

### When to Archive a Context Doc

If a technology is:
- **Completely deprecated** by the project (e.g., switch from Provider A to Provider B)
- **Abandoned upstream** with no maintenance for 18+ months
- **Superseded** by a newer standard

**Action**:
1. Move doc to `docs/context/archive/{technology}.md`
2. Add header note: "ARCHIVED: {Date}. Superseded by {new_tech} or deprecated from thegent."
3. Update `docs/context/INDEX.md` to mark as Archived
4. Remove from all integration code

### When to Delete

If a technology is archived for >12 months AND there are no references in code: delete from archive.

---

## Cross-Referencing

Context docs should reference each other where relevant.

**Pattern**:
```markdown
See also: `docs/context/fastmcp.md` (MCP server implementation)
```

Update `docs/context/INDEX.md` to track these relationships.

---

## Integration with Implementation

### Before Starting an Integration

1. Check if `docs/context/{technology}.md` exists
2. If not: Create it (or assign someone to) **before implementation starts**
3. If exists but stale: Refresh it first
4. During implementation: Reference the context doc for exact API shapes

### During Implementation

- Link code comments to relevant context doc sections
- Update context doc if you discover gaps or inaccuracies
- Example: `# See docs/context/openrouter.md - API/Interfaces section`

### After Implementation

- Verify context doc is accurate
- Add any integration-specific notes to "Relevant to thegent" section
- Update "Sources & References" with integration URL

---

## Tooling & Automation

### Creating a Context Doc

**Checklist** (see `CONTEXT_DOCS_PROCESS.md` for full process):
1. [ ] Gather official docs (web fetch or webarchive)
2. [ ] Extract technical specs (API, auth, concepts)
3. [ ] Write sections following GOVERNANCE.md template
4. [ ] Add working code examples
5. [ ] Cross-reference with implementation code
6. [ ] Pass pre-write validation hook
7. [ ] Add to `docs/context/INDEX.md`

### Verifying Accuracy

**Cross-reference checklist**:
- [ ] Sample 3-5 API examples against official docs (test if possible)
- [ ] Verify auth requirements match actual implementation
- [ ] Check error codes against real API responses
- [ ] Confirm code examples run without modification

### Automation CLI Commands (Future)

```bash
# Check all context docs for required sections
thegent context verify

# Refresh staleness dates on all docs
thegent context refresh-dates

# Check for hallucinations (compare against official docs)
thegent context validate-accuracy --fetch

# List missing P0 context docs
thegent context missing-priority0
```

---

## Quality Gates

### At Commit Time

Pre-write validation hook checks:
- All required sections present
- No placeholder/TODO content
- Fetch date is recent (< 6 months)
- No duplicated content from other docs

### At Integration Time

Before using a context doc in code:
- Cross-reference 3+ API examples
- Verify at least one code example runs
- Check error handling against real errors
- Confirm auth setup matches docs

### At Release Time

Before shipping:
- All P0 context docs exist and are current (< 90 days)
- All integrated technologies have context docs
- No broken cross-references

---

## Examples

### Example 1: Minimal Atomic Doc (OpenRouter)

```markdown
# OpenRouter API Context

> Unified API gateway for 400+ AI models from OpenAI, Anthropic, Google, Meta, etc.
> Sources: openrouter.ai/docs (fetched 2026-02-20).

---

## What is OpenRouter
[150-300 words explaining...]

## Key Concepts
**Model routing**: ...
**Fallover**: ...

## API/Interfaces

### Endpoint: POST /api/v1/chat/completions
[Full spec with headers, body, response]

## Authentication
[Bearer token + attribution headers]

## Code Examples
[Python + JS examples]

## Sources & References
[Links + dates]

## Quick Reference
[One-page cheat sheet]
```

### Example 2: Multi-File Doc Set (Ante)

```
docs/context/ante/
  index.md                          # Navigation and overview
  core-concepts.md                  # Agent, memory, skills, eval
  architecture.md                   # Subsystem interactions
  quickstart.md                      # Get up and running
  agents-and-organization.md         # Team/org features
  memory.md                          # Memory management
  skills.md                          # Custom skill development
  model-provider-catalog.md          # Supported providers
  eval-benchmark.md                  # Evaluation framework
  preferences.md                     # Config and tuning
  offline-mode.md                    # Standalone operation
  third-party-providers.md           # Integration partners
```

Each file: 150-400 lines, follows GOVERNANCE.md template, cross-references others.

---

## Revision History

| Date | Change | Author |
|------|--------|--------|
| 2026-02-20 | Initial governance document | (Agent) |

---

## See Also

- `docs/context/INDEX.md` - Index of all context docs
- `docs/governance/CONTEXT_DOCS_PROCESS.md` - Step-by-step process for creating/updating
- `docs/context/openrouter.md` - Example context doc (atomic)
- `docs/context/ante/index.md` - Example context doc set (multi-file)

---

## Source: context/INDEX.md

# Consolidated Index

## Files

* `ANTE_FILES.md`
* `GOVERNANCE.md`
* `INDEX.md`
* `ai-gateway-landscape.md`
* `ante-analysis.md`
* `ante-quick-reference.md`
* `ante.md`
* `bifrost.md`
* `claude-code.md`
* `cloudflare-ai-gateway.md`
* `codex.md`
* `fastmcp.md`
* `gemini-cli.md`
* `kong-ai-gateway.md`
* `litellm-proxy.md`
* `litellm.md`
* `mcp-protocol.md`
* `nats.md`
* `openai-responses-api.md`
* `openrouter.md`
* `portkey.md`
* `process-compose.md`
* `temporalio.md`
* `trpc.md`
* `vercel-ai-gateway.md`
* `vercel-ai-sdk.md`
* `workos-authkit.md`
* `workos.md`

## Subdirectories

* ante

---

## Source: context/ai-gateway-landscape.md

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

---

## Source: context/ante-analysis.md

# ANTE: Deep Differentiator Analysis & Strategic Implications

> Strategic analysis of what makes Ante unique as a terminal AI coding agent, with focus on architectural differentiators, protocol foundations, and implications for thegent integration and governance.
>
> Analysis date: 2026-02-20 | Based on: Official ANTE documentation, architecture review, comparative analysis vs Claude Code and Codex.

---

## Executive Summary

ANTE is fundamentally a **provider-agnostic, Rust-native terminal agent** with a deliberately tight core, designed for extensibility without bloat. Its key differentiators:

1. **Client-daemon separation** - clean boundary between presentation and engine, enabling multiple frontends
2. **Skills as first-class extensibility** - custom capabilities without modifying core
3. **Structured sub-agent spawning** - hierarchical agent coordination with message-passing
4. **Eval/benchmark mode** - systematic testing of agent capabilities (A/B testing, performance regression)
5. **Persistent cross-session memory** - learnings survive session boundaries
6. **Provider abstraction layer** - models and providers are interchangeable, not locked to one ecosystem
7. **Headless-first design** - parity between interactive TUI and automation-friendly CLI

**Strategic Value for thegent**: ANTE's patterns for skills, sub-agent coordination, and multi-provider abstraction should inform thegent's agent organization and extensibility model.

---

## Architecture Differentiators

### 1. Client-Daemon Separation (Core Insight)

ANTE's defining architectural choice: strict separation of presentation from execution engine.

```
Client (presentation)      Daemon (execution engine)
├─ TUI (ratatui)          ├─ Session manager
├─ Headless CLI           ├─ LLM provider dispatch
├─ Script integration     ├─ Tool scheduler
└─ API layer (future)     └─ Long-term memory store

         Async channels (Tokio) with message IDs for tracing
```

**Why this matters:**
- **Frontend swapping**: TUI can be replaced with IDE panel, web UI, or pure API without touching core
- **Clean testing**: Engine can be tested independently of presentation
- **Multi-tenant potential**: Single daemon can serve multiple client connections (future enhancement)

**Contrast with Claude Code & Codex:**
- **Claude Code**: IDE-centric; tight coupling between Claude-specific features and presentation (Go harness)
- **Codex**: Python-based; presentation bundled with engine; harder to extract for reuse
- **ANTE**: Rust native, deliberate separation; easier to sandbox and test

**thegent implication**: Consider adopting a similar daemon/client split for thegent core vs orchestration layer. Currently, thegent bundles MCP server + CLI proxy tightly; explicit separation would enable better testing and future multi-tenant scenarios.

---

### 2. Skills System: Extensibility Without Core Modification

ANTE treats skills as a first-class, discoverable type. Not "add a tool to the tool list" but "register a skill that has capabilities, versioning, and lifecycle."

**Skill Structure:**

| Aspect | Details |
|--------|---------|
| **Storage** | `~/.ante/skills/` (user-level), `.ante/skills/` (project-level) |
| **Discovery** | Automatic enumeration at session init; version tracking per skill |
| **Invocation** | Available to agent as tools; agent calls by skill name + operation |
| **Lifecycle** | Versioning, enable/disable, permission model (future) |
| **Scope** | User-level or project-scoped; project overrides user |

**Skill Registration Protocol:**

Skills are discovered through filesystem enumeration (not a registry service). Each skill:
1. Declares capabilities (what operations it supports)
2. Has versioning metadata
3. Can be enabled/disabled per session
4. Is isolated; errors in skill don't crash daemon

**Example Skill Flow:**
```
Agent: "Use the deployment skill to deploy to production"
        ↓
Daemon: Looks up skill: ~/.ante/skills/deployment/
        Reads: metadata.json { version: 1.2, operations: ["deploy", "rollback"] }
        Invokes: skill.deploy(target="production")
        Returns: Result
```

**Why this is different:**

| Aspect | ANTE | Claude Code | Codex |
|--------|------|-------------|-------|
| **Extension model** | Skills (versioned, discoverable) | Custom pattern/plugin (informal) | Plugin registry (centralized) |
| **Permission model** | Per-skill control (future) | Agent-wide (not granular) | Provider-enforced |
| **Scope** | User + project-level | IDE-scoped | Workspace-scoped |
| **Versioning** | Per-skill semantic versioning | Implicit | Plugin version |

**thegent implication**: thegent's hook system is procedural (`hooks/qa-<name>.sh`), not discoverable as entities. Skills model suggests treating hooks as discoverable, versioned capabilities. Consider evolving hook registry to expose capabilities metadata.

---

### 3. Sub-Agent Spawning & Hierarchical Coordination

ANTE enables agents to spawn other agents for complex tasks. Critical difference from "tool calling" — spawned sub-agents are **full agents**, not tools.

**Sub-Agent Lifecycle:**

```
Parent Agent                    Daemon
  |
  +-- Task("Deploy to prod")
       |
       ├─ Spawn SubAgent(type="deployment", model="claude-opus-4.6")
       |   ├─ Session initialized
       |   ├─ Daemon assigns TaskID
       |   └─ Sub-agent runs independently
       |
       ├─ Monitor: Poll for completion via message passing
       |
       └─ Collect Results: Sub-agent report merged into parent context
```

**Key Design Patterns:**

1. **Isolation**: Each sub-agent has independent session state, memory, configuration
2. **Communication**: Parent-child via daemon message queue (not shared memory)
3. **Coordination**: Parent waits for completion, collects structured results
4. **Error handling**: Sub-agent failure doesn't cascade; parent can retry or escalate
5. **Resource limits**: Each sub-agent can have memory/CPU caps (not yet implemented but designed for)

**Discovery & Routing:**

Sub-agents enumerated from `~/.ante/agents/` and `.ante/agents/`. Agent selection:
```bash
ante run --sub-agent deployment --model claude-opus  # Explicit
ante run --auto-sub-agents                           # Auto-route based on task type
```

**Comparison:**

| Aspect | ANTE | Claude Code | Codex |
|--------|------|-------------|-------|
| **Sub-agent capability** | First-class (agent spawning agent) | Yes, but tightly coupled | Yes, worker pattern |
| **Isolation** | Session-scoped; independent state | Thread/process-scoped | Process-isolated |
| **Communication** | Async channels + structured messages | Direct function calls | IPC/RPC |
| **Parent waits** | Yes, explicit coordination | Yes, blocking | Yes, blocking |
| **Discovery mechanism** | Filesystem + daemon catalog | Hardcoded or env-based | Plugin registry |

**thegent implication**: thegent's agent crew pattern could adopt ANTE's structured messaging and isolation model. Current crew implementation uses direct method calls; structured message passing would improve observability and enable better async coordination.

---

### 4. Eval & Benchmark Mode

ANTE includes a systematic evaluation framework — not just "run a task" but **measure, compare, and report**.

**Benchmark Capabilities:**

```
Benchmark Suite
├─ Predefined task benchmarks (e.g., "code completion", "bug fix", "refactor")
├─ Custom eval criteria (pass/fail, latency, token efficiency, accuracy)
├─ Metrics collection
│   ├─ Latency (TTFT, total generation time)
│   ├─ Accuracy (if oracle available)
│   ├─ Token usage (prompt + completion)
│   ├─ Tool calls count
│   └─ Success rate
└─ Comparison runs (A/B testing)
    ├─ Model A vs Model B
    ├─ Provider X vs Provider Y
    ├─ Provider + Model combinations
    └─ Statistical reporting (mean, stddev, p50/p95/p99 latency)
```

**Benchmark Run Example:**

```bash
ante benchmark run \
  --suite code-completion \
  --model claude-opus-4.6 vs gpt-4o \
  --provider anthropic vs openai \
  --iterations 100 \
  --output benchmark-results.json
```

**Output Format:**
```json
{
  "suite": "code-completion",
  "runs": [
    {
      "model": "claude-opus-4.6",
      "provider": "anthropic",
      "iterations": 100,
      "metrics": {
        "latency_ms": { "p50": 234, "p95": 512, "p99": 890 },
        "accuracy": 0.97,
        "tokens": { "prompt": 4521, "completion": 2134 },
        "success_rate": 1.0
      }
    }
  ],
  "comparison": "claude-opus-4.6 / anthropic is 23% faster than gpt-4o / openai"
}
```

**Why this is unique:**

| Aspect | ANTE | Claude Code | Codex | thegent |
|--------|------|-------------|-------|---------|
| **Benchmarking** | Built-in, systematic | Manual or external tools | Manual/external | Minimal (test-focused) |
| **A/B testing** | First-class (compare models, providers) | Not native | Not native | Not native |
| **Metrics** | Rich (latency, accuracy, tokens) | Basic (exec time) | Basic (exec time) | None |
| **Comparison reporting** | Statistical, automated | Manual interpretation | Manual | Not supported |

**thegent implication**: thegent's quality-gate hooks could emit structured metrics. A benchmark mode would enable systematic testing of quality gates, policy effectiveness, and agent capability regressions. Currently missing.

---

### 5. Memory System: Cross-Session Persistence & Learning

ANTE maintains both short-term and long-term memory, enabling learning across sessions.

**Memory Architecture:**

```
Session Memory (in-process)
├─ Current turn context
├─ Recent history (last N exchanges)
└─ Working state

         ↓ (persist at session end)

Long-term Memory Store
├─ Session transcripts (indexed, searchable)
├─ Task summaries (compressed)
├─ Learnings & patterns
│   ├─ "This pattern works well for refactoring"
│   ├─ "Provider X fails on tool calls with large JSON"
│   └─ "Model Y needs explicit type hints in prompts"
├─ Context compression (auto-summarization)
└─ Retrieval index (semantic + keyword)
```

**Persistence & Retrieval:**

- **Storage backend**: File-based (JSON/SQLite) by default; pluggable
- **Compression**: Auto-summarization when context budgets near limit (configurable)
- **Retrieval**: Semantic search (embeddings) + keyword search
- **Lifecycle**: Sessions expire after TTL (default 30 days); summaries persist longer

**Retrieval at Session Init:**

```rust
// Pseudo-code: ANTE daemon startup
session = Session::new()
past_learnings = memory_store.retrieve_by_task_type(session.task_type)
  .top_k(5)  // Most relevant past sessions
session.context.add_prefix("Relevant past learnings: " + summarize(past_learnings))
// Agent now has context from previous sessions
```

**Key distinction:**

| Aspect | ANTE | Claude Code | Codex | thegent |
|--------|------|-------------|-------|---------|
| **Memory scope** | Cross-session, persistent | Session-only | Session-only | Work-stream segments |
| **Learning capture** | Automatic (transcripts + summaries) | Manual (user-maintained) | Manual | Manual (conversation dumps) |
| **Retrieval** | Semantic + keyword search | None | None | Grep + manual search |
| **Context injection** | Automatic at session init | Manual via prompts | Manual | Manual |
| **Compression** | Auto-summarization | None | None | Requested in dumps |

**thegent implication**: thegent's work-stream + conversation dumps pattern is similar but manual. ANTE's automatic memory retrieval and compression could inform a smarter work-stream system. Current limitation: no automatic "What have we learned before?" injection.

---

### 6. Provider Abstraction Layer

ANTE is built around provider abstraction — no hard-coded model dependencies. Every provider implements a common trait.

**Provider Interface (Rust trait):**

```rust
pub trait Provider: Send + Sync {
    async fn send(&self, request: ProviderRequest) -> Result<ProviderResponse>;
    fn capability(&self) -> ProviderCapability;
}
```

**Supported Providers & Wire Formats:**

| Provider | API | Models | Auth | Streaming |
|----------|-----|--------|------|-----------|
| Anthropic | Messages API | Claude family | ANTHROPIC_API_KEY | Yes |
| OpenAI | Chat Completions | GPT-4o, o1, Mini | OPENAI_API_KEY | Yes |
| Gemini | Gemini API | Gemini 2.0 Flash, 1.5 Pro | GOOGLE_API_KEY | Yes |
| Grok | OpenAI-compat | Grok 2 | GROK_API_KEY | Yes |
| OpenRouter | OpenAI-compat | 400+ models | OPENROUTER_API_KEY | Yes |
| Local | llama.cpp | GGUF models (Qwen, Llama) | None (local) | Yes |

**Provider Resolution at Session Init:**

```bash
# User specifies
ante run --provider anthropic --model claude-opus-4.6

# Or auto-resolve from settings
~/.ante/settings.json: { "provider": "openai", "model": "gpt-4o" }

# Or env variables (fallback)
ANTE_PROVIDER=openai ANTE_MODEL=gpt-4o ante run

# Resolution order: CLI flag > Project config (.ante/) > User settings > Env > Default
```

**Provider Switching Is Trivial:**

```bash
# Same prompt, different providers
ante run --provider anthropic "Analyze this code"
ante run --provider openai "Analyze this code"
ante run --provider gemini "Analyze this code"

# All use same Tool system, same LLM message protocol, same streaming
```

**Capability Declaration:**

Each provider declares capabilities (what sampling parameters it supports):

```json
{
  "provider": "anthropic",
  "capabilities": {
    "streaming": true,
    "tool_calling": true,
    "sampling_parameters": ["temperature", "top_p", "max_tokens"],
    "vision": false,
    "extended_context": true
  }
}
```

Agent can check capabilities before routing.

**Comparison:**

| Aspect | ANTE | Claude Code | Codex | thegent |
|--------|------|-------------|-------|---------|
| **Provider abstraction** | Trait-based, pluggable | Anthropic-primary; others secondary | OpenAI-primary | Router abstraction |
| **Provider count** | 6+ | 3-4 (fallback pattern) | 5+ (plugin-based) | Via OpenRouter (400+) |
| **Switching cost** | Zero (same interface) | Non-zero (model-specific prompting) | Non-zero | Non-zero |
| **Local inference** | Yes (llama.cpp) | Limited | Yes (custom) | No (API-only) |
| **Offline capable** | Yes | No | Limited | No |

**thegent implication**: thegent uses LiteLLM/OpenRouter for multi-provider support. ANTE's trait-based abstraction is more elegant. Consider evaluating whether moving to Rust for core (or using a language-agnostic RPC) would improve provider flexibility. Current approach (HTTP proxy) works but adds latency and complexity.

---

### 7. Headless Mode: Parity Between Interactive & Automated

ANTE treats headless mode as equal citizen to TUI, not an afterthought.

**Headless Command Variants:**

```bash
# One-shot execution (most common)
ante run "Your prompt here"

# Task mode (structured, with retries)
ante task "Your task with success criteria"

# Streaming raw output (for scripts)
ante run --stream --no-headers "Your prompt"

# JSON output (structured data)
ante run --output json "Your prompt"

# With approvals (non-interactive approval)
ante run --require-approval "Deploy to production"
  # Polls ANTE_APPROVAL_ENDPOINT or reads from stdin
```

**Key Design Principles:**

1. **No TUI-specific features in interactive mode** - feature parity enforced
2. **Exit codes as contracts** - 0 = success, 1-127 = defined errors
3. **Structured output** - JSON mode for parsing by other tools
4. **Streaming vs buffering** - choose based on use case

**Output Modes:**

```bash
# Human-readable text (default)
ante run "Analyze code" > output.txt

# JSON (for parsing)
ante run --output json "Analyze code" | jq '.response'

# Raw streaming (for live monitoring)
ante run --stream "Analyze code"

# Debug (includes tool calls, reasoning)
ante run --debug "Analyze code"
```

**thegent implication**: thegent's work-stream + continuous loop pattern benefits from headless-first thinking. Current design requires explicit loop control. ANTE's parity principle suggests: design for automation first (exit codes, structured output), make interactive TUI second (wrapper around automation).

---

## Protocol Analysis

### Core Concepts & Message Format

ANTE operates on a simple, extensible message protocol internal to the daemon.

**Session Flow:**

```
Client ──Op──▶ Daemon

         Session(id=S1)
         ├─ Model: claude-opus-4.6
         ├─ Provider: anthropic
         └─ Task(id=T1)
              └─ Turn(id=Tu1)
                  ├─ User Message: "Refactor this"
                  ├─ Daemon → LLM Provider
                  ├─ LLM Response
                  ├─ Tool execution
                  └─ Event: "turn_complete"

Client ◀─Evt─ Daemon
```

**Message Types:**

| Direction | Type | Payload | Example |
|-----------|------|---------|---------|
| C→D | `Op::Run` | prompt, model, provider | `Op::Run { prompt: "...", model: "claude-opus", provider: "anthropic" }` |
| C→D | `Op::Cancel` | session_id, task_id | `Op::Cancel { session: S1, task: T1 }` |
| D→C | `Evt::StreamChunk` | token, source (agent/tool) | `Evt::StreamChunk { token: "Hello", source: "agent" }` |
| D→C | `Evt::ToolCall` | tool_name, args, status | `Evt::ToolCall { name: "Write", args: {...}, status: "executing" }` |
| D→C | `Evt::Complete` | session_id, result | `Evt::Complete { session: S1, result: "..." }` |

**Message Tracing:**

All operations have `message_id` fields for correlation:

```
Client Op: { id: msg-123, op: Run { prompt: "..." } }
 ↓
Daemon receives, creates Session(msg_id: msg-123)
 ↓
All subsequent events tagged with msg-123
 ↓
Client correlates responses to original Op
```

### Tool Calling Protocol

Tools are invoked via explicit `ToolCall` events; agent doesn't directly execute.

**Tool Call Flow:**

```
LLM Response: { tool_calls: [{ name: "Write", args: { path: "x.py", content: "..." } }] }
      ↓
Daemon receives, creates ToolCall event
      ↓
Event: ToolCall { name: "Write", args: {...}, status: "pending" }
      ↓
Client renders: "Executing tool: Write"
      ↓
Daemon executes tool (in sandbox/approval context)
      ↓
Event: ToolCall { name: "Write", args: {...}, status: "complete", result: "Wrote 100 bytes" }
      ↓
LLM receives tool result in next turn
```

**Tool Filtering:**

Configured at session init:

```rust
Session {
  allowed_tools: ["Read", "Write", "Bash"],
  disallowed_tools: [],
  tool_matcher: ToolMatcher::Allowlist,
}
```

If agent calls disallowed tool:
```
Event: ToolCall { name: "BashOutput", status: "blocked", error: "Tool not in allowlist" }
```

**Approval Flow (Interactive):**

```
Client requests approval: Op::ApprovalRequest { tool_name: "Bash", args: {...} }
      ↓
Client (TUI) renders prompt: "Allow execution of: bash rm -rf /"
      ↓
User presses Y/N
      ↓
Client sends: Op::ApprovalResponse { approval: false }
      ↓
Daemon: Tool execution blocked
      ↓
Event: ToolCall { status: "rejected_by_user" }
```

### Streaming Format

Streaming is event-based, not line-based. Enables multiplexing multiple streams.

**Stream Format:**

```
event: stream_chunk
data: {"type":"text","content":"Hello ","source":"agent"}

event: stream_chunk
data: {"type":"text","content":"world","source":"agent"}

event: tool_call
data: {"name":"Read","status":"executing","path":"file.py"}

event: tool_call
data: {"name":"Read","status":"complete","result":"...","path":"file.py"}

event: stream_chunk
data: {"type":"text","content":" Done!","source":"agent"}

event: complete
data: {"session":"S1","status":"success","result":"..."}
```

### Session Storage Format

Sessions persisted to disk (JSONL or SQLite):

```json
{
  "session_id": "S1",
  "created_at": "2026-02-20T10:30:00Z",
  "model": "claude-opus-4.6",
  "provider": "anthropic",
  "task_id": "T1",
  "turns": [
    {
      "id": "Tu1",
      "user_message": "Refactor this function",
      "assistant_response": "...",
      "tool_calls": [
        { "name": "Read", "args": {...}, "result": "..." }
      ]
    }
  ],
  "metadata": {
    "total_tokens": 2500,
    "duration_ms": 5234
  }
}
```

---

## Provider & Model Handling

### Provider Catalog & Model Resolution

ANTE maintains a provider catalog — curated list of known models per provider.

**Catalog Structure:**

```yaml
providers:
  anthropic:
    models:
      - name: claude-opus-4.6
        context_window: 200000
        supports: [streaming, tool_calling, vision, extended_thinking]
      - name: claude-sonnet-4-5
        context_window: 200000
      - name: claude-haiku-4-5
        context_window: 200000
  openai:
    models:
      - name: gpt-4o
        context_window: 128000
        supports: [streaming, tool_calling, vision, structured_output]
  local:
    models:
      - name: qwen-32b-gguf
        backend: llama.cpp
        context_window: 32000
        local_only: true
```

**Model Alias System:**

```bash
# User says "claude" → daemon resolves to "claude-opus-4.6" (default)
# User says "gpt" → resolves to "gpt-4o" (default)
# User says "fast" → resolves to "claude-haiku" (tag-based, configured in settings)
```

### Offline Mode

True offline inference via llama.cpp:

```bash
# Requires: GGUF model file locally
ante run --model qwen-32b-gguf --provider local "Analyze code"

# No network; runs on CPU/GPU locally
# Latency: 1-2 sec per token (CPU), 100ms/token (GPU, if available)
```

**Offline Strategy:**

1. User runs `ante setup-offline --model qwen-32b`
2. ANTE downloads GGUF (~8-40GB depending on quantization)
3. Model cached in `~/.ante/models/`
4. Headless mode `ante run --provider local ...` works without internet

**Fallback Chain:**

```
Try: User-specified provider
→ If offline: Try local provider
→ If no local: Fail with clear message: "No online provider available. Run 'ante setup-offline'"
→ No silent failures
```

### Adding Custom Providers

Extensibility point for custom LLM providers:

```rust
// Define custom provider
pub struct MyCustomProvider {
    api_key: String,
}

impl Provider for MyCustomProvider {
    async fn send(&self, request: ProviderRequest) -> Result<ProviderResponse> {
        // Call custom API, return normalized response
    }

    fn capability(&self) -> ProviderCapability {
        ProviderCapability {
            supports_streaming: true,
            supports_tool_calling: true,
            max_tokens: 100000,
        }
    }
}

// Register in catalog
provider_registry.register("my-custom", MyCustomProvider::new(api_key))
```

Once registered, available via:
```bash
ante run --provider my-custom --model some-model "Your prompt"
```

---

## UX/AX Differentiators

### Interactive TUI

Built with `ratatui` (native Rust terminal UI library). Features:

| Feature | Capability |
|---------|-----------|
| **Real-time streaming** | Tokens appear as they arrive (no buffering) |
| **Tool tracking** | Live pane shows "Executing: Read (file.py)" |
| **History navigation** | Arrow keys to browse past exchanges |
| **Search** | Ctrl+F within session history |
| **Multi-pane layout** | Response, tool status, session metadata visible simultaneously |
| **Theming** | Dark/light modes, custom colors in config |
| **Approvals** | Interactive Y/N prompts for tool execution |
| **Session replay** | Load past sessions, replay step-by-step |

**TUI Principles:**
- No scrolling required for core operations
- All critical info visible; less critical info in side panes
- Real-time feedback (tokens, tool status, errors)
- Keyboard-first navigation

### Headless Mode Quality

Headless is not a second-class citizen:

1. **Exit codes**: Defined, scriptable
   ```
   0 = success
   1 = input error (invalid prompt)
   2 = execution error (tool failed)
   3 = provider error (API down)
   4 = cancelled (user abort)
   ```

2. **Structured output**: JSON mode for parsing
   ```bash
   ante run --output json "Your task" | jq '.response'
   ```

3. **Streaming**: Real-time token output
   ```bash
   ante run --stream "Your task" | tee output.log
   ```

4. **Non-interactive approvals**: Approval via environment or API
   ```bash
   ANTE_APPROVAL="yes" ante run --require-approval "Deploy"
   ```

**Key principle**: Whatever works in interactive mode works headless. No "feature only in TUI" or "feature only headless."

### Preferences & Configuration System

Configuration layering:

```
CLI flags (highest priority)
  ↓
Project config (.ante/config.json)
  ↓
User settings (~/.ante/settings.json)
  ↓
Environment variables
  ↓
Compiled defaults (lowest priority)
```

**Example settings.json:**

```json
{
  "model": "claude-opus-4.6",
  "provider": "anthropic",
  "context_limit": 100000,
  "auto_approve_safe_tools": ["Read", "Write"],
  "auto_approve_unsafe": false,
  "theme": "dark",
  "allowed_tools": ["Read", "Write", "Bash", "Task"],
  "retention_days": 30,
  "memory_compression": "auto",
  "offline_preference": false,
  "aliases": {
    "fast": "claude-haiku-4-5",
    "smart": "claude-opus-4.6",
    "local": "qwen-32b-gguf"
  }
}
```

**Per-project override (.ante/config.json):**

```json
{
  "allowed_tools": ["Read", "Write"],
  "auto_approve_safe_tools": [],
  "model": "claude-sonnet-4-5"
}
```

---

## Gaps in ANTE vs Claude Code & Codex

### What ANTE Lacks

| Gap | Impact | Workaround |
|-----|--------|-----------|
| **IDE integration** | Can't use from IDE panel (yet) | Planned future feature; currently CLI-only |
| **Windows support** | Linux/macOS only | Rust tier support; Windows planned for 2026-Q2 |
| **Team features** | Single-user focused | Could add org-level settings (planned) |
| **Web UI** | No browser-based interface | Client-daemon split enables future web client |
| **Deployment** | No cloud hosting | Users run locally; could be containerized |
| **Debugger integration** | Can't debug code in ANTE's IDE | Would require IDE extension (future) |
| **RAG system** | No built-in knowledge base | Skills could implement RAG; not baked in |
| **Advanced auth** | Only env vars + OAuth | SAML, enterprise SSO not yet supported |

### Where Claude Code & Codex Are Stronger

| Aspect | Claude Code | Codex | thegent | ANTE |
|--------|-------------|-------|---------|------|
| **IDE integration** | Native (VSCode) | Cursive IDE | N/A | Not yet |
| **Mature ecosystem** | Yes | Yes | Growing | Early |
| **Enterprise support** | Anthropic-backed | OpenAI-backed | Self-hosted | Antigma Labs |
| **Breaking changes** | Rare | Rare | Monitored | Expected (preview) |
| **Debugging tools** | Yes (IDE-embedded) | Yes (IDE-embedded) | Limited | None yet |
| **Performance benchmarks** | Public | Public | Internal | Starting |
| **User docs** | Comprehensive | Comprehensive | Detailed | Good |

---

## Strategic Implications for thegent

### 1. Adopt Structured Sub-Agent Messaging

**Current thegent approach:**
```python
# Direct method calls, tightly coupled
agent1.execute(prompt)
agent2.process(result)
```

**ANTE approach (to adopt):**
```
agent1 → Daemon message queue → agent2
                    ↓
              Event correlation
              Structured results
              Error isolation
```

**Benefit**: Better observability, async coordination, failure isolation.

### 2. Implement Discoverable Capabilities Registry

**Current approach**: Hooks are scripts; no metadata.

**ANTE approach (to adopt)**: Hooks expose capabilities.

```yaml
hooks:
  qa-gate-coverage:
    version: 1.0.0
    category: "quality"
    triggers: ["stop"]
    inputs: [code_files]
    outputs: [coverage_report]
    can_block: true
    approval_required: false
```

**Benefit**: Agents can query available hooks, understand dependencies, make decisions based on capabilities.

### 3. Add Systematic Benchmarking

**Current approach**: Manual test runs; no A/B testing framework.

**ANTE approach (to adopt)**: Built-in benchmarks with statistical reporting.

```bash
thegent benchmark run \
  --policy-set standard vs strict \
  --iterations 50 \
  --metrics latency,compliance,tool-accuracy
```

**Benefit**: Detect quality regressions, compare policy effectiveness.

### 4. Implement Persistent Cross-Session Memory

**Current approach**: Conversation dumps (manual).

**ANTE approach (to adopt)**: Automatic memory store with retrieval.

```python
# At session start
past_learnings = memory_store.retrieve(task_type="code-review", count=3)
# Inject into system prompt: "Relevant past reviews: ..."
```

**Benefit**: Agents learn from history without explicit prompting.

### 5. Decouple Presentation from Engine (Long-term)

**Current architecture**: MCP server + CLI proxy bundled.

**ANTE architecture (to aspire to)**:
- Core daemon (governance engine)
- Multiple clients (CLI, TUI, API, IDE plugin)

**Benefit**: Easier testing, future extensibility, multi-tenant support.

### 6. Treat Headless Mode as First-Class

**Current approach**: TUI-centric; headless is retrofit.

**ANTE approach (to adopt)**: Design for automation, wrap with interactivity.

**Concrete step**: Separate thegent core (CLI, exit codes, JSON) from orchestration layer (work-stream, plan loop).

### 7. Standardize Multi-Provider Support

**Current approach**: OpenRouter proxy (works, but indirect).

**ANTE approach (to consider)**: Trait-based provider abstraction.

**Evaluation point**: Does moving to Rust or exposing provider interface improve flexibility? Current approach works but adds latency. For thegent's governance use case, current HTTP routing is probably sufficient.

---

## What thegent Does Better

| Dimension | ANTE | thegent | Advantage |
|-----------|------|---------|-----------|
| **Governance** | Tool filtering only | Comprehensive policy engine | thegent is purpose-built for governance |
| **Quality gates** | Not native | 5-layer security pipeline | thegent has systematic quality enforcement |
| **Agent organization** | Hierarchies (basic) | Crew patterns + work-stream | thegent better for multi-agent coordination at scale |
| **Persistence** | Long-term memory (sessions) | Work-stream + research docs | thegent maintains organizational knowledge |
| **Enterprise** | Single-user | Multi-tenant ready | thegent designed for orgs |
| **Extensibility** | Skills + sub-agents | Hooks + modular governance | Both strong; different patterns |
| **Maturity** | Preview | Stable | thegent more production-ready |

---

## Integration Opportunities

### Pattern 1: ANTE as Task Executor

thegent delegates specialized work to ANTE:

```
thegent (orchestrator)
  ├─ Route: "Code review task"
  └─ Spawn: ante task "Review PR #123"
       └─ ANTE session (independent)
           ├─ Model: claude-opus-4.6
           ├─ Tools: Read, Write, Bash
           └─ Result: Review report
```

**Requirements**:
- ANTE CLI exits cleanly with JSON output
- thegent work-stream integrates ANTE task results
- Error handling: ANTE failure doesn't crash thegent

### Pattern 2: Skill Composition

thegent skills + ANTE skills:

```
~/.thegent/skills/
  ├─ deployment/
  ├─ security-audit/
  └─ ...

~/.ante/skills/
  ├─ code-generation/
  ├─ refactoring/
  └─ ...
```

thegent discovers ANTE skills, makes available to agents.

### Pattern 3: Memory Sharing

Long-term memory store accessible to both:

```
thegent work-stream → research docs
  ↓
Shared memory store (SQLite)
  ↓
ANTE session init: "Relevant past work: ..."
```

---

## Conclusion

ANTE's architectural patterns — client-daemon separation, discoverable capabilities, hierarchical sub-agents, systematic evaluation, and cross-session memory — are directly applicable to thegent's evolution. Most valuable:

1. **Structured messaging for multi-agent coordination** (replace direct calls)
2. **Discoverable capabilities metadata** (hooks → first-class entities)
3. **Systematic benchmarking** (quality gates → metrics framework)
4. **Persistent learning** (dumps → automatic memory)
5. **Headless-first design** (reverse current priority)

ANTE's provider abstraction and offline inference are less critical for thegent (which is orchestration-layer), but demonstrate clean extensibility patterns worth studying.

**Strategic recommendation**: Adopt ANTE's sub-agent communication and memory patterns as thegent evolves toward systematic governance and learning. Consider ANTE as an integration target for specialized tasks (code review, refactoring), not a wholesale replacement.

---

## Sources

- ANTE Official Documentation: https://docs.useante.com/
- ANTE GitHub: https://github.com/antigmaplex/ante
- Antigma Labs: https://antigmalabs.com/
- thegent docs/context/ante.md (comprehensive ANTE overview)
- Comparative analysis vs Claude Code, Codex, thegent

*Analysis date: 2026-02-20*

---

## Source: context/ante-quick-reference.md

# ANTE Quick Reference Guide

A rapid reference for ANTE (Another Terminal) terminal AI agent for developers and integrators.

## One-Liner

ANTE is a lightweight, native Rust terminal AI agent by Antigma Labs. Provider-agnostic, security-focused, with extensible skills and sub-agents.

## Installation & First Use

```bash
# Install
brew install ante  # or build from source

# First prompt (under 1 minute)
ante
# or
ante run "Your prompt here"
```

## Architecture at a Glance

```
Client (TUI/Headless) ←→ Daemon (Sessions, Tools, Providers)
                        ↓
                   LLM Provider (Claude, GPT-4, Gemini, Grok, Local)
```

**Key Components:**
- **Session**: Isolated execution context
- **Turn**: Agent-user exchange with tool execution
- **Tool**: Executable capability (File I/O, Shell, Web, etc.)
- **Skill**: Custom extension (user or project-level)
- **Provider**: LLM backend abstraction

## Supported LLM Providers

| Provider | Models | Wire Format | Auth |
|----------|--------|-------------|------|
| Anthropic | Claude | Messages API | ENV var / OAuth |
| OpenAI | GPT-4o, o1 | Chat Completions | ENV var / OAuth |
| Gemini | Gemini family | Native API | ENV var |
| Grok | Grok models | OpenAI-compatible | ENV var |
| Open Router | Multi | OpenAI-compatible | ENV var |
| Local | GGUF (llama.cpp) | Local inference | File path |

Set via: `--provider NAME --model MODEL` or `~/.ante/settings.json`

## Built-in Tools

**File I/O**: Read, Write, Edit, Glob, Grep

**Shell**: Bash (approval required), BashOutput, KillShell

**Web**: WebFetch, WebSearch

**Agent**: Task (spawn sub-agent), TodoWrite

Filter tools: `--allowed-tools Read,Write,Bash`

## Configuration

### Environment Variables

```bash
ANTHROPIC_API_KEY=...     # Anthropic auth
OPENAI_API_KEY=...        # OpenAI auth
ANTE_HOME=~/.ante         # Config directory
ANTE_DEBUG=1              # Debug logging
NO_COLOR=1                # Disable colors
```

### Settings File

`~/.ante/settings.json`:

```json
{
  "model": "claude-opus-4.6",
  "provider": "anthropic",
  "theme": "dark",
  "context_limit": 100000,
  "allowed_tools": ["Read", "Write", "Bash"],
  "auto_approve": false
}
```

### Directory Structure

```
~/.ante/
├── settings.json        # User preferences
├── skills/              # User-level skills
└── agents/              # User-level sub-agents

.ante/                   # Project-local config
├── settings.json        # Project overrides
├── skills/
└── agents/
```

## CLI Commands

```bash
# Interactive mode
ante                        # Start REPL

# One-shot execution
ante run "prompt"          # Execute and exit

# Headless mode
ante task "task"           # Headless execution

# Session management
ante sessions              # List all sessions
ante resume <session-id>   # Resume session
ante export <session-id>   # Export session

# Configuration
ante config get model      # Get setting
ante config set model claude-opus-4.6  # Set
ante config reset          # Reset to defaults

# Info
ante version              # Version info
ante doctor               # Environment diagnostics
```

## Advanced Features

### Skills (Custom Capabilities)

Store custom skills for domain-specific operations:

```bash
~/.ante/skills/my_skill.md      # User-level
.ante/skills/deploy.md          # Project-level
```

Skills are discoverable and invokable as tools.

### Sub-Agents (Task Decomposition)

Spawn independent agents for parallel work:

```bash
# In ANTE prompt:
Use the Task tool to spawn a sub-agent for:
- Code generation
- Data analysis
- Testing
```

Sub-agents maintain isolated sessions and state.

### Memory

**Session Memory**: In-process context for current session.

**Long-term Memory**: Persistent across sessions with:
- Session transcripts
- Task summaries
- Semantic search
- Auto-compaction at context limits (10:1 compression)

### Offline Mode (Experimental)

Use local LLMs without internet:

```bash
ante run --provider local --model ggml-model.gguf "prompt"
```

## Integration Patterns

### With thegent

```yaml
# In thegent config
harnesses:
  ante:
    binary: /usr/local/bin/ante
    capabilities: [tui, headless, skills, sub_agents, memory]
    providers: [anthropic, openai, gemini, local]
    default_model: claude-opus-4.6
```

### Via Scripts/CI/CD

```bash
# Headless mode for CI
ante task "Run tests and report" \
  --provider openai \
  --model gpt-4o \
  --allowed-tools Bash,Read

# JSON output for parsing
ante run "..." --output json > result.json
```

### Custom Provider

Implement provider trait and register in catalog:

```rust
#[async_trait]
pub trait Provider: Send + Sync {
    async fn send(&self, req: ProviderRequest) -> Result<ProviderResponse>;
}
```

## Performance Characteristics

| Metric | Value | Notes |
|--------|-------|-------|
| First Token | 200-800ms | Provider-dependent |
| Streaming | Real-time | Token-by-token delivery |
| Tool Overhead | <100ms | Most tools complete quickly |
| Process Memory | ~50-200MB | Baseline + per-session |
| Session Overhead | ~1-10MB | Per active session |
| Context Limit | ~100K tokens | Auto-compaction enabled |

## File Locations

| Location | Purpose |
|----------|---------|
| `~/.ante/settings.json` | User preferences |
| `~/.ante/skills/` | User-level skills |
| `~/.ante/agents/` | User-level sub-agents |
| `.ante/` | Project-local config |
| `.claude/` | Claude.ai compatibility |
| `/tmp/ante/` | Temporary files |

Override with: `ANTE_HOME=/custom/path`

## Key Concepts

**Session**: Isolated context. Each has independent state, memory, and configuration. Initialized with model/provider/policy.

**Task**: Unit of work within a session representing a user request or agent operation.

**Turn**: Individual exchange between user and agent with tool execution and state updates.

**Step**: Sub-operation within a turn (tool call, approval request, completion).

**Provider**: LLM abstraction layer. ANTE supports 6+ providers, making it model-agnostic.

**Tool**: Executable capability (file operations, shell, web, custom). Filterable and approvable.

**Skill**: Custom extension without modifying core. User or project-level.

**Sub-Agent**: Spawned agent instance for hierarchical task decomposition and parallel work.

## Comparison Matrix

| Feature | ANTE | Claude Code | Codex | Gemini CLI |
|---------|------|-------------|-------|-----------|
| Language | Rust | Go | Python | Go |
| Providers | 6+ | Anthropic | 3+ | Gemini |
| Offline Capable | Yes (exp) | Limited | Yes | No |
| Skills | Yes | Pattern-based | Yes | Limited |
| Sub-Agents | Yes | Yes | Yes | Limited |
| TUI | ratatui | CLI/panel | IDE | CLI |
| Maturity | Preview | Stable | Stable | Beta |
| Principle | Minimal core | IDE-first | Codex-centric | Gemini-centric |

## Resources

- **Docs**: https://docs.useante.com/
- **GitHub**: https://github.com/antigmaplex/ante
- **Antigma Labs**: https://antigmalabs.com/
- **Local Docs**: `/thegent/docs/context/ante/` (16 comprehensive guides)

## Status & Support

**Current Status**: Preview / Under Active Development

**Supported Platforms**: macOS, Linux (Windows TBD)

**Breaking Changes**: Expected during preview phase

**Community**: See GitHub issues and discussions

---

*Quick reference for ANTE terminal AI agent. For comprehensive documentation, see `/thegent/docs/context/ante/`.*

---

## Source: context/ante.md

# Ante: Comprehensive Context & Reference Document

> **What is Ante?** Ante (Another Terminal) is a lightweight, native Rust terminal AI agent by Antigma Labs. It is the closest existing product to thegent's vision for autonomous agent orchestration. It is proprietary, currently in preview, and has documented reliability issues — but its design philosophy and architecture serve as the reference target for "turning Codex into Ante."
>
> **Source URLs:** https://docs.useante.com/ | https://antigma.ai/ | https://github.com/AntigmaLabs
> **Local archives:** ~/Downloads/*Ante.webarchive (16 pages extracted 2026-02-20)
> **Runtime version confirmed:** `ante 0.0.preview6` (from antigma_drift_report)
> **Last verified:** 2026-02-20

---

## 1. What Ante Does

Ante is a self-contained terminal AI coding agent. It occupies the same problem space as Claude Code and Codex CLI but with distinct architectural choices:

- **Problem it solves:** Autonomous, terminal-native AI agent that can read/write code, execute shell commands, search the web, spawn sub-agents, and accumulate persistent memory — all from a CLI/TUI interface.
- **Primary interface:** Terminal (TUI or headless CLI), not IDE panel or web UI.
- **Core differentiator:** Native Rust for performance and security, provider-agnostic multi-LLM support, clean client-daemon architecture, headless-first design.
- **Evaluation standing:** Topped Terminal Bench 1.0 leaderboard (2025) and Terminal Bench 2.0 leaderboard (February 2026, verified agent, best-in-class for Gemini). Uses Terminal Bench / Harbor as primary evaluation suite.
- **Status:** Preview (`0.0.preview6`). macOS and Linux only. Breaking changes expected. Windows planned for 2026-Q2.
- **Company:** Antigma Labs — mission is "building substrate for self-organizing intelligence." Treats agents as teammates, and treats users as another agent.

---

## 2. Key Features (Exhaustive)

### 2.1 Interface Modes

**Interactive TUI:**
- Built with `ratatui` (native Rust terminal UI library)
- Renders inline (up to 24 lines); debounced rendering at ~100fps
- Real-time streaming tokens as they arrive (no buffering)
- Chat interface with markdown rendering
- Tool approval prompts (Allow / Deny) for gated tools (Bash, Write)
- Fullscreen diff view on alternate screen for file edit proposals
- Model and provider selection during session (no restart needed)
- Theme selection system (dark/light, configurable)
- History navigation with keyboard shortcuts
- Ctrl+C to interrupt; Escape to cancel input; Enter to send
- Streaming can be disabled via `ANTE_DISABLE_STREAMING=1`

**Headless Mode:**
- Invoked with: `ante "prompt"` or `ante --prompt "prompt"` or `ante -p "prompt"`
- Accepts stdin input (`cat file | ante -p "review"`)
- When stdin + prompt provided: concatenated (stdin first)
- Streaming disabled — responses buffered for cleaner output
- Yolo policy implied — all tool calls auto-approved
- Authentication checked eagerly — exits immediately if not authenticated
- Automatically appends current directory folder structure to prompt (project layout awareness)
- `--check` flag: runs verification pass after main task (agent reviews its own work)

**Output formats (headless):**
- `minimal` (default) — agent messages, info, errors only
- `human` — all events, ANSI colors, human-readable
- `json` — every event as JSON object (one per line) for machine consumption

### 2.2 Tool System

All tools implement the `Tool` trait:

```rust
#[async_trait]
pub trait Tool: Send + Sync {
    fn metadata(&self) -> &ToolMetadata;
    async fn call(&self, input: ToolCallInput) -> Result<ToolCallOutput>;
}
```

**Built-in tools (12 total):**

| Tool | Category | Approval | Description |
|------|----------|----------|-------------|
| Read | File I/O | No | Read file contents; supports text, images (PNG/JPG), PDFs, Jupyter notebooks; offset/limit for large files |
| Write | File I/O | Yes | Create or overwrite files |
| Edit | File I/O | Yes | Exact string replacement (old_string → new_string; optional replace_all) |
| Glob | File I/O | No | Find files by glob pattern (e.g., `**/*.rs`) |
| Grep | File I/O | No | Search file contents with regex; built on ripgrep; supports path, glob, type filters, output_mode |
| Bash | Shell | Yes | Execute shell commands; default timeout 2 minutes, max 10 minutes |
| BashOutput | Shell | No | Read output from running/completed background shell by ID |
| KillShell | Shell | No | Terminate background shell by ID |
| Task | Builtin | No | Spawn sub-agent for complex tasks |
| TodoWrite | Builtin | No | Manage task list (id, content, status) for multi-step progress tracking |
| WebFetch | Builtin | No | Fetch URL content and process it |
| WebSearch | Builtin | No | Search the web and return results |

**Tool filtering:**
```bash
ante --allowed-tools Read Glob Grep "analyze only"       # allowlist
ante --disallowed-tools Bash Write "read-only analysis"  # denylist
ante --allowed-tools "Read" "Bash(cargo test)" "Bash(cargo clippy)"  # ToolMatcher syntax
```

- Tool names matched case-insensitively
- `ToolMatcher` syntax supports fine-grained pattern control
- `--yolo` flag skips all tool approval prompts

### 2.3 Skills System

Skills are the primary extensibility mechanism. They follow an open format called "Agent Skills" — portable across compatible agent products.

**Skill structure:**
```
my-skill/
├── SKILL.md           # Required — YAML frontmatter + instructions
├── scripts/           # Executable code the agent can run
├── references/        # Detailed docs loaded on demand
└── assets/            # Templates, schemas, data files
```

**SKILL.md frontmatter fields:**

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| name | No | Directory name | Skill identifier |
| description | No | First paragraph | When to use; shown to main agent for delegation |
| argument-hint | No | — | Hint for expected arguments (e.g., `<path>`) |
| user-invocable | No | true | Whether user can invoke via `/skillname` slash command |
| disable-model-invocation | No | false | Prevent model from auto-invoking |
| allowed-tools | No | — | Pre-approved tools (e.g., `Read`, `Bash(git diff -- *)`) |
| metadata | No | — | Arbitrary key-value pairs |

**Discovery order (later overrides earlier):**
1. System-level built-in skills
2. `~/.ante/skills/` (user-level)
3. `agents/skills/` (project-level)
4. `.ante/skills/` (project-level)
5. `.claude/skills/` (project-level — Claude.ai compatibility)

**Invocation:**
```bash
/commit                    # Invoke by name
/review src/core/session.rs  # With arguments ($ARGUMENTS placeholder)
```

### 2.4 Sub-Agents

Sub-agents are full independent agents (not just tools) spawned by the main agent via the `Task` tool.

**Built-in sub-agents (2):**
- **General** — General-purpose research, code search, multi-step tasks. Main agent delegates when it needs complex search it isn't confident completing in a few tries.
- **Explorer** — Fast agent specialized for codebase exploration. Finds files by pattern, searches keywords, answers structural questions.

**Custom sub-agents:**
Created as markdown files in `~/.ante/agents/` with YAML frontmatter:

```yaml
---
name: "security-reviewer"
description: "Reviews code for security vulnerabilities and OWASP top 10 issues"
color: "red"
---
You are a security-focused code reviewer...
```

Frontmatter fields: `name` (required), `description` (required), `model` (optional override), `tools` (optional restrict), `color` (optional TUI display).

**How delegation works:**
1. Main agent evaluates available sub-agents and their descriptions
2. Delegates via `Task` tool with a detailed prompt
3. Sub-agent runs independently with its own context
4. Result returned to main agent, incorporated into conversation

**State isolation:** Each sub-agent has its own independent session, memory, and configuration. Failures don't cascade to parent.

**Discovery:**
- Built-in agents (General, Explorer)
- `~/.ante/agents/` directory (user-level)
- All registered at session initialization time

### 2.5 Memory System

**Project memory (per-project, automatic):**
- Memory directory: `.claude/projects/<project-path>/memory/`
- Key file: `MEMORY.md` — first 200 lines injected into system prompt at every session start
- Agent consults existing memory, records new insights, updates/removes outdated memories
- Fully editable plain markdown; agent can also update via Write/Edit tools

**Memory file organization:**
```
memory/
├── MEMORY.md           # Auto-loaded (max 200 lines); link to details
├── debugging.md        # Detailed debugging notes
├── patterns.md         # Code patterns and conventions
└── architecture.md     # Architecture decisions
```

**Memory principles:** Concise (truncated at 200 lines), semantic (topic-organized, not chronological), accurate (updated/removed when wrong), actionable (what worked, what didn't, why).

**Per-project scoping:** Different projects have independent memory directories — React frontend knowledge doesn't bleed into Rust backend.

### 2.6 Eval & Benchmark

- Uses Terminal Bench and Harbor as primary external benchmark
- Philosophy: "Grade outcomes, not trajectories" — did the agent solve the problem?
- Principles: start early/simple, honest eval from actual failures, isolate and reproduce regressions
- Topped Terminal Bench 1.0 leaderboard (2025)
- Topped Terminal Bench 2.0 leaderboard (February 2026) — verified agent, best-in-class for Gemini
- Self-described: "Evaluation is the backbone of building a reliable AI agent."

### 2.7 Offline Mode (Experimental)

- Integrated llama.cpp inference engine (no external dependency)
- Discovers GGUF models on system (single-file and sharded models)
- Memory estimation based on model file size + KV cache (scales with context window)
- Minimum context window: 32K tokens
- Model preferences: `context_window`, `thinking`, `temperature`
- Antigma maintains curated list of verified GGUF models; also publishes models on Hugging Face
- Future: building toward self-contained agent stack (`AntigmaLabs/nanochat-rs` in progress)

### 2.8 Agent Organization (Experimental)

Four multi-agent coordination architectures:

**Independent:**
- Agents work in parallel with no interaction
- Aggregator synthesizes outputs at end
- Best for: diverse perspectives, brainstorming, redundant verification
- Pattern: Start → Parallel fan-out → Barrier/sync → Aggregator → End

**Decentralized:**
- Parallel rounds; agents read each other's prior outputs, propose refinements
- Fixed number of rounds; consensus without central coordinator
- Best for: debate-style reasoning, peer review, negotiation
- Pattern: Initialize → Shared board → Parallel read+propose → Append deltas → Convergence check loop

**Centralized Iterative:**
- Central orchestrator decomposes, dispatches in parallel, evaluates, decides refine-or-finish
- Best for: complex tasks with quality gates (code generation + review, multi-step research)
- Pattern: Setup → Orchestrator decomposes → Parallel execute → Barrier → Orchestrator evaluates → Done? → Final synthesis

**Hybrid Iterative:**
- Orchestrator plans + dispatches; then agents peer-refine each other's work; orchestrator evaluates
- Best for: high-quality collaborative output where structured planning + peer feedback both matter
- Pattern: Orchestrator plans → Parallel draft → Peer refine round → Orchestrator evaluates → Loop or done

---

## 3. Architecture

### 3.1 Client-Daemon Split

```
┌────────────────┐          ┌─────────────────────────────┐
│     Client      │    Op    │          Daemon             │
│                 │ ───────▶ │                             │
│  TUI (ratatui)  │          │  Session → Turn → Step      │
│  or Headless    │ ◀─────── │                             │
│                 │    Evt   │  Tools   Providers  Store   │
└────────────────┘          └─────────────────────────────┘
```

**Client** — User-facing layer (TUI or headless CLI). Sends `Op` operations and renders `Evt` events.

**Daemon** — Core engine. Receives operations, manages sessions, dispatches to LLM providers, schedules tool execution, emits events.

**Transport** — Bounded async channels (Tokio) within the same process. Message IDs enable tracing.

This architecture allows swapping frontends without touching the core engine.

### 3.2 Concept Hierarchy

```
Project
 └── Session
      └── Task
           └── Turn
                └── Step
```

| Concept | Description |
|---------|-------------|
| Project | Git repo or root directory. Multiple sessions possible. |
| Session | One episode of interaction. Manages dialog state, token usage, context compaction. |
| Task | One piece of work. Can span multiple turns. Generally 1 task = 1 turn without approval interruption. |
| Turn | One back-and-forth with agent. Starts with user input, ends with agent message or approval request. |
| Step | One interaction from agent with LLM. Handles tool calls and mechanics. |

### 3.3 Op/Evt Message Protocol

**Message ID prefixes:**
- `op_` — operations (client → daemon)
- `evt_` — events (daemon → client)
- `ses_` — sessions
- `step_` — steps

**Operations reference:**

| Op | Fields | Description |
|----|--------|-------------|
| NewSession | model, provider, policy, streaming, config | Initialize new session |
| UserInput | String | Submit user prompt |
| ApprovalResponse | allow/deny | Respond to tool approval |
| SlashCommand | skill name, args | Invoke a skill |
| OfflineMode | OfflineModeOp | Offline mode operations |
| Interrupt | — | Abort current task |
| Shutdown | — | Clean shutdown |

**Events reference:**

| Evt | Fields | Description |
|-----|--------|-------------|
| SessionInit | metadata | Session is ready |
| TaskStarted | id | New task begun |
| TaskFinished | id, error, is_interrupted | Task completed or failed |
| AgentMessage | String | Text response from agent |
| Thinking | String | Chain-of-thought content |
| MessageDelta | String | Streaming content chunk |
| ToolCallStarted | tool_use | Tool execution began |
| ToolCallFinished | result | Tool execution completed |
| ToolCallCancelled | — | Tool execution was cancelled |
| RequestApproval | tool_use | Agent needs permission |
| UsageUpdate | tokens, cost | Token/cost tracking |
| Info | String | Informational message |
| Error | String | Error message |

### 3.4 LLM Provider System

Each provider implements a common interface:

```rust
pub trait Provider: Send + Sync {
    async fn send(&self, request: ProviderRequest) -> Result<ProviderResponse>;
    fn capability(&self) -> ProviderCapability;
}
```

**Provider catalog (from docs and runtime drift analysis):**

| ID | Provider | Wire Format | Models | Runtime Status |
|----|----------|------------|--------|---------------|
| anthropic | Anthropic | Messages API | Claude family | Confirmed in runtime |
| openai | OpenAI | Chat Completions | GPT-4o, o1, etc. | Confirmed |
| openai-response | OpenAI | Responses API | GPT-4o | Confirmed |
| gemini | Google Gemini | Gemini API | Gemini family | Docs only — NOT in runtime v0.0.preview6 (drift!) |
| open-router | Open Router | OpenAI-compatible | 400+ models | Confirmed |
| xai | Grok (xAI) | OpenAI-compatible | Grok models | Confirmed |
| local | llama.cpp | GGUF local | Qwen, Llama, etc. | Confirmed |

**Runtime drift note:** `gemini` provider is documented but NOT present in `ante 0.0.preview6` runtime (confirmed via network/binary analysis in `antigma_drift_report.md`). This is a known discrepancy between docs and implementation.

**Provider resolution order (CLI → project → user → env → defaults):**
1. CLI flags (`--provider`, `--model`)
2. Project config (`.ante/config.json`)
3. User settings (`~/.ante/settings.json`)
4. Environment variables
5. Compiled defaults

**Third-party / OpenAI-compatible providers:**
- Open Router: `export OPEN_ROUTER_API_KEY="sk-or-..."` then `ante --provider open-router --model anthropic/claude-sonnet-4-5`
- Custom base URL: `export OPENAI_API_BASE="https://api.together.xyz/v1"` then use `--provider openai`
- Requirement: model MUST support tool use (function calling) — Ante relies on tools for agent capabilities

### 3.5 Storage Layout

| Location | Purpose |
|----------|---------|
| `~/.ante/settings.json` | User preferences |
| `~/.ante/skills/` | User-level skills |
| `~/.ante/agents/` | User-level sub-agents |
| `.ante/` | Project-local config |
| `.claude/` | Claude.ai compatibility directory |
| `.claude/projects/<path>/memory/` | Per-project auto-memory |
| `/tmp/ante/<project-hash>/` | Temporary files, per-project scoped |
| `~/.ante/models/` | Local GGUF models (offline mode) |

Override home config via `ANTE_HOME` environment variable.

---

## 4. Session & Context Management

### 4.1 Session Lifecycle

1. Client sends `Op::NewSession` with model, provider, and policy
2. Daemon resolves provider, authenticates, discovers skills and sub-agents
3. Daemon creates Session, emits `Evt::SessionInit`
4. User sends `Op::UserInput` to start task
5. Session spawns a Turn → communicates with LLM
6. Turn executes tools, requests approvals, eventually completes
7. When context budget nears limit: auto-compaction summarizes history

### 4.2 Context Compaction

- Automatic summarization when approaching context limit
- No manual trigger required
- `MEMORY.md` truncated at 200 lines; only first 200 lines injected into system prompt
- Sessions expire after TTL (default 30 days); summaries persist longer

### 4.3 Session Commands

```bash
ante sessions              # List all sessions
ante resume <session-id>   # Resume a session
ante export <session-id>   # Export session
ante config get model      # Get setting
ante config set model claude-opus-4.6  # Set setting
ante config reset          # Reset to defaults
ante version               # Version info
ante doctor                # Environment diagnostics
```

---

## 5. Configuration Reference

### 5.1 Settings File (`~/.ante/settings.json`)

```json
{
  "model": "claude-sonnet-4-5-20250514",
  "provider": "anthropic",
  "theme": "default",
  "policy": "default",
  "has_completed_onboarding": true
}
```

Policy values: `"default"` (approval required for gated tools) or `"yolo"` (all auto-approved).

### 5.2 Environment Variables

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Anthropic API auth |
| `OPENAI_API_KEY` | OpenAI API auth |
| `OPEN_ROUTER_API_KEY` | Open Router API auth |
| `OPENAI_API_BASE` | Custom OpenAI-compatible base URL |
| `ANTE_HOME` | Override home config directory |
| `ANTE_DISABLE_STREAMING` | Disable streaming in TUI mode |

### 5.3 Headless CLI Flags

| Flag | Description |
|------|-------------|
| `-p, --prompt <PROMPT>` | The prompt to run |
| `-m, --model <MODEL>` | Override model name |
| `--provider <PROVIDER>` | Override API provider |
| `--yolo` | Skip all tool approval prompts |
| `--output-format <FORMAT>` | Output format: json, human, minimal (default: minimal) |
| `--system-prompt <PROMPT>` | Replace default system prompt entirely |
| `--append-system-prompt <TEXT>` | Append text to system prompt |
| `--allowed-tools <TOOLS>...` | Only allow these tools (space-separated) |
| `--disallowed-tools <TOOLS>...` | Disallow these tools (space-separated) |
| `--check` | Run verification pass after main task |

---

## 6. Known Issues & Limitations

### 6.1 Documented Reliability Issues (Why Ante is "Insanely Buggy")

- **Preview instability:** `v0.0.preview6` — breaking changes expected and acknowledged
- **Gemini provider drift:** Docs advertise Gemini support; runtime binary does not include it (confirmed via binary analysis)
- **Context management fragility:** Context compaction at 200-line MEMORY.md limit is blunt; no semantic prioritization
- **Sub-agent coordination:** Parent-child coordination is basic — parent simply waits for result, no partial result streaming, no parallel sub-agent fan-out with progress visibility
- **Resource limits:** CPU/memory caps per sub-agent are designed for but not yet implemented
- **Agent organization:** All four patterns (Independent, Decentralized, Centralized Iterative, Hybrid Iterative) are "experimental" — no production reliability guarantees
- **Offline mode:** "Experimental" — llama.cpp integration, memory estimation not always accurate
- **Eval framework:** No built-in A/B testing between providers/models; Terminal Bench is external
- **Installation:** "Installation instructions coming soon" — quickstart page is a stub
- **Windows:** Not supported (Linux/macOS only)
- **IDE integration:** Not yet available (CLI-only)
- **Web UI:** No browser-based interface
- **SAML/enterprise SSO:** Not supported (env vars + OAuth only)
- **Debugging tools:** No integrated debugger
- **RAG system:** Not built-in; must be implemented via skills

### 6.2 Known Architecture Gaps vs Claude Code / Codex

| Gap | Impact |
|-----|--------|
| No IDE integration | Can't use from VS Code / Cursor panel |
| No team/org features | Single-user focused; no org-level settings |
| Smaller ecosystem | Fewer community skills/agents than established players |
| No cloud hosting | Users run locally; no managed service |
| No structured output schema | No first-class JSON output mode from agent (only from Bash tools) |
| Breaking changes | Not production-stable; upgrade paths not guaranteed |

---

## 7. Comparison to Alternatives

| Dimension | Ante | Claude Code | Codex | Gemini CLI | thegent |
|-----------|------|-------------|-------|-----------|---------|
| **Language** | Rust | Go | Rust (core) + Python (SDK) | Go | Python |
| **Interface** | CLI/TUI (ratatui) | CLI/IDE panel | CLI/IDE/Web | CLI | CLI/TUI (compositor) |
| **Dependencies** | Minimal (Rust native) | Low-moderate | Moderate | Low | Moderate |
| **Provider Support** | 6+ (incl. local) | Anthropic-primary | OpenAI-primary | Gemini-native | Via OpenRouter (400+) |
| **Offline Capable** | Yes (experimental) | Limited | Limited | No | No |
| **Skills System** | Yes (open format, portable) | Pattern-based (informal) | Plugin registry | Limited | Hooks (script-based) |
| **Sub-Agents** | Yes (built-in General + Explorer + custom) | Yes (via Task) | Yes (via Task) | Limited | Crew pattern |
| **Memory** | Persistent per-project (MEMORY.md auto-injected) | Session-based | Session-based | Session-based | Work-stream + dumps (manual) |
| **Eval/Benchmark** | Terminal Bench #1 (2025+2026) | Anthropic internal | OpenAI internal | Google internal | Quality gates (compliance focus) |
| **Maturity** | Preview (v0.0.preview6) | Stable | Stable | Beta | Active development |
| **Open Source** | Partial | Partial | Partial | Limited | Internal |
| **Agent Organization** | 4 patterns (experimental) | Limited | Worker pattern | Limited | Crew + work-stream |
| **Governance** | Tool filtering + approval only | Similar | Similar | Similar | Comprehensive policy engine |
| **Enterprise** | Single-user | Anthropic-backed | OpenAI-backed | Google-backed | Multi-tenant designed |

**Where Ante is stronger:**
- Native Rust (performance, security, minimal deps)
- True offline capability (local GGUF via llama.cpp)
- Headless-first design with structured output formats
- Clean client-daemon separation (testable, swappable frontends)
- Skills as open, portable, versioned format
- Terminal Bench leadership (real-world task completion)
- Multi-agent architecture patterns (4 named patterns with clear use-when guidance)

**Where Ante is weaker:**
- Preview reliability (bugs, missing features, breaking changes)
- No IDE integration (CLI-only)
- No org/enterprise features
- No built-in A/B benchmarking or metrics collection
- Governance is minimal (no policy engine, no quality gates)
- Gemini docs-vs-runtime gap (trust issues)

---

## 8. "Turn Codex into Ante" — Gap Analysis

This section identifies what Codex CLI (thegent's current harness foundation) needs to become Ante-equivalent. thegent's strategy is: use Codex as the harness foundation, implement Ante-like orchestration features on top of thegent's routing/governance/TUI infrastructure.

### 8.1 What Codex Already Has (Do Not Reinvent)

| Feature | Codex Status | Notes |
|---------|-------------|-------|
| Responses API integration | Complete | Core of Codex; app-server protocol |
| Tool system | Complete | apply_patch, exec, web_search, image_view |
| Streaming (SSE + WebSocket) | Complete | 8-event sequence fully implemented |
| TUI (ratatui) | Complete | Codex has its own ratatui-based TUI |
| Headless/exec mode | Complete | `codex exec` subcommand |
| Multi-provider routing | Via thegent proxy | CLIProxy + LiteLLM router |
| MCP server mode | Complete | `codex --mcp-server` |
| Sub-agent spawning | Via Task tool | Basic; needs enhancement |

### 8.2 Feature Gaps: What Codex Needs to Match Ante

**Gap 1: Skills System (High Priority)**

Ante has a discoverable, versioned, open-format skills system. Codex has no equivalent.

What to build:
- Skills discovery from `~/.codex/skills/` and `.codex/skills/` (+ `.claude/skills/` for compat)
- SKILL.md format: YAML frontmatter + markdown instructions
- `allowed-tools` per skill (pre-approved tool list)
- `/skillname` slash command invocation in TUI and headless
- `$ARGUMENTS` placeholder substitution
- `scripts/`, `references/`, `assets/` subdirectory support
- Override: project-level skills override user-level by name
- User-invocable vs model-invocable distinction

**Gap 2: Persistent Per-Project Memory (High Priority)**

Ante auto-injects `MEMORY.md` (first 200 lines) into every session system prompt. Codex has no persistent memory.

What to build:
- `MEMORY.md` at `.claude/projects/<hash>/memory/MEMORY.md` (or equivalent path)
- Auto-load and inject into system prompt at session init
- Agent can read/write memory files via existing Write/Edit tools
- 200-line injection limit; topic-file linking pattern
- Per-project scoping (project hash as directory key)

**Gap 3: Named Sub-Agent Types with Descriptions (Medium Priority)**

Ante has built-in General + Explorer sub-agents with natural-language descriptions used for routing. Codex's Task tool spawns agents but has no type system.

What to build:
- Sub-agent definition format (markdown + YAML frontmatter: name, description, model, tools, color)
- Discovery from `~/.codex/agents/` and `.codex/agents/`
- Built-in General and Explorer equivalents
- Main agent can query available sub-agents and their descriptions for delegation decisions
- All sub-agents registered at session init

**Gap 4: `--check` Verification Pass (Medium Priority)**

Ante's `--check` flag runs a second verification pass where the agent reviews its own work.

What to build:
- Post-completion hook: `--check` or `check: true` config
- Second LLM pass with prompt: "Review what was accomplished vs the original request. Complete anything missing. Optimize without affecting correctness."
- Exits with non-zero code if verification detects incomplete work

**Gap 5: Structured Headless Output Formats (Medium Priority)**

Ante has `minimal`, `human`, and `json` output modes with event-per-line JSON. Codex's headless output is less structured.

What to build:
- `--output-format json` mode: each agent event as JSON object, one per line
- Event types: agent_message, tool_call_started, tool_call_finished, usage_update, error
- `--output-format minimal` (default): only agent messages + errors
- `--output-format human`: all events with ANSI formatting
- Standard exit codes: 0=success, 1=input error, 2=execution error, 3=provider error, 4=cancelled

**Gap 6: Agent Organization Patterns (Lower Priority — Future)**

Ante defines four multi-agent coordination architectures. Codex/thegent has ad-hoc crew patterns.

What to build (eventually):
- Independent: parallel fan-out + aggregator synthesis
- Decentralized: shared board, parallel read+propose, convergence detection
- Centralized Iterative: orchestrator with quality-gated refinement loop
- Hybrid Iterative: orchestrator + peer refine rounds
- Selection via `--agent-organization independent|decentralized|centralized|hybrid`

**Gap 7: Context-Aware Directory Injection (Low Priority — Easy Win)**

Ante automatically appends current directory folder structure to headless prompts.

What to build:
- In headless mode: enumerate `fd -t f -d 3` output (or equivalent) and append to system prompt
- Or: inject `.tree` summary of top-level structure

**Gap 8: Offline / Local Model Support (Lower Priority)**

Ante integrates llama.cpp for fully offline GGUF inference.

What to build (eventually):
- `--provider local` flag routing to local llama.cpp or Ollama
- GGUF model discovery and memory estimation
- thegent already has OpenRouter for multi-provider; local models are an extension

### 8.3 What thegent Adds on Top of Codex (Ante Doesn't Have)

| thegent Feature | Ante Equivalent | Gap Direction |
|----------------|----------------|---------------|
| Comprehensive policy engine | Tool filtering + approval only | thegent is stronger |
| 5-layer security pipeline | None | thegent is stronger |
| Quality gates (coverage, complexity, SAST) | Terminal Bench external eval only | thegent is stronger |
| Multi-tenant org features | Single-user only | thegent is stronger |
| Work-stream (WORK_STREAM.md) | No equivalent | thegent is stronger |
| Hook system (lifecycle hooks) | No hooks | thegent is stronger |
| OpenRouter 400+ model routing | 6 providers (no OpenRouter equivalent by default) | thegent is stronger |
| Conversation dumps | Minimal memory (MEMORY.md) | thegent is stronger |
| thegent plan loop (autonomous continuous work) | No equivalent | thegent is stronger |

### 8.4 Implementation Priority (Ranked)

| Priority | Feature | Effort | Value |
|----------|---------|--------|-------|
| P1 | Skills system (SKILL.md format, discovery, slash commands) | M | Extensibility foundation |
| P1 | Persistent MEMORY.md injection | S | Cross-session continuity |
| P2 | Named sub-agent types with descriptions | M | Better task delegation |
| P2 | `--check` verification pass | S | Output quality |
| P2 | Structured headless output formats + exit codes | S | CI/CD integration |
| P3 | Context-aware directory injection (headless) | XS | Easy win |
| P3 | Agent organization patterns (4 modes) | L | Advanced orchestration |
| P4 | Offline / local model support | L | Air-gap capability |

---

## 9. Sources & References

| Source | URL | Fetched |
|--------|-----|---------|
| Ante official docs | https://docs.useante.com/ | 2026-02-20 |
| Antigma Labs homepage | https://antigma.ai/ | 2026-02-20 |
| Antigma GitHub | https://github.com/AntigmaLabs | 2026-02-20 |
| Antigma X/Twitter | https://x.com/antigma_labs | 2026-02-20 |
| nanochat-rs (Rust LLM core) | https://github.com/AntigmaLabs/nanochat-rs | 2026-02-20 |
| Terminal Bench leaderboard | https://www.tbench.ai/leaderboard | 2026-02-20 |
| Harbor framework (eval) | https://harborframework.com/docs/datasets/running-tbench | 2026-02-20 |
| Local webarchives | ~/Downloads/*Ante.webarchive (16 pages) | 2026-02-20 |
| Runtime drift analysis | docs/research/antigma/antigma_drift_report.md | 2026-02-20 |

**Ante documentation pages archived (16 total):**
Overview, Quickstart, Core Concepts & Protocol, Architecture, Interactive TUI, Headless Mode, Skills, Sub-Agents, Tools, Memory, Model & Provider Catalog, Preferences, Adding a 3rd Party Provider, Offline Mode (Experimental), Agent Organization (Experimental), Eval & Benchmark

---

## 10. Quick Reference

```
ANTE AT A GLANCE
================

Company:    Antigma Labs
Language:   Rust (native)
Status:     Preview v0.0.preview6 (breaking changes expected)
Platforms:  macOS, Linux
Benchmark:  #1 Terminal Bench 1.0 (2025) + Terminal Bench 2.0 (Feb 2026)

ARCHITECTURE:
  Client (TUI/Headless) ←Op/Evt→ Daemon (Sessions, Tools, Providers, Memory)
  Concept hierarchy: Project → Session → Task → Turn → Step

PROVIDERS (runtime-confirmed):
  anthropic | openai | openai-response | open-router | xai | local
  (gemini: documented but NOT in runtime v0.0.preview6)

BUILT-IN TOOLS (12):
  File I/O: Read, Write*, Edit*, Glob, Grep
  Shell:    Bash*, BashOutput, KillShell
  Builtin:  Task, TodoWrite, WebFetch, WebSearch
  (* = approval required by default)

SKILLS:
  Directory: ~/.ante/skills/ (user) or .ante/skills/ (project)
  Format:    SKILL.md (YAML frontmatter + markdown)
  Invoke:    /skillname [arguments]

SUB-AGENTS:
  Built-in: General, Explorer
  Custom:   ~/.ante/agents/*.md (YAML frontmatter: name, description, model, tools)

MEMORY:
  Location: .claude/projects/<path>/memory/MEMORY.md
  Behavior: First 200 lines auto-injected into system prompt every session
  Scope:    Per-project, independent between projects

KEY COMMANDS:
  ante                           # Interactive TUI
  ante "prompt"                  # Headless (minimal output)
  ante -p "prompt" --check       # Headless + self-verification
  ante --provider openai --model gpt-4o "prompt"
  ante --yolo "fix all warnings"
  ante --allowed-tools Read Glob Grep "read-only analysis"
  ante sessions                  # List sessions
  ante resume <id>               # Resume session

OUTPUT FORMATS (headless):
  minimal (default) | human | json (--output-format json)

AGENT ORGANIZATION (experimental):
  Independent | Decentralized | Centralized Iterative | Hybrid Iterative

KEY ENV VARS:
  ANTHROPIC_API_KEY | OPENAI_API_KEY | OPEN_ROUTER_API_KEY
  ANTE_HOME | ANTE_DISABLE_STREAMING | OPENAI_API_BASE

GAP ANALYSIS — "TURN CODEX INTO ANTE":
  P1: Skills system (SKILL.md, discovery, slash commands)
  P1: Persistent MEMORY.md auto-injection
  P2: Named sub-agent types with descriptions
  P2: --check verification pass
  P2: Structured headless output formats + exit codes
  P3: Context-aware directory injection (headless)
  P4: Offline / local model support
```

---

*Comprehensive Ante context document. Synthesized from 16 official Ante documentation pages (webarchive), runtime binary analysis (v0.0.preview6), and web research. Last updated: 2026-02-20. Maintained in: docs/context/ante.md*

---

## Source: context/bifrost.md

# Bifrost (AI Gateway)

**Product:** Bifrost by Maxim AI
**GitHub:** https://github.com/maximhq/bifrost
**Docs:** https://docs.getbifrost.ai
**License:** Apache 2.0 (Enterprise tier available)
**Language:** Go
**Research date:** 2026-02-20

---

## What It Is

Bifrost is a self-hosted, open-source AI gateway written in Go. It exposes a single
OpenAI-compatible HTTP API and routes requests across 15–20+ LLM providers. It is the fastest
known open-source LLM gateway: 11 µs mean overhead at 5,000 RPS, 50x faster P99 latency vs.
LiteLLM in benchmarks, 100% success rate at scale (vs. 88.78% for LiteLLM at 500 RPS).

Key value props:
- Near-zero latency overhead (Go, connection pooling, zero-alloc weighted key selection)
- Semantic caching (vector similarity, not exact match)
- Three-layer routing: CEL routing rules → governance → adaptive load balancing
- Enterprise governance: virtual keys, hierarchical budgets, rate limiting, SSO, audit logs
- Native MCP gateway (connects to MCP servers, injects tools into model function schema)
- Self-hosted = data sovereignty (prompts never leave controlled infra)

---

## Deployment

**One-liner (local dev):**
```bash
npx -y @maximhq/bifrost           # NPX
docker run -p 8080:8080 maximhq/bifrost   # Docker
```

**With persistence:**
```bash
docker run -p 8080:8080 -v $(pwd)/data:/app/data maximhq/bifrost
```

**Configuration modes:**
- **Web UI** (default): SQLite-backed, real-time config at `http://localhost:8080`
- **File-based**: `config.json` in app directory; disables Web UI; requires restart on changes

**Kubernetes (Helm):**
- Official Helm chart; production HA = 3 replicas, HPA to 20, 70% CPU / 80% memory targets
- PostgreSQL backend recommended for production
- Vector store (Weaviate, Qdrant, Redis) for semantic cache

**Embedded Go SDK:**
```go
import "github.com/maximhq/bifrost/core"
// Bypass HTTP transport entirely; embed in process
```

---

## Authentication

**Client to Bifrost:** Pass `api_key="dummy"` — Bifrost handles all provider credentials.

**With governance enabled:** Client passes `x-bf-vk: <virtual-key>` header.

**Provider credentials:** Configured via Web UI, REST API (`POST /api/providers`), or config.json.

**Environment variable injection in config:**
```json
{"value": "env.OPENAI_API_KEY"}
```

**Secrets management:** Kubernetes secrets, Vault, AWS Secrets Manager, Azure Key Vault.

---

## API Compatibility

**Primary endpoint:**
```
POST http://localhost:8080/v1/chat/completions
Content-Type: application/json

{
  "model": "openai/gpt-4o-mini",
  "messages": [...]
}
```

**Model ID format:** `provider/model` (e.g., `openai/gpt-4o`, `anthropic/claude-3-5-sonnet`)

**SDK-specific base URLs (drop-in replacement):**
```
http://localhost:8080/openai     # OpenAI SDK
http://localhost:8080/anthropic  # Anthropic SDK
http://localhost:8080/genai      # Google GenAI SDK
```

**Additional endpoints:**
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v1/chat/completions` | POST | Primary; OpenAI-compatible |
| `/api/providers` | POST | Dynamic provider configuration |
| `/v1/mcp/tool/execute` | POST | Explicit MCP tool execution |
| `/metrics` | GET | Prometheus scrape |

---

## Provider Support

15–20+ providers including:

| Provider | Notes |
|----------|-------|
| OpenAI | Full support |
| Anthropic | Claude 3.x, 4.x |
| AWS Bedrock | ARN + deployment mapping required |
| Google Vertex AI | Deployment config required |
| Azure OpenAI | Deployment mapping + api_version required |
| Cerebras | Fast inference |
| Cohere | Command family |
| Mistral | Full family |
| Ollama | Local models |
| Groq | Ultra-fast inference |
| Google GenAI | Gemini family |
| Hugging Face | Via inference API |
| Together AI | Supported |
| Perplexity | Supported |

Special key schemas for cloud providers:
- **Bedrock**: `access_key`, `secret_key`, `session_token`, `region`, `arn`, `deployments` map
- **Azure**: `deployments` map, `api_version` (default: `2024-10-21`)
- **Vertex**: deployment config

---

## Routing / Fallbacks

Three-layer pipeline, evaluated in order (first match wins):

```
1. Routing Rules (CEL expressions)     → override provider+model
2. Governance Routing (weighted random) → from virtual key provider_configs
3. Adaptive Load Balancing (enterprise) → performance-scored key+provider selection
```

### Layer 1: Routing Rules (CEL)

Dynamic, evaluated per request. Context variables available:
```
model, provider
headers["x-tier"], params["region"]
virtual_key_id, team_name, customer_id
budget_used, tokens_used    // 0-100 percentages
request                     // full request object
```

Example:
```cel
headers["x-tier"] == "premium"
budget_used > 85                    // failover at budget threshold
team_name == "ml-research"
```

Scope order: VirtualKey → Team → Customer → Global

### Layer 2: Governance Routing

Uses virtual key `provider_configs`:
- Validates model against `allowed_models` (empty = Model Catalog = all supported)
- Filters providers by budget limits and rate limits
- Weighted random selection among eligible providers
- Fallback chain = remaining providers sorted by weight (descending)

### Layer 3: Adaptive Load Balancing (Enterprise)

Two sub-levels:
- **Provider selection**: scored by error rate (50%), latency MV-TACOS (20%), utilization (5%)
- **Key selection**: always runs; scored by error rate, latency, TPM hits, health state

Health state machine per key: Healthy → Degraded → Failed → Recovering
- 90% penalty reduction in 30s (fast recovery)
- 25% exploration factor probes recovering keys

### Fallback Behavior

On failure: remaining providers tried in weight/score order. Circuit-broken keys (Failed state)
skipped entirely. Keys in Recovering state eligible with reduced probability.

### Model Catalog

Internal catalog downloaded from `https://getbifrost.ai/datasheet` (startup + 24h refresh) and
provider `/v1/models` endpoints. Provides O(1) model-to-provider lookup.

---

## Caching

**Type:** Semantic (vector similarity), not exact-match. This is the key differentiator.

```json
{
  "cache": {
    "provider": "openai",
    "embedding_model": "text-embedding-3-small",
    "ttl": 3600,
    "threshold": 0.8,
    "conversation_history_threshold": 0.7,
    "cache_by_model": true,
    "cache_by_provider": false
  }
}
```

**Vector store backends:** Weaviate, Qdrant, Redis
**Cache hit latency:** ~5ms (vs. ~2,000ms for full LLM call)
**Cache miss with embedding:** ~60ms

Prometheus metric: `bifrost_cache_hits_total`

---

## Observability

### Prometheus (native)

Endpoint: `GET /metrics`

Key metrics:
- `bifrost_upstream_requests_total`
- `bifrost_cost_total`
- `bifrost_cache_hits_total`

Custom labels via request headers:
- `x-bf-prom-team`: tag by team
- `x-bf-prom-environment`: tag by environment

### OpenTelemetry

```json
{
  "telemetry": {
    "service_name": "my-gateway",
    "collector_url": "http://otel-collector:4318",
    "trace_type": "genai_extension",
    "headers": {"Authorization": "Bearer ..."}
  }
}
```

Uses GenAI OpenTelemetry semantic conventions.

### Structured Logging

SQLite (dev) or PostgreSQL (prod). Fields: request, response, tokens, cost, latency, errors.

### Maxim AI Plugin

Native integration; auto-forwards all traces to Maxim platform for evaluation, A/B testing, alerts.

### Web UI Dashboard

Real-time monitoring at `http://localhost:8080` (requires SQLite/Web UI mode):
analytics, provider health, cache hit rate, model catalog, virtual key management, budget charts.

---

## Unique Features

1. **Semantic caching**: Vector-similarity based; most gateways use exact-match only
2. **CEL routing rules**: Common Expression Language expressions with rich request context
3. **Adaptive Load Balancing**: ML-scored two-level (provider + key) routing (Enterprise)
4. **MCP gateway**: Native client+server MCP support with governance on tool execution
5. **Go implementation**: 11 µs overhead vs. ~1ms+ for Python-based alternatives
6. **Hierarchical budgets**: Customer → Team → User → VirtualKey with hard limits per level
7. **Health state machine**: Per-key circuit breaking with fast recovery and exploration probes
8. **Embedded SDK mode**: Go SDK can be embedded in-process, bypassing HTTP transport entirely
9. **Model Catalog**: Self-maintained pricing + availability data refreshed every 24h
10. **Enterprise SSO**: OIDC with Okta, Entra ID; SAML 2.0; LDAP; role sync from IdP groups

---

## Key Differences from OpenRouter / LiteLLM

### vs. OpenRouter

| Dimension | Bifrost | OpenRouter |
|-----------|---------|------------|
| Deployment | Self-hosted (full control) | SaaS only |
| Data sovereignty | Yes | No (data transits OpenRouter) |
| Provider count | 15–20+ | 300+ models, 50+ providers |
| Pricing | Free OSS + paid Enterprise | Per-token markup |
| Semantic cache | Yes | No |
| CEL routing rules | Yes | No |
| MCP gateway | Yes | No |
| Compliance (HIPAA/SOC2) | Yes (self-hosted) | Not documented |
| Performance overhead | 11 µs | N/A (external service) |

### vs. LiteLLM

| Dimension | Bifrost | LiteLLM |
|-----------|---------|---------|
| Language | Go | Python |
| Overhead at 5k RPS | 11 µs | ~1,000+ µs |
| P99 at 500 RPS | 1.68s | 90.72s |
| Memory at 500 RPS | 120MB | 372MB |
| Provider count | 15–20 | 100+ |
| Semantic caching | Yes | Yes (via integration) |
| CEL routing | Yes | No |
| MCP gateway | Yes | No |
| Embedded SDK | Yes (Go) | No |
| Enterprise SSO | Yes | Yes (proxy server) |

---

## Proxy Considerations for thegent CLIProxy

### What Bifrost Does That CLIProxy Does Not

1. **Semantic caching**: CLIProxy has no caching layer at all. Bifrost's vector-similarity cache
   hits at ~5ms vs. full provider call at ~2s. For thegent's use case (repeated agent queries),
   this would be a significant cost and latency win.

2. **CEL routing rules**: CLIProxy's routing is static config-based. Bifrost evaluates CEL
   expressions with request context (headers, budget utilization, team name) per-request. This
   enables dynamic routing without code changes.

3. **Adaptive load balancing with health scoring**: CLIProxy passes through to a single backend
   or uses LiteLLM's round-robin/cheapest/fastest strategies. Bifrost's two-level ML-scored
   selection with per-key health state machines is more sophisticated.

4. **Per-key circuit breaking**: Bifrost tracks health state per API key, not just per provider.
   Multiple keys for the same provider are managed independently with exploration probes.

5. **MCP gateway**: CLIProxy has no native MCP client/server integration. Bifrost centralizes
   tool discovery, schema injection, and governed execution.

6. **Hierarchical budget enforcement**: CLIProxy's cost tracking (WP-5003 / Economic Governance
   Framework) is implemented but operates at a different granularity. Bifrost's Customer → Team →
   User → VirtualKey hierarchy is multi-tenant by design.

7. **Web UI**: CLIProxy has no operational UI. Bifrost ships a built-in dashboard.

8. **Native Prometheus metrics**: CLIProxy has no `/metrics` endpoint. Bifrost exposes
   `bifrost_upstream_requests_total`, `bifrost_cost_total`, `bifrost_cache_hits_total` natively.

9. **Provider-namespaced endpoints**: Bifrost exposes `/openai`, `/anthropic`, `/genai` so SDK
   clients need only a base URL change. CLIProxy requires `transform_responses` mode for
   Responses API compatibility but has no provider-namespaced routing.

10. **Enterprise SSO/RBAC**: CLIProxy has no authentication layer. Bifrost has OIDC, SAML 2.0,
    LDAP, role mapping, and audit logs.

### What CLIProxy Does That Bifrost Does Not

1. **Responses API translation**: CLIProxy translates OpenAI Responses API format to Chat
   Completions and back, emitting the correct 8-event SSE sequence. This is Codex CLI
   compatibility that Bifrost does not implement.

2. **WebSocket transport for Responses API**: CLIProxy bridges WebSocket `/v1/responses` to HTTP
   streaming, enabling persistent multi-turn Codex sessions. Bifrost is HTTP-only.

3. **Codex model metadata enrichment**: CLIProxy transforms `/v1/models` responses into the
   Codex-format schema (`models` key, 20+ required fields, `x-models-etag` header). Bifrost
   uses the standard `data` array format.

4. **thegent-internal model ID mapping**: CLIProxy maps thegent catalog IDs
   (`claude-sonnet-4.5`, `gemini-3-flash`) to backend-specific IDs. Bifrost uses
   `provider/model` format directly.

5. **Agent-specific session management**: CLIProxy integrates with thegent's session registry,
   work stream, and lifecycle hooks. Bifrost is a general-purpose gateway.

### Priority Gaps to Close

| Priority | Feature | Bifrost Approach | CLIProxy Gap |
|----------|---------|-----------------|--------------|
| P1 | Semantic caching | Vector store + threshold | No caching |
| P1 | Native Prometheus | `/metrics` endpoint | No metrics |
| P1 | Health-state circuit breaking | Per-key state machine | LiteLLM-level only |
| P2 | CEL routing rules | Per-request CEL evaluation | Static config only |
| P2 | Adaptive load balancing | ML-scored two-level | cheapest/fastest/round_robin |
| P2 | Virtual key governance | Hierarchical budget + rate limit | Budget tracking only |
| P3 | Web UI dashboard | Built-in at :8080 | None |
| P3 | MCP gateway integration | Native client+server | Separate MCP server only |
| P3 | Enterprise SSO | OIDC + SAML | None |

---

*Full research report: `docs/research/BIFROST_RESEARCH_2026-02-20.md`*
*Related: `docs/research/OPENROUTER_GAP_ANALYSIS_2026-02-20.md`*
*Context for: `docs/context/openrouter.md`*

---

## Source: context/claude-code.md

# Claude Code CLI Context

> Definitive reference for implementing Claude Code support in thegent (agent harness integration, CLI subprocess execution, tool system interop).
> Sources: claude.ai/install.sh, @anthropic-ai/claude-code npm package, official documentation, GitHub anthropics/claude-code (fetched 2026-02-20).

---

## What is Claude Code

Claude Code is Anthropic's official agentic coding harness: a command-line interface that provides conversational access to Claude AI models directly from the terminal. Unlike web-based interfaces, Claude Code:

- Maintains full codebase context with deep file system access
- Executes real filesystem, git, and shell operations without manual approval
- Supports Model Context Protocol (MCP) servers for external tool integration
- Spawns parallel subagents (up to 7) for decomposed task execution
- Integrates git workflows (branch creation, commits, pull requests) natively
- Provides extensibility through slash commands, skills, and custom hooks

Claude Code is specifically designed for pair-programming workflows: helping developers understand complex code, execute routine tasks, implement features, debug, test, and manage CI/CD workflows.

**Key distinction**: Claude Code is the harness/CLI, not an LLM. It wraps Anthropic's Claude models (Haiku, Sonnet, Opus) with tooling, persistence, and agent orchestration.

---

## Installation & Authentication

### Installation Methods

**Option 1: Native binary (recommended)**
```bash
# macOS/Linux
curl -fsSL https://claude.ai/install.sh | bash

# Windows PowerShell
irm https://claude.ai/install.ps1 | iex
```

**Option 2: npm (legacy, requires Node.js 18+)**
```bash
npm install -g @anthropic-ai/claude-code
```

### Authentication

Claude Code requires a valid Claude subscription:
- **Claude Pro**: $20/month (includes API access)
- **Claude Max**: $100-200/month (higher rate limits)
- **Teams/Enterprise**: Via Anthropic

Authentication uses your `ANTHROPIC_API_KEY` environment variable:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
claude "your query"
```

API keys are created in the [Anthropic Console](https://console.anthropic.com/keys).

---

## Core CLI Usage

### Interactive Mode (Default)

```bash
claude "your natural language query"
```

Launches a conversational session where Claude can run multiple agentic turns until the task is complete. Supports:
- File operations (read, write, edit)
- Shell command execution
- File globbing and search
- Git operations
- Web research
- Tool invocation

Exit with `Ctrl+C` or by responding "done" to the agent.

### Non-Interactive Mode (--print)

```bash
claude -p "query"
```

Executes a single query and exits, printing results to stdout. Useful for:
- Scripting and batch automation
- CI/CD integration
- Piping output to other commands
- One-shot analysis tasks

Does not enter conversation loop; all work is completed in a single agent execution window.

### Session Management

| Command | Purpose |
|---------|---------|
| `claude` | Start new session |
| `claude -c` / `--continue` | Resume most recent session |
| `claude --resume <session-id>` | Resume specific prior session |

---

## Key CLI Flags

### Output & Format

| Flag | Values | Description |
|------|--------|-------------|
| `-p`, `--print` | boolean | Non-interactive mode; single query and exit |
| `--output-format` | `text`, `json`, `stream-json` | Response format |

**Output format details**:
- `text`: Plain text; default for interactive mode
- `json`: Full response with metadata as JSON object
- `stream-json`: Streaming JSONL format; one JSON object per message as it arrives (useful for real-time processing)

**Example**:
```bash
claude -p --output-format json "List TypeScript files"
```

```json
{"type":"message","content":"Found the following TypeScript files:...","tool_calls":[]}
{"type":"tool_result","name":"glob","content":"src/index.ts src/utils.ts..."}
```

### Model Selection

| Flag | Values | Description |
|------|--------|-------------|
| `--model` | `haiku`, `sonnet`, `opus`, or full model name | Which Claude model to use |

**Examples**:
```bash
claude --model opus "complex analysis task"
claude --model haiku "simple file listing"
claude --model claude-opus-4-20250514 "specific version"
```

Default: `sonnet` (balanced cost/capability). Use `opus` for complex reasoning; `haiku` for simple, fast tasks.

### Agent Control

| Flag | Values | Description |
|------|--------|-------------|
| `--max-turns` | integer | Maximum agent conversation turns (default: unlimited) |
| `--allow-subagents` | boolean | Enable spawning parallel subagents (default: true) |

**Example**:
```bash
claude --max-turns 10 "refactor this codebase"
```

Prevents runaway agentic loops. Useful for controlling costs in CI/CD.

### Tool & Permission Control

| Flag | Values | Description |
|------|--------|-------------|
| `--allowedTools` | comma-separated list | Whitelist of tools; only these can be called |
| `--disallowedTools` | comma-separated list | Blacklist of tools; these are forbidden |
| `--permission-mode` | `auto`, `manual` | Auto-approve actions or request permission for each |
| `--dangerously-skip-permissions` | boolean | Skip all permission checks (dangerous; CI/CD only) |

**Tools available** (can be controlled):
- `bash`: Shell command execution
- `read_file`: File read (read-only)
- `write_file`: File creation
- `edit_file`: File modification (precise edits)
- `glob`: File pattern matching
- `grep`: Content search
- `web_search`: Internet research
- `git_*`: Git operations (branch, commit, pr, etc.)

**Example**:
```bash
claude --disallowedTools bash,web_search "refactor code without shell access"
```

---

## Configuration System

Claude Code uses a hierarchical configuration system, with later entries overriding earlier ones:

1. **Organizational policies** (enterprise only)
2. **Project shared** (`.claude/settings.json`)
3. **Project local** (`.claude/settings.local.json`)
4. **User global** (`~/.claude/settings.json`)

### Configuration File Format

```json
{
  "modelName": "sonnet",
  "maxTokens": 8000,
  "maxTurns": 20,
  "tools": {
    "allowedTools": ["bash", "read_file", "write_file", "git_*"],
    "disallowedTools": [],
    "permissionMode": "manual"
  },
  "mcpServers": [
    {
      "name": "postgres",
      "command": "node",
      "args": ["~/mcp-servers/postgres/index.js"]
    }
  ],
  "hooks": {
    "preToolUse": ["scripts/pre-tool-check.sh"],
    "postToolUse": ["scripts/post-tool-cleanup.sh"]
  },
  "extendedThinking": true,
  "memory": {
    "enabled": true,
    "persistenceFile": ".claude/memory.json"
  }
}
```

### Key Configuration Fields

| Field | Type | Description |
|-------|------|-------------|
| `modelName` | string | Claude model to use (haiku, sonnet, opus) |
| `maxTokens` | integer | Max output tokens per response |
| `maxTurns` | integer | Max agentic turns before stopping |
| `tools.allowedTools` | array | Whitelist of tools |
| `tools.disallowedTools` | array | Blacklist of tools |
| `tools.permissionMode` | enum | `auto` or `manual` (request per action) |
| `mcpServers` | array | MCP server configurations |
| `hooks` | object | Lifecycle event hooks (see below) |
| `extendedThinking` | boolean | Enable Claude's extended reasoning mode (default: true) |
| `memory.enabled` | boolean | Persist conversation memory across sessions |

---

## Project Memory (CLAUDE.md)

Claude Code searches for `.claude/CLAUDE.md` files at project root and parent directories, using them as persistent project context. This file should contain:

- Project architecture and key concepts
- Development standards and conventions
- Common workflows and patterns
- Known limitations or gotchas
- Integration instructions for external tools

Example:
```markdown
# My Project

## Architecture
- Backend: Node.js/Express (src/server/)
- Frontend: React (src/client/)
- Database: PostgreSQL with Prisma ORM

## Standards
- Use TypeScript for all code
- Follow ESLint config in .eslintrc.json
- All PRs require tests

## Quick Start
1. npm install
2. npm run dev
3. Visit http://localhost:3000
```

Claude Code loads and references this automatically, improving code decisions and reducing token waste explaining basics.

---

## Hooks System

Claude Code supports event-driven hooks for lifecycle management. Hooks are shell scripts triggered at specific points in the agent execution.

### Hook Events

| Event | Fires When | Pass Arguments |
|-------|-----------|-----------------|
| `PreToolUse` | Before any tool invocation | tool name, tool arguments (JSON) |
| `PostToolUse` | After tool completes | tool name, exit code, result |
| `UserPromptSubmit` | Before processing user input | prompt text |
| `Stop` | Agent session ends | exit reason, task summary |
| `SessionStart` | New session begins | session metadata |

### Hook Registration

In `.claude/settings.json`:
```json
{
  "hooks": {
    "preToolUse": ["scripts/pre-tool-check.sh"],
    "postToolUse": ["scripts/post-tool-cleanup.sh"],
    "stop": ["scripts/cleanup.sh"]
  }
}
```

### Hook Script Example

`scripts/pre-tool-check.sh`:
```bash
#!/bin/bash
tool_name=$1
tool_args=$2

# Reject bash if running in CI
if [[ "$tool_name" == "bash" && "$CI" == "true" ]]; then
  echo "error: bash forbidden in CI"
  exit 1
fi

exit 0
```

---

## MCP (Model Context Protocol) Integration

Claude Code supports MCP servers for connecting to external tools: databases, cloud services, APIs, local file systems, version control systems.

### MCP Configuration

In `.claude/settings.json`:

```json
{
  "mcpServers": [
    {
      "name": "postgres",
      "command": "node",
      "args": ["~/.mcp-servers/postgres.js"],
      "env": {
        "DATABASE_URL": "postgresql://..."
      },
      "timeout": 5000,
      "transport": "stdio"
    },
    {
      "name": "github",
      "command": "npx",
      "args": ["@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_..."
      }
    }
  ]
}
```

### Supported MCP Transports

| Transport | Use Case | Notes |
|-----------|----------|-------|
| `stdio` | Local tools, CLI apps | Most common; subprocess over stdin/stdout |
| `sse` | HTTP servers | Server-sent events; stateful connections |
| `websocket` | Browser-like clients | Real-time bidirectional communication |

### MCP Tool Discovery

After configuring MCP servers, available tools are automatically discovered and exposed. Example: Postgres MCP server provides tools like `query_database`, `execute_transaction`, etc.

```bash
claude "Query my postgres database for user count"
```

Claude automatically invokes the Postgres MCP tool without explicit configuration.

---

## Tool System

### Built-In Tools (Always Available)

| Tool | Purpose | Permissions |
|------|---------|-----------|
| `read_file` | Read file contents | Requires read permission |
| `write_file` | Create or overwrite file | Requires write permission |
| `edit_file` | Precise edits (character ranges) | Requires write permission |
| `glob` | Pattern-based file finding | Read-only |
| `grep` | Content search (regex) | Read-only |
| `bash` | Shell command execution | Dangerous; gated |
| `git_*` | Git operations (branch, commit, status, pr, etc.) | Gated; requires git repo |
| `web_search` | Internet research via Exa API | Requires API key |

### Tool Invocation in Prompts

Claude Code automatically detects when tools are needed and invokes them. You can hint at tool use:

```bash
claude "Find all Python files with 'async def' using glob and grep"
```

Alternatively, force tool invocation with special syntax:

```bash
claude "@path/to/file.py show me the main function"
# References specific file in context
```

### Tool Approval Flow

With `permissionMode: manual` (default):

1. Agent identifies tool need
2. Claude Code requests user approval
3. User approves or denies
4. If approved, tool executes and result feeds back to agent
5. If denied, agent continues without that tool

With `permissionMode: auto`: Tools execute immediately without prompting.

---

## Stdin Input & Piping

Claude Code accepts input via stdin for scripting:

```bash
echo "analyze this code:" | cat - myfile.py | claude --output-format json
```

Or from a file:

```bash
claude < input_prompt.txt
```

Useful for:
- Batch analysis
- Shell pipeline integration
- Pulling prompts from templates
- CI/CD automation

---

## Subagents (Task Parallelization)

Claude Code can spawn up to 7 parallel subagents for decomposed task execution:

```bash
claude "Refactor the API, frontend, and database schema in parallel"
```

Claude automatically:
1. Breaks task into subtasks
2. Spawns subagents for each
3. Coordinates execution
4. Merges results

Controlled via:

| Flag | Description |
|------|-------------|
| `--allow-subagents true/false` | Enable/disable subagent spawning |
| `--max-parallel` | Max concurrent subagents (default: 7) |

---

## Non-Interactive / Subprocess Execution (Python)

To use Claude Code as a subprocess from Python:

```python
import subprocess
import json

result = subprocess.run(
    ["claude", "-p", "--output-format", "json", "Find all TODO comments"],
    capture_output=True,
    text=True,
    env={**os.environ, "ANTHROPIC_API_KEY": api_key}
)

output = json.loads(result.stdout)
todo_comments = output["content"]  # Tool results embedded
exit_code = result.returncode
```

### Streaming Mode (stream-json)

For large operations, use streaming to process results incrementally:

```python
import subprocess
import json

process = subprocess.Popen(
    ["claude", "-p", "--output-format", "stream-json", "Refactor entire codebase"],
    stdout=subprocess.PIPE,
    text=True,
    env={**os.environ, "ANTHROPIC_API_KEY": api_key}
)

for line in process.stdout:
    if line.strip():
        event = json.loads(line)
        if event["type"] == "message":
            print(f"Claude: {event['content']}")
        elif event["type"] == "tool_result":
            print(f"Tool {event['name']}: {event['content']}")

exit_code = process.wait()
```

---

## Exit Codes & Error Handling

| Code | Meaning | Recovery |
|------|---------|----------|
| `0` | Success | Task completed normally |
| `1` | General error | Check stderr for details |
| `2` | Permission denied | User rejected tool use or insufficient permissions |
| `3` | API error | API key invalid, rate limited, or quota exceeded |
| `4` | Timeout | Task exceeded max-turns or wall-clock timeout |
| `5` | Invalid arguments | CLI args malformed or invalid |
| `130` | Interrupted (SIGINT) | User pressed Ctrl+C |

**Always check stderr** for detailed error messages:

```bash
claude "query" 2>&1 | tee claude.log
echo "Exit code: $?"
```

---

## Git Integration

Claude Code is deeply integrated with git:

```bash
claude "Create a feature branch, implement user auth, and commit with good messages"
```

Available git operations:
- `git_branch_create`: Create and switch to new branch
- `git_status`: Check repo status
- `git_diff`: Show changes
- `git_add`: Stage files
- `git_commit`: Commit with message
- `git_push`: Push to remote
- `git_pull_request`: Create PR (via GitHub API)

Example:
```bash
claude "Fix the bug in auth.js (see the error in logs), commit, and create a PR"
```

Claude will:
1. Read auth.js
2. Analyze the error context
3. Implement fix
4. Add and commit
5. Push to a new branch
6. Create GitHub PR with description

---

## Extended Thinking (Reasoning Mode)

By default, Claude Code uses extended thinking for complex reasoning tasks:

```json
{
  "extendedThinking": true
}
```

This enables Claude to think through problems carefully before responding. Consumes more tokens but produces higher-quality results for complex tasks (architecture decisions, debugging, code reviews).

Disable with:

```bash
claude --disable-extended-thinking "list files quickly"
```

---

## Model Selection Best Practices

| Task | Recommended | Reasoning |
|------|------------|-----------|
| Complex refactoring | `opus` | Reasoning, large context, API design |
| Feature implementation | `sonnet` | Good balance; 200k context |
| Bug fixes | `sonnet` or `haiku` | Depends on complexity |
| Code analysis/review | `opus` | Nuanced judgment |
| File operations | `haiku` | Fast, cheap, sufficient |
| One-shot tasks | `haiku` | Minimize cost |

---

## How thegent Integrates Claude Code

thegent uses Claude Code as one of its primary harnesses via:

1. **Subprocess execution**: Spawns `claude -p --output-format json` for batch execution
2. **MCP forwarding**: Exposes thegent MCP tools to Claude Code via `.claude/settings.json`
3. **Configuration propagation**: Passes thegent governance policies to Claude Code via hooks and settings
4. **Session coordination**: Manages Claude Code sessions through the agent orchestration layer
5. **Cost tracking**: Routes API keys and tracks usage through CLIProxyAPIPlus

**Key integration point**: thegent wraps Claude Code invocations to provide:
- Unified model routing
- Cost aggregation across harnesses
- Governance enforcement (approval policies, sandbox modes)
- MCP tool registry management
- Session state persistence

---

## Common Workflows

### Analyze Codebase + Generate Report

```bash
claude "Analyze our src/ directory for architectural issues, security concerns, and performance problems. Provide a structured report."
```

### Test-Driven Development

```bash
claude "Write failing tests for the user login feature in test/auth.test.ts, then implement the feature in src/auth.ts"
```

### Debugging with Context

```bash
claude "Debug this error: $(cat error.log). The stack trace shows lib/parser.js:42. What's wrong?"
```

### Parallel Code Review

```bash
claude "Review the API endpoints (src/api/), database schema (db/), and frontend components (src/components/) in parallel for best practices"
```

### Batch Refactoring

```bash
claude --max-turns 15 "Refactor all TypeScript files to remove deprecated lodash methods. Use native ES6 alternatives."
```

---

## Key Differences from Web Claude

| Feature | Web Claude | Claude Code CLI |
|---------|-----------|-----------------|
| File system access | Upload/download only | Deep, bidirectional |
| Git integration | Manual workflows | Native branch/commit/PR |
| Tool availability | Limited (web tools only) | All tools + MCP servers |
| Session persistence | Per-browser | Cross-session memory |
| Automation | Interactive only | Scriptable via CLI |
| MCP servers | Not supported | Full support |
| Subagents | No | Up to 7 parallel |
| Speed | Fast but single-threaded | Parallel execution possible |
| Cost | Per-token | Per-token (same models) |

---

## Relevant to thegent Because

thegent integrates Claude Code as a primary harness for:

1. **Coding tasks**: thegent routes code-related work to Claude Code via task spawning
2. **Tool orchestration**: Claude Code's MCP server system aligns with thegent's MCP tool registry
3. **Governance**: thegent's policy engine coordinates with Claude Code's hooks and permission modes
4. **Cost tracking**: API calls through Claude Code are aggregated into thegent's usage reports
5. **Agent coordination**: thegent orchestrates multiple Claude Code instances for parallel work
6. **Configuration**: Project-level `.claude/settings.json` integrates with thegent's global CLAUDE.md

---

## Sources

- [Claude Code Overview](https://code.claude.com/docs/en/overview)
- [Claude Code MCP Integration](https://code.claude.com/docs/en/mcp)
- [Shipyard Claude Code Cheat Sheet](https://shipyard.build/blog/claude-code-cheat-sheet/)
- [Claude Code CLI Reference (2025)](https://www.eesel.ai/blog/claude-code-cli-reference)
- [Claude Code Complete Guide 2026](https://www.jitendrazaa.com/blog/ai/claude-code-complete-guide-2026-from-basics-to-advanced-mcp-2/)
- [GitHub: anthropics/claude-code](https://github.com/anthropics/claude-code)
- [Building Agents with Claude Agent SDK](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk)

---

## Source: context/cloudflare-ai-gateway.md

# Cloudflare AI Gateway

**Last updated:** 2026-02-20
**Research source:** `docs/research/CLOUDFLARE_AI_GATEWAY_RESEARCH_2026-02-20.md`

---

## What It Is (Edge-Hosted Gateway)

Cloudflare AI Gateway is a fully managed, edge-native AI control plane. It proxies all AI API requests through Cloudflare's global network (300+ PoPs) before forwarding them to providers. Unlike LiteLLM (self-hosted) or Portkey (SaaS centralized), Cloudflare's gateway runs on its CDN infrastructure — the same backbone used for its core DDoS/CDN product.

Key identity: it is a **proxy** (not a router or SDK). You point your existing OpenAI client at a different URL. No code changes beyond `baseURL`.

Introduced: 2023. Major feature expansion: August 2025 (dynamic routing, DLP, BYOK, Unified Billing).

---

## URL Structure / Authentication

### Base URL Pattern

```
https://gateway.ai.cloudflare.com/v1/{account_id}/{gateway_id}/{provider}
```

### OpenAI-Compatible Unified Endpoint

```
https://gateway.ai.cloudflare.com/v1/{account_id}/{gateway_id}/compat
```

This is the recommended drop-in replacement for `https://api.openai.com/v1`. Any OpenAI SDK client pointing here will work across all supported providers without further code changes.

### Universal Endpoint (Fallback Chains)

```
POST https://gateway.ai.cloudflare.com/v1/{account_id}/{gateway_id}
```

Request body is a JSON array of provider objects tried in sequence.

### Dynamic Routing Endpoint

```
https://gateway.ai.cloudflare.com/v1/{account_id}/{gateway_id}/dynamic/{route_name}
```

### Authentication Modes

| Mode | How | When to Use |
|------|-----|------------|
| **Pass-through** | Provider key in `Authorization: Bearer {key}` as normal | Default for unauthenticated gateways |
| **Gateway Auth** | Add `cf-aig-authorization: Bearer {cf_token}` alongside provider key | When gateway-level auth is enabled |
| **BYOK** | No provider key in request; add `cf-aig-byok-alias: {alias}` | Keys stored in Cloudflare Secret Store |
| **Unified Billing** | Only `Authorization: Bearer {cf_token}`; no provider key | For supported providers via Cloudflare credits |

---

## OpenAI Compatibility

Full drop-in replacement for OpenAI SDK clients:

```python
from openai import OpenAI

client = OpenAI(
    api_key="{cf_api_token_or_provider_key}",
    base_url="https://gateway.ai.cloudflare.com/v1/{account_id}/{gateway_id}/compat"
)
```

Supported OpenAI endpoints via `/compat`:
- `/chat/completions`
- `/responses`
- `/v1/models` (lists available models with cost metadata)

The gateway translates provider-specific request/response formats automatically via its Unified Request/Response Translation layer (launched August 2025).

---

## Providers Supported

**24 providers** as of early 2026:

Workers AI, OpenAI, Anthropic, Google AI Studio, Google Vertex AI, Azure OpenAI, Amazon Bedrock, Mistral AI, Cohere, Groq, xAI (Grok), DeepSeek, Replicate, HuggingFace, Perplexity, OpenRouter, ElevenLabs, Cartesia, Cerebras, Fal AI, Baseten, Ideogram, Deepgram, Parallel.

Plus: **Custom Providers** — any OpenAI-compatible endpoint (self-hosted, regional, proprietary).

Unified Billing providers (5): OpenAI, Anthropic, Google AI Studio, xAI, Groq.

---

## Caching

- **Strategy:** Exact match only. Semantic/vector caching is **planned, not yet released**.
- **Scope:** Text and image responses. Audio/video not cached.
- **Backend:** Cloudflare's global CDN edge — responses served from nearest PoP.
- **Claimed benefit:** Up to 90% latency reduction on cache hits.

### Per-Request Cache Control Headers

| Header | Purpose |
|--------|---------|
| `cf-aig-cache-ttl` | TTL in seconds (min 60, max ~2.6M / ~1 month) |
| `cf-aig-skip-cache` | Bypass cache entirely for this request |
| `cf-aig-cache-key` | Override default key (use for per-user caching by embedding user ID) |
| `cf-aig-cache-status` | Response: `HIT` or `MISS` |

**Per-user caching:** Not native. Implement by setting `cf-aig-cache-key` to include a user identifier — this namespaces cache entries per user.

**Cache hits:** Always report $0 cost in analytics.

**Note:** Volatile cache — simultaneous identical requests may not share a cache entry during initial population.

---

## Rate Limiting

### Gateway-Level Configuration

Set in dashboard or via API. Applies uniformly to all requests through the gateway.

| Parameter | Values |
|-----------|--------|
| `rate_limiting_interval` | Seconds (e.g., 60) |
| `rate_limiting_limit` | Max requests in interval |
| `rate_limiting_technique` | `fixed` (time buckets) or `sliding` (rolling window) |

- **429 Too Many Requests** returned when exceeded.
- No per-user or per-IP rate limiting natively at this level.

### Per-User / Per-Key Rate Limiting

Use **Dynamic Routing Rate Limit nodes** and **Budget Limit nodes** for per-user quota enforcement. This is the recommended path for fine-grained rate limiting. Supports fallback to cheaper model when quota exceeded.

---

## Observability / Analytics

### Analytics Dashboard

Metrics tracked:
- Total requests
- Token usage (input + output tokens)
- Cost estimates (per provider, per model)
- Error counts
- Cache hit rate (%)

Access: Cloudflare Dashboard > AI > AI Gateway. GraphQL API for external querying.

### Logging

Logged per request: prompt, response, provider, model, timestamp, status, tokens, cost, duration, cache status, custom metadata.

| Plan | Log Limit |
|------|-----------|
| Free | 100,000 total across all gateways |
| Paid | 10M per gateway |

Storage rate limit: 500 logs/second per gateway. Max log size: 10 MB (larger not stored).

Storage behavior: configure auto-delete oldest, stop at limit, or manual deletion.

**Logpush:** Export logs to S3, R2, Splunk, New Relic, etc. Workers Paid plan only. 4 jobs max; $0.05/M requests overage.

### Custom Metadata

Tag requests via `cf-aig-metadata` header (JSON, max 5 entries, string/number/boolean only):

```
cf-aig-metadata: {"user_id": "u_123", "session": "abc", "env": "prod"}
```

Metadata appears in logs and enables filtering.

### OpenTelemetry

Export traces to any OTEL backend (Jaeger, Grafana, Datadog, etc.) — added 2025-09-24.

### Response Headers for Observability

| Header | Description |
|--------|-------------|
| `cf-aig-event-id` | Unique event ID (all requests, including failures) |
| `cf-aig-log-id` | Log ID for feedback submission |
| `cf-aig-step` | Fallback chain step that handled request (0=primary) |
| `cf-aig-cache-status` | `HIT` or `MISS` |

### Cost Tracking

Per-request cost based on token usage × model pricing. Custom pricing override per request:

```
cf-aig-custom-cost: {"per_token_in": 0.000001, "per_token_out": 0.000002}
```

Covers voice models (added 2025-11-14) and async video (Sora 2, Veo 3; added 2025-10-24).

---

## Guardrails

Added 2025-02-26.

- Real-time content moderation for both **incoming prompts** and **outgoing responses**
- Applied uniformly across all providers through a single configuration
- Categories configurable (examples: violence, hate, sexual content)
- Per-category action: **block** (reject request/response) or **flag** (allow + log)
- Audit trails for all guardrail decisions (compliance: GDPR, HIPAA, etc.)
- Works at edge, before provider is called (if blocking prompt)

---

## Data Loss Prevention (DLP)

Added 2025-08-28. Part of the AI Gateway Firewall.

- Scans both incoming prompts and outgoing responses
- Pre-built profiles: financial data, SSN/Tax IDs, PII, healthcare data
- Custom pattern profiles supported
- Compliance frameworks: GDPR, HIPAA, PCI DSS
- Per-request logs show matched profiles and action taken
- Actions: **block** or **alert/flag**
- Configured as gateway-level policy (not per-request)

---

## Evaluations

- Create **datasets** from filtered log subsets (up to 10 per gateway)
- Run evaluators against datasets to measure performance
- **Human Feedback evaluator** (open beta): measures % positive ratings
- Metrics: cost, latency, accuracy
- **Model Playground** (added 2025-10-14): test and compare models in the dashboard without code
- Feedback submission API uses `cf-aig-log-id` response header
- Additional evaluators planned but not yet released

---

## Workers AI Integration

Workers AI = Cloudflare's own edge GPU inference service. Deep integration with AI Gateway:

- Access via `env.AI.run()` in Workers — no extra API token after 2025-11-14
- Same gateway features (caching, logging, guardrails) apply to Workers AI calls
- Workers AI runs colocated with the gateway on Cloudflare edge — zero extra network hop
- Supports Deepgram models via WebSocket
- Supports Pipecat models (voice/audio pipelines)
- Native binding: pre-authenticated within the Cloudflare account context

---

## Dynamic Routing

Flagship feature added August 2025.

Visual (drag-and-drop) or JSON-based routing flow configuration. No code changes needed. Deployed as versioned routes with instant rollback.

### Node Types

| Node | Purpose |
|------|---------|
| **Conditional** | Branch on request body, headers, or metadata expressions |
| **Percentage** | Probabilistic traffic split (A/B testing, gradual rollouts) |
| **Rate Limit** | Per-key request quotas; fallback on exceeded |
| **Budget Limit** | Per-key spend caps per period |
| **Provider** | Route to specific provider/model |
| **Fallback** | Handle provider failure |

### Use Cases

- Paid users → GPT-4o, free users → GPT-4o-mini
- 80% GPT-4o / 20% Claude 3.5 Sonnet A/B test
- Cap free tier at 100 requests/day, fallback to cheaper model
- Chain: sanitize prompt → main model → post-process response
- Geography-based model selection

---

## Unique Edge Advantages

1. **CDN-Native Caching**: Responses cached at 300+ global edge PoPs. Cache hits served at CDN speeds, not from a centralized server.

2. **Workers AI Colocation**: When using Workers AI, inference and gateway are on the same edge node — no external network hop.

3. **DDoS Protection Bundled**: Cloudflare's core DDoS mitigation applies to AI Gateway traffic automatically.

4. **Edge Routing Decisions**: Dynamic Routing rules evaluated at edge, not in a centralized gateway server. Minimal routing decision latency.

5. **Cloudflare Ecosystem Synergy**: Native integration with R2 (log storage), Workers (custom proxy logic), Zero Trust (access control), Secret Store (BYOK), DLP, and the broader platform.

6. **Zero Infrastructure Ops**: Fully managed. No servers to run, no ingress to configure, no scale-out planning.

7. **Argo Smart Routing** (if enabled): Optimized TCP paths from Cloudflare's network to AI providers, potentially reducing provider round-trip latency.

---

## Key Differences from OpenRouter / LiteLLM / Portkey

| Dimension | Cloudflare | OpenRouter | LiteLLM | Portkey |
|-----------|-----------|-----------|---------|---------|
| **Hosting** | CDN edge (SaaS) | SaaS centralized | OSS / self-hosted | SaaS centralized |
| **Provider count** | 24 + custom | 300+ models | 100+ providers | 250+ models |
| **Caching** | Edge (exact match) | None | Semantic + exact | Semantic + exact |
| **Dynamic routing** | Visual + JSON flows | None | Config-file-based | Limited |
| **DLP** | Yes (Firewall) | No | No | Limited |
| **Guardrails** | Yes (edge) | No | No | Yes (rules) |
| **WebSocket/Realtime** | Yes | No | Partial | No |
| **BYOK** | Yes (Secret Store) | No | No | Virtual keys |
| **Unified billing** | 5 providers | No (5% markup per req) | No | No |
| **OTEL export** | Yes | No | Yes | Yes |
| **Evaluation system** | Yes (basic, beta) | No | No | Yes (advanced) |
| **Model playground** | Yes | No | No | No |
| **Zero data retention** | Yes (OAI + Anthropic) | No | No | No |
| **Self-host option** | No | No | Yes | No |
| **Free tier** | Yes (generous) | Usage markup | Free OSS | $49/mo base |
| **Deployment overhead** | Zero | Zero | High (ops) | Zero |

**Cloudflare's moat:** Edge caching, Workers AI native colocation, DLP, ZDR, and seamless Cloudflare ecosystem integration.

**Cloudflare's gaps:** No semantic caching (yet), smaller provider catalog than OpenRouter, evaluation system immature vs. Portkey, SaaS-only (no on-prem).

---

## What thegent Should Steal

### High Priority

1. **`cf-aig-metadata` pattern** — Allow callers to attach structured metadata (user_id, session_id, env, team) to every proxied request. Store in request context, expose in logs and analytics. Max 5 key-value pairs per request is a reasonable initial constraint.

2. **`cf-aig-step` response header** — When thegent's CLIProxy handles fallbacks, return a header/field indicating which provider/model ultimately served the request. Critical for debugging and cost attribution.

3. **`cf-aig-event-id` on every response** — Return a unique trace ID on every proxied response, including failures. This is the anchor point for all downstream observability (logs, feedback, OTEL spans).

4. **Per-request retry/backoff headers** — `cf-aig-max-attempts`, `cf-aig-retry-delay`, `cf-aig-backoff` (constant/linear/exponential). Callers control retry behavior without changing routing config.

5. **Per-request custom cost override** — `cf-aig-custom-cost: {"per_token_in": float, "per_token_out": float}`. Essential for accurate cost tracking when using negotiated provider rates.

6. **`cf-aig-skip-cache` per-request** — Allow callers to bypass cache on a per-request basis, not just globally. Needed for non-deterministic, time-sensitive, or user-personalized requests.

7. **`cf-aig-collect-log` override** — Per-request ability to suppress or force logging. Needed for PII-sensitive requests or high-volume debug scenarios.

### Medium Priority

8. **Cache-Key per-user namespacing** — Allow callers to include a user/session identifier in the cache key, enabling per-user caching semantics without building a separate cache system.

9. **Fixed vs. Sliding window rate limiting** — Both techniques should be available. Sliding window prevents burst clustering at window boundaries, which is a real pathological case for AI API usage.

10. **`cf-aig-cache-status` response header** — Always return HIT/MISS so callers can observe cache behavior without dashboard access. Useful for testing and client-side cost optimization.

11. **Fallback chain with step tracking** — Universal endpoint pattern: JSON array of provider configs tried in order. `step` in response (or header) tells you which one succeeded. This is more expressive than thegent's current fallback model.

12. **Zero Data Retention flag** — `cf-aig-zdr` header that routes to a provider endpoint that doesn't retain data. Implement as a routing hint to ZDR-capable provider endpoints. Critical for enterprise/regulated customers.

13. **Customizable log storage policies** — Auto-delete oldest vs. stop-on-limit. Don't silently drop logs; make the policy explicit and configurable.

### Lower Priority / Aspirational

14. **Visual dynamic routing** — A JSON/YAML-defined routing flow with conditional nodes, percentage splits, and budget limits. The JSON config approach is achievable before building a visual UI. This is a superset of thegent's current cost-aware routing.

15. **OTEL trace export** — Export per-request spans to external OTEL backends. The `cf-aig-event-id` anchor makes this implementable as a post-processing export rather than in-path instrumentation.

16. **Model playground** — A CLI or TUI interface to test and compare models against each other with the same prompt. `thegent compare "prompt" --models gpt-4o,claude-3-5 --metrics cost,latency`.

17. **DLP scanning** — Regex/pattern-based PII scanning on prompts and responses before they are logged or forwarded. Even a basic implementation (SSN, credit card patterns) provides significant compliance value.

18. **Evaluation datasets** — Allow users to create named sets of logged requests, then run evaluators (cost, latency, accuracy) against them. Builds on existing log storage.

### What NOT to Copy

- **Cloudflare ecosystem lock-in**: Logpush to R2, Workers AI binding, Secret Store — these only make sense within the Cloudflare platform. thegent must remain provider-agnostic.
- **Only exact-match caching**: thegent should implement semantic caching (Cloudflare has yet to release this).
- **No self-host option**: thegent is designed to be runnable locally/on-prem. That is a differentiation to preserve.
- **Centralized Unified Billing**: This is a complex billing product, not a gateway feature. Not worth replicating.

---

## Source: context/codex.md

# Codex Harness Context

> Definitive reference for implementing Codex support in thegent (agent harness integration, programmatic SDK, app-server protocol, MCP server, CLI invocation, sandbox/approval system).
> Primary source: Direct analysis of codex-upstream Rust monorepo at `/Users/kooshapari/temp-PRODVERCEL/485/API/codex-upstream/`. Verified 2026-02-20.
> Full research: `docs/research/CODEX_HARNESS_RESEARCH_2026-02-20.md`

---

## What is Codex

Codex is OpenAI's agentic coding harness: a compiled Rust binary (`codex-rs`) with a TypeScript CLI shim (`codex-cli`) and a TypeScript programmatic SDK (`@openai/codex-sdk`). Unlike web-based tools, Codex:

- Operates on files and shell via `apply_patch` and `shell_exec` tools registered with the OpenAI Responses API
- Enforces approval policies (untrusted / on-failure / on-request / never) for each command and file change
- Provides platform-specific sandboxing: Linux Landlock + seccomp, macOS sandbox profiles, Windows token restriction
- Exposes a bidirectional JSON-RPC-like protocol over stdio (`codex app-server`) for IDE/tool integration
- Provides a formal programmatic TypeScript SDK (`@openai/codex-sdk`) wrapping the exec subprocess
- Exposes a prototype MCP server mode (`codex mcp server`) with two tools
- Maintains layered TOML configuration: MDM > system > user > project > session flags

**Architecture**:

```
codex (binary, Rust)
├── codex-rs/app-server          <- App Server daemon (JSON-RPC-like over stdio)
├── codex-rs/app-server-protocol <- Protocol schemas (v1 deprecated + v2 current)
├── codex-rs/mcp-server          <- MCP server mode (prototype, 2 tools)
├── codex-rs/codex-api           <- Backend client (Responses API, exclusively streaming)
├── codex-rs/exec                <- `codex exec` non-interactive subcommand
├── codex-rs/tui                 <- Terminal UI (Ratatui-based)
└── sdk/typescript               <- @openai/codex-sdk (Node.js 18+)
```

The App Server powers ALL surfaces: CLI TUI, VS Code extension, JetBrains, Xcode, macOS desktop, web app, and Codex Cloud. The TypeScript SDK (`@openai/codex-sdk`) wraps `codex exec --experimental-json` as a subprocess — it does NOT use the app-server protocol.

---

## Key Concepts

| Term | Definition |
|------|-----------|
| Thread | Persistent conversation session, recorded as rollout file in `$CODEX_HOME/sessions/` |
| Turn | One user-input → agent-response cycle within a thread |
| Item | Atomic event during a turn: agent_message, command_execution, file_change, mcp_tool_call, etc. |
| App Server | Codex daemon process communicating over bidirectional JSONL stdio |
| v1 protocol | Deprecated method namespace (`newConversation`, `sendUserTurn`); do not use |
| v2 protocol | Current method namespace (`thread/start`, `turn/start`); use exclusively |
| Sandbox policy | Filesystem/network access policy: `read-only`, `workspace-write`, `danger-full-access` |
| Approval policy | Human-in-the-loop gate: `untrusted`, `on-failure`, `on-request`, `never` |
| Dynamic tool | Client-registered tool that the model can invoke; execution routed back to the client |
| Skill | SKILL.md/SKILL.json reusable agent instructions discoverable from `.codex/skills/` directories |

---

## Backend API: `/v1/responses`

Codex exclusively uses the OpenAI **Responses API** (`POST /v1/responses`), always with `stream: true`. It does NOT use Chat Completions API (except for legacy local-provider fallback).

### Request Shape

```
POST /v1/responses
Content-Type: application/json
Authorization: Bearer $CODEX_API_KEY

{
  "model": "gpt-5.1-codex-max",
  "instructions": "...",
  "input": [...],               // ResponseItem array
  "tools": [...],               // apply_patch, shell_exec, web_search, etc.
  "tool_choice": "auto",
  "parallel_tool_calls": true,
  "reasoning": {                // o-series models
    "effort": "high",           // minimal | low | medium | high | xhigh
    "summary": "..."
  },
  "store": true,                // Azure: true; OpenAI direct: false
  "stream": true,               // always true
  "text": {                     // structured output
    "format": {
      "type": "json_schema",
      "strict": true,
      "schema": { ... }
    }
  }
}
```

### Provider Routing

Codex only natively supports OpenAI and Azure. For other providers, use `OPENAI_BASE_URL` to proxy through a compatible gateway (LiteLLM, CLIProxy, etc.). The proxy MUST support the Responses API format (not just Chat Completions).

```bash
export OPENAI_BASE_URL="http://localhost:8317/v1"
export CODEX_API_KEY="your-proxy-key"
```

---

## CLI Subcommands and Flags

### Primary Subcommands

| Command | Description |
|---------|-------------|
| `codex` | Interactive TUI |
| `codex exec` | Non-interactive (alias: `codex e`) |
| `codex app-server` | App Server mode (JSON-RPC stdio) |
| `codex mcp server` | MCP server mode (prototype) |
| `codex resume <id>` | Resume previous session |
| `codex fork` | Fork previous session |
| `codex login` | Authenticate |
| `codex logout` | Remove credentials |

### Key Global Flags

| Flag | Values | Purpose |
|------|--------|---------|
| `--model, -m` | string | Override model |
| `--sandbox, -s` | `read-only` / `workspace-write` / `danger-full-access` | Sandbox policy |
| `--ask-for-approval, -a` | `untrusted` / `on-request` / `on-failure` / `never` | Approval policy |
| `--cd, -C` | path | Working directory |
| `--add-dir` | path | Additional writable directory |
| `--config, -c` | `key=value` | Config override (TOML key=value) |
| `--profile, -p` | string | Named config profile |
| `--image, -i` | path(s) | Attach local images |
| `--full-auto` | — | Alias for workspace-write sandbox |
| `--dangerously-bypass-approvals-and-sandbox` | — | No approvals, no sandbox |
| `--search` | — | Enable live web search |

### Exec-Mode-Specific Flags

| Flag | Purpose |
|------|---------|
| `--experimental-json` | REQUIRED for JSONL machine-parseable output |
| `--ephemeral` | Skip session persistence |
| `--output-schema <path>` | JSON Schema file for structured output |
| `--skip-git-repo-check` | Allow running outside git repos |
| `--output-last-message, -o <path>` | Write final agent message to file |

### IMPORTANT: Correct Flag Names

The following are correct flag names as of 2026. Earlier context docs had wrong names:

- CORRECT: `--ask-for-approval` (NOT `--approval-policy`)
- CORRECT: `--experimental-json` (NOT `--json`)
- CORRECT: `--sandbox` (same, but values use hyphens: `read-only`, `workspace-write`, `danger-full-access`)

---

## Programmatic TypeScript SDK

**Package**: `@openai/codex-sdk`
**Requirements**: Node.js 18+

The SDK spawns `codex exec --experimental-json` as a subprocess and parses JSONL output. It does NOT use the app-server protocol.

### Public API

```typescript
import { Codex } from "@openai/codex-sdk";

const client = new Codex({
  apiKey: "sk-...",              // or use CODEX_API_KEY env var
  baseUrl: "http://...",         // override for proxy routing
  config: { ... },              // CodexConfigObject flattened to --config flags
});

// Create a new thread
const thread = client.startThread({
  model: "gpt-5.1-codex-max",
  sandboxMode: "workspace-write",
  workingDirectory: "/path/to/project",
  skipGitRepoCheck: true,
  modelReasoningEffort: "high",   // minimal | low | medium | high | xhigh
  networkAccessEnabled: false,
  webSearchMode: "live",           // disabled | cached | live
  approvalPolicy: "never",         // never | on-request | on-failure | untrusted
  additionalDirectories: ["/extra/dir"],
});

// Resume an existing thread
const resumed = client.resumeThread("thread-id-123", { ... });

// Run (blocking, returns completed Turn)
const turn = await thread.run("Fix the TypeScript errors", {
  outputSchema: { type: "object", properties: { ... } },
  signal: new AbortController().signal,
});
console.log(turn.finalResponse);
console.log(turn.items);          // ThreadItem[]
console.log(turn.usage);          // { input_tokens, output_tokens }

// Run streamed (async generator)
const { events } = await thread.runStreamed("Build a REST API");
for await (const event of events) {
  if (event.type === "item.completed" && event.item.type === "agent_message") {
    console.log(event.item.text);
  }
}
```

### Input Types

```typescript
// Simple string
await thread.run("your prompt");

// Rich input array
await thread.run([
  { type: "text", text: "Analyze this image and fix the UI" },
  { type: "local_image", path: "/path/to/screenshot.png" },
]);
```

### ThreadItem Union (SDK)

```typescript
type ThreadItem =
  | { type: "agent_message"; id: string; text: string }
  | { type: "reasoning"; id: string; text: string }
  | { type: "command_execution"; id: string; command: string; aggregated_output: string; exit_code?: number; status: "in_progress" | "completed" | "failed" }
  | { type: "file_change"; id: string; changes: { path: string; kind: "add" | "delete" | "update" }[]; status: "completed" | "failed" }
  | { type: "mcp_tool_call"; id: string; server: string; tool: string; arguments: unknown; result?: { content: McpContentBlock[]; structured_content: unknown }; error?: { message: string }; status: "in_progress" | "completed" | "failed" }
  | { type: "web_search"; id: string; query: string }
  | { type: "todo_list"; id: string; items: { text: string; completed: boolean }[] }
  | { type: "error"; id: string; message: string }
```

### ThreadEvent Union (SDK streaming)

```typescript
type ThreadEvent =
  | { type: "thread.started"; thread_id: string }
  | { type: "turn.started" }
  | { type: "turn.completed"; usage: Usage }
  | { type: "turn.failed"; error: { message: string } }
  | { type: "item.started"; item: ThreadItem }
  | { type: "item.updated"; item: ThreadItem }
  | { type: "item.completed"; item: ThreadItem }
  | { type: "error"; message: string }
```

### How the SDK Invokes the Binary

```bash
codex exec --experimental-json \
    [--config key=val]... \
    [--model MODEL] \
    [--sandbox MODE] \
    [--cd DIR] \
    [--add-dir DIR]... \
    [--skip-git-repo-check] \
    [--output-schema FILE] \
    [--image FILE]... \
    [resume THREAD_ID]
```

The prompt is piped to stdin. JSONL events come from stdout. The SDK sets `CODEX_INTERNAL_ORIGINATOR_OVERRIDE=codex_sdk_ts` for telemetry. Platform-specific binaries are vendored in `vendor/{targetTriple}/codex/codex`.

---

## App Server Protocol (Advanced Integration)

The App Server is the highest-fidelity integration surface. It enables approval flows, dynamic tools, diff streaming, and full thread management that the TypeScript SDK does not expose.

### Transport

- Bidirectional JSONL over stdio
- NOT strict JSON-RPC 2.0: the `"jsonrpc": "2.0"` field is OMITTED from the wire
- Wire format: `{ id?, method, params? }` (request/notification) or `{ id, result }` / `{ id, error }` (response)

### Protocol Namespaces

- **v1**: `newConversation`, `sendUserTurn`, etc. — DEPRECATED. Do not use.
- **v2**: `thread/start`, `turn/start`, etc. — CURRENT. Use exclusively.

### Handshake

```
Client -> Server: { "id": 1, "method": "initialize", "params": { ... } }
Server -> Client: { "id": 1, "result": { ... } }
Client -> Server: { "method": "initialized" }   // notification, no id
```

### Key Client Requests (v2)

| Method | Params | Purpose |
|--------|--------|---------|
| `thread/start` | `ThreadStartParams` | Create new thread |
| `thread/resume` | `ThreadResumeParams` | Resume by id or path |
| `thread/list` | `ThreadListParams` | Paginated thread list |
| `thread/read` | `ThreadReadParams` | Read thread + items |
| `thread/rollback` | `ThreadRollbackParams` | Drop last N turns |
| `thread/fork` | `ThreadForkParams` | Fork existing thread |
| `turn/start` | `TurnStartParams` | Submit user input |
| `turn/interrupt` | `TurnInterruptParams` | Cancel in-flight turn |
| `review/start` | `ReviewStartParams` | Code review turn |
| `skills/list` | `SkillsListParams` | List available skills |
| `model/list` | — | List available models |
| `config/read` | `ConfigReadParams` | Read layered config |
| `config/value/write` | `ConfigValueWriteParams` | Write config key |
| `mcpServerStatus/list` | — | MCP server health |

### TurnStartParams (key fields)

```typescript
{
  thread_id: string,
  input: UserInput[],
  cwd?: string,
  approval_policy?: "untrusted" | "on-failure" | "on-request" | "never",
  sandbox_policy?: "read-only" | "workspace-write" | "danger-full-access",
  model?: string,
  effort?: "minimal" | "low" | "medium" | "high" | "xhigh",
  output_schema?: JsonValue,        // structured output (JSON Schema)
  collaboration_mode?: string,      // EXPERIMENTAL
}
```

### UserInput Union (v2)

```typescript
type UserInput =
  | { type: "Text"; text: string }
  | { type: "Image"; url: string }
  | { type: "LocalImage"; path: string }
  | { type: "Skill"; name: string; path: string }      // SKILL.md invocation
  | { type: "Mention"; name: string; path: string }    // file mention
```

### Key Server Notifications (v2)

| Notification | Content |
|-------------|---------|
| `thread/started` | Thread created with id |
| `turn/started` | Turn begin |
| `turn/completed` | Turn finished |
| `item/started` | Item lifecycle begin |
| `item/completed` | Item lifecycle complete |
| `item/agentMessage/delta` | Streaming text delta |
| `item/commandExecution/outputDelta` | Streaming shell output |
| `item/fileChange/outputDelta` | Streaming patch delta |
| `turn/diff/updated` | Aggregate unified diff update |
| `thread/tokenUsage/updated` | Per-turn token usage |

### Server Requests (Approval Flows)

The server sends these to the client and waits for a response:

| Method | Purpose |
|--------|---------|
| `item/commandExecution/requestApproval` | Human-in-the-loop exec approval |
| `item/fileChange/requestApproval` | Human-in-the-loop patch approval |
| `item/tool/call` | Client-side dynamic tool execution |
| `item/tool/requestUserInput` | EXPERIMENTAL: elicit user input |

### Dynamic Tools

Register client-side tools in `ThreadStartParams.dynamic_tools`:

```typescript
dynamic_tools: [
  {
    name: "open_file_in_editor",
    description: "Opens a file in the IDE editor",
    input_schema: { type: "object", properties: { path: { type: "string" } }, required: ["path"] }
  }
]
```

When the model calls a dynamic tool, the server sends `item/tool/call` with `{ callId, name, arguments }`. Client must respond with `{ output: string, success: boolean }`.

---

## MCP Server Mode (Prototype)

Start: `codex mcp server` (or `codex --mcp-server`)

Exposes exactly **two tools** over standard MCP protocol (JSON-RPC, JSONL stdio):

### Tool: `codex`

Starts a new Codex session. Input schema:

```json
{
  "required": ["prompt"],
  "properties": {
    "prompt": { "type": "string" },
    "model": { "type": "string" },
    "profile": { "type": "string" },
    "cwd": { "type": "string" },
    "approval-policy": { "type": "string", "enum": ["untrusted","on-failure","on-request","never"] },
    "sandbox": { "type": "string", "enum": ["read-only","workspace-write","danger-full-access"] },
    "config": { "type": "object" },
    "base-instructions": { "type": "string" },
    "developer-instructions": { "type": "string" },
    "compact-prompt": { "type": "string" }
  }
}
```

Output: `{ threadId: string, content: string }`

### Tool: `codex-reply`

Continues an existing session. Input schema:

```json
{
  "required": ["prompt"],
  "properties": {
    "threadId": { "type": "string" },
    "conversationId": { "type": "string", "description": "DEPRECATED: use threadId" },
    "prompt": { "type": "string" }
  }
}
```

### MCP Server Limitations

- Marked as prototype (`//! Prototype MCP server.` in source)
- Does NOT support approval flows, streaming events, or fine-grained item observation
- Use App Server protocol for serious integrations

---

## Configuration System

### Config Layers (precedence low to high)

1. MDM managed preferences (`com.openai.codex` domain on macOS)
2. System (`managed_config.toml`)
3. User (`~/.codex/config.toml` or `$CODEX_HOME/config.toml`)
4. Project (`.codex/config.toml` files from CWD up to repo root)
5. Session flags (`-c key=value` overrides)

### Key Config Fields

```toml
model = "gpt-5.1-codex-max"
approval_policy = "on-request"   # untrusted | on-failure | on-request | never
sandbox_mode = "workspace-write" # read-only | workspace-write | danger-full-access
web_search = "live"              # disabled | cached | live
model_reasoning_effort = "high"  # minimal | low | medium | high | xhigh
instructions = "..."
developer_instructions = "..."

[sandbox_workspace_write]
writable_roots = ["/path1"]
network_access = false

[profiles.fast]
model = "gpt-5.1"
approval_policy = "never"
```

### Session Flag Overrides

```bash
codex -c model="gpt-5.1" -c web_search="live" -c approval_policy="never" "query"
```

---

## Input/Output Modalities

### Text Input
- String prompt via stdin (exec mode)
- `UserInput::Text` with optional `text_elements` spans (app-server)

### Image Input
- `--image <path>` flag (one or more, exec mode)
- `{ type: "local_image", path }` in SDK input array
- `UserInput::Image { url }` for remote images (app-server only)

### Structured Output (JSON Schema)
- `--output-schema <json-schema-file>` (exec mode)
- `outputSchema` in SDK `TurnOptions`
- `output_schema` in `TurnStartParams` (app-server)
- Translated to `text.format.json_schema` with `strict: true` in Responses API

### Web Search
- Config: `web_search = "disabled" | "cached" | "live"`
- Flag: `--search` (enables live)
- SDK: `webSearchMode: "live"` in `ThreadOptions`

### Reasoning Control
- Config: `model_reasoning_effort = "minimal" | "low" | "medium" | "high" | "xhigh"`
- SDK: `modelReasoningEffort` in `ThreadOptions`
- App-server: `effort` in `TurnStartParams`

---

## Thread Persistence

- All sessions recorded as rollout files in `$CODEX_HOME/sessions/`
- `thread.id` is available after first turn starts (via `thread.started` event)
- Resume by thread ID: SDK `client.resumeThread(id)` or CLI `codex resume <id>`
- Fork: `thread/fork` creates new thread from existing rollout
- Rollback: `thread/rollback` drops N turns (does NOT revert file changes)

### Thread ID Capture (SDK)

```typescript
const thread = client.startThread({ ... });
const { events } = await thread.runStreamed("initial prompt");
for await (const event of events) {
  // thread.id is populated after thread.started event
}
const threadId = thread.id;  // persist this for resumption
```

---

## thegent Integration

### Current State

thegent integrates Codex via `codex exec --experimental-json` subprocess calls. Provider routing is done via `OPENAI_BASE_URL` pointing to CLIProxy.

### Correct Environment Variables

```python
env = {
    **os.environ,
    "OPENAI_BASE_URL": "http://localhost:8317/v1",  # CLIProxy
    "CODEX_API_KEY": proxy_api_key,                  # NOT OPENAI_API_KEY
}
```

Note: Codex reads `CODEX_API_KEY` (not `OPENAI_API_KEY`) as of the current version.

### Subprocess Invocation Pattern

```python
import asyncio
import json

async def invoke_codex_streamed(
    prompt: str,
    model: str = "gpt-5.1-codex-max",
    sandbox: str = "workspace-write",
    approval_policy: str = "never",
    working_dir: str | None = None,
    thread_id: str | None = None,
) -> AsyncGenerator[dict, None]:
    args = [
        "codex", "exec", "--experimental-json",
        "--sandbox", sandbox,
        "--ask-for-approval", approval_policy,
        "--skip-git-repo-check",
    ]
    if model:
        args.extend(["--model", model])
    if working_dir:
        args.extend(["--cd", working_dir])
    if thread_id:
        args.extend(["resume", thread_id])

    env = {
        **os.environ,
        "OPENAI_BASE_URL": "http://localhost:8317/v1",
        "CODEX_API_KEY": get_proxy_api_key(),
    }

    process = await asyncio.create_subprocess_exec(
        *args,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=env,
    )
    process.stdin.write(prompt.encode())
    process.stdin.close()

    async for line in process.stdout:
        line = line.decode().strip()
        if line:
            yield json.loads(line)

    await process.wait()
    if process.returncode != 0:
        stderr = await process.stderr.read()
        raise RuntimeError(f"Codex exited {process.returncode}: {stderr.decode()}")
```

### Recommended Overhaul Tiers

**Tier 1 — Config/Env (implement immediately):**
- Ensure `OPENAI_BASE_URL` + `CODEX_API_KEY` forwarded for proxy routing
- Map thegent model aliases to Codex `--model` values
- Expose sandbox and approval policy as thegent config
- Use `--config web_search=...` for web search toggle

**Tier 2 — TypeScript SDK wrapper (short term):**
- Thin Node.js wrapper using `@openai/codex-sdk`
- Thread persistence (store/restore `thread.id`)
- Structured output support via `outputSchema`
- Image input via `[{type:"local_image",path}]`
- Reasoning effort via `modelReasoningEffort`

**Tier 3 — App Server protocol client (medium term):**
- Full bidirectional JSON-RPC client
- Approval flows, dynamic tools, diff streaming
- TypeScript schema exports from protocol crate enable code generation

---

## Gaps vs Claude Code

| Feature | Codex | Claude Code |
|---------|-------|-------------|
| Structured JSON output | Yes (`output_schema`) | Yes |
| Image input | Yes (local + URL) | Yes |
| Programmatic SDK | Yes (`@openai/codex-sdk`) | No |
| Thread persistence/rollback | Yes (rollout files) | Yes |
| Multi-agent collab | Yes (`CollabAgentToolCall`) | No |
| App-server embedding protocol | Yes (JSON-RPC stdio) | No |
| MCP client | Yes | Yes |
| MCP server | Yes (2 tools, prototype) | No |
| Skills/extensions | Yes (SKILL.md) | Yes (CLAUDE.md) |
| Dynamic client tools | Yes | No |
| Code review mode | Yes (`review/start`) | No |
| Config layer system | Yes (MDM + system + user + project) | Limited |
| Model reasoning control | Yes (effort + summary + verbosity) | Yes |
| Context compaction | Yes (automated) | Yes |
| Approval flows | Yes (per-command, per-file) | Yes |
| Sandbox modes | Yes (read-only, workspace-write, full) | Limited |
| Provider routing | Only via proxy (`OPENAI_BASE_URL`) | No |

---

## Important Caveats

1. **Responses API only**: Codex is deeply coupled to the OpenAI Responses API. Any proxy must support it. Chat Completions is not sufficient.

2. **v1 protocol is deprecated**: Do not build against `newConversation`, `sendUserTurn`, or other v1 methods.

3. **UNSTABLE fields**: `chatgptAuthTokens` auth mode, `history` in `ThreadResumeParams`, `experimental_raw_events`, `CollaborationMode` — do not use in production integrations.

4. **MCP server is prototype**: The comment `//! Prototype MCP server.` signals not production-grade. Use App Server for serious integrations.

5. **Platform binary matrix**: SDK vendors platform-specific binaries for `x86_64-linux-musl`, `aarch64-linux-musl`, `x86_64-darwin`, `aarch64-darwin`, `x86_64-windows-msvc`, `aarch64-windows-msvc`.

6. **No computer use modality**: Codex does not have a `computer_use` tool. The "operator" positioning is marketing. Codex operates on files and shell only.

---

## Quick Reference

```bash
# Basic exec with proxy routing
OPENAI_BASE_URL=http://localhost:8317/v1 CODEX_API_KEY=key \
  codex exec --experimental-json --sandbox workspace-write \
  --ask-for-approval never --skip-git-repo-check \
  --model gpt-5.1-codex-max <<< "your prompt"

# Resume a thread
codex exec --experimental-json resume <thread-id> <<< "continue..."

# Config overrides
codex exec -c web_search="live" -c model_reasoning_effort="high" <<< "search and reason"

# With structured output
codex exec --experimental-json --output-schema ./schema.json <<< "extract data"

# MCP server mode (prototype)
codex mcp server   # JSONL stdin/stdout MCP protocol

# App Server mode (full protocol)
codex app-server   # JSONL stdin/stdout JSON-RPC-like protocol
```

```typescript
// SDK usage
import { Codex } from "@openai/codex-sdk";

const client = new Codex({ apiKey: "...", baseUrl: "http://localhost:8317/v1" });
const thread = client.startThread({
  model: "gpt-5.1-codex-max",
  sandboxMode: "workspace-write",
  approvalPolicy: "never",
  skipGitRepoCheck: true,
});
const turn = await thread.run("implement feature X");
console.log(turn.finalResponse);
// Persist thread.id for resumption
```

---

## Sources

- **Primary**: Direct source analysis of `/Users/kooshapari/temp-PRODVERCEL/485/API/codex-upstream/` (2026-02-20), specifically:
  - `codex-rs/app-server-protocol/src/protocol/v2.rs` — full v2 protocol types
  - `codex-rs/app-server-protocol/src/protocol/common.rs` — all method definitions
  - `codex-rs/app-server-protocol/src/jsonrpc_lite.rs` — wire format
  - `codex-rs/mcp-server/src/codex_tool_config.rs` — MCP tool schemas
  - `codex-rs/codex-api/src/requests/responses.rs` — Responses API request builder
  - `sdk/typescript/src/codex.ts`, `thread.ts`, `exec.ts`, `events.ts`, `items.ts`, `threadOptions.ts`
- Full research: `docs/research/CODEX_HARNESS_RESEARCH_2026-02-20.md`

---

## Source: context/fastmcp.md

# FastMCP Context

> Definitive technical reference for implementing FastMCP servers in thegent and trace.
> Sources: gofastmcp.com/changelog, jlowin.dev/blog/fastmcp-3-whats-new, jlowin.dev/blog/fastmcp-3-launch, github.com/jlowin/fastmcp (fetched 2026-02-20).
> **Version covered: FastMCP 3.0.0 (GA, 2026-02-18)**

---

## What is FastMCP

**FastMCP** is a Pythonic framework for building MCP (Model Context Protocol) servers and clients. It wraps the raw `mcp` SDK with:

- **Declarative API**: Decorators (`@mcp.tool()`, `@mcp.resource()`, `@mcp.prompt()`) for defining server capabilities
- **Composable Architecture**: Providers, Transforms, and Middleware form a three-layer pipeline
- **Context API**: User input elicitation, progress reporting, structured logging, LLM sampling, session state
- **Multiple Transports**: STDIO (default), Streamable HTTP (production), SSE (legacy)
- **Production Features**: OpenTelemetry tracing, background tasks, granular auth, component versioning

**Why FastMCP over raw MCP SDK?** FastMCP turns multi-hundred-line protocol boilerplate into 5-10 lines. Pydantic auto-generates tool schemas from type hints; the decorator pattern matches Python idioms.

**thegent Usage:** FastMCP is the core for thegent's MCP server (`src/thegent/mcp/server.py`) with 30+ tools, middleware pipeline (caching, rate limiting, timing, error handling), and bearer auth.

**trace Usage:** `fastmcp>=3.0.0b1` — uses FastMCP as the MCP layer for trace's MCP server.

---

## Version History

| Version | Date | Notes |
|---------|------|-------|
| 3.0.0 | 2026-02-18 | GA release. Composable providers/transforms, component versioning, granular auth, OpenTelemetry |
| 3.0.0rc1 | 2026-02-12 | Release candidate |
| 3.0.0b2 | 2026-02-07 | Second beta; "2 Fast 2 Beta" |
| 3.0.0b1 | 2026-01-20 | First beta; initial 3.0 architecture |
| 2.x | 2025 | Previous stable; decorators returned component objects |

---

## Installation

```bash
# Stable (GA)
pip install fastmcp

# With background task support
pip install "fastmcp[tasks]"

# Check installed version
python -c "import fastmcp; print(fastmcp.__version__)"
# → 3.0.0
```

---

## Core Architecture (3.0)

FastMCP 3.0 is built on three composable primitives:

```
┌─────────────────────────────────────────────────┐
│              FastMCP Server                     │
├─────────────────────────────────────────────────┤
│ PROVIDERS (where components originate):         │
│   • LocalProvider — decorated functions         │
│   • FileSystemProvider — filesystem discovery   │
│   • OpenAPIProvider — REST API → tools          │
│   • ProxyProvider — remote MCP server           │
│   • SkillsProvider — agent skill files          │
│   • Custom — implement Provider base class      │
│                                                 │
│ TRANSFORMS (modify component pipeline):         │
│   • Namespace — prefix all names                │
│   • ToolTransform — rename/redescribe tools     │
│   • VersionFilter — expose by version           │
│   • ResourcesAsTools — expose resources as tools│
│   • PromptsAsTools — expose prompts as tools    │
│   • Custom — implement Transform base class     │
│                                                 │
│ MIDDLEWARE (intercept requests):                │
│   • CachingMiddleware, RateLimitingMiddleware   │
│   • TimingMiddleware, LoggingMiddleware         │
│   • ErrorHandlingMiddleware                     │
│   • AuthMiddleware — server-wide auth           │
│   • PingMiddleware — keep-alive pings           │
└─────────────────────────────────────────────────┘
```

### Transport Options

| Transport | Use Case | Status |
|-----------|----------|--------|
| **STDIO** | Local CLI, Claude Desktop, Cursor | Default |
| **Streamable HTTP** | Remote, web dashboards | Production-ready |
| **SSE** | Legacy clients | Deprecated |

---

## Core Decorators

### Tools (`@mcp.tool`)

Tools are callable operations that clients invoke.

```python
from fastmcp import FastMCP

mcp = FastMCP("thegent")

# Basic tool — decorators return the original function (callable)
@mcp.tool
def thegent_status() -> str:
    """Get thegent status."""
    return "Running"

# Callable normally (for testing)
thegent_status()  # → "Running"
```

**Tool with parameters and annotations:**

```python
@mcp.tool(
    readOnlyHint=True,           # Does not modify environment
    destructiveHint=False,
    idempotentHint=True,
    tags={"execution", "core"},
    timeout=60.0,                # Max execution seconds
    version="2.0",               # Component version for versioning system
)
def list_agents(include_stopped: bool = False) -> dict:
    """List all available agents.

    Args:
        include_stopped: Include stopped agents in results
    """
    return {"agents": []}
```

**Generated schema (auto from type hints + docstring):**

```json
{
  "name": "list_agents",
  "description": "List all available agents.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "include_stopped": {
        "type": "boolean",
        "description": "Include stopped agents in results",
        "default": false
      }
    }
  }
}
```

**Structured output with ToolResult:**

```python
from fastmcp.tools.tool import ToolResult

@mcp.tool
def thegent_run(command: str) -> ToolResult:
    """Run a command."""
    import subprocess
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return ToolResult(
        content=f"Exit code: {result.returncode}",
        structured_content={
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        },
        meta={"command": command},
    )
```

### Resources (`@mcp.resource`)

Resources expose readable data via URI.

```python
@mcp.resource("thegent://sessions")
def list_sessions() -> list[dict]:
    """List active sessions."""
    return [{"id": "sess_123", "status": "running"}]

# URI template parameters
@mcp.resource("thegent://session/{id}")
def get_session(id: str) -> dict:
    """Get session by ID."""
    return {"id": id, "status": "running"}

# Optional query parameters (RFC 6570)
@mcp.resource("thegent://session/{id}/meta{?include_logs}")
def get_session_meta(id: str, include_logs: bool = False) -> dict:
    meta = {"id": id}
    if include_logs:
        meta["logs"] = []
    return meta
```

### Prompts (`@mcp.prompt`)

```python
@mcp.prompt
def agent_instructions(agent_type: str = "general") -> str:
    """Get agent instructions."""
    return f"You are a {agent_type} agent. Execute tasks precisely."
```

---

## Context API

Inject `Context` for logging, progress, elicitation, and session state.

```python
from fastmcp.server.dependencies import CurrentContext
from fastmcp.server.context import (
    AcceptedElicitation,
    DeclinedElicitation,
    CancelledElicitation,
)
# Context type (use Any for flexibility in thegent pattern)
from typing import Any
Context = Any
```

### Logging

```python
@mcp.tool
async def my_tool(ctx: Context = CurrentContext()) -> str:
    await ctx.info("Starting operation")
    await ctx.debug("Debug detail")
    await ctx.warning("Watch out")
    await ctx.error("Something failed")
    return "done"

# Structured logging with logger name and extra fields
await ctx.info(
    "Agent spawned",
    logger_name="thegent.orchestration",
    extra={"agent_id": "123", "timeout": 30},
)
```

### Progress Reporting

```python
from fastmcp.server.dependencies import Progress, ProgressLike

@mcp.tool
async def batch_process(
    items: list[str],
    ctx: Context = CurrentContext(),
    progress: ProgressLike = Progress(),
) -> dict:
    await progress.set_total(len(items))
    results = []
    for item in items:
        await progress.set_message(f"Processing {item}...")
        results.append(await process_item(item))
        await progress.increment()
    return {"results": results}
```

### User Input Elicitation

```python
@mcp.tool
async def configure_env(ctx: Context = CurrentContext()) -> str:
    # Simple string prompt
    result = await ctx.elicit("Working directory?", response_type=str)
    if isinstance(result, AcceptedElicitation):
        return f"Using: {result.data}"
    elif isinstance(result, DeclinedElicitation):
        return "Declined"
    elif isinstance(result, CancelledElicitation):
        return "Cancelled"

# Single-select from options dict
options = {
    "dev": {"title": "Development"},
    "staging": {"title": "Staging"},
    "prod": {"title": "Production"},
}
result = await ctx.elicit("Select environment:", response_type=options)
env = result.data  # "dev", "staging", or "prod"

# Structured data (Pydantic model)
from pydantic import BaseModel
class AgentConfig(BaseModel):
    name: str
    timeout_secs: int

result = await ctx.elicit("Configure agent:", response_type=AgentConfig)
if isinstance(result, AcceptedElicitation):
    config: AgentConfig = result.data
```

### Session State (Async in 3.0)

```python
# v3: state methods are async (breaking change from v2)
@mcp.tool
async def set_config(key: str, value: str, ctx: Context = CurrentContext()) -> str:
    state = await ctx.get_state()
    state.setdefault("config", {})[key] = value
    await ctx.set_state(state)
    return f"Saved: {key}={value}"

@mcp.tool
async def get_config(key: str, ctx: Context = CurrentContext()) -> str:
    state = await ctx.get_state()
    return str(state.get("config", {}).get(key))
```

**Redis backend for session state:**

```python
from key_value.aio.stores.redis import RedisStore

mcp = FastMCP("server", session_state_store=RedisStore(url="redis://localhost:6379"))
```

### Transport Detection

```python
@mcp.tool
def my_tool(ctx: Context = CurrentContext()) -> str:
    if ctx.transport == "stdio":
        return "compact"      # Short output for CLI
    return "detailed"          # Rich output for HTTP
# ctx.transport: "stdio" | "sse" | "streamable-http"
```

---

## Providers

### LocalProvider (Decorators)

```python
from fastmcp.server.providers import LocalProvider

# Reusable provider (shared across multiple server instances)
provider = LocalProvider()

@provider.tool
def shared_tool() -> str:
    return "available everywhere"

server1 = FastMCP("Server1", providers=[provider])
server2 = FastMCP("Server2", providers=[provider])
```

### FileSystemProvider

```python
from fastmcp.server.providers import FileSystemProvider

# Discovers tools from .py files in directory; hot-reload on changes
mcp = FastMCP("server", providers=[
    FileSystemProvider("mcp/", reload=True)
])
```

### OpenAPIProvider

```python
from fastmcp.server.providers.openapi import OpenAPIProvider
import httpx

spec = {...}  # OpenAPI dict or URL
client = httpx.AsyncClient(base_url="https://api.example.com")
provider = OpenAPIProvider(openapi_spec=spec, client=client)
mcp = FastMCP("API Server", providers=[provider])
```

### ProxyProvider / create_proxy

```python
from fastmcp.server import create_proxy

# Proxy a remote MCP server
server = create_proxy("http://remote-mcp-server:3000/mcp")

# Mount subserver with namespace
main = FastMCP("Main")
sub = FastMCP("Sub")
main.mount(sub, prefix="sub")
# "greet" in sub becomes "sub_greet" in main
```

### SkillsProvider

```python
from fastmcp.server.providers.skills import SkillsDirectoryProvider
from pathlib import Path

mcp = FastMCP("Skills Server")
mcp.add_provider(SkillsDirectoryProvider(
    roots=Path.home() / ".claude" / "skills"
))
# Exposes .md skill files as MCP resources
```

---

## Transforms

### Namespace

```python
from fastmcp.server.transforms import Namespace

provider.add_transform(Namespace("thegent"))
# "run" → "thegent_run"; "data://x" → "data://thegent/x"
```

### VersionFilter

```python
from fastmcp.server.transforms import VersionFilter

api_v1 = FastMCP("v1", providers=[components])
api_v1.add_transform(VersionFilter(version_lt="2.0"))

api_v2 = FastMCP("v2", providers=[components])
api_v2.add_transform(VersionFilter(version_gte="2.0"))
```

### ResourcesAsTools / PromptsAsTools

```python
from fastmcp.server.transforms import ResourcesAsTools, PromptsAsTools

mcp.add_transform(ResourcesAsTools(mcp))   # Resources → tools
mcp.add_transform(PromptsAsTools(mcp))     # Prompts → tools
```

### Visibility Control

```python
mcp.disable(tags={"admin"})           # Hide admin tools by default
mcp.disable(names={"dangerous_op"})   # Hide specific tool
mcp.enable(tags={"public"}, only=True)  # Allowlist: show only public

# Per-session visibility (via context)
@mcp.tool
async def unlock_premium(ctx: Context = CurrentContext()) -> str:
    await ctx.enable_components(tags={"premium"})
    return "Premium unlocked for this session"
```

---

## Middleware

thegent uses these middleware in `server.py`:

```python
from fastmcp.server.middleware.caching import CallToolSettings, ResponseCachingMiddleware
from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware
from fastmcp.server.middleware.logging import LoggingMiddleware
from fastmcp.server.middleware.rate_limiting import RateLimitingMiddleware
from fastmcp.server.middleware.response_limiting import ResponseLimitingMiddleware
from fastmcp.server.middleware.timing import TimingMiddleware

mcp = FastMCP(
    "thegent",
    middleware=[
        ErrorHandlingMiddleware(),
        LoggingMiddleware(),
        TimingMiddleware(),
        RateLimitingMiddleware(requests_per_minute=60),
        ResponseCachingMiddleware(ttl=300),
        ResponseLimitingMiddleware(max_bytes=1024 * 1024),  # 1MB
    ],
)
```

---

## Authorization (3.0)

### Component-Level Auth

```python
from fastmcp.server.auth import require_auth, require_scopes

@mcp.tool(auth=require_auth)
def protected_tool(): ...

@mcp.resource("data://secret", auth=require_scopes("read"))
def secret_data(): ...

@mcp.prompt(auth=require_scopes("admin"))
def admin_prompt(): ...
```

### Server-Wide Auth (AuthMiddleware)

```python
from fastmcp.server.middleware import AuthMiddleware
from fastmcp.server.auth import require_auth, restrict_tag

# All endpoints require auth
mcp = FastMCP(middleware=[AuthMiddleware(auth=require_auth)])

# Tag-based restrictions
mcp = FastMCP(middleware=[
    AuthMiddleware(auth=restrict_tag("admin", scopes=["admin"]))
])
```

**thegent pattern (Bearer token, custom middleware):**

```python
# src/thegent/mcp/server.py — BearerAuthMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

class BearerAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if settings.mcp_auth_mode == "bearer":
            if request.url.path == "/health":
                return await call_next(request)
            auth = request.headers.get("Authorization")
            if not auth or not auth.startswith("Bearer "):
                return JSONResponse({"error": "Missing Authorization"}, status_code=401)
            token = auth[7:]
            if token not in valid_tokens:
                return JSONResponse({"error": "Invalid token"}, status_code=401)
        return await call_next(request)
```

---

## Component Versioning

```python
# Register multiple versions of the same tool
@mcp.tool(version="1.0")
def add(x: int, y: int) -> int:
    return x + y

@mcp.tool(version="2.0")
def add(x: int, y: int, z: int = 0) -> int:
    return x + y + z

# Highest version served by default
# Client calls specific version:
result = await client.call_tool("add", {"x": 1, "y": 2}, version="1.0")
```

---

## Background Tasks

```python
from fastmcp.server.tasks.config import TaskConfig
from datetime import timedelta

@mcp.tool(task=TaskConfig(mode="optional", poll_interval=timedelta(seconds=5)))
async def long_running(command: str) -> str:
    """Client can choose sync or async execution."""
    import asyncio
    await asyncio.sleep(30)
    return "Done"

@mcp.tool(task=TaskConfig(mode="required"))
async def must_be_async() -> str:
    """Client MUST use async mode (exceeds HTTP timeout)."""
    ...

# Shorthand
@mcp.tool(task=True)
async def background_task() -> str: ...

# Sync code runs in threadpool automatically — no asyncio.to_thread needed
@mcp.tool
def sync_blocking() -> str:
    import time; time.sleep(10)  # Dispatched to threadpool automatically
    return "done"
```

**Install tasks extra:**

```bash
pip install "fastmcp[tasks]"
```

---

## Server Lifecycle (Lifespan)

```python
from fastmcp.server.lifespan import lifespan

@lifespan
async def db_lifespan(server):
    db = await connect_db()
    try:
        yield {"db": db}
    finally:
        await db.close()

@lifespan
async def cache_lifespan(server):
    cache = await connect_cache()
    try:
        yield {"cache": cache}
    finally:
        await cache.close()

# Compose lifespans with pipe operator
mcp = FastMCP("server", lifespan=db_lifespan | cache_lifespan)
```

---

## Transports

### STDIO (Local)

```python
import asyncio

async def main():
    async with mcp.stdio_server() as (read, write):
        await mcp.run(read, write)

if __name__ == "__main__":
    asyncio.run(main())
```

### Streamable HTTP (Remote)

```python
async def main():
    async with mcp.http_server(host="0.0.0.0", port=8000) as server:
        await server.wait()
```

**HTTP request:**

```
POST http://localhost:8000/mcp/tools/call
Authorization: Bearer <token>
Content-Type: application/json

{"tool": "thegent_run", "arguments": {"command": "thegent ps"}}
```

### CLI Run

```bash
# Run server
fastmcp run server.py

# Run with hot reload
fastmcp run server.py --reload
fastmcp dev server.py   # Shorthand (reload + inspector)

# List tools
fastmcp list server.py

# Call a tool
fastmcp call server.py tool_name --arg1 val1

# Install with harness
fastmcp install server.py --name "thegent"   # Claude Desktop, Cursor, Goose
```

---

## OpenTelemetry Tracing

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
trace.set_tracer_provider(provider)

# FastMCP auto-instruments tool calls — no changes to tool code needed
mcp = FastMCP("server")
```

---

## Testing

```python
import pytest
from fastmcp import FastMCP

@pytest.fixture
def mcp_server():
    mcp = FastMCP("test")

    @mcp.tool
    def sample_tool(value: str) -> str:
        return f"Result: {value}"

    return mcp

@pytest.mark.asyncio
async def test_tool_execution(mcp_server):
    # Direct call (decorators return original functions)
    result = mcp_server._tool_registry["sample_tool"].fn("test")
    assert result == "Result: test"

# In-process client testing
from fastmcp import Client

@pytest.mark.asyncio
async def test_with_client(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("sample_tool", {"value": "hello"})
        assert "Result: hello" in str(result)
```

---

## Breaking Changes: v2 → v3

| Change | v2 Behavior | v3 Behavior | Fix |
|--------|-------------|-------------|-----|
| Decorators | Return component objects | Return original function | Set `FASTMCP_DECORATOR_MODE=object` for v2 compat |
| `ctx.get_state()` | Synchronous | **Async** (must `await`) | Add `await` |
| `ctx.set_state()` | Synchronous | **Async** (must `await`) | Add `await` |
| `enabled=` parameter | `@mcp.tool(enabled=False)` | Removed | Use `mcp.disable(names={"tool"})` |
| Auth env vars | Auto-loaded from env | Must configure explicitly | Configure auth providers manually |
| `fastmcp dev` | Direct subcommand | `fastmcp dev inspector` | Update scripts |
| `ui=` parameter | `@mcp.tool(ui=...)` | Changed to `app=AppConfig(...)` | Update usage |
| Metadata namespace | `_fastmcp` | `fastmcp` (no underscore) | Update metadata readers |
| `require_auth` | `@mcp.tool(require_auth=True)` | `@mcp.tool(auth=require_auth)` | Use new auth param |

**Upgrade path:**

```bash
pip install fastmcp==3.0.0
# Run server; fix any async state calls; configure auth explicitly
```

---

## Sources & References

- **Official Docs**: https://gofastmcp.com (fetched 2026-02-20)
- **GitHub**: https://github.com/jlowin/fastmcp (fetched 2026-02-20)
- **What's New in 3.0**: https://www.jlowin.dev/blog/fastmcp-3-whats-new (fetched 2026-02-20)
- **3.0 GA Announcement**: https://www.jlowin.dev/blog/fastmcp-3-launch (fetched 2026-02-20)
- **Changelog**: https://gofastmcp.com/changelog (fetched 2026-02-20)
- **PyPI**: https://pypi.org/project/fastmcp/
- **thegent server**: `src/thegent/mcp/server.py`
- **Last Verified**: 2026-02-20

See also: `docs/context/mcp-protocol.md`

---

## Quick Reference

| Item | Value |
|------|-------|
| Package | `fastmcp>=3.0.0` |
| Extra (tasks) | `fastmcp[tasks]` |
| Latest stable | 3.0.0 (2026-02-18) |
| Transport default | STDIO |
| HTTP port | Configurable (thegent: 3847) |
| Auth | BearerAuthMiddleware (thegent pattern) |

### Decorator Quick Patterns

```python
@mcp.tool                                    # Basic tool
@mcp.tool(tags={"core"}, timeout=30.0)       # Annotated tool
@mcp.tool(task=TaskConfig(mode="optional"))  # Background task
@mcp.resource("scheme://path/{id}")          # Resource with template
@mcp.prompt                                  # Prompt template
```

### Context Quick Patterns

```python
ctx: Context = CurrentContext()         # Inject context
await ctx.info("message")              # Log
await ctx.get_state()                  # Session state (async in v3!)
await ctx.set_state(data)              # Session state (async in v3!)
await ctx.elicit("msg", response_type=str)  # User input
ctx.transport                          # "stdio" | "sse" | "streamable-http"
```

### Common Middleware Stack (thegent)

```python
from fastmcp.server.middleware.caching import ResponseCachingMiddleware
from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware
from fastmcp.server.middleware.logging import LoggingMiddleware
from fastmcp.server.middleware.rate_limiting import RateLimitingMiddleware
from fastmcp.server.middleware.timing import TimingMiddleware
```

---

## Source: context/gemini-cli.md

# Gemini CLI Context

> Definitive reference for integrating Google Gemini CLI as an agent harness in thegent/CLIProxyAPIPlus.
> Sources: google-gemini/gemini-cli on GitHub, official documentation (fetched 2026-02-20).

---

## What is Gemini CLI

Gemini CLI is an open-source terminal-first AI agent that integrates Google's Gemini models directly into your command line. It provides lightweight access to Gemini's reasoning and tool-calling capabilities, designed for developers who work in the terminal.

Key characteristics:
- **Terminal-first design**: Full agent workflows in the CLI
- **Open source**: Apache 2.0 license
- **Multimodal support**: Code analysis, generation from prompts
- **Built-in tools**: Google Search (grounding), file operations, shell commands, web fetching
- **MCP extensible**: Custom integrations via Model Context Protocol
- **Free tier**: 60 requests/min, 1,000 requests/day with personal Google account
- **Paid tiers**: Available via Gemini API key or Vertex AI for enterprise

---

## Installation

### Via npm (Global)

```bash
npm install -g @google/gemini-cli
```

### Via Homebrew

```bash
brew install gemini-cli
```

### Via npx (No Installation)

```bash
npx @google/gemini-cli [args]
```

Verify installation:
```bash
gemini --version
```

---

## Authentication

Three authentication methods are supported:

| Method | Use Case | Setup |
|--------|----------|-------|
| **Google OAuth** | Individual developers, free tier | `gemini auth` → browser OAuth flow |
| **Gemini API Key** | Model selection, paid usage | `GEMINI_API_KEY=...` environment variable or `~/.gemini/config` |
| **Vertex AI** | Enterprise workloads, GCP integration | GCP service account credentials |

### OAuth Authentication

```bash
gemini auth
# Opens browser for Google OAuth, stores credentials locally in ~/.gemini/
```

### API Key Authentication

```bash
export GEMINI_API_KEY="your-api-key-here"
gemini --prompt "What is 2+2?"
```

### Vertex AI Authentication

Set up via GCP service account and environment variables:

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
gemini --model gemini-2.0-flash-exp --prompt "Hello"
```

---

## Configuration

Config file location: `~/.gemini/config` (YAML or JSON format)

Alternatively, set `GEMINI_HOME` environment variable to use a custom config directory.

### Sample Configuration

```yaml
auth:
  method: api_key  # or oauth, vertex_ai
  api_key: your-api-key

models:
  default: gemini-2.0-flash
  experimental: gemini-2.0-flash-exp

tools:
  google_search:
    enabled: true
    max_results: 5
  file_operations:
    enabled: true
  shell_commands:
    enabled: true
    restricted: false
  web_fetch:
    enabled: true

sandbox:
  enabled: false  # Set true to enable sandbox mode by default
```

---

## CLI Flags and Modes

### Core Flags

| Flag | Short | Description | Example |
|------|-------|-------------|---------|
| `--model` | `-m` | Model to use | `-m gemini-2.0-flash` |
| `--prompt` | `-p` | Provide prompt directly (non-interactive mode) | `-p "Analyze this code"` |
| `--non-interactive` | `-n` | Run without interactivity | Implicit with `--prompt` |
| `--yolo` | | Enable YOLO mode (auto-approve all tool calls) | `--yolo` |
| `--approval-mode` | | Set approval behavior | `--approval-mode=yolo` or `--approval-mode=manual` |
| `--sandbox` | | Enable sandbox mode for this session | `--sandbox` |
| `--help` | `-h` | Show help | `gemini --help` |
| `--version` | `-v` | Show version | `gemini --version` |

### Interactive Mode (Default)

```bash
gemini
```

Starts an interactive session. The model waits for user approval before executing tool calls unless `--yolo` is set.

### Non-Interactive Mode

```bash
gemini --prompt "Write a Python function that calculates Fibonacci"
gemini -p "Explain this code" < code.py
```

Passes prompt directly, executes in non-interactive mode. Returns response and exits.

### YOLO Mode

```bash
gemini --yolo
# or during session: press Ctrl+Y
```

Automatically approves all tool calls without user confirmation. Useful for:
- CI/CD pipelines
- Automated scripts
- Unattended execution

**Note**: YOLO mode automatically enables sandbox mode by default for security.

### Sandbox Mode

```bash
gemini --sandbox
```

Restricts tool execution within a sandboxed environment. Tool calls are isolated and cannot access system resources outside the sandbox.

### Model Selection

```bash
gemini --model gemini-2.0-flash
gemini -m gemini-2.0-flash-exp
```

Available models (as of 2026-02-20):
- `gemini-2.0-flash` (stable, recommended)
- `gemini-2.0-flash-exp` (experimental, latest features)
- `gemini-1.5-pro`
- `gemini-1.5-flash`

---

## Built-in Tools

Gemini CLI provides native integration with several tools without custom MCP configuration:

### Google Search (Grounding)

Enable real-time web search results in model context:

```bash
gemini --prompt "Latest news about AI in 2026"
# Model has access to current web search results
```

### File Operations

Read, write, and manipulate files:

```bash
gemini --prompt "Analyze file contents" < data.csv
```

Configuration in `~/.gemini/config`:
```yaml
tools:
  file_operations:
    enabled: true
```

### Shell Commands

Execute shell commands (with approval):

```bash
# Interactive: model suggests commands, you approve
gemini --prompt "Show me the top 10 largest files in this directory"

# YOLO mode: auto-execute commands
gemini --yolo --prompt "List all Python files and count lines"
```

### Web Fetching

Retrieve and analyze web content:

```bash
gemini --prompt "Summarize this article: https://example.com/article"
```

---

## MCP (Model Context Protocol) Support

Gemini CLI supports MCP for extending capabilities with custom tools and resources.

### Using MCP Servers

Configure MCP servers in `~/.gemini/config`:

```yaml
mcp:
  servers:
    - name: custom-tools
      command: python /path/to/mcp_server.py
      transport: stdio
    - name: web-search
      command: npx web-search-mcp
      transport: stdio
    - name: database
      url: http://localhost:3000
      transport: sse
```

### Transport Types Supported

- **STDIO** (default): Subprocess-based communication
- **SSE**: HTTP Server-Sent Events for remote servers
- **HTTP**: Streamable HTTP transport

### Example: Custom MCP Tool

Create `custom_mcp_server.py`:

```python
#!/usr/bin/env python3
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, ToolCall

server = Server("custom-tools")

@server.tool("calculate_md5")
def calculate_md5(text: str) -> str:
    """Calculate MD5 hash of text."""
    import hashlib
    return hashlib.md5(text.encode()).hexdigest()

# Register and serve
if __name__ == "__main__":
    import asyncio
    with stdio_server(server) as streams:
        asyncio.run(server.run(streams[0], streams[1]))
```

Then use in Gemini CLI:
```bash
gemini --prompt "Calculate MD5 hash of 'hello world'"
# Gemini will use the custom tool
```

---

## Non-Interactive / Subprocess Invocation

For automation, CI/CD, and programmatic use:

```bash
#!/bin/bash
# Single prompt, exit after response
gemini --prompt "Generate a test file for this code" < src/main.py > output.txt

# Chain multiple invocations
output=$(gemini -p "Explain this error" 2>&1 <<< "$error_message")
echo "Analysis: $output"

# With YOLO mode in scripts
gemini --yolo -p "Refactor this code for performance" < code.js

# Export results
gemini -p "Generate CSV report" --output json > report.json
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |
| 127 | Command not found |

### Subprocess Best Practices

- Use `--prompt` (or `-p`) for direct input
- Combine with `--yolo` for auto-approval
- Use `--model` to specify model explicitly
- Pipe input via stdin when appropriate
- Capture stdout for automation
- Log stderr for debugging

---

## Comparison to Other Harnesses

### vs. Codex

| Aspect | Gemini CLI | Codex |
|--------|-----------|-------|
| **Model** | Google Gemini 2.0 | OpenAI GPT-5.3 |
| **Open Source** | Yes (Apache 2.0) | No |
| **CLI-first** | Yes | Yes, but Codex is API-first |
| **Tool Support** | MCP extensible | OpenAI tools native |
| **Free Tier** | Yes (1K req/day) | No free tier |
| **Reasoning** | Gemini 2.0 advanced reasoning | GPT-5.3 built-in reasoning |
| **Speed** | Fast (optimized for CLI) | Very fast (API optimized) |

### vs. Claude Code

| Aspect | Gemini CLI | Claude Code |
|--------|-----------|-----------|
| **Interface** | Terminal CLI only | IDE plugin + terminal |
| **Model** | Google Gemini 2.0 | Anthropic Claude |
| **Authentication** | OAuth or API key | Claude API key |
| **Ecosystem** | Google Cloud focused | Anthropic SDK focused |
| **Built-in Tools** | Search, files, shell | Advanced reasoning, artifacts |

### vs. Local Models

| Aspect | Gemini CLI | Local (Ollama, GGUF) |
|--------|-----------|----------------------|
| **Latency** | ~500ms (API call) | <100ms (local) |
| **Cost** | Pay per request | Free (local compute) |
| **Capability** | State-of-the-art | Smaller, less capable |
| **Authentication** | Cloud auth required | None |
| **Data Privacy** | Google-hosted | Complete local privacy |

---

## Thegent Integration

Gemini CLI can be registered as an alternative harness in thegent's provider registry:

### Registration

In thegent's harness registry (`providers/registry.yaml` or equivalent):

```yaml
harnesses:
  gemini:
    name: "Google Gemini CLI"
    executable: "gemini"
    api_type: "subprocess_cli"
    auth_methods:
      - oauth
      - api_key
      - vertex_ai
    models:
      - gemini-2.0-flash
      - gemini-2.0-flash-exp
      - gemini-1.5-pro
    tool_support: mcp
    min_version: "0.11.0"
    config_path: "~/.gemini/config"
```

### CLI-to-APIPlus Bridge

To expose Gemini CLI via thegent's OpenAI-compatible proxy at localhost:8317:

```python
# In CLIProxyAPIPlus routing layer
class GeminiCLIHandler(CLIHandler):
    def call(self, messages: List[Dict], model: str, **kwargs):
        prompt = self._format_messages(messages)
        result = subprocess.run(
            ["gemini", "--prompt", prompt, "--model", model, "--yolo"],
            capture_output=True,
            text=True,
            timeout=60
        )
        return self._parse_response(result.stdout)
```

### Features via Proxy

- Model selection: `POST /v1/chat/completions` with `model: "gemini/gemini-2.0-flash"`
- Tool calling: Routed through MCP servers declared in `~/.gemini/config`
- Streaming: Via subprocess output streaming
- Cost tracking: Integration with Gemini API quota metrics

---

## Release Schedule and Versions

**Release Cycle**: Weekly stable releases on Tuesdays at 2000 UTC

- **Stable Tag**: Each week's promotion of previous week's preview release + bug fixes
- **Preview Tag**: Experimental features available before stable
- **Recommendation**: Always use the latest stable tag

Check releases: `gemini --version` or visit GitHub releases.

---

## Key Differences from OpenAI / Anthropic APIs

| Area | Gemini CLI | OpenAI API | Anthropic API |
|------|-----------|-----------|--------------|
| **Invocation** | Subprocess CLI | HTTP REST | HTTP REST |
| **Models** | Gemini 2.0 family | GPT-4, GPT-5 family | Claude family |
| **Authentication** | OAuth, API key, Vertex AI | API key only | API key only |
| **Tool Protocol** | MCP | OpenAI native tools | Tool use protocol |
| **Reasoning Access** | Gemini 2.0 reasoning | Extended thinking (o1, o3) | Built-in, no opt-in |
| **State Management** | Manual (session-based) | Manual (messages array) | Manual (messages array) |

---

## Sources

- [Google Gemini CLI GitHub](https://github.com/google-gemini/gemini-cli)
- [Gemini CLI Official Documentation](https://google-gemini.github.io/gemini-cli/)
- [Gemini CLI Releases](https://github.com/google-gemini/gemini-cli/releases)
- [Gemini CLI Configuration Guide](https://google-gemini.github.io/gemini-cli/docs/get-started/configuration.html)
- [Gemini CLI Tutorial: Command Line Parameters](https://medium.com/google-cloud/gemini-cli-tutorial-series-part-2-gemini-cli-command-line-parameters-e64e21b157be)
- [Model Context Protocol (MCP) Integration](https://modelcontextprotocol.io/)

---

## Source: context/kong-ai-gateway.md

# Kong AI Gateway

> Context document for thegent competitive analysis and feature parity audit.
> Full research: `docs/research/KONG_AI_GATEWAY_RESEARCH_2026-02-20.md`

---

## What It Is

Kong AI Gateway is a **plugin-based connectivity and governance layer** for LLM traffic, built on top of Kong Gateway (Nginx/LuaJIT). It does not replace Kong — it extends it with 21 AI-specific plugins.

Design philosophy:
- LLM traffic gets the same controls as REST/gRPC APIs (auth, rate limiting, WAF, RBAC, logging, circuit breakers)
- No code changes required in applications — platform teams configure policy at the gateway layer
- Provider-agnostic universal API: clients send OpenAI-format; Kong translates to any backend provider
- Composable: stack plugins on any route declaratively in YAML

---

## Deployment (OSS / Konnect / Enterprise)

| Tier | Details |
|------|---------|
| **OSS** | Free. 6 AI plugins. No GUI. Self-hosted. |
| **Konnect (SaaS)** | Cloud control plane + self-hosted data planes. Free tier for AI. Full analytics. ~$105/mo/service + $34.25/1M requests. |
| **Enterprise** | Self-hosted. All 21 AI plugins. Kong Manager GUI. RBAC, SSO/OIDC, audit logs, developer portal. $50k+/year. |

All modes support declarative YAML (DB-less), Kubernetes via KIC, and hybrid topologies.

**Key friction**: Customization is in **Lua**. No Python plugin runtime. AI teams must learn Lua or Go.

---

## Core AI Plugins

### Free / OSS

| Plugin | What It Does |
|--------|-------------|
| `ai-proxy` | Routes requests to a single LLM provider. Translates OpenAI format ↔ provider format. |
| `ai-prompt-decorator` | Injects system messages before/after user chat history. Hidden from client. |
| `ai-prompt-guard` | Regex allow/deny list on prompt content. Blocks before LLM call. |
| `ai-prompt-template` | Fill-in-the-blank templates with `{{variable}}` injection prevention. |
| `ai-request-transformer` | Uses a (separate) LLM to rewrite the upstream request body. |
| `ai-response-transformer` | Uses a (separate) LLM to rewrite the upstream response body. |

### Enterprise / AI License

| Plugin | What It Does |
|--------|-------------|
| `ai-proxy-advanced` | Multi-target load balancing across providers (7 algorithms). |
| `ai-rate-limiting-advanced` | Token- and cost-based rate limiting per consumer/window. |
| `ai-semantic-cache` | Vector similarity caching (Redis/pgvector). Avoids redundant LLM calls. |
| `ai-semantic-prompt-guard` | Embedding-based semantic allow/deny. Multilingual. Beats regex circumvention. |
| `ai-semantic-response-guard` | Same as above, applied to LLM response content. |
| `ai-rag-injector` | Gateway-level RAG: auto-retrieves context from vector DB, injects into prompt. |
| `ai-pii-sanitizer` | Detects/redacts 20+ PII categories across 12 languages. Re-inserts in response. |
| `ai-prompt-compressor` | LLM-based prompt compression (up to 5x token reduction). |
| `ai-llm-as-judge` | Use one LLM to score/evaluate responses from another LLM. |
| `ai-mcp-proxy` | MCP protocol gateway (passthrough, REST-to-MCP conversion, aggregation). |
| `ai-mcp-oauth2` | OAuth2 for MCP endpoints. |
| `ai-aws-guardrails` | AWS Bedrock Guardrails integration. |
| `ai-azure-content-safety` | Azure Content Safety integration. |
| `ai-gcp-model-armor` | Google Cloud Model Armor integration. |
| `ai-lakera-guard` | Lakera Guard prompt injection detection. |

---

## ai-proxy / ai-proxy-advanced

### ai-proxy (OSS)

Single upstream. Accepts OpenAI-format → translates → routes → translates back.

Supported route types: `llm/v1/chat`, `llm/v1/completions`, `llm/v1/embeddings`, `llm/v1/audio/transcriptions`, `llm/v1/audio/speech`, `llm/v1/images/generations`.

Supported providers: OpenAI, Anthropic, Azure OpenAI, AWS Bedrock, Gemini, Vertex AI, Cohere, Mistral, Hugging Face, Llama.

### ai-proxy-advanced (Enterprise)

Multiple targets with load balancing. Key additions over ai-proxy:

- Unlimited targets with independent auth, models, weights
- 7 load balancing algorithms (see below)
- Configurable failover criteria (e.g., failover on HTTP 429, 502)
- Circuit breakers (v3.13+): auto-removes unhealthy targets
- Cost-based routing via `lowest-usage` + per-target pricing config
- Native LLM format support (skip OpenAI translation where not needed)

---

## Semantic Caching

Plugin: `ai-semantic-cache` (Enterprise)

Stores LLM responses in a vector database by semantic meaning. On new requests:
1. Embed the prompt
2. VSS query Redis/pgvector for similar prior requests (cosine similarity)
3. Cache hit at threshold → return cached response (no LLM call)
4. Cache miss → call LLM, store embedding + response

Backends: Redis VSS, AWS MemoryDB, PostgreSQL pgvector, AWS ElastiCache, Azure Managed Redis, Google Cloud Memorystore.

Default TTL: 300 seconds. Configurable threshold (0.0–1.0). Respects `Cache-Control` headers.

Headers: `X-Cache-Status: Hit|Miss`, `X-Cache-Key`, `Age`, `X-Cache-Ttl`.

Both exact caching (hash match) and semantic caching run simultaneously.

---

## AI Rate Limiting (Token-Based)

Plugin: `ai-rate-limiting-advanced` (Enterprise)

Extends standard rate limiting with LLM token awareness.

**Token strategies**: `total_tokens`, `prompt_tokens`, `completion_tokens`, `cost` (USD).

**Window strategies**: `local` (per-node in-memory), `cluster` (data store), `redis`.

**Scoping**: Per consumer, per consumer group, per route, per service.

**Enforcement lag**: Costs from the current response apply to the *next* request (one-request lag due to LLM returning token counts post-completion).

Response headers: `X-AI-RateLimit-Limit-{window}-{provider}`, `X-AI-RateLimit-Remaining-...`, `X-AI-RateLimit-Retry-After`.

---

## Guardrails (prompt-guard, semantic-prompt-guard)

### ai-prompt-guard (OSS) — Regex-Based

- Allow list: request must match at least one pattern
- Deny list: request matching any pattern → HTTP 400
- Deny takes precedence over allow
- Limitation: circumventable by paraphrasing

### ai-semantic-prompt-guard (Enterprise) — Semantic

- Vector embedding comparison against reference prompts
- Multilingual (embedding models handle cross-language semantic similarity)
- Embedding providers: Azure, Bedrock, Gemini, HuggingFace, Mistral, OpenAI
- Storage: Redis VSS / pgvector
- Also: `ai-semantic-response-guard` applies same to LLM responses

### External Guardrail Integrations (Enterprise)

AWS Bedrock Guardrails, Azure Content Safety, GCP Model Armor, Lakera Guard.

---

## Request/Response Transformation

### ai-request-transformer (OSS)

Runs before `ai-proxy`. Sends the entire request body to a configured LLM with an admin-defined transformation prompt. LLM's response becomes the new request body forwarded upstream.

Use cases: normalize request formats, inject context, translate schemas.

### ai-response-transformer (OSS)

Runs after `ai-proxy`. Sends response body to a configured LLM. Transformed response returned to client.

Feature: `parse_llm_response_json_instructions: true` — LLM can set response headers, status codes, and body in its response.

---

## Observability

### Metrics

- Prometheus: token counts, latency (TTFT, e2e), error rates, cache hit/miss, cost per request
- OpenTelemetry: GenAI span attributes (`gen_ai.system`, `gen_ai.request.model`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, `gen_ai.response.finish_reason`)
- Streaming: Kong parses SSE chunks to extract token counts mid-stream

### Integrations

Grafana (official dashboard #24057), Prometheus, Datadog, Dynatrace, Langfuse, AWS CloudWatch, Konnect Advanced Analytics (Enterprise).

### Audit Logging

Full request/response body logging with redaction options. Structured JSON. Compliance-grade.

---

## Load Balancing Across Providers

Via `ai-proxy-advanced`. Seven algorithms:

| Algorithm | Strategy |
|-----------|----------|
| `round-robin` | Weighted distribution |
| `consistent-hashing` | Sticky sessions by header |
| `least-connections` | Route to target with most spare capacity (v3.13+) |
| `lowest-latency` | Peak EWMA latency tracking → fastest model |
| `lowest-usage` | Route by prompt/completion tokens or USD cost |
| `semantic` | Vector similarity: route prompt to model whose description matches best |
| `priority` | Tiered failover groups; cascade on failure |

Failover: configurable `failover_criteria` (HTTP status codes). Circuit breakers (v3.13+) with configurable `max_fails` and `fail_timeout`.

---

## Enterprise Features

Beyond AI plugins, Kong Enterprise adds:

- **Kong Manager GUI**: Visual configuration and monitoring
- **RBAC**: Role-based access with workspace isolation
- **SSO / OIDC**: Enterprise identity provider integration
- **Audit Logs**: Full admin action and API request audit trail
- **Developer Portal**: Self-service API/AI endpoint discovery for internal teams
- **Konnect Advanced Analytics**: Pre-built cost/token/latency dashboards
- **decK**: Declarative configuration management (git-compatible)
- **All 21 AI plugins**: Enterprise-only AI plugins require AI license add-on

---

## Key Differences from OpenRouter / LiteLLM / Portkey

| | Kong AI Gateway | OpenRouter | LiteLLM | Portkey |
|--|----------------|------------|---------|---------|
| Architecture | Plugin on API gateway (Nginx) | Cloud SaaS router | Python proxy + SDK | Cloud + self-hosted |
| Self-hostable | Yes | No | Yes | Enterprise |
| Provider breadth | 12+ (curated) | 500+ | 100+ | 200+ |
| Semantic routing | Yes (native vector) | No | No | No |
| Semantic caching | Yes | No | No | Yes |
| MCP gateway | Yes (4 modes + ACLs) | No | Basic | No |
| RAG injection | Yes (gateway layer) | No | No | No |
| PII sanitization | Yes (20+ categories) | No | No | Partial |
| Enterprise governance | Yes (RBAC, SSO, audit) | None | None | Partial |
| Performance | Highest (Nginx/LuaJIT) | High (cloud) | Lowest (Python) | Medium |
| Customization | Lua (niche) | None | Python | JS |
| Cost | Highest ($50k+/yr enterprise) | Free + per-call | Free (OSS) | Free + Enterprise |

**Kong's unique moat**: Semantic routing, gateway-layer RAG, MCP gateway with tool ACLs, and unified governance across AI + traditional API traffic.

---

## What thegent Should Steal

Ordered by impact:

1. **Semantic load balancing**: Route agent tasks to specialist models via prompt-model description similarity (vector embeddings + cosine similarity). Kong's `semantic` algorithm applied to thegent's model routing.

2. **Token budget enforcement per session/agent**: Kong's `ai-rate-limiting-advanced` `cost` strategy — enforce per-agent USD budgets, not just request counts.

3. **Priority failover chains**: Declarative primary/secondary/emergency model sequences. Kong's `priority` algorithm as a routing config primitive.

4. **Semantic response caching**: Cache agent LLM responses by semantic query similarity. Reuse near-identical results without re-calling the LLM.

5. **Circuit breaker per provider**: When a provider fails N times in a window, remove from routing pool for a timeout period. Auto-restore on recovery.

6. **Cost-aware routing**: `lowest-cost` mode routes to the cheapest adequate model. Informed by per-model token pricing config.

7. **MCP tool ACLs**: Per-agent fine-grained authorization over which MCP tools an agent can invoke. Prevent privilege escalation.

8. **Prompt decoration as routing middleware**: Inject system prompts at the CLIProxy routing layer, not in agent code.

9. **EWMA latency tracking**: Track time-per-output-token per provider using exponential moving average. Route to fastest active provider.

10. **Consistent-hashing for conversation sessions**: Route multi-turn conversations to the same provider for context consistency.

---

## Source: context/litellm-proxy.md

# LiteLLM Proxy

> Concise reference for AI agents working on thegent CLIProxy parity with LiteLLM's gateway product.
> Full research: `docs/research/LITELLM_PROXY_RESEARCH_2026-02-20.md`
> Sources fetched: 2026-02-20

---

## What It Is / Deployment

LiteLLM Proxy (also called "LiteLLM AI Gateway") is a self-hosted OpenAI-compatible HTTP server
that fronts 100+ LLM providers behind a single `POST /v1/chat/completions` interface.

**Install:** `pip install litellm[proxy]`
**Start:** `litellm --config config.yaml` (default port: 4000)
**Performance:** 1,500+ req/sec, 8ms P95 at 1k RPS (self-reported)

**Deployment stack:**
- Docker/Docker Compose (primary deployment path)
- **PostgreSQL** — required for virtual keys, spend logs, audit logs
- **Redis** — required for distributed rate-limiting, cross-instance load balancing, caching
- Single-binary mode (no DB/Redis) works for development only

Enterprise tier available via AWS Marketplace (~$30k/year) adds SSO, RBAC, audit logs, dedicated
support. Open-source (MIT) core is fully functional for routing, caching, cost tracking.

---

## Configuration (config.yaml Key Fields)

```yaml
model_list:
  - model_name: gpt-4o            # User-facing name (what clients send as model=)
    litellm_params:
      model: azure/gpt-4o         # provider/model-id format
      api_base: https://...
      api_key: os.environ/AZURE_API_KEY
      rpm: 500                    # Rate limit per deployment
      tpm: 100000
      extra_headers: {}
    model_info:
      id: "deployment-stable-uuid" # Stable ID for fallback references
      tags: ["eu", "paid"]         # For tag-based routing
      order: 1                     # Priority (lower = higher priority)

router_settings:
  routing_strategy: "usage-based-routing-v2"
  model_group_alias:
    gpt-4: gpt-4o                 # Rename incoming model names
  num_retries: 3
  timeout: 30
  redis_host: redis
  enable_pre_call_checks: true    # Context window + region checks
  enable_tag_filtering: true
  provider_budget_config:         # Cap spend per provider
    openai: {budget_limit: 100, time_period: "1d"}
    anthropic: {budget_limit: 200, time_period: "7d"}

litellm_settings:
  fallbacks:
    - {gpt-4o: [claude-sonnet, gemini-pro]}
  context_window_fallbacks:
    - {gpt-4o: [gpt-4o-128k]}
  allowed_fails: 3                # Failures before deployment cooldown
  cooldown_time: 60               # Cooldown seconds
  cache: true
  cache_params:
    type: redis-semantic
    ttl: 600
    similarity_threshold: 0.85
  success_callback: [langfuse, prometheus]

general_settings:
  master_key: sk-admin-key        # Proxy admin auth key
  database_url: postgresql://...
  max_budget: 10000               # Global proxy spend cap (USD)
  alerting: [slack]
```

---

## Authentication (Virtual Keys, Master Key)

**Master key:** Configured in `general_settings.master_key` or `LITELLM_PROXY_MASTER_KEY` env var.
Grants full admin access to all endpoints including management APIs. Must start with `sk-`.

**Virtual keys:** All external callers use virtual keys generated via the proxy's management API.
Format: `sk-{random}`. Only the hash is stored. Plaintext returned once at creation.

Key properties at creation time:
- `budget_limit` + `budget_duration` — hard spend cap with auto-reset
- `tpm_limit`, `rpm_limit`, `max_parallel_requests` — rate limits
- `models` — restrict to named models
- `team_id` — attach to a team (inherits team's budget)
- `aliases` — per-key model aliasing (`gpt-4` → `gpt-4o-mini` silently)
- `tags` — for tag-based routing and cost tracking
- `expires` — expiration timestamp
- `allowed_routes` — restrict to `llm_api_routes` or `management_routes`
- `auto_rotate` + `rotation_interval` — automatic key rotation

Key management endpoints: `/key/generate`, `/key/update`, `/key/delete`, `/key/regenerate`,
`/key/block`, `/key/info`, `/key/list`.

Custom header: configurable via `litellm_key_header_name` (default: `Authorization: Bearer`).

**Budget hierarchy (8 levels, checked in order):**
Key → User → Team → Organization → Model-specific → Global Proxy → Provider → Tag

Rate limit types: `input`, `output`, or `total` tokens (config: `token_rate_limit_type`).
Admin keys bypass all rate limits.

---

## Provider Support

100+ providers. Notable ones:

| Provider | Config `model` string |
|----------|----------------------|
| OpenAI | `openai/gpt-4o` |
| Anthropic | `anthropic/claude-3-5-sonnet` |
| Google / Vertex | `google/gemini-pro`, `vertex_ai/gemini-pro` |
| AWS Bedrock | `bedrock/anthropic.claude-3-sonnet-20240229-v1:0` |
| Azure OpenAI | `azure/<deployment-name>` |
| Cohere | `cohere/command-r` |
| Groq | `groq/llama-3.1-70b` |
| DeepSeek | `deepseek/deepseek-chat` |
| Mistral | `mistral/mistral-large` |
| NVIDIA NIM | `openai/meta-llama2-70b` (with `api_base`) |
| vLLM / Ollama | `openai/<model>` (with `api_base` pointing to local server) |
| HuggingFace | `huggingface/<model-id>` |
| OpenRouter | `openrouter/<model>` |

**Wildcard routing** — route any model from a provider without listing it:
```yaml
- model_name: openai/*
  litellm_params:
    model: openai/*
    api_key: os.environ/OPENAI_API_KEY
```

With `check_provider_endpoint: true`, the `/v1/models` endpoint dynamically queries the provider.

---

## Load Balancing Strategies

Multiple entries with the same `model_name` form a deployment pool:

| Strategy | Key | Use Case |
|----------|-----|----------|
| `simple-shuffle` | Weighted random (default) | General; lowest overhead |
| `usage-based-routing-v2` | Routes to deployment with lowest current TPM usage (Redis) | Rate-limit avoidance |
| `latency-based-routing` | Selects lowest-latency deployment (TTFT history) | Latency-sensitive |
| `least-busy` | Fewest in-flight concurrent requests | Parallel-heavy |
| `cost-based-routing` | Cheapest deployment via built-in cost map | Budget optimization |
| Custom | `CustomRoutingStrategyBase` | Any application logic |

**Weight distribution:** Set `weight: 9` vs `weight: 1` on deployments for proportional traffic.

**Priority ordering:** `model_info.order: 1` (primary), `order: 2` (secondary fallback).

**Max parallel requests:** `litellm_params.max_parallel_requests: 10` caps concurrency per deployment.

**Traffic mirroring:** Shadow deployments receive a copy of production traffic for silent A/B evaluation.

---

## Reliability (Fallbacks / Retries / Circuit Breakers)

**Three fallback types:**
1. **Regular** — any error: `fallbacks: [{gpt-4o: [claude-sonnet, gemini-pro]}]`
2. **Context window** — context exceeded: `context_window_fallbacks`
3. **Content policy** — moderation reject: `content_policy_fallbacks`
4. **Default** — catch-all: `default_fallbacks: [gpt-4o-mini]`

Fallbacks can reference specific deployment UUIDs (`model_info.id`) for precise control.
Per-request override: send `disable_fallbacks: true` in request body.

**Retries:**
- `num_retries: 3` — retries per deployment before attempting fallback
- `retry_after: 5` — delay between retries (seconds)
- `RateLimitError` → exponential backoff; generic errors → immediate retry

**Circuit breaker (cooldown):**
- `allowed_fails: 3` — failure threshold within the monitoring window
- `cooldown_time: 60` — seconds to exclude failing deployment from routing pool
- After cooldown, deployment is automatically re-admitted
- Prometheus: `litellm_deployment_cooled_down` tracks current cooldowns

**Pre-call checks** (`enable_pre_call_checks: true`):
- Context window check: rejects before calling if prompt would overflow; routes to `context_window_fallbacks`
- Region check: routes only to deployments matching region constraints (EU data residency)

---

## Caching

**7 cache backends:** `local` (in-memory), `disk`, `redis`, `redis-semantic`, `qdrant-semantic`, `s3`, `gcs`

**DualCache (L1+L2):** All Redis-backed deployments use two-tier caching:
- L1 (in-process dict): sub-millisecond, local only
- L2 (Redis): shared across all proxy instances

**Key config fields:**
```yaml
cache_params:
  type: redis-semantic         # or "redis", "local", "qdrant-semantic", "s3"
  ttl: 600                     # Default TTL seconds
  default_in_memory_ttl: 60    # L1 TTL
  default_in_redis_ttl: 3600   # L2 TTL
  namespace: "litellm.prod"    # Key prefix for multi-env isolation
  mode: default_off            # Opt-in: clients must send cache.use-cache=true
  similarity_threshold: 0.85   # Semantic cache match threshold
  embedding_model: "text-embedding-3-small"
  supported_call_types:        # Restrict caching to specific call types
    - completion
    - embedding
```

**Semantic caching:** Redis RediSearch module required. On a cache hit, returns stored response if
similarity score ≥ threshold. Response header `x-litellm-semantic-similarity` contains the score.

**Cache hit headers:** `x-litellm-cache-key` (hash), `x-litellm-semantic-similarity` (score).

**Per-request control:** `{"cache": {"use-cache": true}, "ttl": 120}` in request body.

---

## Cost Tracking + Budgets

**Auto-tracking:** Every request's token counts, model, cost (from built-in price map), key, user,
team, and tags are stored in `LiteLLM_SpendLogs` (PostgreSQL).

**Custom pricing:**
```yaml
litellm_params:
  input_cost_per_token: 0.000002
  output_cost_per_token: 0.000006
```
Provider margins (markup) and discounts also configurable.

**Tag-based cost tracking:** Attach `tags` to requests; view spend breakdown per tag. Tag budgets
(Enterprise) enforce hard USD caps per tag:
```yaml
tag_budgets:
  - tag: "cost-center-eng"
    max_budget: 500.0
    budget_duration: "30d"
```

**Provider budget routing:** Cap spending per provider; auto-route away when budget exhausted:
```yaml
router_settings:
  provider_budget_config:
    openai: {budget_limit: 100, time_period: "1d"}
```

**Budget reset periods:** `Xs`, `Xm`, `Xh`, `Xd`, `Xmo`

**End-user tracking:** The `user` field on each request attributes cost to an end-user identifier
without creating a key. `max_end_user_budget` sets a default limit per end-user.

**Spend query API:** Filter by key, team, model, date range. `/spend/report` for analytics (Enterprise).

**Budget alerts:** Soft-budget threshold alerts via Slack webhook before hard limit is hit.

---

## Guardrails

All guardrails run at configurable hooks: `pre_call`, `post_call`, `during_call`, `logging_only`.

| Guardrail | Type | Notes |
|-----------|------|-------|
| LiteLLM Content Filter | Built-in | Regex/keyword matching; no external deps |
| Presidio PII/PHI Masking | External (Presidio containers) | Mask/block SSN, credit cards, phone, email etc. |
| Prompt Injection Detection | Built-in | In-memory detection |
| OpenAI Moderation | External (OpenAI API) | Filters via OpenAI's moderation endpoint |
| LlamaGuard / LLM Guard | External LLM-based | Safety classification |
| Pillar Security | Third-party API | Injection, jailbreak, PII+PCI, secrets |
| Lasso Security | Third-party API | Enterprise content security |
| Secret Detection/Redaction | Enterprise | Masks API keys in logs/callbacks |
| Banned Keywords | Enterprise | Configurable keyword blocklist |

**PII/PHI masking config example:**
```yaml
guardrails:
  - guardrail_name: presidio-pii
    litellm_params:
      guardrail: presidio
      mode: pre_call
      presidio_filter_scope: both   # "input", "output", or "both"
      pii_entities_config:
        SSN: BLOCK
        PHONE_NUMBER: MASK
        EMAIL_ADDRESS: MASK
```

---

## Tag / Team / User Routing

**Tag routing** (preferred, replaces deprecated team-based routing):
- Assign `tags` to deployments in `model_info`
- Request tagged via `x-litellm-tags: free,eu` header or `"tags": ["free"]` in body
- `enable_tag_filtering: true` in `router_settings`
- `"default"` tag acts as fallback for untagged requests

**Four-level tenant hierarchy:**
```
Organization → Team → User → Virtual Key
```
Team budgets cannot exceed org budgets. User budgets cannot exceed team budgets.

**Team creation:** `POST /team/new` with `max_budget`, `budget_duration`, `models`, `tpm_limit`, `rpm_limit`

**Team-to-tag routing (Enterprise):** Teams are assigned tags; members' requests automatically receive team tags — no client-side tag injection needed.

**Roles:** `proxy_admin` (all access), `proxy_admin_viewer` (read-only), `internal_user` (default),
`org_admin` (Enterprise), `team_admin` (Enterprise)

---

## Observability

**Prometheus** (`/metrics` endpoint, ~25 metric families):
- Spend/budget metrics per key/team/user/provider with full label dimensions
- Deployment health: success/failure responses, cooldown state, fallback counts
- Latency histograms: e2e, TTFT, LLM API, Redis overhead
- Rate limit remaining: RPM/TPM per key and model

**Alerting** (24+ alert types via Slack/Discord/Teams webhooks):
- LLM performance: hanging calls, slow calls, failures, outages
- Budget: threshold alerts, daily spend reports
- Region outage: ≥5 failures/min in a region (Enterprise)

**Pre-built callbacks:**
- Langfuse (full LLM tracing with cost)
- Helicone, Lunary, Promptlayer, MLflow, Traceloop/OpenTelemetry
- Datadog: via Prometheus scrape of `/metrics`

**Audit logs (Enterprise):** Who created/modified/deleted any entity (key, team, model, user),
with timestamp and actor, with configurable retention.

---

## Key Differences from OpenRouter

| Aspect | LiteLLM Proxy | OpenRouter |
|--------|---------------|------------|
| **Model count** | 100+ | 300+ |
| **Deployment** | Self-hosted | SaaS |
| **Data residency** | Full on-prem control | Data flows through OpenRouter |
| **Virtual key management** | Full lifecycle: create, rotate, block, expire, alias | Simple API keys |
| **Budget system** | 8-level hierarchy (key/user/team/org/model/global/provider/tag) | Per-key credits |
| **Tag routing** | Route to deployment pools by request tags | No |
| **Provider budget caps** | Auto-skip provider when spend budget exhausted | No |
| **Semantic caching** | Redis-semantic, Qdrant-semantic (configurable threshold) | Prompt caching (exact) |
| **PII masking** | Presidio integration (pre-call scrubbing) | No |
| **Prompt injection detection** | Built-in + third-party integrations | No |
| **MCP Gateway** | Centralized MCP server registry with auth + budgets | No |
| **Prometheus metrics** | Native, ~25 metric families with label dimensions | No |
| **Circuit breaker** | `allowed_fails` + `cooldown_time` per deployment | Implicit provider switching |
| **Traffic mirroring** | Shadow deployments for silent A/B | No |
| **Wildcard routing** | Route `openai/*` without listing models | Not applicable |
| **Custom routing logic** | `CustomRoutingStrategyBase` | Not supported |
| **SSO / RBAC** | Enterprise SAML/OIDC + org/team/user roles | No |
| **Audit logs** | Enterprise: full action log with retention | No |
| **Config-as-code** | YAML `config.yaml`, GitOps friendly | API/UI only |
| **Pricing** | Free open-source + infra costs (~$200-500/mo) | No-markup pay-per-use |
| **Setup time** | 15-30 min | < 5 min |

---

## What We Should Steal for thegent

These LiteLLM features have the highest value for thegent's CLIProxy/routing layer:

### High Priority (Core Provider Aggregation)

1. **Provider budget routing** — `provider_budget_config` per provider with auto-skip when
   exhausted. thegent has per-model cost tracking but no per-provider spend caps that trigger
   routing changes. This is critical for cost governance when mixing free and paid providers.

2. **Virtual key budget hierarchy** — thegent has a single-level cost tracker. LiteLLM's
   8-level hierarchy (key → user → team → org) enables multi-tenant agent deployments where
   different teams/projects have isolated spend caps. Especially relevant for thegent's
   teammate runner isolation model.

3. **Tag-based routing to deployment pools** — thegent routes by model name only. LiteLLM's
   tag routing lets you define multiple deployment pools for the same model name (free tier vs.
   paid tier, EU vs. US region) and route by request/key/team tags. Directly enables thegent's
   multi-tier provider strategy.

4. **Wildcard provider routing** — `openai/*` style config so any new OpenAI-compatible model
   can be routed without code changes. thegent must update `harness_model_mapping.py` and
   `model_metadata.py` for every new model; LiteLLM's wildcard avoids this.

5. **Context window fallbacks** — distinct from general fallbacks. When a request overflows
   one model's context, route to a larger-context variant automatically. thegent's
   `validate_context_window()` only warns; no automatic fallback is triggered.

### Medium Priority (Reliability/Operations)

6. **Per-deployment cooldown (circuit breaker)** — thegent has retry logic but no deployment-level
   cooldown. LiteLLM's `allowed_fails` + `cooldown_time` removes a failing deployment from the pool
   for a configurable period. This prevents continuous hammering of a degraded provider.

7. **Pre-call context window check** — validate that the request will fit before making the API
   call; fail fast with a specific error rather than getting a provider error mid-request. Avoids
   wasted latency on certain-to-fail calls.

8. **Content policy fallbacks** — separate fallback path for moderation rejections vs. errors.
   Important when mixing providers with different content policies.

9. **Traffic mirroring / shadow deployments** — route production traffic to a secondary model
   silently for benchmarking. Useful for validating new models in thegent's catalog before
   promoting them.

### Medium Priority (Observability/Multi-Tenant)

10. **Prometheus metrics with label dimensions** — thegent has basic cost tracking but no
    Prometheus-native metrics. LiteLLM's ~25 metric families with `team`, `end_user`, `model`,
    `api_provider` labels are directly importable by existing infrastructure monitoring.

11. **Per-provider budget Prometheus metric** — `litellm_provider_remaining_budget_metric`
    gives real-time budget burn visibility per provider. thegent's `cost_tracker.py` has daily
    totals but no per-provider remaining budget signal.

12. **Budget reset periods** — LiteLLM supports flexible reset cadences (`30m`, `6h`, `7d`,
    `1mo`). thegent currently uses daily reset only.

### Lower Priority (Guardrails/Security)

13. **PII/PHI masking via Presidio** — Pre-call scrubbing enables GDPR-compliant use of
    cloud LLMs for agent workloads handling user data. No equivalent in thegent today.

14. **Prompt injection detection** — built-in detection as a pre-call guardrail. Relevant for
    any agentic scenario where user-controlled content is passed to the LLM.

15. **MCP gateway with per-key permissions** — LiteLLM's MCP gateway lets you register MCP
    servers and restrict which keys/teams can access which tools. thegent has MCP management
    (`thegent mcp prune`) but not per-key MCP tool access control.

### Lower Priority (Audit/Compliance)

16. **Audit logs** — Who generated/rotated/deleted which key, when, and from which IP.
    Important for enterprise thegent deployments.

17. **Custom key header** — `litellm_key_header_name` lets operators rename the auth header.
    Minor but useful for integrating with enterprise API gateways that use non-standard headers.

18. **Region-aware routing** — Pre-call region check that ensures requests only go to
    deployments in configured regions (EU data residency). Relevant for thegent enterprise.

---

## Source: context/litellm.md

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

---

## Source: context/mcp-protocol.md

# Model Context Protocol (MCP) Context

> Definitive reference for implementing and using Model Context Protocol in thegent.
> Sources: modelcontextprotocol.io specification, official documentation (fetched 2026-02-20).

---

## What is MCP

The Model Context Protocol (MCP) is a standardized protocol that enables AI models and applications to access tools, data, and capabilities from external systems. It defines how clients (AI applications like Claude, Gemini) connect to servers (tools, APIs, databases) and request execution of operations or retrieval of information.

Key characteristics:
- **Standardized**: JSON-RPC 2.0 message format, shared across providers
- **Bidirectional**: Both model-to-server and server-to-client communication
- **Extensible**: Tools, resources, prompts, sampling, and more
- **Transport-agnostic**: STDIO, SSE, Streamable HTTP, or custom transports
- **Multi-capability**: Tools (side effects), Resources (read-only data), Prompts (templates), Sampling (model control)
- **Recent**: Latest spec version 2025-11-25
- **Growing ecosystem**: Hugging Face, Vercel, local inference providers, many open-source servers

---

## Architecture

### Conceptual Model

```
┌─────────────────────────────────────┐
│  AI Host (Client)                   │
│  - Claude                           │
│  - Gemini CLI                       │
│  - thegent / LLM Application        │
└────────────────┬────────────────────┘
                 │ JSON-RPC 2.0
                 │
    ┌────────────┴────────────┐
    │                         │
┌───▼──────────────┐  ┌──────▼──────────┐
│ MCP Server 1     │  │ MCP Server 2    │
│ - Tools          │  │ - Resources     │
│ - Resources      │  │ - Tools         │
│ - Prompts        │  │ - Prompts       │
└──────────────────┘  └─────────────────┘
```

### Components

| Component | Role | Example |
|-----------|------|---------|
| **Host** | AI application, client | Claude, Gemini CLI, thegent |
| **Client** | Connects to servers | MCP client library |
| **Server** | Provides tools/resources | FastMCP server, local tool server |
| **Transport** | Message delivery mechanism | STDIO, SSE, HTTP |

---

## Message Format (JSON-RPC 2.0)

All MCP communication uses JSON-RPC 2.0, which defines three message types:

### Request

A message that requires a response:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list",
  "params": {}
}
```

### Response

Successful reply to a request:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {
        "name": "get_weather",
        "description": "Get weather for a location",
        "inputSchema": {...}
      }
    ]
  }
}
```

### Error Response

Failed request:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32600,
    "message": "Invalid Request"
  }
}
```

### Notification

One-way message, no response expected:

```json
{
  "jsonrpc": "2.0",
  "method": "notification/example",
  "params": {}
}
```

---

## Transport Protocols

### STDIO Transport

Direct communication via child process stdin/stdout.

**Setup**: Host spawns MCP server as subprocess:

```python
import subprocess
import json

process = subprocess.Popen(
    ["python", "mcp_server.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Send request
request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2025-11-25",
        "capabilities": {},
        "clientInfo": {"name": "thegent", "version": "1.0"}
    }
}

process.stdin.write(json.dumps(request) + "\n")
process.stdin.flush()

# Read response
response_line = process.stdout.readline()
response = json.loads(response_line)
```

**Advantages**:
- Simple, no network setup
- Built-in process isolation
- Direct stdout/stderr communication

**Disadvantages**:
- Local only
- Single connection per process

### SSE (Server-Sent Events) Transport

HTTP-based streaming for remote servers:

```bash
# Start SSE server on localhost:3000
curl -X POST http://localhost:3000/sse/initialize \
  -H "Content-Type: application/json" \
  -d '{
    "protocolVersion": "2025-11-25",
    "capabilities": {},
    "clientInfo": {"name": "thegent"}
  }'

# Server responds with stream of events
event: server.ready
data: {"status": "initialized"}

# Client sends requests
event: tools/list
data: {}
```

**Advantages**:
- Remote server access
- Browser-compatible
- Bi-directional streaming

**Disadvantages**:
- Network latency
- Requires HTTP server

### Streamable HTTP Transport

Modern HTTP with bi-directional streaming:

```
POST /mcp HTTP/1.1
Content-Type: application/octet-stream

[request frames as binary or JSON]
```

**Advantages**:
- Efficient, multiplexed
- Works with proxies
- Supports both directions

---

## Initialization Handshake

Every MCP connection begins with initialization:

### Client Sends Initialize Request

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-11-25",
    "capabilities": {
      "roots": {
        "listChanged": true
      },
      "sampling": {}
    },
    "clientInfo": {
      "name": "thegent",
      "version": "1.0.0"
    }
  }
}
```

### Server Responds with Capabilities

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2025-11-25",
    "capabilities": {
      "tools": {},
      "resources": {},
      "prompts": {},
      "logging": {}
    },
    "serverInfo": {
      "name": "my-mcp-server",
      "version": "1.0"
    },
    "instructions": "Server usage instructions..."
  }
}
```

### Client Acknowledges with Initialized Notification

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/initialized",
  "params": {}
}
```

---

## Core Capabilities

### Tools

Functions the model can call to perform actions (side effects).

#### Listing Tools

**Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list",
  "params": {}
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "tools": [
      {
        "name": "get_weather",
        "description": "Get current weather for a location",
        "inputSchema": {
          "type": "object",
          "properties": {
            "location": {
              "type": "string",
              "description": "City name or coordinates"
            },
            "unit": {
              "type": "string",
              "enum": ["celsius", "fahrenheit"],
              "default": "celsius"
            }
          },
          "required": ["location"]
        }
      },
      {
        "name": "send_email",
        "description": "Send an email message",
        "inputSchema": {
          "type": "object",
          "properties": {
            "to": { "type": "string" },
            "subject": { "type": "string" },
            "body": { "type": "string" }
          },
          "required": ["to", "subject", "body"]
        }
      }
    ]
  }
}
```

#### Calling a Tool

**Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "get_weather",
    "arguments": {
      "location": "San Francisco",
      "unit": "fahrenheit"
    }
  }
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Current weather in San Francisco: 65°F, partly cloudy"
      }
    ],
    "isError": false
  }
}
```

### Resources

Read-only data sources that the model can query.

#### Listing Resources

**Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "resources/list",
  "params": {}
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "result": {
    "resources": [
      {
        "uri": "file:///data/customer_db.csv",
        "name": "Customer Database",
        "description": "Customer records and preferences",
        "mimeType": "text/csv"
      },
      {
        "uri": "sqlite:///knowledge.db",
        "name": "Knowledge Base",
        "description": "Company policies and procedures",
        "mimeType": "application/json"
      }
    ]
  }
}
```

#### Reading a Resource

**Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "method": "resources/read",
  "params": {
    "uri": "file:///data/customer_db.csv"
  }
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "result": {
    "contents": [
      {
        "uri": "file:///data/customer_db.csv",
        "mimeType": "text/csv",
        "text": "id,name,email\n1,Alice,alice@example.com\n2,Bob,bob@example.com\n..."
      }
    ]
  }
}
```

### Prompts

Reusable prompt templates and workflows for standardizing interactions.

#### Listing Prompts

**Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 6,
  "method": "prompts/list",
  "params": {}
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 6,
  "result": {
    "prompts": [
      {
        "name": "code_review",
        "description": "Code review prompt template",
        "arguments": [
          {
            "name": "code",
            "description": "Code to review"
          },
          {
            "name": "language",
            "description": "Programming language"
          }
        ]
      }
    ]
  }
}
```

#### Getting a Prompt

**Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 7,
  "method": "prompts/get",
  "params": {
    "name": "code_review",
    "arguments": {
      "code": "def add(a, b):\n    return a + b",
      "language": "python"
    }
  }
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 7,
  "result": {
    "messages": [
      {
        "role": "user",
        "content": "Review the following Python code for best practices:\n\ndef add(a, b):\n    return a + b"
      }
    ]
  }
}
```

### Sampling (Reverse)

Server can request the AI model to generate text (model-in-the-loop):

**Request** (from server to host):
```json
{
  "jsonrpc": "2.0",
  "id": 8,
  "method": "sampling/createMessage",
  "params": {
    "messages": [
      {
        "role": "user",
        "content": "Generate a test case for this function"
      }
    ],
    "modelPreferences": {
      "costPriority": 1,
      "latencyPriority": 50,
      "intelligencePriority": 25
    },
    "systemPrompt": "You are a test engineer..."
  }
}
```

**Response** (from host to server):
```json
{
  "jsonrpc": "2.0",
  "id": 8,
  "result": {
    "content": {
      "type": "text",
      "text": "def test_add():\n    assert add(2, 3) == 5\n    assert add(-1, 1) == 0"
    },
    "model": "gpt-4o",
    "stopReason": "end_turn",
    "usage": {
      "inputTokens": 50,
      "outputTokens": 30
    }
  }
}
```

---

## Python SDK (Official)

### Server Implementation (FastMCP)

```python
from mcp.server.fastmcp import FastMCP

server = FastMCP("my-server")

# Define a tool
@server.tool()
def get_weather(location: str, unit: str = "celsius") -> str:
    """Get weather for a location."""
    # Implementation
    return f"Weather in {location}: 20°C"

# Define a resource
@server.resource("file:///knowledge.db")
def knowledge_db() -> str:
    """Read knowledge database."""
    with open("/path/to/knowledge.db") as f:
        return f.read()

# Define a prompt
@server.prompt()
def code_review(code: str, language: str) -> list:
    """Code review prompt template."""
    return [
        {
            "role": "user",
            "content": f"Review this {language} code:\n{code}"
        }
    ]

# Run server
if __name__ == "__main__":
    server.run()
```

### Client Usage

```python
import asyncio
from mcp.client import StdioClient

async def main():
    # Connect to STDIO-based server
    client = StdioClient(["python", "mcp_server.py"])

    # Initialize
    await client.initialize()

    # List tools
    tools = await client.list_tools()
    print(f"Available tools: {[t.name for t in tools]}")

    # Call a tool
    result = await client.call_tool("get_weather", {"location": "NYC"})
    print(f"Result: {result.text}")

    # List resources
    resources = await client.list_resources()
    for resource in resources:
        print(f"Resource: {resource.uri}")

    # Read a resource
    content = await client.read_resource("file:///knowledge.db")
    print(f"Content: {content.text}")
```

---

## Schema Definition

### Tool Input Schema

Tools use JSON Schema for input validation:

```json
{
  "name": "database_query",
  "description": "Execute SQL query",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "SQL SELECT query"
      },
      "timeout": {
        "type": "integer",
        "minimum": 1,
        "maximum": 300,
        "description": "Query timeout in seconds"
      }
    },
    "required": ["query"]
  }
}
```

### Accepted Types

```
- string
- number
- integer
- boolean
- array
- object
- null
```

---

## Thegent Integration

MCP servers integrate into thegent in three ways:

### 1. Direct Tool Registration

```python
# In thegent's MCPToolRegistry
class MCPToolRegistry:
    def register_server(self, server_config: dict):
        """Register MCP server and expose its tools."""
        transport = server_config.get("transport", "stdio")

        if transport == "stdio":
            client = StdioClient(server_config["command"])
        elif transport == "sse":
            client = SSEClient(server_config["url"])

        # Auto-register all tools from server
        tools = await client.list_tools()
        for tool in tools:
            self.register_tool(tool.name, client.call_tool)
```

### 2. Gemini CLI MCP Support

Configured in `~/.gemini/config`:

```yaml
mcp:
  servers:
    - name: custom-tools
      command: python /path/to/mcp_server.py
      transport: stdio
    - name: web-tools
      url: http://localhost:3000
      transport: sse
```

### 3. Responses API MCP Integration

```json
{
  "model": "gpt-4o",
  "input": {"type": "message", "content": "..."},
  "tools": [
    {
      "type": "mcp",
      "server": {
        "type": "stdio",
        "command": "python /path/to/mcp_server.py"
      }
    }
  ]
}
```

---

## Capability Negotiation

### Server Declares Capabilities

```json
{
  "result": {
    "capabilities": {
      "tools": {
        "listChanged": false
      },
      "resources": {
        "subscribe": true,
        "listChanged": true
      },
      "prompts": {
        "listChanged": false
      },
      "logging": {
        "level": "debug"
      },
      "sampling": {
        "supported": true
      }
    }
  }
}
```

### Client Declares Capabilities

```json
{
  "capabilities": {
    "roots": {
      "listChanged": true
    },
    "sampling": {
      "supported": true
    },
    "experimental": {
      "mcp_apps": true
    }
  }
}
```

---

## Error Handling

### Standard JSON-RPC Errors

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32600,
    "message": "Invalid Request",
    "data": { "details": "..." }
  }
}
```

### MCP-Specific Errors

| Code | Message | Meaning |
|------|---------|---------|
| -32700 | Parse error | JSON parse failure |
| -32600 | Invalid Request | Malformed request |
| -32601 | Method not found | Unknown method |
| -32602 | Invalid params | Parameter validation failed |
| -32603 | Internal error | Server error |

---

## MCP Apps (2026 Feature)

MCP Apps allow servers to return interactive UI components:

```json
{
  "result": {
    "content": [
      {
        "type": "app",
        "app": {
          "type": "dashboard",
          "title": "Sales Dashboard",
          "widgets": [
            {
              "type": "chart",
              "data": [...]
            }
          ]
        }
      }
    ]
  }
}
```

The app renders directly in the conversation, enabling:
- Interactive dashboards
- Multi-step workflows
- Forms and inputs
- Real-time visualizations

---

## Security Considerations

### Input Validation

Always validate tool inputs:

```python
@server.tool()
def execute_command(cmd: str) -> str:
    """Execute shell command (restricted)."""
    # Whitelist allowed commands
    allowed = ["ls", "pwd", "whoami"]
    if cmd.split()[0] not in allowed:
        raise ValueError(f"Command {cmd} not allowed")
    return os.popen(cmd).read()
```

### Approval Gates (Elicitation)

```python
@server.tool()
def delete_database() -> str:
    """Requires user approval."""
    # Server notifies host for approval
    return await request_user_approval(
        "Delete database?",
        details="This will erase all data"
    )
```

### Sandboxing

```python
@server.tool()
def run_code(code: str) -> str:
    """Execute code in sandbox."""
    # Use subprocess with restrictions
    result = subprocess.run(
        ["python", "-c", code],
        timeout=5,
        capture_output=True,
        cwd="/tmp/sandbox"  # Restricted directory
    )
    return result.stdout
```

---

## Comparison to Other Tool Protocols

| Feature | MCP | OpenAI Tools | Anthropic Tool Use |
|---------|-----|-------------|-------------------|
| **Standard** | Open standard | OpenAI proprietary | Anthropic proprietary |
| **Transport** | JSON-RPC + multiple | HTTP REST only | HTTP REST only |
| **Bi-directional** | Yes (sampling) | No | No |
| **Resources** | Yes (read-only data) | No | No |
| **Prompts** | Yes (templates) | No | No |
| **Multi-server** | Native | Proxy-only | Proxy-only |
| **Local support** | STDIO native | Requires wrapper | Requires wrapper |

---

## Sources

- [Model Context Protocol Specification (2025-11-25)](https://modelcontextprotocol.io/specification/2025-11-25)
- [MCP GitHub Repository](https://github.com/modelcontextprotocol/modelcontextprotocol)
- [MCP Transports Documentation](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports)
- [MCP Server Development Guide](https://github.com/cyanheads/model-context-protocol-resources/blob/main/guides/mcp-server-development-guide.md)
- [MCP Message Types Reference](https://portkey.ai/blog/mcp-message-types-complete-json-rpc-reference-guide/)
- [Model Context Protocol Complete Guide 2026](https://fast.io/resources/model-context-protocol/)
- [Python SDK Repository](https://github.com/modelcontextprotocol/python-sdk)
- [Roo Code MCP Documentation](https://docs.roocode.com/features/mcp/server-transports)
- [MCP Apps Blog Post](http://blog.modelcontextprotocol.io/posts/2026-01-26-mcp-apps/)

---

## Source: context/nats.md

# NATS (nats-py Python Client) Context

> Definitive reference for NATS messaging with the nats-py Python async client.
> Sources: nats-io.github.io/nats.py, docs.nats.io, github.com/nats-io/nats.py (fetched 2026-02-20).
> **Version covered: nats-py >= 2.12.0 (trace project version)**

---

## What is NATS

**NATS** is a cloud-native, high-performance messaging system. It provides:

- **Core NATS**: At-most-once pub/sub, request-reply, queue groups — fast, ephemeral
- **JetStream**: Persistent streaming, at-least-once and exactly-once delivery, key-value store, object store
- **Subject-based addressing**: Messages routed by subject strings (`"orders.created"`, `"users.>"`), with wildcards

NATS is the transport layer for event-driven, loosely-coupled services. Unlike Kafka, it has no broker-side consumer groups; consumers are process-side.

**trace Use Case:** `nats-py>=2.12.0` + `nkeys>=0.2.1` in `pyproject.toml`. Used for real-time event distribution between trace services (Go backend, Python backend, worker processes) — agent job events, webhook delivery, inter-service messaging.

---

## Key Concepts

| Term | Definition |
|------|-----------|
| **Subject** | Dot-delimited routing key, e.g., `"orders.created"`, `"users.*.updated"` |
| **Wildcard `*`** | Matches one token: `"orders.*.created"` matches `"orders.123.created"` |
| **Wildcard `>`** | Matches remaining tokens: `"orders.>"` matches all under `orders.` |
| **Queue group** | Named group where only one subscriber receives each message (load balancing) |
| **JetStream** | Persistence layer on top of core NATS; streams store messages |
| **Stream** | Named, durable collection of messages filtered by subjects |
| **Consumer** | Named cursor on a stream; tracks delivery progress |
| **KV bucket** | JetStream-backed key-value store |
| **NUID** | NATS unique ID generator (fast, URL-safe) |
| **nkeys** | Ed25519-based decentralized auth for NATS v2+ |

---

## Installation

```bash
pip install nats-py
# With nkeys for NATS v2 decentralized auth
pip install nats-py[nkeys]
# or separately
pip install nkeys

# Versions in trace project:
# nats-py>=2.12.0
# nkeys>=0.2.1
```

**NATS Server (local dev):**

```bash
brew install nats-server
nats-server -js          # With JetStream enabled

# Or Docker
docker run -p 4222:4222 nats:latest -js
```

---

## Connection

```python
import asyncio
import nats
from nats.aio.client import Client as NATS

async def main():
    # Connect to local server
    nc = await nats.connect("nats://localhost:4222")

    # Multiple servers (cluster)
    nc = await nats.connect([
        "nats://server1:4222",
        "nats://server2:4222",
    ])

    # With options
    nc = await nats.connect(
        "nats://localhost:4222",
        name="trace-python-backend",
        connect_timeout=5,            # seconds
        reconnect_time_wait=2,        # seconds between reconnect attempts
        max_reconnect_attempts=10,    # -1 for infinite
        ping_interval=20,             # seconds
        max_outstanding_pings=3,
        # Callbacks
        error_cb=error_handler,
        disconnected_cb=disconnected_handler,
        reconnected_cb=reconnected_handler,
        closed_cb=closed_handler,
    )

    await nc.close()

asyncio.run(main())
```

**Connection state checks:**

```python
nc.is_connected        # bool
nc.is_closed           # bool
nc.is_reconnecting     # bool
nc.connected_url       # URL of active server
nc.max_payload         # Max message size in bytes
nc.client_id           # Unique client identifier
```

---

## Core NATS: Pub/Sub

### Publish

```python
# Publish bytes
await nc.publish("orders.created", b'{"order_id": "123"}')

# With reply subject (for request-reply)
await nc.publish("orders.created", b'data', reply="inbox.123")

# Flush ensures messages reach server
await nc.flush(timeout=5)
```

### Subscribe (Callback-based)

```python
async def message_handler(msg):
    subject = msg.subject
    reply = msg.reply
    data = msg.data.decode()
    print(f"Received on {subject}: {data}")

    # Respond to request-reply
    if msg.reply:
        await nc.publish(msg.reply, b"ACK")

sub = await nc.subscribe("orders.*", cb=message_handler)

# Unsubscribe
await sub.unsubscribe()

# Queue group (load-balanced delivery — only one subscriber gets each message)
sub = await nc.subscribe("orders.created", queue="order-processors", cb=message_handler)
```

### Subscribe (Iterator)

```python
sub = await nc.subscribe("orders.created")

async for msg in sub.messages:
    data = msg.data.decode()
    print(f"Message: {data}")
    if should_stop:
        break

await sub.unsubscribe()
```

### Subscribe (next_msg)

```python
sub = await nc.subscribe("responses")

# Wait for one message
msg = await sub.next_msg(timeout=5.0)
print(msg.data.decode())

await sub.unsubscribe()
```

---

## Request-Reply

```python
# Send request; wait for first reply (1 second timeout)
reply = await nc.request("service.get_user", b'{"user_id": "123"}', timeout=1.0)
user_data = reply.data.decode()

# Service handler
async def user_service(msg):
    user_id = json.loads(msg.data)["user_id"]
    user = await db.get_user(user_id)
    await msg.respond(json.dumps(user).encode())

await nc.subscribe("service.get_user", cb=user_service)
```

**`NoRespondersError`**: Raised when no subscriber matches the subject. Handle it:

```python
from nats.errors import NoRespondersError

try:
    reply = await nc.request("service.unknown", b"", timeout=1.0)
except NoRespondersError:
    print("No service listening on that subject")
```

---

## JetStream

JetStream adds persistence, acknowledgment, and replay capabilities.

### JetStream Context

```python
js = nc.jetstream()
# or with options
js = nc.jetstream(timeout=5)
```

### Stream Management

```python
from nats.js.api import StreamConfig, RetentionPolicy, StorageType

# Create stream
await js.add_stream(StreamConfig(
    name="ORDERS",
    subjects=["orders.>"],          # All subjects under orders.
    retention=RetentionPolicy.LIMITS,
    storage=StorageType.FILE,
    max_msgs=1_000_000,
    max_bytes=1024 * 1024 * 1024,   # 1GB
    max_age=86400,                  # 1 day in seconds
))

# Get stream info
info = await js.stream_info("ORDERS")
print(info.config.subjects)

# Update stream
await js.update_stream(StreamConfig(name="ORDERS", max_msgs=2_000_000, subjects=["orders.>"]))

# Delete stream
await js.delete_stream("ORDERS")

# Purge stream (remove all messages)
await js.purge_stream("ORDERS")
```

### Publishing to JetStream

```python
import json

# Publish and wait for ACK
ack = await js.publish("orders.created", json.dumps({"id": "123"}).encode())
print(f"Published: stream={ack.stream}, seq={ack.seq}")

# Publish with deduplication (exactly-once)
ack = await js.publish(
    "orders.created",
    json.dumps({"id": "123"}).encode(),
    headers={"Nats-Msg-Id": "order-123"},  # Idempotency key
)
```

### Push Subscription (Async, Real-time)

```python
from nats.js.api import ConsumerConfig, AckPolicy, DeliverPolicy

# Subscribe (creates ephemeral consumer)
sub = await js.subscribe("orders.>", durable="order-processor")

async for msg in sub.messages:
    data = json.loads(msg.data)
    try:
        await process_order(data)
        await msg.ack()                  # Acknowledge
    except Exception as e:
        await msg.nak(delay=5)           # Negative ack, retry after 5s

# Or with callback
async def order_handler(msg):
    data = json.loads(msg.data)
    await process_order(data)
    await msg.ack()

sub = await js.subscribe(
    "orders.>",
    cb=order_handler,
    durable="order-processor",
    stream="ORDERS",
    config=ConsumerConfig(
        ack_policy=AckPolicy.EXPLICIT,
        deliver_policy=DeliverPolicy.ALL,  # Start from beginning
        max_deliver=3,                     # Max delivery attempts
    ),
)
```

### Pull Subscription (Batched)

```python
# Create durable pull consumer
sub = await js.pull_subscribe("orders.>", durable="batch-processor", stream="ORDERS")

# Fetch a batch
msgs = await sub.fetch(batch=10, timeout=2.0)
for msg in msgs:
    await process(msg.data)
    await msg.ack()

# Consumer info
info = await sub.consumer_info()
print(f"Pending: {info.num_pending}")
```

**Message acknowledgment modes:**

| Method | Behavior |
|--------|---------|
| `await msg.ack()` | Acknowledge — don't redeliver |
| `await msg.ack_sync()` | Acknowledge with server confirmation |
| `await msg.nak()` | Negative ack — redeliver immediately |
| `await msg.nak(delay=5)` | Negative ack — redeliver after 5 seconds |
| `await msg.in_progress()` | Heartbeat — still processing, reset ack wait |
| `await msg.term()` | Terminate — stop redelivery permanently |

---

## Key-Value Store

JetStream-backed KV with watch capability.

```python
# Create KV bucket
kv = await js.create_key_value(
    bucket="trace-config",
    ttl=3600,            # 1 hour TTL (seconds)
    history=5,           # Keep 5 historical values per key
    storage=StorageType.FILE,
)

# Or get existing bucket
kv = await js.key_value("trace-config")

# CRUD operations
await kv.put("feature.new_ui", b"true")
entry = await kv.get("feature.new_ui")
print(entry.value.decode())    # "true"

await kv.update("feature.new_ui", b"false", last_revision=entry.revision)

await kv.delete("feature.old_flag")
await kv.purge("feature.old_flag")   # Remove all history for key

# Status
status = await kv.status()
print(f"Bucket: {status.bucket}, Keys: {status.values}")

# Watch for changes
async for entry in await kv.watch("feature.*"):
    if entry is None:
        break  # Initial values delivered
    print(f"Key: {entry.key}, Value: {entry.value}, Op: {entry.operation}")
```

---

## Authentication

```python
# Username/password
nc = await nats.connect("nats://user:pass@localhost:4222")

# Token
nc = await nats.connect("nats://mytoken@localhost:4222")
# or
nc = await nats.connect("nats://localhost:4222", token="mytoken")

# NKeys (Ed25519; NATS v2 decentralized auth)
import nkeys

# From seed file
with open("user.nk") as f:
    seed = f.read().strip().encode()
keypair = nkeys.from_seed(seed)

nc = await nats.connect(
    "nats://localhost:4222",
    nkeys_seed=keypair.seed,
)

# TLS
import ssl
ssl_ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
ssl_ctx.load_verify_locations("ca.pem")
ssl_ctx.load_cert_chain("client.pem", "client-key.pem")

nc = await nats.connect("nats://localhost:4222", tls=ssl_ctx)
```

---

## Error Handling

```python
from nats.errors import (
    TimeoutError,
    NoRespondersError,
    ConnectionClosedError,
    AuthorizationError,
    MaxPayloadError,
)
from nats.js.errors import (
    NotFoundError,
    ServiceUnavailableError,
    FetchTimeoutError,
    KeyNotFoundError,
)

# Connection error callbacks
async def error_handler(e):
    if isinstance(e, ConnectionClosedError):
        print("Connection closed:", e)
    elif isinstance(e, AuthorizationError):
        print("Auth failed:", e)
    else:
        print("NATS error:", e)

async def disconnected_handler():
    print("Disconnected from NATS")

async def reconnected_handler():
    print("Reconnected to NATS")

nc = await nats.connect(
    "nats://localhost:4222",
    error_cb=error_handler,
    disconnected_cb=disconnected_handler,
    reconnected_cb=reconnected_handler,
)
```

---

## Graceful Shutdown

```python
async def shutdown(nc):
    # Drain: process pending messages, then close
    await nc.drain()
    # After drain, nc.is_closed == True; do NOT call nc.close() after drain
```

---

## NUID (Unique ID Generator)

```python
from nats.nuid import NUID

nuid = NUID()
unique_id = nuid.next().decode()  # "4kMEXOoWQQ56gd8dqLI4l3"
# Fast URL-safe unique IDs; ~50ns per ID
```

---

## Code Examples: trace Service Pattern

```python
import asyncio
import json
import nats
from nats.aio.client import Client as NATS

class TraceEventBus:
    """Wrapper around NATS for trace service events."""

    def __init__(self, nc: NATS):
        self._nc = nc
        self._js = nc.jetstream()

    @classmethod
    async def connect(cls, servers: list[str]) -> "TraceEventBus":
        nc = await nats.connect(servers, name="trace-backend")
        return cls(nc)

    async def publish_job_event(self, job_id: str, event: str, data: dict) -> None:
        subject = f"jobs.{job_id}.{event}"
        payload = json.dumps({"job_id": job_id, "event": event, **data}).encode()
        await self._js.publish(subject, payload, headers={"Nats-Msg-Id": f"{job_id}-{event}"})

    async def subscribe_job_events(self, job_id: str, handler) -> None:
        sub = await self._js.subscribe(
            f"jobs.{job_id}.>",
            durable=f"job-{job_id}-handler",
        )
        async for msg in sub.messages:
            event_data = json.loads(msg.data)
            await handler(event_data)
            await msg.ack()

    async def close(self) -> None:
        await self._nc.drain()
```

---

## thegent / trace Integration

- **trace**: `nats-py>=2.12.0`, `nkeys>=0.2.1` in `pyproject.toml`
- **Pattern**: JetStream for durable event delivery; KV store for feature flags / runtime config
- **Subjects**: Dot-delimited hierarchy (e.g., `"jobs.{id}.created"`, `"agents.{id}.status"`)
- **Server**: JetStream-enabled (`nats-server -js`); Streams and consumers managed by Python backend on startup

---

## Known Issues / Gotchas

1. **JetStream requires `-js` flag**: `nats-server` without `-js` flag ignores JetStream API calls silently.
2. **Drain vs Close**: After `nc.drain()`, do NOT call `nc.close()` — drain handles the close. Calling both causes errors.
3. **Durable name required for persistence**: Without `durable=`, JetStream creates an ephemeral consumer that disappears when subscription ends.
4. **ACK timeout**: Messages not acked within `ack_wait` (default 30s) are redelivered. Always `await msg.ack()` or `await msg.in_progress()` for long tasks.
5. **At-most-once for core NATS**: Core NATS pub/sub has no persistence. Use JetStream if you need guaranteed delivery.
6. **Max payload**: Default max is 1MB per message. Configure `max_payload` on server for larger messages.
7. **Subject namespace**: Subjects are global. Use dot-delimited namespaces to avoid collision across services.

---

## Sources & References

- **nats-py Documentation**: https://nats-io.github.io/nats.py/ (fetched 2026-02-20)
- **NATS Docs**: https://docs.nats.io (fetched 2026-02-20)
- **GitHub**: https://github.com/nats-io/nats.py (fetched 2026-02-20)
- **JetStream Docs**: https://docs.nats.io/nats-concepts/jetstream (fetched 2026-02-20)
- **PyPI**: https://pypi.org/project/nats-py/ (fetched 2026-02-20)
- **Last Verified**: 2026-02-20

---

## Quick Reference

| Item | Value |
|------|-------|
| Package | `nats-py>=2.12.0` |
| Auth extra | `nats-py[nkeys]` |
| Default port | `4222` |
| JetStream flag | `nats-server -js` |
| Core NATS | At-most-once, ephemeral |
| JetStream | At-least-once / exactly-once, persistent |

### Subject Wildcard Rules

```
orders.*        → matches orders.created, orders.updated (one token)
orders.>        → matches orders.created, orders.123.items (one or more tokens)
>               → matches everything
```

### Common Patterns

```python
# Connect
nc = await nats.connect("nats://localhost:4222")

# Core pub/sub
await nc.publish("subject", b"data")
sub = await nc.subscribe("subject.*", cb=handler)

# Request-reply
reply = await nc.request("service.method", b"data", timeout=1.0)

# JetStream context
js = nc.jetstream()

# Publish to stream
ack = await js.publish("orders.created", b"data", headers={"Nats-Msg-Id": "msg-001"})

# Subscribe from stream
sub = await js.subscribe("orders.>", durable="processor")
async for msg in sub.messages:
    await process(msg.data)
    await msg.ack()

# KV store
kv = await js.key_value("my-bucket")
await kv.put("key", b"value")
entry = await kv.get("key")

# Graceful shutdown
await nc.drain()
```

---

## Source: context/openai-responses-api.md

# OpenAI Responses API Context

> Definitive reference for OpenAI's Responses API as a next-generation agent protocol in thegent.
> Sources: platform.openai.com API documentation, migration guides (fetched 2026-02-20).

---

## What is the Responses API

The Responses API is OpenAI's modern agentic endpoint designed to replace Chat Completions for agent-based workflows. Unlike Chat Completions (stateless, array of messages), the Responses API uses a stateful model with Items, native tools, and persistent reasoning state.

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

---

## Source: context/openrouter.md

# OpenRouter API Context

> Definitive reference for implementing OpenRouter support in the proxy (CLIProxyAPIPlus / thegent routing layer).
> Sources: openrouter.ai/docs (fetched 2026-02-20).

---

## What is OpenRouter

OpenRouter is a unified API gateway that provides access to hundreds of AI models from OpenAI,
Anthropic, Google, Meta, Mistral, DeepSeek, and many others through a single OpenAI-compatible
endpoint. It handles provider selection, failover, load balancing, cost optimization, and
aggregates usage metrics across providers.

Key capabilities:
- Single endpoint for 400+ models
- Automatic provider failover and load balancing
- Cost/throughput/latency-aware routing
- Plugins: real-time web search, PDF parsing, response healing
- Prompt transforms (middle-out context compression)
- Zero Data Retention (ZDR) routing options
- BYOK (Bring Your Own Key) for supported providers
- Generation stats and cost tracking via `/api/v1/generation`

---

## Base URL

```
https://openrouter.ai/api/v1
```

All endpoints are relative to this base.

---

## Authentication

### Required Header

```
Authorization: Bearer <OPENROUTER_API_KEY>
```

API keys are created at `https://openrouter.ai/keys`.

### Optional Attribution Headers

These are not required for API calls but affect app visibility on openrouter.ai leaderboards:

```
HTTP-Referer: https://your-app-url.com
X-Title: Your App Name
```

### Special-Purpose Request Headers

```
structured-outputs-2025-11-13: true
```
Required when using strict tool calls (`tools[].strict: true`). Without this header,
OpenRouter strips the `strict` field and routes normally.

### Auth Key Introspection

```
GET https://openrouter.ai/api/v1/key
Authorization: Bearer <API_KEY>
```

Response fields:

| Field | Type | Description |
|-------|------|-------------|
| `limit` | number\|null | Credit limit; null = unlimited |
| `limit_remaining` | number | Available credits |
| `limit_reset` | string | Reset interval type |
| `usage` | number | All-time credit consumption (USD) |
| `usage_daily` | number | Daily usage |
| `usage_weekly` | number | Weekly usage |
| `usage_monthly` | number | Monthly usage |
| `byok_usage` | object | BYOK usage metrics (same time periods) |
| `is_free_tier` | boolean | Whether account has no purchase history |

---

## Key Differences from Standard OpenAI API

| Area | OpenAI | OpenRouter |
|------|--------|------------|
| Model IDs | `gpt-4o`, `gpt-4o-mini` | `openai/gpt-4o`, `openai/gpt-4o-mini` |
| Extra request fields | None | `provider`, `route`, `models`, `transforms`, `plugins`, `reasoning`, `session_id`, `trace`, `metadata`, `debug` |
| Extra sampling params | None | `top_k`, `repetition_penalty`, `min_p`, `top_a` |
| `finish_reason` | Provider-native | Normalized to `stop\|tool_calls\|length\|content_filter\|error` |
| `native_finish_reason` | Not present | Raw provider finish reason |
| Usage in response | No cost | `/api/v1/generation` endpoint for cost; native token counts in response |
| Streaming SSE comments | None | `": OPENROUTER PROCESSING"` keep-alive comments (safe to ignore) |
| Provider in response | Not present | `model` field reflects actual model used (important with fallbacks) |
| Model routing | Not present | `provider` object, `models` array, model variant suffixes |
| Non-standard params | Rejected | Silently ignored if unsupported by target model |

---

## Model ID Format

OpenRouter model IDs use the format:

```
{provider}/{model-name}[:{variant}]
```

Examples:
- `openai/gpt-4o`
- `anthropic/claude-sonnet-4-5`
- `meta-llama/llama-3.3-70b-instruct`
- `google/gemini-2.0-flash-001`
- `deepseek/deepseek-chat`

### Model Variant Suffixes

Suffixes modify routing behavior. Two categories: **dynamic** (work on any model) and
**static** (only on models that declare support).

| Suffix | Category | Behavior | Equivalent to |
|--------|----------|----------|---------------|
| `:nitro` | Dynamic | Route to highest-throughput provider | `provider.sort: "throughput"` |
| `:floor` | Dynamic | Route to lowest-cost provider | `provider.sort: "price"` |
| `:online` | Dynamic | Enable real-time web search via Exa.ai | `plugins: [{id: "web"}]` |
| `:free` | Static | Use free tier of this model (low rate limits) | n/a — only on models with free variants |
| `:extended` | Static | Extended context window variant | n/a — model-specific |
| `:thinking` | Static | Extended reasoning / thinking tokens | n/a — model-specific |
| `:exacto` | Static | Curated routing for tool-calling accuracy | n/a — model-specific |

Examples:
- `anthropic/claude-3.5-sonnet:nitro` — fastest provider for this model
- `openai/gpt-4o:floor` — cheapest provider
- `openai/gpt-4o:online` — with real-time web search
- `meta-llama/llama-3-8b-instruct:free` — free tier variant
- `anthropic/claude-3-7-sonnet:thinking` — reasoning tokens enabled

### Permaslugs vs Canonical Slugs

- **canonical_slug**: URL-friendly identifier returned in the models API
- **permaslug** (model_id in endpoints API): Immutable ID for a specific model version
- The models API `id` field is the string used in requests

---

## Endpoints

### POST /api/v1/chat/completions

Primary completions endpoint. OpenAI-compatible with OpenRouter-specific extensions.

#### Request Schema

```typescript
{
  // --- Required ---
  messages: Message[];           // Conversation history

  // --- Core (one of model or models required) ---
  model?: string;                // Primary model ID (e.g. "openai/gpt-4o")
  models?: string[];             // Fallback model list in priority order

  // --- Standard OpenAI Sampling Parameters ---
  temperature?: number;          // Default 1.0, range 0.0–2.0
  top_p?: number;                // Default 1.0, range 0.0–1.0
  max_tokens?: number;           // Max output tokens
  max_completion_tokens?: number;// Alias for max_tokens
  stop?: string | string[];      // Stop sequences
  seed?: integer;                // Reproducibility seed
  frequency_penalty?: number;    // Range -2.0–2.0
  presence_penalty?: number;     // Range -2.0–2.0
  logit_bias?: Record<string, number>; // Token ID → bias (-100 to 100)
  logprobs?: boolean;
  top_logprobs?: number;         // 0–20
  stream?: boolean;              // Default false; enables SSE
  stream_options?: {
    include_usage: boolean;      // Include usage in stream final chunk
  };
  response_format?: ResponseFormat;
  structured_outputs?: boolean;
  tools?: Tool[];
  tool_choice?: "none" | "auto" | "required" | NamedToolChoice;
  parallel_tool_calls?: boolean; // Default true
  modalities?: ("text" | "image")[];

  // --- OpenRouter-Extended Sampling Parameters ---
  top_k?: integer;               // 0 = disabled; restricts to top N tokens
  repetition_penalty?: number;   // Default 1.0, range 0.0–2.0
  min_p?: number;                // Min probability relative to best token, 0.0–1.0
  top_a?: number;                // Dynamic top-p, 0.0–1.0

  // --- OpenRouter Routing ---
  provider?: ProviderPreferences; // Provider routing configuration (see below)
  route?: "fallback";            // Legacy; use models[] for fallbacks
  transforms?: string[];         // Currently: ["middle-out"] for prompt compression

  // --- OpenRouter Plugins ---
  plugins?: Plugin[];            // Enable per-request plugins

  // --- OpenRouter Reasoning ---
  reasoning?: {
    effort?: "xhigh" | "high" | "medium" | "low" | "minimal" | "none";
    summary?: "auto" | "concise" | "detailed";
  };

  // --- Observability ---
  user?: string;                 // End-user identifier (passed to providers)
  session_id?: string;           // Max 128 chars; groups related requests
  trace?: {
    trace_id?: string;
    trace_name?: string;
    span_name?: string;
    generation_name?: string;
    parent_span_id?: string;
  };
  metadata?: Record<string, unknown>; // Custom key-value; known keys: trace_id,
                                      // trace_name, span_name, generation_name,
                                      // parent_span_id (get special handling)

  // --- Debug (development only, do not use in production) ---
  debug?: {
    echo_upstream_body: boolean; // Returns upstream request body as first SSE chunk
  };
}
```

#### Message Types

```typescript
type Message =
  | { role: "system";    content: string | ContentPart[]; name?: string }
  | { role: "user";      content: string | ContentPart[]; name?: string }
  | { role: "developer"; content: string | ContentPart[]; name?: string }
  | { role: "assistant"; content?: string | ContentPart[]; tool_calls?: ToolCall[];
      refusal?: string; name?: string }
  | { role: "tool";      content: string | ContentPart[]; tool_call_id: string }
```

Content parts support: `text`, `image_url`, `input_audio`, `input_video`, `video_url`.
Each part may include `cache_control` for prompt caching.

#### ResponseFormat Options

```typescript
type ResponseFormat =
  | { type: "text" }
  | { type: "json_object" }
  | { type: "json_schema"; json_schema: { name: string; description?: string;
      schema: object; strict?: boolean } }
  | { type: "grammar"; grammar: string }    // GBNF grammar string
  | { type: "python" }
```

#### ProviderPreferences Object

```typescript
type ProviderPreferences = {
  order?: string[];              // Provider slugs to try in order
  only?: string[];               // Whitelist: only use these providers
  ignore?: string[];             // Blacklist: skip these providers
  allow_fallbacks?: boolean;     // Default true; if false, only uses order[0]
  require_parameters?: boolean;  // Only route to providers supporting all params
  data_collection?: "allow" | "deny"; // "deny" = no non-transient data collection
  zdr?: boolean;                 // true = Zero Data Retention endpoints only
  enforce_distillable_text?: boolean; // Restrict to models allowing text distillation
  quantizations?: Quantization[]; // Filter by quantization level
  sort?: "price" | "throughput" | "latency" | SortObject;
  max_price?: {                  // Hard limits; request fails if unavailable
    prompt?: number;             // Max $/1M tokens for prompt
    completion?: number;         // Max $/1M tokens for completion
    image?: number;
    request?: number;
  };
  preferred_min_throughput?: number | PercentileObject; // Soft threshold (deprioritizes)
  preferred_max_latency?: number | PercentileObject;    // Soft threshold (deprioritizes)
};

type Quantization = "int4" | "int8" | "fp4" | "fp6" | "fp8" | "fp16" | "bf16" | "fp32" | "unknown";

type SortObject = {
  by: "price" | "throughput" | "latency";
  partition?: "model" | "none";  // "none" = sort globally across fallback models
};

// Percentile-based performance thresholds
type PercentileObject = {
  p50?: number;
  p75?: number;
  p90?: number;
  p99?: number;
};
```

**Important**: `max_price` is a HARD limit — request fails if no provider meets it.
`preferred_min_throughput` and `preferred_max_latency` are SOFT — providers failing
thresholds are deprioritized, not excluded.

**Default load balancing**: OpenRouter excludes providers with outages in the last 30 seconds,
then selects from lowest-cost candidates weighted by inverse square of price.

#### Plugin Object

```typescript
type Plugin =
  | { id: "web"; max_results?: number; enabled?: boolean }     // Web search (Exa.ai)
  | { id: "file-parser"; enabled?: boolean }                   // PDF/file parsing
  | { id: "response-healing"; enabled?: boolean }              // Auto-fix malformed JSON
```

Default: 5 web results. Pricing: $4 per 1,000 web results. `enabled: false` disables a
default plugin for the current request.

#### Transforms

```typescript
transforms?: ["middle-out"]
```

`middle-out`: Compresses prompts exceeding the model's context window by removing messages
from the middle of the conversation. Default for models with context ≤ 8k tokens.

---

#### Response Schema

```typescript
{
  id: string;                    // Completion ID; also the generation ID for /api/v1/generation
  object: "chat.completion";
  created: number;               // Unix timestamp
  model: string;                 // ACTUAL model used (may differ from request if fallback)
  system_fingerprint?: string | null;
  choices: Array<{
    index: number;
    message: {
      role: "assistant";
      content: string | ContentPart[] | null;
      tool_calls?: ToolCall[];
      refusal?: string | null;
      reasoning?: string | null;             // Reasoning text from thinking models
      reasoning_details?: ReasoningDetail[];
      images?: Array<{ image_url: { url: string } }>;
    };
    finish_reason: "stop" | "tool_calls" | "length" | "content_filter" | "error" | null;
    native_finish_reason?: string | null;    // Raw provider finish reason
    logprobs?: LogprobsObject | null;
  }>;
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
    prompt_tokens_details?: {
      cached_tokens?: number;
      cache_write_tokens?: number;
      audio_tokens?: number;
      video_tokens?: number;
    };
    completion_tokens_details?: {
      reasoning_tokens?: number | null;
      audio_tokens?: number | null;
      accepted_prediction_tokens?: number | null;
      rejected_prediction_tokens?: number | null;
    };
  };
}
```

**Note**: The `model` field in the response reflects the model that ACTUALLY processed the
request. When using `models[]` fallbacks, this will be the model that succeeded, not the
primary requested model.

**Note**: `usage.total_cost` is NOT in the chat completion response. Use
`GET /api/v1/generation?id=<id>` to retrieve cost data.

---

### GET /api/v1/models

Lists all available models.

```
GET https://openrouter.ai/api/v1/models
Authorization: Bearer <API_KEY>
```

#### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `category` | string | Filter by use case: `programming`, `roleplay`, `marketing`, `marketing/seo`, `technology`, `science`, `translation`, `legal`, `finance`, `health`, `trivia`, `academia` |
| `supported_parameters` | string | Filter by supported parameter names |

#### Response

```typescript
{
  data: Array<{
    id: string;                  // Model ID for use in requests
    name: string;                // Display name
    canonical_slug: string;      // URL-friendly identifier
    created: number;             // Unix timestamp
    description: string;
    context_length: number | null;
    pricing: {
      prompt: string;            // Price per token (as string, in USD/token)
      completion: string;
      request: string;
      image: string;
      audio: string;
    };
    architecture: {
      tokenizer: string;
      instruct_type: string | null;
      modality: string;          // e.g. "text->text", "text+image->text"
    };
    supported_parameters: string[];
    default_parameters?: {
      temperature?: number;
      top_p?: number;
      frequency_penalty?: number;
    };
    per_request_limits?: {
      prompt_tokens?: number;
      completion_tokens?: number;
    };
    expiration_date?: string | null; // ISO 8601 or null
  }>;
}
```

---

### GET /api/v1/models/{author}/{slug}/endpoints

Returns all provider endpoints for a specific model with real-time performance metrics.

```
GET https://openrouter.ai/api/v1/models/{author}/{slug}/endpoints
Authorization: Bearer <API_KEY>
```

**Example**: `/api/v1/models/openai/gpt-4o/endpoints`

#### Response

```typescript
{
  data: {
    id: string;
    name: string;
    created: number;
    description: string;
    architecture: object;
    endpoints: Array<{
      name: string;
      model_id: string;          // Permaslug (immutable version-specific ID)
      model_name: string;
      provider_name: string;     // Provider slug (use in provider.order/only/ignore)
      tag: string | null;
      context_length: number;
      max_completion_tokens: number | null;
      max_prompt_tokens: number | null;
      pricing: {
        prompt: string;
        completion: string;
        request: string;
        image: string;
        audio: string;
        discount: number;
      };
      uptime_last_30m: number;   // 0.0–1.0 percentage
      latency_last_30m: {        // Milliseconds
        p50: number;
        p75: number;
        p90: number;
        p99: number;
      };
      throughput_last_30m: {     // Tokens per second
        p50: number;
        p75: number;
        p90: number;
        p99: number;
      };
      supported_parameters: string[];
      supports_implicit_caching: boolean;
      quantization: string | null;
    }>;
  };
}
```

Errors: `404` if model does not exist.

---

### GET /api/v1/generation

Retrieves request metadata, token counts, and cost for a completed generation.

```
GET https://openrouter.ai/api/v1/generation?id=<GENERATION_ID>
Authorization: Bearer <API_KEY>
```

The `GENERATION_ID` is the `id` field from the chat completion response, and also returned
in the `openrouter-generation-id` response header.

#### Response

```typescript
{
  data: {
    id: string;
    upstream_id: string | null;      // Provider's own request ID
    model: string;                   // Actual model used
    created_at: string;              // ISO 8601 timestamp
    origin: string;                  // Request origin URL

    // Cost fields (all in USD)
    total_cost: number;              // Total cost charged to your account
    cache_discount: number | null;   // Discount from prompt caching
    upstream_inference_cost: number | null; // What the provider charged
    usage: number;                   // Usage amount in USD

    // Standard token counts (OpenRouter-computed)
    tokens_prompt: number;
    tokens_completion: number;

    // Native token counts (provider-reported; pricing is based on these)
    native_tokens_prompt: number;
    native_tokens_completion: number;
    native_tokens_completion_images: number | null;
    native_tokens_reasoning: number | null;
    native_tokens_cached: number | null;

    // Performance metrics
    latency: number | null;          // Total latency in ms
    generation_time: number | null;  // Generation duration in ms
    moderation_latency: number | null;

    // Completion details
    finish_reason: string | null;
    native_finish_reason: string | null;
    streamed: boolean | null;
    cancelled: boolean | null;

    // Provider details
    provider_name: string | null;    // Which provider handled the request
    is_byok: boolean;
    provider_responses: object[] | null; // Fallback attempt records

    // Media/search
    num_media_prompt: number | null;
    num_media_completion: number | null;
    num_input_audio_prompt: number | null;
    num_search_results: number | null;

    // Routing
    router: string | null;           // Routing strategy used
    api_type: "completions" | "embeddings" | null;
    app_id: number | null;
    external_user: string | null;
  };
}
```

**Timing**: This endpoint may return incomplete data immediately after a request completes.
Add a short delay (100–500ms) before fetching if accurate final costs are needed.

---

### GET /api/v1/key

Checks current API key status, credit balance, and rate limits. See Authentication section above.

---

### POST /api/v1/responses (Beta)

OpenAI Responses API-compatible beta endpoint. Stateless; no server-side conversation state.

```
POST https://openrouter.ai/api/v1/responses
```

Request uses `input` field instead of `messages`. Supports reasoning, tool calling, web search.
Not for production use; subject to breaking changes.

---

### POST /api/v1/embeddings

Embeddings endpoint. OpenAI-compatible. Not covered in this document; see official docs.

---

## Streaming (SSE)

Enable with `stream: true` in the request body.

### Event Format

Each chunk is a standard SSE `data:` event with JSON:

```
data: {"id":"gen-abc","object":"chat.completion.chunk","created":1234567890,
       "model":"openai/gpt-4o","provider":"OpenAI","choices":[{"index":0,
       "delta":{"content":"Hello"},"finish_reason":null,"native_finish_reason":null}]}

data: {"id":"gen-abc","object":"chat.completion.chunk","created":1234567890,
       "model":"openai/gpt-4o","provider":"OpenAI","choices":[{"index":0,
       "delta":{"content":""},"finish_reason":"stop","native_finish_reason":"stop"}],
       "usage":{"prompt_tokens":10,"completion_tokens":5,"total_tokens":15}}

data: [DONE]
```

### Streaming-Specific Fields

- `object` is `"chat.completion.chunk"` (not `"chat.completion"`)
- `choices[].delta` contains partial content (instead of `message`)
- `usage` only present in the **final chunk** before `[DONE]`
- `provider` field present in chunks (provider name string)
- `choices[].native_finish_reason` present in chunks

### Keep-Alive Comments

OpenRouter sends SSE comments to prevent connection timeouts during processing:

```
: OPENROUTER PROCESSING
```

These are valid SSE comments per spec and MUST be ignored by the client.

### Debug First Chunk

When `debug.echo_upstream_body: true` and `stream: true`, the FIRST chunk has:
- Empty `choices` array
- `debug` field containing the upstream request body

This is for development only.

### Mid-Stream Errors

If an error occurs after streaming has started, it arrives as an SSE event (HTTP status
remains 200 since headers were already sent):

```
data: {"error":{"code":500,"message":"Provider error","metadata":{"provider_name":"OpenAI",
       "raw":"...upstream error..."}},"finish_reason":"error","choices":[{"index":0,
       "delta":{},"finish_reason":"error"}]}

data: [DONE]
```

---

## OpenRouter-Specific Request Fields (Summary)

| Field | Type | Description |
|-------|------|-------------|
| `provider` | object | Provider routing preferences (see ProviderPreferences) |
| `models` | string[] | Fallback model list; tried in order if primary fails |
| `route` | `"fallback"` | Legacy routing flag; prefer `models[]` |
| `transforms` | string[] | Prompt transforms; currently `["middle-out"]` |
| `plugins` | Plugin[] | Enable web search, file parsing, response healing |
| `reasoning` | object | Reasoning effort and summary settings |
| `top_k` | integer | Not in OpenAI API; restricts to top N tokens |
| `repetition_penalty` | number | Not in OpenAI API; scales by token probability |
| `min_p` | number | Not in OpenAI API; minimum probability threshold |
| `top_a` | number | Not in OpenAI API; dynamic top-p |
| `session_id` | string | Groups related requests for observability |
| `trace` | object | Distributed tracing fields |
| `metadata` | object | Custom key-value; special keys for tracing |
| `debug` | object | Development: echo upstream request body |
| `verbosity` | enum | Output detail: `low`, `medium`, `high`, `max` |

---

## OpenRouter-Specific Response Fields (Summary)

| Field | Location | Description |
|-------|----------|-------------|
| `model` | root | ACTUAL model used (critical when using `models[]` fallbacks) |
| `provider` | chunk root (streaming only) | Provider name that served the request |
| `choices[].finish_reason` | normalized | Always one of: `stop`, `tool_calls`, `length`, `content_filter`, `error` |
| `choices[].native_finish_reason` | per choice | Raw finish reason string from provider |
| `choices[].message.reasoning` | per message | Reasoning/thinking text from thinking models |
| `choices[].message.reasoning_details` | per message | Structured reasoning token details |

**Cost data is NOT in the completion response.** Use `GET /api/v1/generation?id=<id>`.

---

## Response Headers

Headers returned by OpenRouter on chat completion responses:

| Header | Description |
|--------|-------------|
| `openrouter-generation-id` | Generation ID (same as `id` in body); use to query `/api/v1/generation` |
| `x-request-id` | Unique HTTP request identifier for support/debugging |
| `X-RateLimit-Limit` | Rate limit ceiling (in 429 error metadata) |
| `X-RateLimit-Remaining` | Remaining requests in window (in 429 error metadata) |
| `X-RateLimit-Reset` | Reset timestamp in Unix milliseconds (in 429 error metadata) |
| `Content-Type` | `application/json` or `text/event-stream` for streaming |

Rate limit headers are returned in the `metadata` object of 429 error responses, not as
standard HTTP headers on successful responses.

---

## Error Handling

### Error Response Format

```typescript
type ErrorResponse = {
  error: {
    code: number;      // Matches HTTP status code
    message: string;
    metadata?: {
      // For 429 errors:
      "X-RateLimit-Limit"?: string;
      "X-RateLimit-Remaining"?: string;
      "X-RateLimit-Reset"?: string;    // Unix ms timestamp

      // For 403 moderation errors:
      reasons?: string[];
      flagged_input?: string;          // Max 100 chars, truncated with "..."
      provider_name?: string;
      model_slug?: string;

      // For 502 provider errors:
      provider_name?: string;
      raw?: string;                    // Original provider error
    };
  };
};
```

### HTTP Error Codes

| Code | Meaning | Notes |
|------|---------|-------|
| 400 | Bad Request | Invalid or missing params; also CORS errors |
| 401 | Unauthorized | Invalid/disabled API key; expired OAuth session |
| 402 | Payment Required | Insufficient credits; negative balance |
| 403 | Forbidden | Input flagged by moderation |
| 408 | Request Timeout | Request timed out |
| 429 | Too Many Requests | Rate limited; check metadata for reset time |
| 502 | Bad Gateway | Provider down or returned invalid response |
| 503 | Service Unavailable | No provider meets routing requirements |

### Mid-Stream Errors

When streaming and an error occurs after tokens have been sent, the HTTP status is 200 (headers
already sent). The error arrives as an SSE event with `finish_reason: "error"` in choices.
Always check for `finish_reason === "error"` in streaming responses.

### Rate Limits

- **Free model variants** (`:free` suffix): 60 requests/minute
- **Daily limits without credits**: Limited requests/day
- **Daily limits with 10+ credits purchased**: 1,000 free model requests/day
- **DDoS protection**: Cloudflare blocks requests dramatically exceeding reasonable usage
- **RPS decreases** as account balance depletes; maintain sufficient balance in production

---

## Provider Routing

The `provider` object in requests controls how OpenRouter selects the backend provider.

### Provider Slugs

Provider slugs are the short identifiers used in `provider.order`, `provider.only`, and
`provider.ignore`. Obtain them from `GET /api/v1/models/{author}/{slug}/endpoints`
(`provider_name` field in each endpoint).

Common provider slugs: `OpenAI`, `Anthropic`, `Google`, `Amazon Bedrock`, `Together`,
`Fireworks`, `Groq`, `Replicate`, `DeepInfra`, `Azure`.

### Routing Examples

```json
// Use specific providers in priority order
{
  "provider": {
    "order": ["Anthropic", "Amazon Bedrock"],
    "allow_fallbacks": false
  }
}

// Lowest cost only
{
  "provider": { "sort": "price" }
}

// High throughput, no data collection
{
  "provider": {
    "sort": "throughput",
    "data_collection": "deny"
  }
}

// Hard price cap
{
  "provider": {
    "max_price": { "prompt": 0.001, "completion": 0.002 }
  }
}

// Performance thresholds (soft, deprioritizes non-compliant providers)
{
  "provider": {
    "preferred_max_latency": { "p90": 2.0 },
    "preferred_min_throughput": { "p50": 50 }
  }
}

// Zero data retention
{
  "provider": {
    "data_collection": "deny",
    "zdr": true
  }
}

// Only fp8 quantized endpoints
{
  "provider": {
    "quantizations": ["fp8"]
  }
}
```

### BYOK (Bring Your Own Key)

Supported providers: Amazon Bedrock, Google Vertex AI, Anthropic, Azure AI Services.

Configured in account settings; applied automatically. When BYOK key hits rate limit,
falls back to OpenRouter shared credits unless "Always use this key" is set. BYOK
endpoints are always prioritized over shared endpoints regardless of `provider.order`.
OpenRouter charges a service fee (waived for first N BYOK requests/month).

---

## Proxy Considerations

This section covers what a proxy sitting between a client and OpenRouter must handle.

### Request Pass-Through

A proxy MUST pass through these OpenRouter-specific fields without modification:
- `provider` object (routing preferences)
- `models` array (fallback list)
- `transforms` array
- `plugins` array
- `reasoning` object
- `session_id`, `trace`, `metadata` (observability)
- `top_k`, `repetition_penalty`, `min_p`, `top_a` (extra sampling params)

Fields the proxy may need to rewrite:
- `model`: May need to map from internal model names to `provider/model` format
- `Authorization`: Replace client key with proxy's OpenRouter key
- `HTTP-Referer`, `X-Title`: Set to proxy identity headers

### Response Pass-Through

A proxy MUST pass through:
- The `model` field (actual model used — clients need this for billing/routing decisions)
- `native_finish_reason` (clients may need the raw provider reason)
- `usage` object (token counts)
- `openrouter-generation-id` header (clients may query generation stats independently)
- `x-request-id` header (needed for support escalation)

### Streaming Considerations

- Pass SSE comments (`: OPENROUTER PROCESSING`) through to clients or silently drop them
  (both are valid per SSE spec)
- Mid-stream errors arrive as `data:` events with HTTP 200; proxy must not treat these
  as successful completions
- The `provider` field in streaming chunks should be passed through
- `usage` only in the final chunk before `[DONE]`; proxy must not buffer entire stream
  to inject usage

### Cost / Usage Accounting

The chat completion response does NOT contain cost. To track spend:
1. Capture `openrouter-generation-id` response header (or `id` from response body)
2. After request completes, call `GET /api/v1/generation?id=<id>` for cost data
3. Allow 100–500ms before querying; data may be incomplete immediately

### Model Name Translation

Clients using the OpenAI SDK may send bare model names like `gpt-4o`. A proxy targeting
OpenRouter must translate these to OpenRouter format:
- `gpt-4o` → `openai/gpt-4o`
- `claude-3-5-sonnet-20241022` → `anthropic/claude-3-5-sonnet`
- `gemini-2.0-flash` → `google/gemini-2.0-flash-001`

### Error Code Handling

OpenRouter adds error codes not in the standard OpenAI spec:
- `402`: Insufficient credits (not in OpenAI API)
- `503`: No provider meets routing requirements (not in OpenAI API)

Proxies forwarding to downstream clients should pass these through as-is.

### Strict Tool Calls Header

When a client sends `tools` with `strict: true`, the proxy MUST forward the header:
```
structured-outputs-2025-11-13: true
```
Without this header, OpenRouter strips `strict` from tool definitions.

### Parameter Handling

OpenRouter silently ignores parameters unsupported by the target model. A proxy does NOT
need to strip unknown parameters before forwarding — this is safe by design.

---

## Key Management API

Programmatic API key management. All endpoints under `/api/v1/keys` require a
**Management API key** (different from a standard API key) in the `Authorization` header.

```
GET    /api/v1/keys           # List keys
POST   /api/v1/keys           # Create key
GET    /api/v1/keys/{id}      # Get key
PATCH  /api/v1/keys/{id}      # Update key
DELETE /api/v1/keys/{id}      # Delete key
```

---

## Quick Reference: Complete Endpoint List

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/chat/completions` | Chat completions (primary) |
| POST | `/api/v1/responses` | Responses API beta |
| POST | `/api/v1/embeddings` | Text embeddings |
| GET | `/api/v1/models` | List all models |
| GET | `/api/v1/models/{author}/{slug}/endpoints` | Model provider endpoints + metrics |
| GET | `/api/v1/generation` | Generation stats + cost by ID |
| GET | `/api/v1/key` | Current key status + credit balance |
| GET/POST/PATCH/DELETE | `/api/v1/keys/*` | Key management (Management API key required) |
| GET | `/api/v1/auth/key` | Auth key info (alias for `/api/v1/key`) |

---

## Sources

- [OpenRouter API Reference Overview](https://openrouter.ai/docs/api/reference/overview)
- [Chat Completions Endpoint](https://openrouter.ai/docs/api/api-reference/chat/send-chat-completion-request)
- [Provider Routing Guide](https://openrouter.ai/docs/guides/routing/provider-selection)
- [Model Fallbacks](https://openrouter.ai/docs/guides/routing/model-fallbacks)
- [API Parameters](https://openrouter.ai/docs/api/reference/parameters)
- [Streaming Reference](https://openrouter.ai/docs/api/reference/streaming)
- [Models Endpoint](https://openrouter.ai/docs/api/api-reference/models/get-models)
- [Endpoints Endpoint](https://openrouter.ai/docs/api/api-reference/endpoints/list-endpoints)
- [Generation Endpoint](https://openrouter.ai/docs/api/api-reference/generations/get-generation)
- [Rate Limits](https://openrouter.ai/docs/api/reference/limits)
- [Error Handling](https://openrouter.ai/docs/api/reference/errors-and-debugging)
- [Authentication](https://openrouter.ai/docs/api/reference/authentication)
- [Quickstart](https://openrouter.ai/docs/quickstart)
- [Model Variants: Nitro](https://openrouter.ai/docs/guides/routing/model-variants/nitro)
- [Model Variants: Free](https://openrouter.ai/docs/guides/routing/model-variants/free)
- [Model Variants: Extended](https://openrouter.ai/docs/guides/routing/model-variants/extended)
- [Model Variants: Thinking](https://openrouter.ai/docs/guides/routing/model-variants/thinking)
- [Model Variants: Online](https://openrouter.ai/docs/guides/routing/model-variants/online)
- [Model Variants: Exacto](https://openrouter.ai/docs/guides/routing/model-variants/exacto)
- [Plugins Overview](https://openrouter.ai/docs/guides/features/plugins/overview)
- [BYOK](https://openrouter.ai/docs/guides/overview/auth/byok)
- [Responses API Beta](https://openrouter.ai/docs/api/reference/responses/overview)

---

## Source: context/portkey.md

# Portkey AI Gateway

> Definitive reference for evaluating Portkey as a provider-aggregate gateway.
> Sources: portkey.ai/docs, GitHub Portkey-AI/gateway, cross-product comparisons (fetched 2026-02-20).

---

## What it is / Deployment Options

Portkey is a production AI Gateway and LLMOps control plane that sits between your application and LLM providers. It provides routing, reliability, security, observability, and governance as a transparent proxy.

**Coverage:** 1,600+ models across 45+ providers (OpenAI, Anthropic, Google, Bedrock, Azure, Groq, Mistral, Cohere, Ollama, etc.)

**Three deployment tiers:**

| Mode | Description | Managed by |
|------|-------------|-----------|
| **OSS Gateway (self-hosted)** | Node.js/edge proxy; routing + fallbacks + LB + basic guardrails; no SaaS features | You |
| **Portkey-Managed SaaS** | Full platform on Portkey infra, isolated cluster per org | Portkey |
| **Hybrid (Enterprise)** | Gateway + data plane in your VPC; control plane by Portkey | Split |
| **Fully Airgapped (Enterprise)** | All components inside your network; zero external data | You |

**OSS install:**
```bash
docker pull portkeyai/gateway
docker run -p 8787:8787 portkeyai/gateway
# or: npx @portkey-ai/gateway
```

**Managed SaaS base URL:** `https://api.portkey.ai/v1`

---

## Authentication (x-portkey-* Headers)

### Core Headers

| Header | Purpose |
|--------|---------|
| `x-portkey-api-key` | Portkey account key — required for managed SaaS |
| `x-portkey-provider` | Direct provider name (`openai`, `anthropic`, etc.) |
| `x-portkey-virtual-key` | Virtual key slug (legacy; now `@provider-slug` in Model Catalog) |
| `x-portkey-config` | Config ID or inline JSON config object |

### Observability Headers

| Header | Purpose |
|--------|---------|
| `x-portkey-trace-id` | Custom trace ID |
| `x-portkey-span-id` | Span ID for distributed tracing |
| `x-portkey-parent-span-id` | Parent span for nested traces |
| `x-portkey-span-name` | Human-readable span label |
| `x-portkey-metadata` | JSON key-value pairs attached to every log entry |

### Cache Headers

| Header | Purpose |
|--------|---------|
| `x-portkey-cache-namespace` | Custom partition key (per-user caching) |
| `x-portkey-cache-force-refresh` | Bypass cache for this request |
| `x-portkey-debug` | Must be `true` for caching to work |

### OpenAI SDK Drop-In

```python
from openai import OpenAI
from portkey_ai import PORTKEY_GATEWAY_URL, createHeaders

client = OpenAI(
    api_key="OPENAI_API_KEY",
    base_url=PORTKEY_GATEWAY_URL,
    default_headers=createHeaders(
        api_key="PORTKEY_API_KEY",
        provider="openai"
    )
)
```

W3C `traceparent`/`baggage` OTel headers are also accepted; `x-portkey-*` headers take precedence.

---

## Config-Based Routing

The **Config Object** is the central abstraction. It is JSON and can be:
1. Saved in Portkey UI → referenced by ID in `x-portkey-config: config_id`
2. Passed inline as JSON in `x-portkey-config: {"strategy":...}`
3. Set as default on a Virtual Key / AI Provider

### Config Schema

```json
{
  "strategy": {
    "mode": "single" | "fallback" | "loadbalance" | "conditional",
    "on_status_codes": [429, 500, 503],
    "conditions": [...],
    "default": "target_name"
  },
  "targets": [
    {
      "name": "target_name",
      "provider": "@provider-slug",
      "weight": 0.7,
      "override_params": { "model": "gpt-4o", "temperature": 0.7 },
      "cache": { "mode": "semantic", "max_age": 3600 },
      "retry": { "attempts": 3, "on_status_codes": [429] },
      "request_timeout": 30000,
      "input_guardrails": ["guardrail_id"],
      "output_guardrails": ["guardrail_id"],
      "forward_headers": ["x-custom-header"]
    }
  ],
  "cache": { "mode": "simple", "max_age": 604800 },
  "retry": { "attempts": 3, "use_retry_after_headers": true },
  "request_timeout": 60000,
  "cb_config": {
    "failure_threshold": 5,
    "cooldown_interval": 60000,
    "failure_status_codes": [500, 503]
  }
}
```

Targets are **recursive** — each target can itself be a full config, enabling nested strategies.

---

## Fallbacks + Load Balancing

### Fallback (Sequential Failover)

```json
{
  "strategy": {
    "mode": "fallback",
    "on_status_codes": [429, 500, 503]
  },
  "targets": [
    { "provider": "@openai-primary" },
    { "provider": "@anthropic-backup", "override_params": { "model": "claude-3-5-sonnet" } },
    { "provider": "@azure-tertiary" }
  ]
}
```

### Load Balancing (Weighted Distribution)

```json
{
  "strategy": { "mode": "loadbalance" },
  "targets": [
    { "provider": "@openai-prod", "weight": 0.7 },
    { "provider": "@openai-backup", "weight": 0.2 },
    { "provider": "@azure-openai", "weight": 0.1 }
  ]
}
```

### Nested: Load Balance with Embedded Fallback

```json
{
  "strategy": { "mode": "loadbalance" },
  "targets": [
    { "provider": "@anthropic", "weight": 0.5 },
    {
      "strategy": { "mode": "fallback" },
      "targets": [
        { "provider": "@openai", "override_params": { "model": "gpt-4o" } },
        { "provider": "@azure-openai", "override_params": { "model": "gpt-4o" } }
      ],
      "weight": 0.5
    }
  ]
}
```

### Conditional Routing (Metadata/Params-Based)

```json
{
  "strategy": {
    "mode": "conditional",
    "conditions": [
      {
        "query": { "metadata.user_plan": { "$eq": "enterprise" } },
        "then": "premium-target"
      },
      {
        "query": {
          "$and": [
            { "metadata.user_type": { "$eq": "pro" } },
            { "params.temperature": { "$gte": 0.7 } }
          ]
        },
        "then": "creative-target"
      }
    ],
    "default": "standard-target"
  },
  "targets": [
    { "name": "premium-target", "provider": "@anthropic", "override_params": { "model": "claude-3-5-opus" } },
    { "name": "creative-target", "provider": "@openai", "override_params": { "model": "gpt-4o" } },
    { "name": "standard-target", "provider": "@openai", "override_params": { "model": "gpt-4o-mini" } }
  ]
}
```

**Condition operators:** `$eq`, `$ne`, `$in`, `$nin`, `$regex`, `$gt`, `$gte`, `$lt`, `$lte`, `$and`, `$or`

**Query paths:** `metadata.<key>`, `params.<key>` (model/temperature/etc.), `url.pathname`

### Retry

```json
{
  "retry": {
    "attempts": 5,
    "on_status_codes": [429, 500],
    "use_retry_after_headers": true
  }
}
```

Exponential backoff applied automatically. Max 5 attempts.

### Circuit Breaker

```json
{
  "cb_config": {
    "failure_threshold": 5,
    "failure_threshold_percentage": 50,
    "cooldown_interval": 60000,
    "failure_status_codes": [500, 503],
    "minimum_requests": 10
  }
}
```

Minimum cooldown: 30 seconds. When open, all requests to that target are blocked until cooldown passes.

---

## Caching

Two modes:

| Mode | Matching | Plans | Notes |
|------|---------|-------|-------|
| `simple` | Exact content match | All | Works for all models incl. image gen |
| `semantic` | Cosine similarity on embeddings | Pro/Enterprise | ≤8,191 tokens, ≤4 messages |

```json
{ "cache": { "mode": "semantic", "max_age": 3600 } }
```

**TTL bounds:** 60s min, 90 days max (7,776,000s), default 7 days. Free plan: 1-day cap.

**Per-user cache namespace:**

```python
portkey.chat.completions.create(..., cache_namespace="user-123")
```
```bash
curl ... -H "x-portkey-cache-namespace: user-123"
```

Cache is partitioned solely by this string — all other headers ignored.

**Force refresh per-request:**
```bash
curl ... -H "x-portkey-cache-force-refresh: true"
```

**Per-target override:** Target-level cache config takes precedence over top-level.

---

## Guardrails

Run before (input hook) and/or after (output hook) each LLM call.

### Native Guardrails (All Plans)

| Check | Hook |
|-------|------|
| Regex Match | input/output |
| Word/Sentence/Character Count | input/output |
| JSON Schema validation | output |
| JSON Keys presence | output |
| Contains (word list) | output |
| Valid URLs | output |
| Contains Code (SQL, Python, etc.) | output |
| Ends With | input/output |
| Model Whitelist | input |
| JWT Token Validator | input |
| Webhook (Bring Your Own) | input/output |

### LLM-Based Guardrails (Pro/Enterprise)

| Check | Hook |
|-------|------|
| Moderate Content | input |
| Check Language | input |
| Detect PII | input/output |
| Detect Gibberish | input/output |

### Partner Guardrail Integrations (13)

Aporia, Patronus AI, Pillar, Pangea, Palo Alto Prisma AIRS, AWS Bedrock Guardrails, Azure Content Safety, Acuvity, Javelin, Lasso Security, Mistral Moderation, Prompt Security, Qualifire.

### Bring Your Own Guardrails (Webhook)

```json
{
  "type": "webhook",
  "webhookURL": "https://your-service.com/check",
  "headers": { "Authorization": "Bearer token" }
}
```

Portkey POSTs data to your URL. Return:
```json
{ "verdict": true, "data": { "transformedData": "..." } }
```
Timeout: 3s hardcoded. Timeout = PASS (non-blocking).

### Guardrail in Config Target

```json
{
  "provider": "@openai-prod",
  "input_guardrails": ["pg-pii-detector-abc123"],
  "output_guardrails": ["pg-fact-checker-xyz789"]
}
```

---

## Observability

### What Every Log Captures

- Timestamp, user, application ID
- Full prompt + response content
- Provider, model, routing decision taken
- Latency (TTFT + total), token counts, cost
- Cache outcome (Hit / Miss / Semantic Hit / Refreshed / Disabled)
- Guardrail violations
- Retry attempts and fallback activations
- Custom metadata and tags

**Log retention:** Dev: 3 days | Pro: 30 days | Enterprise: custom.

### Tracing

Hierarchical spans for multi-step agent workflows. Each span: inputs, outputs, model, latency, token usage.

Trace headers:
```
x-portkey-trace-id: my-trace-001
x-portkey-span-id: span-001
x-portkey-parent-span-id: parent-span-001
x-portkey-span-name: "call-llm-for-summarization"
```

### OpenTelemetry

Portkey exposes an OTLP HTTP endpoint:
```
POST https://api.portkey.ai/v1/otel
x-portkey-api-key: YOUR_KEY
```

W3C `traceparent`/`baggage` accepted. Existing OTel instrumentation sends directly to Portkey; trace/span IDs auto-correlated with LLM logs.

### Metrics (40+)

Request count, error rate, latency (p50/p95/p99), cost per request/token, cache hit rate, guardrail violation rate, fallback rate, token usage by model/provider/workspace.

### Feedback API

```python
portkey.feedback.create(
    trace_id="xxx",
    value=1,     # 1 = thumbs up, -1 = thumbs down
    weight=1
)
```

### Custom Metadata

```python
portkey.chat.completions.create(
    ...,
    metadata={"user_id": "123", "environment": "prod", "feature": "search"}
)
```

---

## Virtual Keys + Budget Management

### Model Catalog (Current System, replaces Virtual Keys)

- Provider credentials stored AES-256 encrypted in Portkey vault
- Never exposed in code — reference by slug: `@my-openai-prod`
- Org-level credential creation, provisioned to workspaces
- `@provider_slug/model_name` syntax: `@openai-prod/gpt-4o`

### Budget and Rate Limits (Enterprise)

- USD budget cap per key — auto-expires when limit reached
- Per-workspace and per-team spend caps
- Rate limits: requests per minute/hour/day
- Granular budget tracking by workspace, team, user

### Access Control

- RBAC: Owner, Admin, Member, Viewer roles per workspace
- Key scoping: org-level API keys with specific permission scopes
- Model allowlists: restrict which models each workspace can use

---

## Prompt Library

- Centralized storage (3 templates free, unlimited Pro+)
- Version control: every edit = new version
- Labels: `staging`, `production`, `platform-team`, etc.
- Publish makes a version "production" (default for callers)
- A/B testing via label-based traffic split
- Template variables: `{{variable_name}}` syntax
- Prompt partials: reusable fragments
- Comparison view: side-by-side version diff
- Multimodal playground (text, vision, audio)

**Prompt API call:**
```python
portkey.prompts.completions.create(
    prompt_id="pp-my-prompt-abc",
    variables={"user_name": "Alice", "topic": "ML"}
)
```

---

## Unique Features

1. **Recursive nested strategy configs** — load balance inside fallback inside conditional routing, arbitrarily deep
2. **Model Catalog / `@provider/model` syntax** — unified, governed model references across the org
3. **Semantic caching** — vector-similarity matching; reuses responses to semantically equivalent queries
4. **50+ built-in guardrails** with 13 partner integrations in a unified framework
5. **MCP Gateway** — act as MCP client; govern, auth, and observe all tool calls from agents
6. **Feedback API** — link user thumbs-up/down signals to specific LLM traces
7. **Circuit breaker** — `cb_config` with failure thresholds and configurable cooldown
8. **Cache namespace** — per-user/per-session cache partitioning without custom logic
9. **JWT Validator guardrail** — JWKS-based token validation at gateway level
10. **OTLP endpoint** — ingest external OTel spans; correlate infra traces with LLM calls
11. **`use_retry_after_headers`** — automatically honor provider Retry-After headers
12. **Airgapped enterprise deployment** — zero data leaves your network
13. **Prompt versioning + A/B testing** — full prompt lifecycle management

---

## Key Differences from OpenRouter / LiteLLM / Vercel

| Dimension | Portkey | OpenRouter | LiteLLM | Vercel AI Gateway |
|-----------|---------|-----------|---------|------------------|
| Deployment | SaaS + OSS + airgapped | SaaS only | OSS only | SaaS only |
| Pricing model | Flat monthly | 5% spend markup | Free (self-hosted) | Usage-based |
| Guardrails | 50+ native + 13 partners | None | Basic | None |
| Semantic cache | Yes | No | No | No |
| Prompt management | Full versioning/A/B | None | None | None |
| Conditional routing | Metadata + params | Model-based only | Limited | No |
| Circuit breaker | Yes | No | Limited | No |
| RBAC + SSO | Yes (Enterprise) | No | No | No |
| OTel ingestion | Yes (OTLP endpoint) | No | Via callbacks | No |
| MCP Gateway | Yes | No | No | No |
| Feedback API | Yes | No | No | No |
| Airgapped | Yes (Enterprise) | No | Yes | No |
| Per-user cache namespace | Yes | No | No | No |
| Budget limits per key | Yes | No | No | No |
| Nested strategy configs | Yes (recursive) | No | No | No |

---

## What thegent Should Steal

**Immediately actionable (copy the pattern):**

1. **Config Object schema** — adopt `strategy` + `targets` + `cache` + `retry` + `cb_config` JSON format as thegent's `RouteConfig`; make targets recursive so strategies compose
2. **Conditional routing operators** — `$eq/$ne/$in/$nin/$regex/$gt/$gte/$lt/$lte/$and/$or` on metadata and request params
3. **Circuit breaker pattern** — `failure_threshold`, `cooldown_interval`, `failure_status_codes` fields; state tracked per-target at router level
4. **`use_retry_after_headers`** — check for provider `Retry-After` header before scheduling retry
5. **Cache namespace header** — `x-thegent-cache-namespace: user-123` for per-user cache partitioning
6. **Cache TTL in config** — `max_age` field in cache config (seconds); min/max/org-level caps
7. **`cache_force_refresh` header** — per-request cache bypass without changing config
8. **Webhook guardrail interface** — `verdict` + optional `transformedData` pattern; 3s timeout = PASS
9. **`input_guardrails`/`output_guardrails` in target config** — attach guardrail IDs per target, not just globally
10. **Span header set** — `x-thegent-trace-id`, `x-thegent-span-id`, `x-thegent-parent-span-id`, `x-thegent-span-name`

**Medium-term (architectural investment):**

11. **OTLP endpoint** — `POST /v1/otel` to ingest external OTel traces and correlate with LLM call logs
12. **Feedback API** — `POST /v1/feedback` with `trace_id` + `value` to attach evaluation signals to logs
13. **Model Catalog / `@provider/model` syntax** — unified provider slug system for governed model references
14. **Budget limits per key** — USD cap on virtual keys with auto-expiry enforcement
15. **Per-target `override_params`** — allow per-target model/hyperparameter override in route config

**Skip (out of scope for CLIProxy):**

- Prompt Studio GUI — CLI-first; use YAML/JSON config files
- SCIM provisioning — separate concern
- 13-partner guardrail marketplace — implement the webhook interface; let partners be plugins
- FinOps GUI dashboards — expose raw metrics; let consumers build visualizations

---

## Source: context/process-compose.md

# Process Compose: Service Orchestration Reference

> Definitive reference for process-compose as used in thegent. Process Compose is a YAML-based process orchestrator (alternative to goreman/overmind) with built-in TUI, health checks, process dependencies, and REST API.
>
> Last updated: 2026-02-20. Source: thegent/process-compose.yaml configuration and official process-compose documentation.

---

## What is Process Compose

Process Compose is a lightweight, YAML-driven process orchestrator written in Go. It manages the lifecycle of multiple processes as a unified system, with native support for:

- **Process definitions** - Command, arguments, working directory
- **Process dependencies** - Explicit ordering: "B waits for A to be ready"
- **Health checks** - HTTP probes, exec probes, port availability
- **TUI monitoring** - Real-time terminal UI showing process status
- **REST API** - Programmatic control (start/stop/status)
- **Log aggregation** - Unified logs with per-process filtering
- **Environment management** - Shared environment, per-process overrides

**Why Process Compose for thegent**: Replaces manual shell scripts and systemd/supervisor for local dev. Simpler than Docker Compose (no containers), more feature-rich than foreman (Go instead of Ruby, better error handling).

---

## Installation

```bash
# macOS (Homebrew)
brew install process-compose

# Linux / Download
curl -L https://github.com/F1bonacc1/process-compose/releases/download/v[VERSION]/process-compose_[VERSION]_linux_amd64.tar.gz \
  | tar xz
```

**Verify installation:**
```bash
process-compose --version
```

---

## Core Concepts

### Processes

A process is a unit of work: an executable command with configuration.

```yaml
processes:
  server:
    command: python3
    args:
      - -m
      - thegent.main
      - serve
    working_dir: .
```

### Process Lifecycle

```
stopped → starting → running → (health checks) → healthy/unhealthy → stopping → stopped
```

### Readiness Probes

Process Compose waits for readiness before considering a process "ready" for dependents.

**HTTP probe (most common):**
```yaml
readiness_probe:
  http_get:
    host: 127.0.0.1
    port: 8000
    path: /health
  initial_delay_seconds: 2
  period_seconds: 10
  timeout_seconds: 5
  success_threshold: 1
  failure_threshold: 3
```

Process is "ready" when HTTP GET `/health` returns 2xx status.

**Exec probe (run a command):**
```yaml
readiness_probe:
  exec:
    command: sh
    args: ["-c", "test -f /tmp/ready.flag"]
  initial_delay_seconds: 1
  period_seconds: 5
```

Process is "ready" when command exits 0.

**TCP port probe:**
```yaml
readiness_probe:
  tcp_socket:
    host: 127.0.0.1
    port: 5432
  initial_delay_seconds: 2
```

Process is "ready" when port accepts connection.

### Restart Policies

Define behavior when a process exits.

```yaml
availability:
  restart: on_failure      # Restart if exit code != 0
  max_restarts: 10         # Max restart attempts
  backoff_seconds: 1       # Wait before restart
```

**Restart modes:**
- `no` - Never restart
- `always` - Always restart, even if exit code 0
- `on_failure` - Restart only if non-zero exit code
- `on_failure_with_backoff` - Exponential backoff on restart

### Process Dependencies

Control startup order; Process Compose waits for dependencies to be "ready".

```yaml
processes:
  db:
    command: postgres
    readiness_probe: ...

  api:
    command: node app.js
    depends_on:
      db:
        condition: process_healthy  # or process_started
    readiness_probe: ...
```

Process Compose guarantees: DB passes health check before API starts.

---

## thegent Configuration (process-compose.yaml)

### Overview Structure

```yaml
version: "0.5"
log_location: .process-compose/process-compose.log
log_level: info

environment:
  - PYTHONUNBUFFERED=1
  - PYTHONPATH=src
  - THGENT_MCP_HOST=127.0.0.1
  - THGENT_MCP_PORT=3847
  - ... (service-specific env vars)

processes:
  server:
    # MCP server (daemon)
  control-plane:
    # Control plane (governance engine)
  serena:
    # Optional: Serena integration (code search/navigation)
```

### thegent Processes

#### 1. server (MCP Server)

Core daemon: LLM routing, tool execution, session management.

```yaml
server:
  command: python3
  args:
    - -m
    - thegent.main
    - serve
    - --host=127.0.0.1
    - --port=3847
  working_dir: .
  availability:
    restart: on_failure
    max_restarts: 10
    backoff_seconds: 1
  readiness_probe:
    http_get:
      host: 127.0.0.1
      port: 3847
      path: /health
    initial_delay_seconds: 2
    period_seconds: 10
    timeout_seconds: 5
    success_threshold: 1
    failure_threshold: 3
  log_location: .process-compose/logs/server.log
  log_length: 5000
```

**Readiness check**: HTTP GET `/health` returns 200 ↔ MCP server ready for RPC calls.

**Typical lifecycle**:
1. Process starts
2. Python imports thegent modules (may take 2-3s on first run)
3. Server binds to 127.0.0.1:3847
4. Health check HTTP GET succeeds
5. Process marked "ready"
6. Control-plane can now connect

**Logs**: `.process-compose/logs/server.log` (last 5000 lines)

#### 2. control-plane (Governance Engine)

Separate daemon managing policies, hooks, approvals.

```yaml
control-plane:
  command: python3
  args:
    - -m
    - thegent.main
    - control-plane
    - serve
    - --port=3849
  working_dir: .
  availability:
    restart: on_failure
    max_restarts: 10
    backoff_seconds: 1
  readiness_probe:
    http_get:
      host: 127.0.0.1
      port: 3849
      path: /health
    initial_delay_seconds: 2
    period_seconds: 10
    timeout_seconds: 5
    success_threshold: 1
    failure_threshold: 3
  log_location: .process-compose/logs/control-plane.log
```

**Readiness check**: Similar to server; HTTP `/health` on port 3849.

**Design note**: Separate from server for isolation and independent scaling (future).

#### 3. serena (Optional: Code Search)

Serena provides code search/navigation via MCP. Disabled by default.

```yaml
serena:
  command: sh
  args:
    - -c
    - |
      if [ "${THGENT_MCP_MOUNT_SERENA:-0}" = "1" ]; then
        exec uvx --from 'git+https://github.com/oraios/serena' \
          serena start-mcp-server --transport sse --port 3848 \
          --context ide --project-from-cwd --open-web-dashboard false
      else
        exec sleep infinity  # Prevents restart loops when disabled
      fi
  availability:
    restart: on_failure
    max_restarts: 5
    backoff_seconds: 2
  readiness_probe:
    exec:
      command: sh
      args: ["-c", "test \"${THGENT_MCP_MOUNT_SERENA:-0}\" != 1 || nc -z 127.0.0.1 3848"]
    initial_delay_seconds: 5
    period_seconds: 10
  log_location: .process-compose/logs/serena.log
```

**Design note**: Serena is optional; `if [ ... ] = "1"` gate allows disabling without restart loops.

**When disabled** (`THGENT_MCP_MOUNT_SERENA=0`): Process runs `sleep infinity` (does nothing, doesn't restart).

**When enabled** (`THGENT_MCP_MOUNT_SERENA=1`): Starts MCP server on port 3848.

---

## Environment Variables

Global environment vars (inherited by all processes) configured at top level:

```yaml
environment:
  - PYTHONUNBUFFERED=1           # Disable Python output buffering
  - PYTHONPATH=src               # Add src/ to Python import path
  - THGENT_MCP_HOST=127.0.0.1    # MCP server bind address
  - THGENT_MCP_PORT=3847         # MCP server port
  - THGENT_CLIPROXY_PORT=8317    # CLI proxy (for HTTP requests)
  - THGENT_CLIPROXY_ADAPTER=1    # Enable adapter mode
  - THGENT_CONTROL_PLANE_PORT=3849
  - THGENT_CONTROL_PLANE_URL=http://127.0.0.1:3849
  - THGENT_BUNDLE_PROXY=1        # MCP server spawns CLI proxy internally
  - THGENT_RELOAD=${THGENT_RELOAD:-0}  # Hot reload (0=disabled)
  - THGENT_MCP_MOUNT_PLAYWRIGHT=0      # Disable Playwright MCP tool
  - THGENT_MCP_MOUNT_SERENA=0          # Disable Serena integration
  - THGENT_MCP_MOUNT_OCTOCODE=0        # Disable Octocode integration
  - THGENT_SERENA_URL=http://127.0.0.1:3848/mcp
```

**Override at runtime:**
```bash
THGENT_MCP_MOUNT_SERENA=1 process-compose up
```

---

## Common Commands

### Start All Processes

```bash
process-compose up
```

**Output:**
```
✓ server        | Started, waiting for readiness...
✓ control-plane | Started, waiting for readiness...
✓ serena        | Sleeping (disabled)

All processes ready
Ctrl+C to stop
```

Press Ctrl+C to stop all processes.

### Stop All Processes

```bash
process-compose down
```

### View Logs

**All processes:**
```bash
process-compose logs
```

**Specific process:**
```bash
process-compose logs server
```

**Follow (tail) mode:**
```bash
process-compose logs --follow server
```

**Filter by time:**
```bash
process-compose logs --since 5m server
```

### Check Process Status

```bash
process-compose ps
```

**Output:**
```
NAME           PID     STATUS      DURATION
server         1234    running     12:34
control-plane  1235    running     12:30
serena         1236    sleeping    12:34
```

### Restart a Process

```bash
process-compose restart server
```

### Kill a Process (Manual Restart)

```bash
process-compose kill server
```

Process Compose will restart per `availability.restart` policy.

### Reload Configuration

```bash
process-compose reload
```

Applies changes to `process-compose.yaml` without full shutdown (requires `THGENT_RELOAD=1`).

---

## REST API

Process Compose exposes a REST API (by default on port 5000) for programmatic control.

### Endpoints

#### GET /processes

List all processes with status.

```bash
curl http://localhost:5000/processes
```

**Response:**
```json
{
  "processes": [
    {
      "name": "server",
      "pid": 1234,
      "status": "running",
      "uptime_seconds": 754,
      "restart_count": 0
    },
    {
      "name": "control-plane",
      "pid": 1235,
      "status": "running",
      "uptime_seconds": 730,
      "restart_count": 0
    }
  ]
}
```

#### POST /processes/{name}/stop

Stop a process by name.

```bash
curl -X POST http://localhost:5000/processes/server/stop
```

#### POST /processes/{name}/start

Start a stopped process.

```bash
curl -X POST http://localhost:5000/processes/server/start
```

#### POST /processes/{name}/restart

Restart a process.

```bash
curl -X POST http://localhost:5000/processes/server/restart
```

#### GET /processes/{name}/logs

Fetch logs for a process.

```bash
curl "http://localhost:5000/processes/server/logs?lines=100"
```

**Query params:**
- `lines=N` - Last N lines
- `follow=true` - Stream logs (EventStream)

### Example: Health Check Integration

```bash
# Check if MCP server is healthy
curl -f http://localhost:5000/processes/server/logs?lines=1 && \
  echo "Server is healthy" || \
  echo "Server is unhealthy"
```

---

## TUI Interface

When running `process-compose up`, a terminal UI appears.

**Features:**

- **Process list pane** - Shows all processes, status, PID, uptime
- **Log pane** - Real-time logs for selected process
- **Navigation:**
  - Arrow keys: Select process
  - Enter: View detailed logs
  - L: View logs only
  - Ctrl+C: Shutdown all

**Keyboard shortcuts:**
| Key | Action |
|-----|--------|
| ↑/↓ | Select process |
| ← / → | Switch panes |
| L | Log view |
| S | Status view |
| R | Restart selected |
| K | Kill selected |
| Ctrl+C | Shutdown all |

---

## Health Checks: Deep Dive

### HTTP Probe Behavior

```yaml
readiness_probe:
  http_get:
    host: 127.0.0.1
    port: 8000
    path: /health
  initial_delay_seconds: 2      # Wait 2s after process start
  period_seconds: 10            # Check every 10s
  timeout_seconds: 5            # Fail if no response in 5s
  success_threshold: 1          # 1 success → "ready"
  failure_threshold: 3          # 3 failures → "unhealthy"
```

**Timeline:**
```
T=0s: Process starts
T=2s: First health check attempt
      GET http://127.0.0.1:8000/health
      ✓ Returns 200 → success_threshold--
      → ready (success_threshold = 1)

T=12s: Second health check (period = 10s)
       ✓ Returns 200 → still ready

T=25s: Third health check
       ✗ Returns 503 or timeout → failure_threshold--
       ✗ Returns 503 again → failure_threshold--
       ✗ Returns 503 again → failure_threshold = 0
       → unhealthy, trigger restart policy
```

### Exec Probe Behavior

```yaml
readiness_probe:
  exec:
    command: sh
    args: ["-c", "test -f /tmp/ready && [ $(cat /tmp/ready) = 'yes' ]"]
```

Process is "ready" when the command exits 0.

**Common patterns:**
```bash
# Check for file existence
test -f /tmp/server.ready

# Check for port listening
nc -z 127.0.0.1 8000

# Conditional based on env var
[ "${ENABLED:-0}" = "1" ]
```

### Failed Probe Handling

When a probe fails repeatedly:

```
failure_threshold = 3
Attempt 1: FAIL (failures = 1)
Attempt 2: FAIL (failures = 2)
Attempt 3: FAIL (failures = 3 → threshold reached)
  → Process marked unhealthy
  → Restart policy triggered
  → availability.restart = on_failure
  → Process killed and restarted
```

---

## Dependency Management

### Process Dependencies with Conditions

```yaml
processes:
  db:
    command: postgres
    readiness_probe: ...

  api:
    command: node app.js
    depends_on:
      db:
        condition: process_healthy
```

**Conditions:**
- `process_healthy` - Wait for readiness probe to pass
- `process_started` - Wait for process to just start (no health check)

**Typical use:**
```yaml
api:
  depends_on:
    db:
      condition: process_healthy  # DB must be ready
    cache:
      condition: process_started  # Cache can be starting
```

### Dependency Chain Behavior

```
Start order:
1. db (no deps)
2. api depends_on: db → waits for db to be healthy
3. worker depends_on: api → waits for api to be healthy

Startup sequence:
db starts → db healthy ✓
api starts → api healthy ✓
worker starts → ready

Shutdown sequence (reverse):
worker stopped
api stopped
db stopped
```

---

## Log Management

### Log Locations

```
.process-compose/process-compose.log   # Overall log
.process-compose/logs/
  ├─ server.log
  ├─ control-plane.log
  └─ serena.log
```

### Log Configuration

```yaml
log_location: .process-compose/process-compose.log
log_level: info                # debug, info, warning, error

processes:
  server:
    log_location: .process-compose/logs/server.log
    log_length: 5000           # Keep last 5000 lines
```

### Viewing Logs

**CLI:**
```bash
process-compose logs server
process-compose logs --follow server      # tail -f
process-compose logs --since 5m server    # Last 5 minutes
process-compose logs --lines 100 server   # Last 100 lines
```

**REST API:**
```bash
curl http://localhost:5000/processes/server/logs?lines=50
curl "http://localhost:5000/processes/server/logs?lines=50&follow=true"
```

---

## Practical Examples

### Example 1: Check if thegent is Ready

```bash
#!/bin/bash

# Wait for server to be healthy
timeout 30 bash -c '
  until curl -f http://127.0.0.1:3847/health 2>/dev/null; do
    echo "Waiting for server..."
    sleep 1
  done
'

if [ $? -eq 0 ]; then
  echo "thegent is ready"
else
  echo "thegent failed to start"
  exit 1
fi
```

### Example 2: Enable Serena at Runtime

```bash
# Restart with Serena enabled
THGENT_MCP_MOUNT_SERENA=1 process-compose restart serena
```

### Example 3: Monitor Process Health

```bash
#!/bin/bash

while true; do
  response=$(curl -s http://localhost:5000/processes)
  unhealthy=$(echo "$response" | jq '.processes[] | select(.status != "running")')

  if [ -n "$unhealthy" ]; then
    echo "Unhealthy processes detected:"
    echo "$unhealthy" | jq .
  fi

  sleep 30
done
```

### Example 4: Collect Logs Before Shutdown

```bash
#!/bin/bash

# Save logs before shutdown
mkdir -p logs-backup
process-compose logs server > logs-backup/server.log
process-compose logs control-plane > logs-backup/control-plane.log

# Shutdown
process-compose down
```

---

## Troubleshooting

### Process Keeps Restarting

**Symptom**: Process restarts every few seconds

**Check**: Health probe configuration

```bash
# View logs
process-compose logs server

# Check if health endpoint is responding
curl http://127.0.0.1:3847/health -v
```

**Common causes:**
- Health check endpoint not implemented
- Health check timeout too short
- Application startup takes longer than `initial_delay_seconds`

**Fix**:
```yaml
readiness_probe:
  http_get: ...
  initial_delay_seconds: 5  # Increase initial delay
  timeout_seconds: 10       # Increase timeout
  period_seconds: 15        # Space out checks
```

### Process Never Becomes "Ready"

**Symptom**: Process starts but "ready" status never achieved

**Cause**: Health check failing

```bash
# Manually test health check
curl -v http://127.0.0.1:3847/health

# View logs for errors
process-compose logs --follow server
```

**Check**:
1. Is process actually listening on the configured port?
2. Does health endpoint exist?
3. Is firewall blocking access?

### Multiple Processes Failing

**Symptom**: Multiple processes keep restarting

**Check dependency chain**:
```yaml
# If A depends_on B, but B fails:
# A will wait forever, then fail
```

**Fix**: Check logs for the first failing process.

```bash
process-compose logs control-plane
```

### Logs Are Truncated

**Symptom**: Can't see historical logs; only recent logs available

**Cause**: `log_length` limit reached; old lines deleted

**View current limit**:
```yaml
processes:
  server:
    log_length: 5000   # Keep max 5000 lines
```

**Increase if needed**:
```yaml
    log_length: 50000  # Keep more history
```

---

## Best Practices

### 1. Always Set Readiness Probes

Never omit readiness probes. Without them, Process Compose can't determine when a process is "ready," leading to race conditions.

```yaml
readiness_probe:
  http_get:
    host: 127.0.0.1
    port: 8000
    path: /health
  initial_delay_seconds: 2
```

### 2. Use Realistic Timeouts

Health check timeouts should match actual response times:

```yaml
timeout_seconds: 5        # Reasonable for local services
failure_threshold: 3      # Allow 3 transient failures
```

### 3. Version Your Configuration

Track `process-compose.yaml` in git; review changes carefully.

```bash
git diff process-compose.yaml
```

### 4. Logs Are Your Debugging Tool

Always check logs when troubleshooting:

```bash
process-compose logs --follow server
```

### 5. Use Environment Variables for Configuration

Avoid hardcoding; use env vars for extensibility:

```yaml
environment:
  - THGENT_MCP_PORT=${THGENT_MCP_PORT:-3847}
  - THGENT_LOG_LEVEL=${THGENT_LOG_LEVEL:-info}
```

### 6. Test Startup & Shutdown

Ensure graceful shutdown:

```bash
process-compose up
# ... verify services are running
process-compose down
# ... verify clean shutdown (no zombie processes)
```

---

## Integration with thegent

### Starting thegent Services

```bash
# From project root
process-compose -f process-compose.yaml up

# Or via thegent CLI (recommended)
thegent mcp up
```

### Stopping thegent Services

```bash
process-compose down

# Or via thegent CLI
thegent mcp down
```

### Enabling Optional Tools

```bash
# Enable Serena at startup
THGENT_MCP_MOUNT_SERENA=1 process-compose up

# Or restart just Serena
THGENT_MCP_MOUNT_SERENA=1 process-compose restart serena
```

### Checking Service Health

```bash
# CLI
process-compose ps

# REST API
curl http://localhost:5000/processes

# Manual health check
curl http://127.0.0.1:3847/health
curl http://127.0.0.1:3849/health
```

---

## Sources

- **Process Compose GitHub**: https://github.com/F1bonacc1/process-compose
- **Process Compose Documentation**: https://f1bonacc1.github.io/process-compose/
- **thegent process-compose.yaml**: `/thegent/process-compose.yaml`
- **thegent Service Architecture**: `AGENTS.md`, `ADR*.md`

---

*Reference valid as of 2026-02-20. Process Compose v1.8.0+*

---

## Source: context/temporalio.md

# Temporal (temporalio Python SDK) Context

> Definitive reference for building durable workflows with the Temporal Python SDK (temporalio).
> Sources: pypi.org/project/temporalio, github.com/temporalio/sdk-python/releases, docs.temporal.io (fetched 2026-02-20).
> **Version covered: temporalio 1.23.0 (2026-02-18, latest stable)**

---

## What is Temporal

**Temporal** is a durable workflow orchestration platform. It provides a fault-tolerant execution environment where:

- **Workflows** are long-running, resumable functions that survive process restarts, network failures, and server crashes
- **Activities** are individual steps of a workflow (external API calls, DB writes, etc.) that are executed with automatic retry
- **Workers** are processes that poll Temporal Server for work and execute workflows/activities
- **Temporal Server** stores workflow state, manages scheduling, and handles failure recovery

**Why Temporal over job queues?** Standard queues lose state on failure. Temporal durably persists every event and can replay workflow execution from any point. Workflows can sleep for days, wait for external signals, and span multiple services — without managing that state yourself.

**trace Use Case:** `temporalio>=1.7.0` in `pyproject.toml`. Used for long-running orchestration tasks (AI agent job coordination, multi-step pipelines, async background processing) where durable execution across restarts is required.

---

## Key Concepts

| Term | Definition |
|------|-----------|
| **Workflow** | Deterministic, durable function decorated with `@workflow.defn`; must not have side effects |
| **Activity** | Regular function with side effects (I/O, API calls) decorated with `@activity.defn` |
| **Worker** | Process hosting workflow/activity executors; polls Temporal Server for tasks |
| **Task Queue** | Named queue pairing workflows/activities to workers |
| **Workflow ID** | Business-level unique ID for a workflow instance |
| **Run ID** | Temporal-assigned unique ID for a specific workflow run |
| **Signal** | Async message sent to a running workflow to change its state |
| **Query** | Synchronous read of a running workflow's state |
| **Update** | Sync call into a running workflow that can return a value |
| **Schedule** | Cron-like trigger for workflows |
| **Namespace** | Isolation boundary (like a tenant); `default` namespace for dev |
| **Nexus** | Temporal's cross-namespace, cross-cluster workflow RPC layer |

---

## Installation

```bash
pip install temporalio
# Current stable: temporalio >= 1.7.0 (trace), 1.23.0 latest

# With OpenTelemetry
pip install "temporalio[opentelemetry]"
```

**Temporal Server for local dev:**

```bash
# Via Temporal CLI (recommended)
brew install temporal
temporal server start-dev   # Starts on localhost:7233; UI at localhost:8233

# Or Docker
docker run --network=host temporalio/auto-setup:latest
```

---

## Client

Connect to Temporal Server to start workflows, send signals, query state.

```python
import asyncio
from temporalio.client import Client

async def main():
    # Connect to local dev server
    client = await Client.connect("localhost:7233")

    # Connect to Temporal Cloud (API key auth since temporalio 1.21+)
    client = await Client.connect(
        "mynamespace.acct.tmprl.cloud:7233",
        api_key=os.getenv("TEMPORAL_API_KEY"),
        # TLS enabled automatically when API key is provided
        namespace="mynamespace.acct",
    )

    return client
```

### Starting a Workflow

```python
# Start workflow and get handle
handle = await client.start_workflow(
    MyWorkflow.run,                     # Workflow method
    args=["input_data"],               # Positional args
    id="my-workflow-id-001",           # Unique business ID
    task_queue="my-task-queue",        # Must match worker's task_queue
    execution_timeout=timedelta(hours=1),  # Max total runtime
    run_timeout=timedelta(minutes=30),     # Max single run
    retry_policy=RetryPolicy(
        maximum_attempts=3,
        backoff_coefficient=2.0,
    ),
)

# Wait for result
result = await handle.result()

# Or start and wait in one call
result = await client.execute_workflow(
    MyWorkflow.run,
    "input_data",
    id="my-workflow-id-001",
    task_queue="my-task-queue",
)
```

### Workflow Handles

```python
# Get handle for existing workflow
handle = client.get_workflow_handle("my-workflow-id-001")

# Operations on handle
result = await handle.result()          # Wait for completion
await handle.signal(MyWorkflow.my_signal, "signal_data")
value = await handle.query(MyWorkflow.my_query)
await handle.cancel()
await handle.terminate(reason="cleanup")
description = await handle.describe()   # WorkflowExecutionDescription
```

---

## Workflows

Workflows are **deterministic** functions. No I/O, no random, no time.time() — use `workflow.now()` and `asyncio.sleep()` (which maps to Temporal timers).

```python
import asyncio
from dataclasses import dataclass
from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy

@dataclass
class ProcessJobInput:
    job_id: str
    config: dict

@workflow.defn
class ProcessJobWorkflow:
    def __init__(self):
        self._status = "pending"
        self._result = None

    @workflow.run
    async def run(self, input: ProcessJobInput) -> dict:
        """Main workflow entry point."""
        self._status = "running"

        # Execute activity (with automatic retry)
        result = await workflow.execute_activity(
            validate_job,                           # Activity function
            input.job_id,
            schedule_to_close_timeout=timedelta(minutes=5),
            retry_policy=RetryPolicy(maximum_attempts=3),
        )

        # Sleep for a duration (durable — survives restarts)
        await asyncio.sleep(1)  # Temporal timer, not OS sleep

        # Execute another activity
        final_result = await workflow.execute_activity(
            process_job,
            args=[input.job_id, result],
            start_to_close_timeout=timedelta(minutes=10),
        )

        self._status = "completed"
        self._result = final_result
        return final_result

    @workflow.signal
    async def cancel_job(self) -> None:
        """Signal handler — cancel running job."""
        self._status = "cancelled"
        # Raise CancelledError to stop workflow
        raise asyncio.CancelledError("Job cancelled by signal")

    @workflow.query
    def get_status(self) -> str:
        """Query handler — return current status."""
        return self._status

    @workflow.update
    async def pause_and_resume(self, seconds: int) -> str:
        """Update handler — pause and return when done."""
        await asyncio.sleep(seconds)
        return "Resumed"
```

### Child Workflows

```python
@workflow.run
async def run(self, parent_id: str) -> str:
    # Start child workflow
    child_handle = await workflow.start_child_workflow(
        ChildWorkflow.run,
        args=["child_input"],
        id=f"{parent_id}-child",
        task_queue="child-queue",
    )
    result = await child_handle
    return result

    # Or execute synchronously
    result = await workflow.execute_child_workflow(
        ChildWorkflow.run,
        "child_input",
        id=f"{parent_id}-child",
    )
```

### Workflow Versioning

```python
@workflow.run
async def run(self, input: str) -> str:
    # Version check for safe code evolution
    version = workflow.patched("add-validation-step")
    # version is True for new executions, False for old replaying ones
    if version:
        await workflow.execute_activity(validate, input, ...)
    return await workflow.execute_activity(process, input, ...)
```

---

## Activities

Activities are **regular Python functions** (or class methods) that perform I/O and side effects.

```python
import asyncio
from temporalio import activity

@activity.defn
async def validate_job(job_id: str) -> dict:
    """Validate job exists and is runnable."""
    # I/O is fine here
    result = await database.get_job(job_id)
    if not result:
        raise ValueError(f"Job {job_id} not found")
    return {"job_id": job_id, "status": result.status}

@activity.defn
async def process_job(job_id: str, validation: dict) -> dict:
    """Process the job."""
    # Access activity context
    info = activity.info()
    activity.logger.info(f"Processing {job_id}, attempt {info.attempt}")

    # Send heartbeat for long-running activities
    activity.heartbeat(f"Processing step 1...")

    result = await do_heavy_work(job_id)

    activity.heartbeat("Processing step 2...")
    final = await finalize(result)

    return {"status": "done", "output": final}
```

**Activity timeouts:**

| Timeout | Description |
|---------|-------------|
| `schedule_to_close_timeout` | Max time from scheduling to completion (including retries) |
| `start_to_close_timeout` | Max time for a single attempt |
| `schedule_to_start_timeout` | Max wait time in queue before worker picks up |
| `heartbeat_timeout` | Max time between heartbeats; worker considered dead if exceeded |

**Heartbeats** (required for long-running activities):

```python
@activity.defn
async def long_running_activity(items: list[str]) -> list[str]:
    results = []
    for i, item in enumerate(items):
        # Heartbeat allows cancellation and reports liveness
        activity.heartbeat({"progress": i, "total": len(items)})
        result = await process_item(item)
        results.append(result)
        await asyncio.sleep(0.1)
    return results
```

### Activity Dependency Injection

Inject shared resources (DB pools, HTTP clients) via class-based activities:

```python
from dataclasses import dataclass

@dataclass
class DatabaseActivities:
    db_pool: asyncpg.Pool
    http_client: httpx.AsyncClient

    @activity.defn
    async def get_user(self, user_id: str) -> dict:
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM users WHERE id=$1", user_id)
            return dict(row)

    @activity.defn
    async def call_external_api(self, endpoint: str) -> dict:
        response = await self.http_client.get(endpoint)
        return response.json()
```

---

## Workers

Workers poll Temporal Server and execute workflows and activities.

```python
import asyncio
from temporalio.client import Client
from temporalio.worker import Worker

async def run_worker():
    client = await Client.connect("localhost:7233")

    # Inject shared dependencies
    db_pool = await asyncpg.create_pool(dsn=DATABASE_URL)
    http_client = httpx.AsyncClient()
    db_activities = DatabaseActivities(db_pool=db_pool, http_client=http_client)

    worker = Worker(
        client,
        task_queue="my-task-queue",
        workflows=[ProcessJobWorkflow],          # Register workflow classes
        activities=[
            validate_job,                        # Function-based activities
            process_job,
            db_activities.get_user,              # Instance method activities
            db_activities.call_external_api,
        ],
        # Worker options
        max_concurrent_workflow_tasks=100,
        max_concurrent_activities=50,
        max_concurrent_local_activities=50,
    )

    # Run until cancelled
    await worker.run()

if __name__ == "__main__":
    asyncio.run(run_worker())
```

### Worker + FastAPI (trace pattern)

Run Temporal worker alongside FastAPI in same process:

```python
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from temporalio.client import Client
from temporalio.worker import Worker

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue="trace-task-queue",
        workflows=[ProcessJobWorkflow],
        activities=[process_job, validate_job],
    )
    worker_task = asyncio.create_task(worker.run())

    yield {"temporal_client": client}  # Available via request.state

    # Shutdown
    worker_task.cancel()
    await asyncio.gather(worker_task, return_exceptions=True)
    await client.close()

app = FastAPI(lifespan=lifespan)

@app.post("/jobs/{job_id}/start")
async def start_job(job_id: str, request: Request):
    client: Client = request.state.temporal_client
    handle = await client.start_workflow(
        ProcessJobWorkflow.run,
        ProcessJobInput(job_id=job_id, config={}),
        id=f"job-{job_id}",
        task_queue="trace-task-queue",
    )
    return {"run_id": handle.first_execution_run_id}
```

---

## Schedules (Cron)

```python
from temporalio.client import Client, Schedule, ScheduleActionStartWorkflow, ScheduleSpec, ScheduleIntervalSpec
from datetime import timedelta

client = await Client.connect("localhost:7233")

# Create a schedule (every hour)
await client.create_schedule(
    "hourly-cleanup",
    Schedule(
        action=ScheduleActionStartWorkflow(
            CleanupWorkflow.run,
            id="cleanup-scheduled",
            task_queue="cleanup-queue",
        ),
        spec=ScheduleSpec(
            intervals=[ScheduleIntervalSpec(every=timedelta(hours=1))],
        ),
    ),
)

# Manage schedules
handle = client.get_schedule_handle("hourly-cleanup")
await handle.trigger()    # Manual trigger
await handle.pause()      # Pause
await handle.unpause()    # Resume
await handle.delete()     # Remove
```

---

## Error Handling & Retry

```python
from temporalio.common import RetryPolicy
from temporalio.exceptions import ApplicationError, ActivityError

# Custom retry policy
retry_policy = RetryPolicy(
    initial_interval=timedelta(seconds=1),
    backoff_coefficient=2.0,
    maximum_interval=timedelta(minutes=1),
    maximum_attempts=10,
    non_retryable_error_types=["ValueError", "AuthorizationError"],
)

# In workflow
result = await workflow.execute_activity(
    my_activity,
    retry_policy=retry_policy,
    schedule_to_close_timeout=timedelta(hours=1),
)

# Non-retryable error from activity
@activity.defn
async def my_activity(data: str) -> str:
    if not is_valid(data):
        # This error won't be retried (matching non_retryable_error_types)
        raise ApplicationError("Invalid data format", non_retryable=True)
    return process(data)
```

---

## 2026 Features (temporalio 1.23.0, 2026-02-20)

| Feature | Version Added | Status |
|---------|--------------|--------|
| Experimental standalone activity support | 1.23.0 | Experimental |
| OpenTelemetry v2 integration | 1.23.0 | Stable |
| Payload limit validation from server | 1.23.0 | Stable |
| Deployment-based Worker Versioning GA | 1.22.0 | GA |
| Worker Heartbeating (Public Preview) | 1.20.0 | Public Preview |
| TLS auto-enabled with API key | 1.21.0 | Stable |
| Python 3.9 support removed | 1.19.0 | Breaking |
| Nexus cross-cluster RPC | 1.x | Experimental |

---

## thegent / trace Integration

- **trace**: `temporalio>=1.7.0` in `pyproject.toml`; used for background job orchestration
- **Task queue**: `"trace-task-queue"` (verify in trace/src)
- **Temporal Server**: Local dev via `temporal server start-dev`; prod via Temporal Cloud or self-hosted
- **Pattern**: FastAPI lifespan starts/stops worker; route handlers dispatch workflows via client

---

## Known Issues / Gotchas

1. **Workflows must be deterministic**: No `random`, `datetime.now()`, `os.environ`, or direct I/O. Use `workflow.now()` for time, `workflow.execute_activity()` for I/O.
2. **Sandbox importing**: Modules imported after workflows load produce warnings (1.19+). Import before loading workflows or configure `ImportPolicy`.
3. **Heartbeat required**: Activities running > `heartbeat_timeout` without heartbeating are considered dead and rescheduled. Always heartbeat in loops.
4. **Worker versioning**: Changing workflow code for running instances requires `workflow.patched()` guards to handle both old and new codepaths during replay.
5. **Dataclass parameters**: Use dataclasses (not plain dicts) for workflow/activity inputs — Temporal serializes them as JSON via `dataclasses.asdict()`.
6. **Python 3.9 removed**: Since 1.19.0, minimum Python is 3.10.

---

## Sources & References

- **GitHub**: https://github.com/temporalio/sdk-python (fetched 2026-02-20)
- **Releases**: https://github.com/temporalio/sdk-python/releases (fetched 2026-02-20)
- **PyPI**: https://pypi.org/project/temporalio/ (fetched 2026-02-20)
- **Samples**: https://github.com/temporalio/samples-python (fetched 2026-02-20)
- **Temporal Docs**: https://docs.temporal.io (fetched 2026-02-20)
- **Last Verified**: 2026-02-20

---

## Quick Reference

| Item | Value |
|------|-------|
| Package | `temporalio>=1.7.0` |
| Latest version | `1.23.0` (2026-02-18) |
| Default server port | `localhost:7233` |
| Temporal UI port | `localhost:8233` (dev server) |
| Dev server | `temporal server start-dev` |
| Min Python | 3.10 (since 1.19.0) |

### Decorator Cheat Sheet

```python
@workflow.defn         # Mark class as workflow
@workflow.run          # Entry point (exactly one per workflow class)
@workflow.signal       # Async signal handler
@workflow.query        # Sync query handler (must be synchronous)
@workflow.update       # Sync or async update handler (can return value)
@activity.defn         # Mark function/method as activity
```

### Client Quick Patterns

```python
# Connect
client = await Client.connect("localhost:7233")

# Start workflow
handle = await client.start_workflow(MyWf.run, arg, id="id", task_queue="queue")

# Start and wait
result = await client.execute_workflow(MyWf.run, arg, id="id", task_queue="queue")

# Get existing handle
handle = client.get_workflow_handle("workflow-id")

# Signal / Query
await handle.signal(MyWf.my_signal, "data")
status = await handle.query(MyWf.get_status)
result = await handle.update(MyWf.pause_and_resume, 5)
```

---

## Source: context/trpc.md

# tRPC Context

> Definitive reference for tRPC v10 — end-to-end typesafe TypeScript APIs without code generation.
> Sources: trpc.io/docs/v10, github.com/trpc/trpc (fetched 2026-02-20).
> **Version covered: tRPC v10.45.2 (trace project version)**

---

## What is tRPC

**tRPC** lets you build and consume fully typesafe APIs without schemas or code generation. You define procedures on the server; the TypeScript client gets full autocompletion for inputs, outputs, and errors — enforced at build time.

Key properties:
- **No code generation**: Types flow from server to client via TypeScript inference
- **No schema language**: Define inputs with Zod; types are inferred
- **Procedure types**: `query` (read), `mutation` (write), `subscription` (streaming)
- **Middleware**: Auth, logging, rate limiting in a composable pipeline
- **React integration**: `@trpc/react-query` wraps `@tanstack/react-query` with tRPC types
- **Framework adapters**: Express, Next.js (App/Pages Router), Fastify, Bun

**trace Use Case:** `@trpc/client@^10.45.2`, `@trpc/react-query@^10.45.2`, `@trpc/server@^10.45.2` in trace web app. Used for type-safe API calls between the React frontend and backend.

**Note**: tRPC v11 exists (announced Jan 2025) but trace uses v10. This doc covers v10.

---

## Key Concepts

| Term | Definition |
|------|-----------|
| **Router** | Container for procedures; routers compose into the `AppRouter` |
| **Procedure** | An API endpoint — `query`, `mutation`, or `subscription` |
| **`t` (initTRPC)** | Factory for creating type-safe routers, procedures, and middleware |
| **Context** | Per-request data (user session, DB connection) — flows through all procedures |
| **Middleware** | Function wrapping procedures; used for auth, logging |
| **Input** | Zod schema defining expected request shape |
| **Output** | Optional Zod schema for response validation |
| **`AppRouter`** | Root router type exported from server; imported as type-only on client |
| **Caller** | Server-side tRPC caller (for testing or SSR) |

---

## Installation

```bash
# Server
npm install @trpc/server zod
bun add @trpc/server zod

# Client
npm install @trpc/client

# React Query integration
npm install @trpc/react-query @tanstack/react-query

# Versions in trace:
# @trpc/client@^10.45.2
# @trpc/react-query@^10.45.2
# @trpc/server@^10.45.2
```

---

## Server Setup

### Step 1: Initialize tRPC (`t`)

```typescript
// server/trpc.ts
import { initTRPC, TRPCError } from '@trpc/server';
import type { Context } from './context';

const t = initTRPC.context<Context>().create({
    // Optional: transform errors before sending to client
    errorFormatter({ shape, error }) {
        return {
            ...shape,
            data: {
                ...shape.data,
                zodError: error.cause instanceof ZodError
                    ? error.cause.flatten()
                    : null,
            },
        };
    },
});

// Export building blocks
export const router = t.router;
export const publicProcedure = t.procedure;
export const middleware = t.middleware;
```

### Step 2: Define Context

```typescript
// server/context.ts
import type { CreateNextContextOptions } from '@trpc/server/adapters/next';

export interface Context {
    user: { id: string; email: string } | null;
    db: DatabaseClient;
}

// Context factory — called once per request
export async function createContext({ req, res }: CreateNextContextOptions): Promise<Context> {
    const user = await getUserFromSession(req);
    return {
        user,
        db: getDatabase(),
    };
}
```

### Step 3: Create Middleware

```typescript
// Auth middleware
const isAuthed = middleware(({ ctx, next }) => {
    if (!ctx.user) {
        throw new TRPCError({ code: 'UNAUTHORIZED', message: 'Not authenticated' });
    }
    return next({
        ctx: {
            ...ctx,
            user: ctx.user,  // Narrow type: user is non-null after this middleware
        },
    });
});

// Protected procedure (requires auth)
export const protectedProcedure = publicProcedure.use(isAuthed);

// Logging middleware
const logger = middleware(async ({ path, type, next }) => {
    const start = Date.now();
    const result = await next();
    const ms = Date.now() - start;
    console.log(`${type} ${path} took ${ms}ms`);
    return result;
});

export const loggedProcedure = publicProcedure.use(logger);
```

### Step 4: Define Procedures

```typescript
// server/routers/jobs.ts
import { z } from 'zod';
import { router, publicProcedure, protectedProcedure } from '../trpc';

export const jobsRouter = router({
    // Query: read operation
    getJob: publicProcedure
        .input(z.object({ jobId: z.string() }))
        .query(async ({ input, ctx }) => {
            const job = await ctx.db.jobs.findById(input.jobId);
            if (!job) {
                throw new TRPCError({ code: 'NOT_FOUND', message: 'Job not found' });
            }
            return job;
        }),

    // Query: list with filters
    listJobs: protectedProcedure
        .input(z.object({
            status: z.enum(['pending', 'running', 'completed', 'failed']).optional(),
            limit: z.number().min(1).max(100).default(20),
            cursor: z.string().optional(),
        }))
        .query(async ({ input, ctx }) => {
            const jobs = await ctx.db.jobs.findMany({
                where: { userId: ctx.user.id, status: input.status },
                take: input.limit + 1,
                cursor: input.cursor ? { id: input.cursor } : undefined,
            });

            const hasMore = jobs.length > input.limit;
            return {
                jobs: jobs.slice(0, input.limit),
                nextCursor: hasMore ? jobs[input.limit - 1].id : null,
            };
        }),

    // Mutation: write operation
    createJob: protectedProcedure
        .input(z.object({
            name: z.string().min(1).max(200),
            config: z.record(z.unknown()),
        }))
        .mutation(async ({ input, ctx }) => {
            return ctx.db.jobs.create({
                data: {
                    ...input,
                    userId: ctx.user.id,
                    status: 'pending',
                },
            });
        }),

    // Mutation: update
    cancelJob: protectedProcedure
        .input(z.object({ jobId: z.string() }))
        .mutation(async ({ input, ctx }) => {
            const job = await ctx.db.jobs.findById(input.jobId);
            if (!job || job.userId !== ctx.user.id) {
                throw new TRPCError({ code: 'FORBIDDEN' });
            }
            return ctx.db.jobs.update({
                where: { id: input.jobId },
                data: { status: 'cancelled' },
            });
        }),
});
```

### Step 5: Merge Routers

```typescript
// server/routers/_app.ts
import { router } from '../trpc';
import { jobsRouter } from './jobs';
import { usersRouter } from './users';
import { agentsRouter } from './agents';

export const appRouter = router({
    jobs: jobsRouter,
    users: usersRouter,
    agents: agentsRouter,
});

// Export type for client
export type AppRouter = typeof appRouter;
```

---

## Server Adapters

### Next.js App Router

```typescript
// app/api/trpc/[trpc]/route.ts
import { fetchRequestHandler } from '@trpc/server/adapters/fetch';
import { appRouter } from '@/server/routers/_app';
import { createContext } from '@/server/context';

const handler = (req: Request) =>
    fetchRequestHandler({
        endpoint: '/api/trpc',
        req,
        router: appRouter,
        createContext: () => createContext({ req }),
    });

export { handler as GET, handler as POST };
```

### Express / Node.js

```typescript
import express from 'express';
import { createExpressMiddleware } from '@trpc/server/adapters/express';
import { appRouter } from './routers/_app';
import { createContext } from './context';

const app = express();
app.use('/api/trpc', createExpressMiddleware({
    router: appRouter,
    createContext,
}));
```

---

## Client Setup

### Vanilla TypeScript Client

```typescript
// client/trpc.ts
import { createTRPCProxyClient, httpBatchLink } from '@trpc/client';
import type { AppRouter } from '../server/routers/_app';

export const trpc = createTRPCProxyClient<AppRouter>({
    links: [
        httpBatchLink({
            url: 'http://localhost:3000/api/trpc',
            // Add auth headers
            headers() {
                return {
                    authorization: `Bearer ${getToken()}`,
                };
            },
        }),
    ],
});

// Usage (fully typed!)
const job = await trpc.jobs.getJob.query({ jobId: 'job_123' });
// job is inferred as: { id: string; name: string; status: string; ... }

const created = await trpc.jobs.createJob.mutate({
    name: 'Process dataset',
    config: { timeout: 30 },
});

// Cursor pagination
let cursor: string | null = null;
const result = await trpc.jobs.listJobs.query({ status: 'running', cursor: cursor ?? undefined });
cursor = result.nextCursor;
```

---

## React Query Integration (`@trpc/react-query`)

### Provider Setup

```tsx
// app/providers.tsx
'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { createTRPCReact, httpBatchLink } from '@trpc/react-query';
import type { AppRouter } from '../server/routers/_app';
import { useState } from 'react';

export const trpc = createTRPCReact<AppRouter>();

export function TRPCProvider({ children }: { children: React.ReactNode }) {
    const [queryClient] = useState(() => new QueryClient());
    const [trpcClient] = useState(() =>
        trpc.createClient({
            links: [
                httpBatchLink({
                    url: '/api/trpc',
                    headers() {
                        return { authorization: `Bearer ${getToken()}` };
                    },
                }),
            ],
        })
    );

    return (
        <trpc.Provider client={trpcClient} queryClient={queryClient}>
            <QueryClientProvider client={queryClient}>
                {children}
            </QueryClientProvider>
        </trpc.Provider>
    );
}
```

### Hooks

```tsx
// components/JobList.tsx
'use client';

import { trpc } from '../providers';

export function JobList() {
    // Query (GET-like)
    const { data, isLoading, error } = trpc.jobs.listJobs.useQuery({
        status: 'running',
        limit: 20,
    });

    // Mutation (POST/PUT/DELETE-like)
    const createJob = trpc.jobs.createJob.useMutation({
        onSuccess: (job) => {
            console.log('Created:', job.id);
            // Invalidate and refetch list
            utils.jobs.listJobs.invalidate();
        },
        onError: (err) => console.error('Error:', err.message),
    });

    const cancelJob = trpc.jobs.cancelJob.useMutation();

    // Utility (invalidation, prefetch, etc.)
    const utils = trpc.useUtils();

    if (isLoading) return <div>Loading...</div>;
    if (error) return <div>Error: {error.message}</div>;

    return (
        <ul>
            {data?.jobs.map(job => (
                <li key={job.id}>
                    {job.name}
                    <button onClick={() => cancelJob.mutate({ jobId: job.id })}>
                        Cancel
                    </button>
                </li>
            ))}
            <button onClick={() => createJob.mutate({ name: 'New Job', config: {} })}>
                Create Job
            </button>
        </ul>
    );
}
```

**`useInfiniteQuery` for cursor pagination:**

```tsx
const { data, fetchNextPage, hasNextPage } = trpc.jobs.listJobs.useInfiniteQuery(
    { limit: 20 },
    {
        getNextPageParam: (lastPage) => lastPage.nextCursor,
        initialCursor: undefined,
    }
);
```

---

## Subscriptions (WebSocket)

```typescript
// Server
import { observable } from '@trpc/server/observable';

export const jobsRouter = router({
    onJobUpdated: publicProcedure
        .input(z.object({ jobId: z.string() }))
        .subscription(({ input }) => {
            return observable<JobUpdateEvent>((emit) => {
                // Subscribe to job updates from event bus
                const unsubscribe = eventBus.subscribe(`job.${input.jobId}`, (event) => {
                    emit.next(event);
                });
                // Cleanup
                return () => unsubscribe();
            });
        }),
});

// Client (with websocket link)
import { createWSClient, wsLink } from '@trpc/client';

const wsClient = createWSClient({ url: 'ws://localhost:3000/api/trpc' });
const trpc = createTRPCProxyClient<AppRouter>({
    links: [wsLink({ client: wsClient })],
});

// Subscribe
const subscription = trpc.jobs.onJobUpdated.subscribe(
    { jobId: 'job_123' },
    {
        onData: (event) => console.log('Update:', event),
        onError: (err) => console.error('Sub error:', err),
    }
);

subscription.unsubscribe();
```

---

## Error Handling

tRPC maps errors to HTTP status codes. Use `TRPCError` to throw typed errors:

```typescript
import { TRPCError } from '@trpc/server';

// Throw typed errors in procedures
throw new TRPCError({ code: 'NOT_FOUND', message: 'Job not found' });
throw new TRPCError({ code: 'UNAUTHORIZED', message: 'Login required' });
throw new TRPCError({ code: 'FORBIDDEN', message: 'Access denied' });
throw new TRPCError({ code: 'BAD_REQUEST', message: 'Invalid input' });
throw new TRPCError({
    code: 'INTERNAL_SERVER_ERROR',
    message: 'Something went wrong',
    cause: originalError,
});
```

| tRPC Code | HTTP Status |
|-----------|------------|
| `BAD_REQUEST` | 400 |
| `UNAUTHORIZED` | 401 |
| `FORBIDDEN` | 403 |
| `NOT_FOUND` | 404 |
| `CONFLICT` | 409 |
| `PRECONDITION_FAILED` | 412 |
| `PAYLOAD_TOO_LARGE` | 413 |
| `UNPROCESSABLE_CONTENT` | 422 |
| `TOO_MANY_REQUESTS` | 429 |
| `CLIENT_CLOSED_REQUEST` | 499 |
| `INTERNAL_SERVER_ERROR` | 500 |

**Client error handling:**

```typescript
import { TRPCClientError } from '@trpc/client';

try {
    await trpc.jobs.getJob.query({ jobId: 'missing' });
} catch (err) {
    if (err instanceof TRPCClientError) {
        console.log(err.data?.code);       // 'NOT_FOUND'
        console.log(err.message);          // 'Job not found'
        console.log(err.data?.httpStatus); // 404
    }
}
```

---

## Server-Side Calling (Caller)

Call procedures server-side (for SSR, testing):

```typescript
// Create a caller with a context
const caller = appRouter.createCaller({ user: { id: 'user_123' }, db });

// Call procedures
const job = await caller.jobs.getJob({ jobId: 'job_123' });
const created = await caller.jobs.createJob({ name: 'Test', config: {} });
```

---

## Input Validation

tRPC uses Zod for input validation. Invalid inputs return `BAD_REQUEST` automatically.

```typescript
.input(z.object({
    name: z.string().min(1, "Name required").max(200),
    email: z.string().email(),
    age: z.number().int().positive().optional(),
    tags: z.array(z.string()).max(10).default([]),
    role: z.enum(['admin', 'user', 'viewer']).default('user'),
}))
```

---

## Authentication Pattern

```typescript
// Middleware that reads session from cookie/header
const isAuthed = middleware(async ({ ctx, next }) => {
    if (!ctx.user) {
        throw new TRPCError({ code: 'UNAUTHORIZED' });
    }
    return next({ ctx: { ...ctx, user: ctx.user } });
});

// Role check
const isAdmin = isAuthed.unstable_pipe(({ ctx, next }) => {
    if (ctx.user.role !== 'admin') {
        throw new TRPCError({ code: 'FORBIDDEN', message: 'Admin required' });
    }
    return next({ ctx });
});

export const adminProcedure = publicProcedure.use(isAdmin);
```

---

## thegent / trace Integration

- **trace web app**: `@trpc/client`, `@trpc/react-query`, `@trpc/server` at v10.45.2
- **Pattern**: `@trpc/react-query` wrapping `@tanstack/react-query` for UI state; type-safe API between Next.js/Vite frontend and Go/Python backends (via adapter or proxy)
- **Router file**: Check `trace/frontend/apps/web/src/` for `trpc.ts` or `api.ts`
- **Note**: tRPC is TypeScript-only; Go/Python backends are accessed via REST/gRPC, not tRPC directly

---

## Known Issues / Gotchas

1. **Type-only import**: Import `AppRouter` as `import type { AppRouter }` — never import the runtime at the client; it imports server-only code.
2. **Batching**: `httpBatchLink` batches multiple queries into one HTTP request. If one fails, all fail (by default). Use `httpLink` to disable batching.
3. **Input required**: Every procedure needs an `.input()` call if it takes arguments. No `.input()` means the procedure accepts no arguments.
4. **Server-side only**: tRPC server cannot run in browser. Router file must not be imported on the client side (only the type).
5. **Subscriptions need WebSocket**: `subscription` procedures require `wsLink` on the client; `httpBatchLink` doesn't support subscriptions.
6. **v10 vs v11**: tRPC v11 exists but trace uses v10. The builder pattern (`t.procedure.input().query()`) is the same; v11 adds streaming improvements.
7. **Zod required**: tRPC v10 input validation requires Zod; alternatives (Yup, custom) require a custom `transformer`.

---

## Sources & References

- **tRPC v10 Docs**: https://trpc.io/docs/v10 (fetched 2026-02-20)
- **GitHub**: https://github.com/trpc/trpc (fetched 2026-02-20)
- **tRPC v10 Client Setup**: https://trpc.io/docs/v10/client/vanilla/setup (fetched 2026-02-20)
- **npm `@trpc/server`**: https://www.npmjs.com/package/@trpc/server (v10.45.2, fetched 2026-02-20)
- **tRPC v11 (migration guide)**: https://trpc.io/docs/migrate-from-v10-to-v11 (fetched 2026-02-20)
- **Last Verified**: 2026-02-20

---

## Quick Reference

| Item | Value |
|------|-------|
| Server package | `@trpc/server@^10.45.2` |
| Client package | `@trpc/client@^10.45.2` |
| React package | `@trpc/react-query@^10.45.2` |
| Input validation | Zod (required) |
| HTTP batching | `httpBatchLink` (default) |
| WebSocket | `wsLink` + `createWSClient` |

### Procedure Builder Cheat Sheet

```typescript
// Public query
publicProcedure.input(z.object({...})).query(({ input, ctx }) => { ... })

// Public mutation
publicProcedure.input(z.object({...})).mutation(({ input, ctx }) => { ... })

// Protected query (with middleware)
protectedProcedure.input(z.object({...})).query(({ input, ctx }) => {
    // ctx.user is non-null here
})

// No input
publicProcedure.query(({ ctx }) => { ... })

// Throw typed errors
throw new TRPCError({ code: 'NOT_FOUND' })
throw new TRPCError({ code: 'UNAUTHORIZED' })
throw new TRPCError({ code: 'FORBIDDEN' })
```

### React Hook Cheat Sheet

```typescript
// Read
const { data, isLoading, error } = trpc.router.procedure.useQuery(input);

// Write
const mutation = trpc.router.procedure.useMutation({ onSuccess, onError });
mutation.mutate(input);

// Infinite scroll
const { data, fetchNextPage } = trpc.router.procedure.useInfiniteQuery(
    input,
    { getNextPageParam: (page) => page.nextCursor }
);

// Invalidate cache
const utils = trpc.useUtils();
await utils.router.procedure.invalidate();
```

---

## Source: context/vercel-ai-gateway.md

# Vercel AI Gateway

> Definitive reference for implementing Vercel AI Gateway support in the proxy (CLIProxy / thegent routing layer).
> Sources: vercel.com/docs/ai-gateway (fetched 2026-02-20).

---

## What it is

Vercel AI Gateway is a SaaS-only LLM routing proxy that provides a unified API for accessing
hundreds of AI models from 37+ providers through a single endpoint. Key properties:

- Hosted at `ai-gateway.vercel.sh` — no self-hosted option
- Zero markup on tokens (charges at provider list price)
- 37 providers: OpenAI, Anthropic, Google, xAI, Amazon Bedrock, Azure, Mistral, Groq, etc.
- Two native API surfaces: OpenAI-compatible (`/v1/`) and Anthropic-compatible (`/`)
- Deep Vercel AI SDK integration (`@ai-sdk/gateway`)
- Automatic provider failover, explicit provider ordering, cross-provider model fallbacks
- Per-provider prompt caching orchestration (no gateway-level semantic cache)
- Spend monitoring, credit-based billing, generation lookup API

---

## Base URL / Authentication

### OpenAI-compatible surface

```
Base URL:  https://ai-gateway.vercel.sh/v1
Auth:      Authorization: Bearer <AI_GATEWAY_API_KEY>
Env var:   AI_GATEWAY_API_KEY
```

### Anthropic-compatible surface

```
Base URL:  https://ai-gateway.vercel.sh
Auth:      x-api-key: <AI_GATEWAY_API_KEY>
           OR  Authorization: Bearer <AI_GATEWAY_API_KEY>
```

### OIDC authentication (Vercel-native projects only)

```
Authorization: Bearer <VERCEL_OIDC_TOKEN>   (expires every 12h)
```

API key takes precedence over OIDC token when both present.

### Configuring existing clients

```python
# OpenAI Python SDK
from openai import OpenAI
client = OpenAI(api_key=os.getenv('AI_GATEWAY_API_KEY'),
                base_url='https://ai-gateway.vercel.sh/v1')

# Anthropic Python SDK
import anthropic
client = anthropic.Anthropic(api_key=os.getenv('AI_GATEWAY_API_KEY'),
                              base_url='https://ai-gateway.vercel.sh')
```

**Claude Code CLI:**

```bash
ANTHROPIC_BASE_URL="https://ai-gateway.vercel.sh"
ANTHROPIC_AUTH_TOKEN="<AI_GATEWAY_API_KEY>"
ANTHROPIC_API_KEY=""     # Must be empty — Claude Code checks this first
```

---

## OpenAI Compatibility

Vercel AI Gateway is fully OpenAI-compatible on the `/v1/` path:

| Endpoint | Notes |
|----------|-------|
| `GET /v1/models` | No auth required; returns model list |
| `GET /v1/models/{model}` | Single model details |
| `GET /v1/models/{creator}/{model}/endpoints` | Per-model provider list with pricing |
| `POST /v1/chat/completions` | Chat completions (streaming + non-streaming) |
| `POST /v1/embeddings` | Vector embeddings |
| `GET /v1/credits` | Credit balance |
| `GET /v1/generation` | Per-generation cost and metadata lookup |

**Model ID format:** `{creator}/{model-name}` — e.g.:
```
openai/gpt-5.2
anthropic/claude-sonnet-4.5
google/gemini-3-flash
xai/grok-4
```

**No `/v1/responses` endpoint** — Vercel AI Gateway does not implement the OpenAI Responses API.

---

## Request Extensions

These fields extend the standard OpenAI chat completions request body:

### `providerOptions.gateway` (object) — routing and configuration

```json
{
  "providerOptions": {
    "gateway": {
      "order": ["bedrock", "anthropic"],
      "only": ["anthropic", "vertex"],
      "caching": "auto",
      "models": ["anthropic/claude-sonnet-4.5", "google/gemini-3-flash"],
      "byok": {
        "anthropic": [{ "apiKey": "sk-ant-..." }],
        "vertex": [
          { "project": "proj-1", "location": "us-east5",
            "googleCredentials": { "privateKey": "...", "clientEmail": "..." } }
        ],
        "bedrock": [{ "accessKeyId": "...", "secretAccessKey": "...", "region": "us-east-1" }]
      }
    }
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `order` | string[] | Provider slugs to try in order (e.g. `["bedrock", "anthropic"]`) |
| `only` | string[] | Allowlist of providers; if none match, request fails |
| `caching` | `"auto"` | Auto-insert `cache_control` breakpoints for Anthropic (not Bedrock) |
| `models` | string[] | Model fallback list tried in order if primary fails |
| `byok` | object | Per-request provider credentials by provider slug |

When both `order` and `only` are set, the final order is the intersection: providers in
`order` that also appear in `only`, preserving `order` sequence.

### `models` (string[]) — top-level model fallback list (alternative to `providerOptions.gateway.models`)

```json
{
  "model": "openai/gpt-5.2",
  "models": ["anthropic/claude-sonnet-4.5", "google/gemini-3-flash"]
}
```

### `reasoning` (object) — cross-provider reasoning control

```json
{
  "reasoning": {
    "enabled": true,
    "max_tokens": 2000,
    "effort": "high",
    "exclude": false
  }
}
```

| Field | Values | Notes |
|-------|--------|-------|
| `enabled` | boolean | Enable reasoning output |
| `max_tokens` | integer | Reasoning token budget; mutually exclusive with `effort` |
| `effort` | `none`, `minimal`, `low`, `medium`, `high`, `xhigh` | Approx 0%, 10%, 20%, 50%, 80%, 95% of max |
| `exclude` | boolean | Suppress reasoning from response (still generates internally) |

### `providerOptions.anthropic` / `providerOptions.openai` — provider-specific options

Can be combined with `providerOptions.gateway`:

```json
{
  "providerOptions": {
    "anthropic": { "thinkingBudget": 0.001 },
    "openai": { "reasoningEffort": "high", "reasoningSummary": "detailed" },
    "gateway": { "order": ["vertex"] }
  }
}
```

### Attribution headers (optional)

```
http-referer: https://myapp.vercel.app
x-title: MyApp
```

Sets for app visibility on AI Gateway pages. No effect on routing.

---

## Response Extensions

### Standard non-streaming response additions

```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "...",
      "reasoning": "Let me think...",
      "reasoning_details": [
        {
          "type": "reasoning.text",
          "text": "Let me think...",
          "signature": "anthropic-sig-xyz",
          "format": "anthropic-claude-v1",
          "index": 0
        }
      ]
    }
  }],
  "usage": {
    "completion_tokens_details": {
      "reasoning_tokens": 50
    }
  }
}
```

**Reasoning detail types:**
- `reasoning.text` — plain text reasoning (Anthropic); may include `signature` field
- `reasoning.encrypted` — encrypted/redacted reasoning payload (OpenAI); has `data` field
- `reasoning.summary` — condensed summary (OpenAI); has `summary` field

### AI SDK `providerMetadata` (gateway routing + cost)

When using `@ai-sdk/gateway` or the AI SDK, responses include:

```json
{
  "providerMetadata": {
    "gateway": {
      "routing": {
        "resolvedProvider": "anthropic",
        "fallbacksAvailable": ["bedrock", "vertex"],
        "attempts": [
          { "provider": "anthropic", "credentialType": "system",
            "success": true, "startTime": 458753.4, "endTime": 459891.7 }
        ]
      },
      "cost": "0.0045405",
      "marketCost": "0.0045405",
      "generationId": "gen_01K8KPJ0FZA7172X6CSGNZGDWY"
    }
  }
}
```

**`gateway.cost`** — Decimal string in USD, amount debited from AI Gateway Credits.
**`gateway.generationId`** — Use with `GET /v1/generation?id=` for detailed stats.

### Cost is NOT in the standard chat completion response body

To retrieve cost data, use:
```
GET https://ai-gateway.vercel.sh/v1/generation?id=gen_01ARZ3NDEKTSV4RRFFQ69G5FAV
Authorization: Bearer <AI_GATEWAY_API_KEY>
```

Returns: `total_cost`, `tokens_prompt`, `tokens_completion`, `native_tokens_cached`,
`native_tokens_reasoning`, `latency`, `generation_time`, `provider_name`, `is_byok`.

---

## Caching

Vercel AI Gateway has **no gateway-level semantic or exact-match response cache**.

It orchestrates **provider-side prompt token caching**:

| Provider | Behavior | Action needed |
|----------|----------|---------------|
| OpenAI, Google, DeepSeek | Implicit caching — automatic | None; provider caches automatically |
| Anthropic (direct, Vertex) | Requires explicit markers | Set `caching: 'auto'` in `providerOptions.gateway`, or add `cache_control: { type: "ephemeral" }` to messages |
| Amazon Bedrock | Not yet supported | Must disable auto-caching for Bedrock routes |

**Auto caching example:**

```json
{
  "providerOptions": { "gateway": { "caching": "auto" } }
}
```

When `caching: 'auto'` is set, the gateway inserts a `cache_control` breakpoint at the
end of static content before forwarding to Anthropic.

**Manual cache_control example:**

```json
{
  "messages": [
    {
      "role": "system",
      "content": "Long system prompt...",
      "cache_control": { "type": "ephemeral" }
    }
  ]
}
```

Cache pricing tracked in model metadata (`input_cache_read`, `input_cache_write`) and in
generation lookup data (`native_tokens_cached`).

---

## Fallbacks / Load Balancing

### Provider-level routing

```json
{
  "providerOptions": {
    "gateway": {
      "order": ["bedrock", "anthropic"],
      "only": ["anthropic", "bedrock"]
    }
  }
}
```

- `order` — try providers in this sequence
- `only` — restrict to this set; request fails if none can serve
- No `sort` by price/throughput/latency (OpenRouter feature that is NOT present here)
- Default: automatic selection by Vercel's internal uptime/latency scoring

### Model-level fallbacks

```json
{
  "model": "openai/gpt-5.2",
  "models": ["anthropic/claude-sonnet-4.5", "google/gemini-3-flash"]
}
```

Failover sequence:
1. Try primary model via configured providers (respecting `order`)
2. On all-provider failure: try first model in `models` list
3. Continue through `models` list until success

The `model` field in the response always reflects the ACTUAL model used.

### BYOK failback

Dashboard-configured or per-request BYOK credentials are tried first. On BYOK credential
failure, the gateway automatically retries with Vercel system credentials (transparent
failback, no extra configuration).

### Load balancing

No explicit load-balancing policy exposed. Vercel auto-selects providers by internal
uptime/latency score. No `sort: "price"` / `sort: "throughput"` options exist (unlike OpenRouter).

---

## Rate Limiting

**No documented gateway-level rate limit configuration.** Rate limits are provider-enforced
and surfaced as `429 Too Many Requests`. No `X-RateLimit-*` headers documented.

Indirect budget controls:
- Credits balance depletes and requests stop when balance is zero
- Auto top-up prevents interruption

Error format on 429:
```json
{ "error": { "message": "...", "type": "...", "param": null, "code": "..." } }
```

No `Retry-After` header documented.

---

## Observability

### Dashboard (Vercel UI)

- **Requests by Model**: request volume per model over time
- **TTFT (Time to First Token)**: P-latency chart
- **Input/Output Token Counts**: token volume
- **Spend**: cost over time
- **Request logs**: per-request detail (model, provider, all token types, cost)
- **Grouped by**: project or API key
- **Scope**: team-wide or per-project

Extended log retention requires Observability Plus (paid add-on).

### Programmatic APIs

| Endpoint | Data |
|----------|------|
| `GET /v1/credits` | `{ "balance": "95.50", "total_used": "4.50" }` |
| `GET /v1/generation?id={id}` | Per-generation cost, tokens, latency, provider |
| `GET /billing/charges` | FOCUS v1.3 JSONL with 1-day granularity |

### No OTEL / External Export

No documented OpenTelemetry export, webhook delivery, or log streaming to external
observability platforms. All metrics are Vercel-dashboard-native.

---

## Key Differences from OpenRouter

| Dimension | Vercel AI Gateway | OpenRouter |
|-----------|-------------------|------------|
| **API surfaces** | OpenAI-compat + Anthropic-compat (two native surfaces) | OpenAI-compat only |
| **Anthropic endpoint** | `POST /v1/messages` native Anthropic format | Not supported |
| **Responses API** | Not documented | Beta (`/api/v1/responses`) |
| **Model routing** | `order`, `only` (Vercel picks default by score) | `order`, `only`, `ignore`, `allow_fallbacks`, `require_parameters` |
| **Load balancing** | Automatic (not configurable) | `sort: "price"/"throughput"/"latency"`, `max_price`, `preferred_min_throughput`, `preferred_max_latency`, percentile thresholds |
| **Routing constraints** | None (no data_collection, no ZDR, no quantization filter) | `data_collection`, `zdr`, `quantizations`, `require_parameters` |
| **Model ID suffixes** | None | `:nitro`, `:floor`, `:online`, `:free`, `:thinking`, `:extended`, `:exacto` |
| **Cost in response** | NOT in response body (use generation lookup or AI SDK providerMetadata) | NOT in response body (use `/api/v1/generation`) |
| **Streaming provider field** | NOT present in SSE chunks | `"provider": "OpenAI"` in every chunk |
| **Streaming keep-alive** | No comment lines | `": OPENROUTER PROCESSING"` comments |
| **Caching** | Provider-side prompt caching orchestration only | Provider-side prompt caching (pass-through only) |
| **Semantic cache** | No | No |
| **Plugins** | Web search tools (Perplexity, Parallel, native per provider) | `plugins: [{id: "web"/"file-parser"/"response-healing"}]` |
| **Context compression** | No | `transforms: ["middle-out"]` |
| **Reasoning normalization** | Deep: `reasoning`, `reasoning_details` with typed blocks and signatures | `reasoning.effort`, `reasoning.summary`; less structured |
| **BYOK** | Dashboard-level + per-request `providerOptions.gateway.byok`; no fee | Dashboard-level only; service fee (waived for first N requests/month) |
| **Pricing** | Zero markup; credit-based | Variable; zero markup on BYOK routes |
| **Self-hosting** | No | No |
| **Image/Video generation** | Yes (Flux, Recraft, Veo, Kling, Wan, Grok Imagine) | Limited |
| **Rate limit docs** | Not documented | Free tier: 60 req/min for `:free`; documented `X-RateLimit-*` in 429 metadata |
| **Framework integrations** | AI SDK (first-class), LangChain, LiteLLM, LlamaIndex, Mastra, Pydantic AI | LangChain, LiteLLM, many others |

---

## Key Differences from LiteLLM

| Dimension | Vercel AI Gateway | LiteLLM |
|-----------|-------------------|---------|
| **Deployment** | SaaS only | Self-hosted (also has hosted Cloud tier) |
| **OpenAI compat** | Yes | Yes |
| **Anthropic compat** | Yes (first-class) | Via proxy with translation |
| **Provider config** | Per-request `providerOptions.gateway` | Config file / environment variables |
| **Budget limits** | Credits balance + auto top-up | `max_budget`, `budget_duration`, `litellm_settings` |
| **Load balancing** | Automatic scoring | `routing_strategy`: `least-busy`, `usage-based`, `latency-based`, `cost-based` |
| **Rate limiting** | Not exposed | Per-user, per-team, per-key RPM/TPM limits |
| **Observability** | Vercel dashboard; no OTEL export | Prometheus, Langfuse, Helicone, Datadog, OTEL integration |
| **Fallbacks** | `models` array | `fallbacks` in config with model-specific fallback lists |
| **Caching** | Provider-side only | Semantic (Redis) + exact (Redis/in-memory) |
| **Pricing** | Zero markup, credit-based | Self-hosted: free; Cloud: pricing per seat |
| **Model management** | Dynamic model discovery via API | Static config file + model list |

---

## Proxy Considerations

What a proxy sitting between a client and Vercel AI Gateway must handle:

### Request Pass-Through (mandatory)

A proxy MUST pass through these Vercel-specific fields without dropping them:
- `providerOptions` object (entire `gateway`, `anthropic`, `openai`, etc. sub-objects)
- `models` array (model fallback list)
- `reasoning` object
- `cache_control` in message objects
- `file` content parts in messages

### Request Rewriting (may be required)

- `model`: Translate from internal catalog IDs (e.g. `claude-sonnet-4.5`) to Vercel format (e.g. `anthropic/claude-sonnet-4.5`)
- `Authorization`: Replace client key with `AI_GATEWAY_API_KEY`
- `http-referer` + `x-title`: Set to proxy identity if desired

### Response Pass-Through (mandatory)

- `model` field (actual model used — critical for fallback awareness)
- `choices[].message.reasoning` (cross-provider reasoning text)
- `choices[].message.reasoning_details` (structured reasoning blocks)
- `usage.completion_tokens_details.reasoning_tokens`
- `id` field (= generationId for generation lookup)
- `providerMetadata.gateway.cost` and `generationId` when using AI SDK

### Streaming Considerations

- No SSE comment lines to handle (Vercel doesn't send them)
- No `provider` field in streaming chunks (Vercel omits it)
- `delta.reasoning` and `delta.reasoning_details` must be forwarded (proxy must not drop these)
- `delta.tool_calls` must be forwarded (proxy must not drop tool call streaming)
- Final chunk contains `usage` stats (same as OpenAI spec)

### Cost / Usage Accounting

The chat completion response does NOT contain cost. To track spend:
1. Capture `id` from response body (= generationId)
2. After request completes: `GET /v1/generation?id={id}` — returns `total_cost`
3. AI SDK: cost is in `providerMetadata.gateway.cost`

### TLS

HTTPS required: `https://ai-gateway.vercel.sh`. Must use `verify=True` (not `verify=False`).

### Authentication

Vercel AI Gateway requires `Authorization: Bearer <AI_GATEWAY_API_KEY>`. The env var is
`AI_GATEWAY_API_KEY`. For BYOK pass-through, the `providerOptions.gateway.byok` object
carries per-provider credentials and must be forwarded as-is; the gateway applies them internally.

### Anthropic-Compatible Surface

To support tools like Claude Code connecting via the Anthropic SDK:
- Expose `POST /v1/messages` endpoint
- Accept `x-api-key` header in addition to `Authorization: Bearer`
- Forward to `https://ai-gateway.vercel.sh/v1/messages` (or translate to OpenAI format if not proxying directly)

### Provider Slug Reference

Used in `providerOptions.gateway.order` / `only`:
`anthropic`, `bedrock`, `vertex`, `openai`, `azure`, `google`, `groq`, `mistral`,
`fireworks`, `togetherai`, `deepinfra`, `deepseek`, `cohere`, `cerebras`, `xai`,
`perplexity`, `sambanova`, `novita`, `nebius`, `crusoe`, `arcee-ai`, `alibaba`,
`bytedance`, `moonshotai`, `morph`, `meituan`, `minimax`, `inception`, `bfl`,
`klingai`, `prodia`, `recraft`, `streamlake`, `baseten`, `parasail`, `voyage`, `zai`, `vercel`

---

## Quick Reference: All Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/v1/models` | Optional | List all models with pricing and capabilities |
| GET | `/v1/models/{model}` | Optional | Single model details |
| GET | `/v1/models/{creator}/{model}/endpoints` | Optional | Per-model provider list |
| POST | `/v1/chat/completions` | Required | Chat completions (OpenAI-compat) |
| POST | `/v1/embeddings` | Required | Vector embeddings |
| POST | `/v1/messages` | Required | Anthropic Messages API (Anthropic-compat) |
| GET | `/v1/credits` | Required | Credit balance |
| GET | `/v1/generation?id={id}` | Required | Per-generation cost + metadata |
| GET | `/billing/charges` | Required | Cost data (FOCUS v1.3 JSONL, 1-day granularity) |

---

## Sources

- https://vercel.com/docs/ai-gateway
- https://vercel.com/docs/ai-gateway/models-and-providers/provider-options
- https://vercel.com/docs/ai-gateway/models-and-providers/model-fallbacks
- https://vercel.com/docs/ai-gateway/sdks-and-apis/openai-compat
- https://vercel.com/docs/ai-gateway/sdks-and-apis/openai-compat/advanced
- https://vercel.com/docs/ai-gateway/sdks-and-apis/anthropic-compat
- https://vercel.com/docs/ai-gateway/authentication-and-byok/byok
- https://vercel.com/docs/ai-gateway/capabilities/observability
- https://vercel.com/docs/ai-gateway/capabilities/usage
- https://vercel.com/docs/ai-gateway/capabilities/web-search
- https://vercel.com/docs/ai-gateway/pricing
- https://vercel.com/docs/ai-gateway/ecosystem/app-attribution

---

## Source: context/vercel-ai-sdk.md

# Vercel AI SDK Context

> Definitive reference for the Vercel AI SDK — TypeScript toolkit for building AI-powered applications across providers.
> Sources: ai-sdk.dev/docs, vercel.com/blog/ai-sdk-6, github.com/vercel/ai (fetched 2026-02-20).
> **Version covered: AI SDK 6.x (latest: 6.0.94 as of 2026-02-20)**

---

## What is Vercel AI SDK

The **AI SDK** (formerly "Vercel AI SDK") is an open-source TypeScript/JavaScript toolkit that provides a unified API for integrating AI models across providers (OpenAI, Anthropic, Google, xAI, etc.). It abstracts provider-specific differences so application code targets one stable interface.

Key capabilities:
- **Provider-agnostic**: Swap models by changing one `model` argument
- **Streaming**: First-class SSE streaming with backpressure and React Suspense integration
- **Structured output**: Generate typed JSON objects, arrays, and choices from any provider
- **Tool calling**: Declare tools with Zod schemas; SDK handles round-trips automatically
- **Agent patterns**: Multi-step tool loops with `maxSteps`; `ToolLoopAgent` for production agents
- **React/Next.js hooks**: `useChat`, `useCompletion`, `useObject` for UI state management
- **MCP support**: Native Model Context Protocol client with HTTP transport + OAuth

**Note on thegent/trace**: trace's web frontend uses `@trpc/client` for API calls, not AI SDK directly. thegent uses AI SDK patterns in proxy/routing layers for provider-agnostic model access.

---

## Key Concepts

| Term | Definition |
|------|-----------|
| **Provider** | A model source adapter (e.g., `@ai-sdk/openai`, `@ai-sdk/anthropic`) |
| **LanguageModel** | Provider-created model instance passed to core functions |
| **`generateText`** | Non-streaming text generation for automation tasks |
| **`streamText`** | Streaming text generation for real-time UI |
| **`generateObject`** | Structured JSON output with schema validation |
| **Tool** | Defined with `tool()` — schema + execute function |
| **Step** | One round of model → tool calls → tool results in a multi-step loop |
| **`maxSteps`** | Max number of steps in a tool call loop |
| **ToolLoopAgent** | New in v6: production agent with automatic tool loops |
| **`useChat`** | React hook for chat UI state management |

---

## Installation

```bash
# Core SDK
npm install ai
bun add ai

# Provider packages (install per provider used)
npm install @ai-sdk/openai         # OpenAI + compatible APIs
npm install @ai-sdk/anthropic      # Anthropic Claude
npm install @ai-sdk/google         # Google Gemini
npm install @ai-sdk/xai            # xAI Grok
npm install @ai-sdk/cohere         # Cohere
npm install @ai-sdk/azure          # Azure OpenAI
npm install @ai-sdk/amazon-bedrock # Amazon Bedrock
npm install @ai-sdk/vercel         # Vercel AI Gateway (all providers)
npm install @ai-sdk/openai-compatible  # OpenRouter, LiteLLM, etc.

# Migration codemod (v5 to v6)
npx @ai-sdk/codemod upgrade v6

# DevTools viewer
npx @ai-sdk/devtools               # Opens viewer at localhost:4983
```

**Current versions (2026-02-20):**

| Package | Version |
|---------|---------|
| `ai` | `6.0.94` |
| `@ai-sdk/vercel` | `2.0.32` |
| `@ai-sdk/openai` | `~1.x` |
| `@ai-sdk/anthropic` | `~1.x` |

---

## Core: `generateText`

Generates text for non-interactive, automation use cases.

```typescript
import { generateText } from 'ai';
import { openai } from '@ai-sdk/openai';

const result = await generateText({
    model: openai('gpt-4o'),
    prompt: 'Summarize the following: ...',
    system: 'You are a helpful assistant.',
    maxOutputTokens: 1000,
    temperature: 0.7,
    maxRetries: 2,
    tools: { myTool },
    toolChoice: 'auto',    // 'auto' | 'none' | 'required' | {type, toolName}
    maxSteps: 5,           // Max tool call rounds
});

// Return fields
result.text             // string: generated text
result.toolCalls        // Array of tool invocations
result.toolResults      // Array of tool results
result.finishReason     // 'stop' | 'length' | 'tool-calls' | 'content-filter' | 'error'
result.usage            // {inputTokens, outputTokens, totalTokens}
result.totalUsage       // Aggregate across all steps
result.steps            // Array of GenerateTextStep — each step in multi-step loop
result.reasoning        // Array of reasoning outputs (models that support it)
result.response         // {id, modelId, timestamp, headers}
```

**Full parameter list:**

```typescript
await generateText({
    model,
    prompt,              // string | MessagePart[]
    messages,            // ModelMessage[]  (use prompt OR messages, not both)
    system,              // string | SystemMessage[]
    tools,               // Record<string, Tool>
    toolChoice,          // 'auto' | 'none' | 'required' | {type, toolName}
    activeTools,         // string[] — limit which tools are active
    output,              // Output.object({schema}), Output.array(), Output.choice(), Output.json()
    maxSteps,
    prepareStep,         // (step) => Promise<StepSettings>
    stopWhen,            // Condition to stop multi-step generation
    temperature,
    topP, topK,
    presencePenalty, frequencyPenalty,
    maxOutputTokens,
    stopSequences,       // string[]
    seed,
    maxRetries,          // Default: 2
    timeout,             // number | {totalMs, stepMs}
    abortSignal,         // AbortSignal
    providerOptions,     // Provider-specific settings
    headers,             // Custom HTTP headers
    experimental_context, // Custom context passed through execution
});
```

---

## Core: `streamText`

Streaming text generation. Returns a `StreamTextResult` with async iterators.

```typescript
import { streamText } from 'ai';
import { anthropic } from '@ai-sdk/anthropic';

const result = streamText({
    model: anthropic('claude-sonnet-4.5'),
    prompt: 'Tell me a story',
});

// Consume text stream
for await (const chunk of result.textStream) {
    process.stdout.write(chunk);
}

// In Next.js App Router API route
export async function POST(req: Request) {
    const { messages } = await req.json();
    const result = streamText({
        model: openai('gpt-4o'),
        messages,
    });
    return result.toDataStreamResponse();   // Response with SSE format
}
```

**Key `streamText` result properties:**

```typescript
result.textStream               // AsyncIterable<string>
result.fullStream               // AsyncIterable<TextStreamPart> (includes tool calls)
result.text                     // Promise<string> — complete text when done
result.finishReason             // Promise<FinishReason>
result.usage                    // Promise<Usage>
result.toDataStreamResponse()   // Next.js Response object (SSE)
result.pipeDataStreamToResponse(res)   // Node.js stream
result.toTextStreamResponse()   // Plain text response
```

---

## Core: `generateObject`

Generate structured JSON output with schema validation.

```typescript
import { generateObject } from 'ai';
import { z } from 'zod';

const { object } = await generateObject({
    model: openai('gpt-4o'),
    schema: z.object({
        title: z.string(),
        priority: z.enum(['low', 'medium', 'high']),
        tags: z.array(z.string()),
    }),
    prompt: 'Create a task for fixing the login bug',
});
// object: { title: string; priority: 'low'|'medium'|'high'; tags: string[] }
```

**Output modes (v6):**

```typescript
import { Output } from 'ai';

await generateText({ ..., output: Output.object({ schema: z.object({...}) }) });
await generateText({ ..., output: Output.array({ schema: z.object({...}) }) });
await generateText({ ..., output: Output.choice(['accept', 'reject', 'defer']) });
await generateText({ ..., output: Output.json() });
```

**`streamObject` for streaming structured output:**

```typescript
import { streamObject } from 'ai';

const result = streamObject({
    model: openai('gpt-4o'),
    schema: z.object({ summary: z.string(), points: z.array(z.string()) }),
    prompt: 'Summarize this document: ...',
});

for await (const partial of result.partialObjectStream) {
    console.log(partial);  // Partial updates as stream arrives
}
const finalObject = await result.object;
```

---

## Tools

```typescript
import { tool, generateText } from 'ai';
import { z } from 'zod';

const getWeather = tool({
    description: 'Get the weather for a location',
    parameters: z.object({
        location: z.string().describe('City name'),
        units: z.enum(['celsius', 'fahrenheit']).default('celsius'),
    }),
    execute: async ({ location, units }) => {
        const weather = await fetchWeatherAPI(location, units);
        return { temperature: weather.temp, condition: weather.cond };
    },
    // v6 features:
    needsApproval: false,        // boolean | async fn — human-in-the-loop
    strict: true,                // Strict JSON Schema validation
    inputExamples: [             // Clarifying examples for the model
        { location: 'San Francisco', units: 'fahrenheit' }
    ],
});

const result = await generateText({
    model: openai('gpt-4o'),
    tools: { getWeather },
    maxSteps: 3,
    prompt: 'What is the weather in SF?',
});
```

**Tool execution approval (human-in-the-loop, v6):**

```typescript
const dangerousTool = tool({
    parameters: z.object({ target: z.string() }),
    needsApproval: true,   // Pause execution; human must call addToolOutput()
    execute: async ({ target }) => {
        return performOperation(target);
    },
});
```

**`toModelOutput` — control what the model sees from tool result:**

```typescript
const richTool = tool({
    parameters: z.object({ query: z.string() }),
    execute: async ({ query }) => {
        const result = await expensiveQuery(query);
        return result;    // Full result stored in toolResults
    },
    toModelOutput: (result) => ({
        text: `Found ${result.count} items`,  // Only summary passed to model context
    }),
});
```

---

## Agents: `ToolLoopAgent` (v6)

Production-ready agent with automatic tool execution loops.

```typescript
import { ToolLoopAgent } from 'ai';
import { openai } from '@ai-sdk/openai';

const agent = new ToolLoopAgent({
    model: openai('gpt-4o'),
    instructions: 'You are a helpful assistant. Use tools to answer questions.',
    tools: { getWeather, searchDocs },
    maxSteps: 10,
});

const result = await agent.generate({
    prompt: 'What is the weather in Tokyo today?',
});
console.log(result.text);

// Streaming
const stream = agent.stream({ prompt: 'Explain...' });
for await (const chunk of stream.textStream) {
    process.stdout.write(chunk);
}
```

**Dynamic call options (v6):**

```typescript
const agent = new ToolLoopAgent({
    model: openai('gpt-4o'),
    callOptionsSchema: z.object({ userId: z.string() }),
    prepareCall: async ({ userId }) => ({
        system: `User ID: ${userId}. Provide personalized help.`,
    }),
    tools: { getProfile },
});

const result = await agent.generate({
    prompt: 'What are my preferences?',
    callOptions: { userId: 'user_123' },
});
```

**`maxSteps` without ToolLoopAgent:**

```typescript
const result = await generateText({
    model: openai('gpt-4o'),
    tools: { searchWeb, readFile, writeCode },
    maxSteps: 10,
    prompt: 'Research and implement a sorting algorithm',
});
// SDK loops: model → tool calls → tool results → model → ... until maxSteps or done
```

---

## Providers

### OpenAI

```typescript
import { openai } from '@ai-sdk/openai';

openai('gpt-4o')
openai('gpt-4o-mini')
openai('o1')
openai('o3-mini')
openai.image('dall-e-3')
openai.embedding('text-embedding-3-small')
```

### Anthropic

```typescript
import { anthropic } from '@ai-sdk/anthropic';

anthropic('claude-opus-4-6')
anthropic('claude-sonnet-4.5')
anthropic('claude-haiku-4.5')

// Provider-specific tools (v6)
import { anthropicTools } from '@ai-sdk/anthropic';
const tools = {
    computer: anthropicTools.computer_20250124(),
    bash: anthropicTools.bash_20250124(),
    textEditor: anthropicTools.textEditor_20250124(),
};
```

### Google

```typescript
import { google } from '@ai-sdk/google';

google('gemini-2.0-flash')
google('gemini-2.0-pro')
google('gemini-2.0-flash-thinking-exp')   // Reasoning model
```

### xAI

```typescript
import { xai } from '@ai-sdk/xai';

xai('grok-3')
xai('grok-3-mini')
```

### OpenAI-Compatible (OpenRouter, LiteLLM)

```typescript
import { createOpenAICompatible } from '@ai-sdk/openai-compatible';

// OpenRouter
const openrouter = createOpenAICompatible({
    name: 'openrouter',
    baseURL: 'https://openrouter.ai/api/v1',
    headers: {
        'Authorization': `Bearer ${process.env.OPENROUTER_API_KEY}`,
        'HTTP-Referer': 'https://example.com',
    },
});
const model = openrouter('anthropic/claude-sonnet-4.5');

// LiteLLM proxy
const litellm = createOpenAICompatible({
    name: 'litellm',
    baseURL: 'http://localhost:4000/v1',
    headers: { 'Authorization': `Bearer ${process.env.LITELLM_API_KEY}` },
});
```

### Vercel AI Gateway

```typescript
import { createVercel } from '@ai-sdk/vercel';

const vercel = createVercel({ apiKey: process.env.AI_GATEWAY_API_KEY });
const model = vercel('anthropic/claude-sonnet-4.5');
```

---

## React Hooks (AI SDK UI)

### `useChat`

```typescript
'use client';
import { useChat } from 'ai/react';

export function ChatComponent() {
    const {
        messages,       // Message[]
        id,             // Chat ID
        status,         // 'submitted' | 'streaming' | 'ready' | 'error'
        error,
        sendMessage,    // Submit new message
        regenerate,     // Recreate last response
        stop,           // Abort streaming
        setMessages,    // Direct state setter
        addToolOutput,  // For tool approval flows
    } = useChat({
        transport: '/api/chat',
        messages: initialMessages,
        onFinish: (message) => console.log('Done:', message),
        onError: (error) => console.error(error),
        onToolCall: async ({ toolCall }) => {
            // Client-side tool handling
            if (toolCall.toolName === 'getLocation') {
                return { lat: 37.7749, lng: -122.4194 };
            }
        },
    });

    return (
        <div>
            {messages.map(m => (
                <div key={m.id}>{m.role}: {m.content}</div>
            ))}
            <button onClick={() => sendMessage('Hello!')}>Send</button>
            <button onClick={stop}>Stop</button>
        </div>
    );
}
```

### `useCompletion`

```typescript
import { useCompletion } from 'ai/react';

const { completion, complete, isLoading } = useCompletion({
    api: '/api/complete',
    onFinish: (text) => console.log('Final:', text),
});

await complete('Summarize this: ...');
// completion updates in real-time as stream arrives
```

### `useObject`

```typescript
import { useObject } from 'ai/react';
import { z } from 'zod';

const TaskSchema = z.object({
    title: z.string(),
    priority: z.enum(['low', 'medium', 'high']),
    steps: z.array(z.string()),
});

const { object, submit, isLoading } = useObject({
    api: '/api/generate-task',
    schema: TaskSchema,
});

await submit('Create a task for fixing the login bug');
// object updates in real-time as stream arrives
```

---

## Embeddings

```typescript
import { embed, embedMany } from 'ai';
import { openai } from '@ai-sdk/openai';

const { embedding } = await embed({
    model: openai.embedding('text-embedding-3-small'),
    value: 'Text to embed',
});
// embedding: number[]  (1536 dimensions)

const { embeddings } = await embedMany({
    model: openai.embedding('text-embedding-3-small'),
    values: ['Text 1', 'Text 2', 'Text 3'],
});
// embeddings: number[][]
```

---

## Image Generation

```typescript
import { generateImage } from 'ai';
import { openai } from '@ai-sdk/openai';

const { image } = await generateImage({
    model: openai.image('dall-e-3'),
    prompt: 'A futuristic city skyline',
    size: '1024x1024',
    // v6: reference images for editing
    images: [existingImageAsBase64OrURL],
});

// image.base64     → base64 string
// image.uint8Array → Uint8Array
```

---

## Middleware: `wrapLanguageModel`

Inject logging, caching, or other behavior around model calls.

```typescript
import { wrapLanguageModel } from 'ai';

const instrumentedModel = wrapLanguageModel({
    model: openai('gpt-4o'),
    middleware: {
        wrapGenerate: async ({ doGenerate, params }) => {
            console.log('Calling model...');
            const result = await doGenerate();
            console.log('Output:', result.text);
            return result;
        },
    },
});
```

**DevTools middleware (v6):**

```typescript
import { devToolsMiddleware } from '@ai-sdk/devtools';

const model = wrapLanguageModel({
    model: openai('gpt-4o'),
    middleware: devToolsMiddleware(),  // Viewer at localhost:4983
});
```

---

## Reranking (v6)

```typescript
import { rerank } from 'ai';
import { cohere } from '@ai-sdk/cohere';

const { rerankedDocuments } = await rerank({
    model: cohere.rerank('rerank-v3.5'),
    query: 'What is the weather like in London?',
    documents: [
        'London has mild weather year-round.',
        'Paris is the capital of France.',
        'The UK experiences frequent rainfall.',
    ],
    topK: 2,
});
```

---

## MCP Support (Native Client)

```typescript
import { experimental_createMcpClient } from 'ai';

const mcpClient = await experimental_createMcpClient({
    transport: {
        type: 'sse',
        url: 'http://localhost:3847/sse',
    },
});

const mcpTools = await mcpClient.tools();

const result = await generateText({
    model: openai('gpt-4o'),
    tools: { ...mcpTools },
    prompt: 'Run thegent ps',
});

// HTTP transport with OAuth
const securedClient = await experimental_createMcpClient({
    transport: {
        type: 'http',
        url: 'https://mcp.example.com',
        headers: { 'Authorization': `Bearer ${token}` },
    },
});
```

---

## Error Handling

```typescript
import { generateText, APICallError, RetryError } from 'ai';

try {
    const result = await generateText({ model: openai('gpt-4o'), prompt: 'Hello' });
} catch (error) {
    if (APICallError.isInstance(error)) {
        console.error('API error:', error.statusCode, error.message);
        console.error('Response body:', error.responseBody);
    } else if (RetryError.isInstance(error)) {
        console.error('Max retries exceeded:', error.errors);
    } else {
        throw error;
    }
}
```

---

## Telemetry

```typescript
const result = await generateText({
    model: openai('gpt-4o'),
    prompt: 'Hello',
    experimental_telemetry: {
        isEnabled: true,
        functionId: 'my-generation',
        metadata: { userId: 'user_123', requestId: 'req_456' },
    },
});
// Outputs OpenTelemetry spans to configured exporters
```

---

## 2026 Features (AI SDK 6.x as of 2026-02-20)

| Feature | Status | Notes |
|---------|--------|-------|
| `ToolLoopAgent` | Stable (v6) | Production agent with tool loops |
| Tool execution approval (`needsApproval`) | Stable (v6) | Human-in-the-loop |
| `Output.*` structured output | Stable (v6) | `Output.object/array/choice/json` |
| Computer use (Anthropic) | Stable | via `anthropicTools.computer_20250124()` |
| Reasoning model support | Stable | `reasoning` field in result |
| MCP native client | Experimental | `experimental_createMcpClient` |
| Image editing | Stable (v6) | `images` param in `generateImage` |
| Reranking | Stable (v6) | `rerank()` function |
| DevTools | Stable (v6) | `devToolsMiddleware()` |
| LangChain adapter rewrite | Stable (v6) | `@ai-sdk/langchain` v2 |
| StandardSchema V1 | Stable (v6) | Arktype, Valibot as tool schemas |

---

## thegent / trace Integration

- **trace web frontend**: uses `@trpc/client` for API calls — AI SDK is server-side only in this stack
- **thegent proxy layer**: AI SDK patterns used for provider-agnostic model access
- **Common provider**: OpenRouter (`@ai-sdk/openai-compatible`) as unified gateway
- **MCP integration**: `experimental_createMcpClient` connects to thegent MCP server on port 3847

---

## Known Issues / Gotchas

1. **`sdk.vercel.ai` deprecated**: Redirects to `ai-sdk.dev`. Update bookmarks and configs.
2. **v5 to v6 migration**: Run `npx @ai-sdk/codemod upgrade v6` — handles most breaking changes automatically.
3. **`maxSteps` required for tools**: Without `maxSteps`, tool calls stop after first round; no automatic continuation.
4. **Streaming + structured output**: `streamObject` is separate from `streamText`; cannot mix in a single call.
5. **Provider options**: Features like prompt caching require `providerOptions` — check provider-specific docs.
6. **`useChat` transport**: Default endpoint is `/api/chat` — must create matching API route.
7. **Tool approval + `useChat`**: When `needsApproval: true`, call `addToolOutput()` in the UI to resume after human approval.

---

## Sources & References

- **Official Docs**: https://ai-sdk.dev/docs (fetched 2026-02-20)
- **AI SDK 6 Announcement**: https://vercel.com/blog/ai-sdk-6 (fetched 2026-02-20)
- **GitHub**: https://github.com/vercel/ai (fetched 2026-02-20)
- **generateText Reference**: https://ai-sdk.dev/docs/reference/ai-sdk-core/generate-text (fetched 2026-02-20)
- **useChat Reference**: https://ai-sdk.dev/docs/reference/ai-sdk-ui/use-chat (fetched 2026-02-20)
- **npm `ai` package**: https://www.npmjs.com/package/ai (v6.0.94, fetched 2026-02-20)
- **Last Verified**: 2026-02-20

See also: `docs/context/openrouter.md`, `docs/context/vercel-ai-gateway.md`

---

## Quick Reference

| Item | Value |
|------|-------|
| Install | `npm install ai @ai-sdk/openai` |
| Latest version | `ai@6.0.94` |
| Docs URL | `https://ai-sdk.dev/docs` |
| Migration codemod | `npx @ai-sdk/codemod upgrade v6` |
| DevTools | `npx @ai-sdk/devtools` — viewer at `localhost:4983` |

### Core Function Cheat Sheet

```typescript
// Text generation (non-streaming)
const { text } = await generateText({ model, prompt, tools, maxSteps });

// Streaming text
const stream = streamText({ model, messages });
for await (const chunk of stream.textStream) { ... }
return stream.toDataStreamResponse();   // For Next.js

// Structured output
const { object } = await generateObject({ model, schema, prompt });
const stream = streamObject({ model, schema, prompt });

// Embeddings
const { embedding } = await embed({ model: openai.embedding('text-embedding-3-small'), value });

// Image generation
const { image } = await generateImage({ model: openai.image('dall-e-3'), prompt });

// Agents (v6)
const agent = new ToolLoopAgent({ model, instructions, tools });
const result = await agent.generate({ prompt });

// Reranking (v6)
const { rerankedDocuments } = await rerank({ model: cohere.rerank('rerank-v3.5'), query, documents });
```

### Provider Quick Lookup

| Provider | Import | Model string |
|----------|--------|-------------|
| OpenAI | `@ai-sdk/openai` | `'gpt-4o'`, `'gpt-4o-mini'`, `'o1'` |
| Anthropic | `@ai-sdk/anthropic` | `'claude-opus-4-6'`, `'claude-sonnet-4.5'` |
| Google | `@ai-sdk/google` | `'gemini-2.0-flash'`, `'gemini-2.0-pro'` |
| xAI | `@ai-sdk/xai` | `'grok-3'`, `'grok-3-mini'` |
| OpenRouter | `@ai-sdk/openai-compatible` | `createOpenAICompatible({baseURL: 'https://openrouter.ai/api/v1', ...})` |
| Vercel Gateway | `@ai-sdk/vercel` | `createVercel({apiKey: ...})` |

---

## Source: context/workos-authkit.md

# WorkOS AuthKit Context

> Definitive reference for WorkOS AuthKit — hosted and embedded authentication UI plus the WorkOS Python SDK for user management.
> Sources: workos.com/docs/authkit, workos.com/docs/user-management/vanilla/python, workos.com/docs/sdks/python, github.com/workos/authkit-nextjs, github.com/workos/python-authkit-example (fetched 2026-02-20).

---

## What is AuthKit

**AuthKit** is WorkOS's authentication layer built on top of the WorkOS User Management API. It provides:

1. **Hosted AuthKit** — Redirect users to a WorkOS-hosted sign-in page (zero frontend UI work)
2. **Embedded Components** — React components for rendering sign-in/sign-up forms in your own UI
3. **Python SDK** — Server-side session management, user lookup, org membership, SSO, MFA

AuthKit sits on top of **WorkOS User Management**, which is the REST API and SDK layer for managing users, organizations, SSO connections, and directory sync. AuthKit specifically refers to the auth UI and session flow; User Management refers to the underlying CRUD/admin API.

**Distinction: AuthKit vs WorkOS User Management**

| Layer | Purpose | SDK Entry Point |
|-------|---------|-----------------|
| AuthKit | Sign-in/sign-up UI flows, session cookies | `workos.user_management.get_authorization_url()` |
| User Management | CRUD: users, orgs, memberships, invitations | `workos.user_management.*` |
| SSO | SAML/OIDC enterprise connections | `workos.sso.*` |
| Directory Sync | SCIM provisioning | `workos.directory_sync.*` |

**thegent Use Case:** AuthKit authenticates thegent dashboard users and CLI operators; the Python SDK validates sessions on protected routes; WorkOS manages org-level isolation for multi-tenant agent workspaces.

---

## Key Concepts

| Term | Definition |
|------|-----------|
| **Sealed session** | Encrypted JWT stored in HTTP-only cookie; encrypted with `WORKOS_COOKIE_PASSWORD` |
| **Authorization URL** | WorkOS-hosted sign-in page URL; generated server-side, user redirected here |
| **Code exchange** | OAuth callback: exchange `code` param for access/refresh tokens and user info |
| **Organization** | A WorkOS entity grouping users; maps to a customer/tenant |
| **SSO Connection** | SAML/OIDC identity provider (IdP) linked to an organization |
| **MFA enrollment** | Per-user MFA devices; enforced via AuthKit automatically when enabled |
| **Cookie password** | 32+ character string used as HMAC key to encrypt session cookies |
| **Admin Portal** | WorkOS-hosted UI for org admins to manage SSO, Directory Sync, Audit Log |

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `WORKOS_API_KEY` | Yes | Server-side API key (`sk_live_...` or `sk_test_...`) |
| `WORKOS_CLIENT_ID` | Yes | Application client ID (`default_org_...`) |
| `WORKOS_COOKIE_PASSWORD` | Yes | 32+ char string for cookie encryption |
| `WORKOS_REDIRECT_URI` | Yes | OAuth callback URL registered in WorkOS dashboard |

**Generate cookie password:**
```bash
openssl rand -hex 16   # Returns 32-char hex string
python3 -c "import secrets; print(secrets.token_hex(16))"
```

---

## Installation

### Python SDK

```bash
pip install workos
# Current stable: workos >= 5.40.0
```

### Node.js / Next.js SDK

```bash
npm install @workos-inc/authkit-nextjs
bun add @workos-inc/authkit-nextjs
```

### React Components (Embedded)

```bash
npm install @workos-inc/authkit-react
bun add @workos-inc/authkit-react
```

---

## Python SDK: WorkOSClient

### Initialization

```python
import os
from workos import WorkOSClient

workos = WorkOSClient(
    api_key=os.getenv("WORKOS_API_KEY"),
    client_id=os.getenv("WORKOS_CLIENT_ID"),
)
```

### Authentication Flow (Authorization Code)

**Step 1: Generate authorization URL**

```python
# Generate the WorkOS-hosted sign-in page URL
authorization_url = workos.user_management.get_authorization_url(
    provider="authkit",           # Use AuthKit hosted UI
    redirect_uri="http://localhost:3000/callback",
    # Optional: pre-select organization for SSO
    organization_id="org_01ARZ...",
    # Optional: pass state for CSRF protection
    state="random_csrf_token",
)
# Redirect user to this URL
```

**Step 2: Handle callback — exchange code for session**

```python
from flask import request, redirect, make_response

cookie_password = os.getenv("WORKOS_COOKIE_PASSWORD")

@app.route("/callback")
def callback():
    code = request.args.get("code")

    # Exchange code for sealed session (encrypted cookie value)
    auth_response = workos.user_management.authenticate_with_code(
        code=code,
        session={
            "seal_session": True,
            "cookie_password": cookie_password,
        },
    )

    # auth_response.sealed_session  → encrypted string to store in cookie
    # auth_response.user            → User object
    # auth_response.access_token    → raw access token (if needed)
    # auth_response.refresh_token   → raw refresh token

    response = make_response(redirect("/dashboard"))
    response.set_cookie(
        "wos-session",
        auth_response.sealed_session,
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=60 * 60 * 24 * 7,  # 7 days
    )
    return response
```

**Step 3: Validate session on protected routes**

```python
from workos.user_management import AuthenticationResponse, SessionStatus

@app.route("/dashboard")
def dashboard():
    sealed_session = request.cookies.get("wos-session")
    if not sealed_session:
        return redirect("/login")

    # Load and authenticate sealed session
    session = workos.user_management.load_sealed_session(
        sealed_session=sealed_session,
        cookie_password=cookie_password,
    )

    auth_result = session.authenticate()
    # auth_result.authenticated: bool
    # auth_result.reason: str (why failed, if not authenticated)
    # auth_result.user: User | None
    # auth_result.session_id: str

    if not auth_result.authenticated:
        return redirect("/login")

    user = auth_result.user
    return f"Hello, {user.email}"
```

**Step 4: Refresh session**

```python
# Call when session is approaching expiry or after role changes
result = session.refresh()
# Returns new sealed_session; update cookie with new value

new_response = make_response(redirect("/dashboard"))
new_response.set_cookie("wos-session", result.sealed_session, ...)
```

**Step 5: Sign out**

```python
@app.route("/logout")
def logout():
    sealed_session = request.cookies.get("wos-session")
    session = workos.user_management.load_sealed_session(
        sealed_session=sealed_session,
        cookie_password=cookie_password,
    )

    # Get WorkOS logout URL (invalidates server-side session)
    logout_url = session.get_logout_url()

    response = make_response(redirect(logout_url))
    response.delete_cookie("wos-session")
    return response
```

---

## Python SDK: Key Methods Reference

### `workos.user_management`

| Method | Description | Returns |
|--------|-------------|---------|
| `get_authorization_url(provider, redirect_uri, ...)` | Generate hosted sign-in URL | `str` |
| `authenticate_with_code(code, session=...)` | Exchange OAuth code for tokens/session | `AuthenticationResponse` |
| `load_sealed_session(sealed_session, cookie_password)` | Deserialize sealed cookie | `Session` |
| `get_user(user_id)` | Fetch user by ID | `User` |
| `list_users(email=None, organization_id=None, limit=10)` | List users with filters | `ListUsersResponse` |
| `create_user(email, password=None, first_name=None, ...)` | Programmatically create user | `User` |
| `update_user(user_id, first_name=None, ...)` | Update user attributes | `User` |
| `delete_user(user_id)` | Delete user | `None` |
| `list_organization_memberships(user_id=None, organization_id=None)` | List org memberships | `ListMembershipsResponse` |
| `create_organization_membership(user_id, organization_id, role_slug=None)` | Add user to org | `OrganizationMembership` |
| `send_invitation(email, organization_id=None)` | Invite user by email | `Invitation` |
| `authenticate_with_magic_auth(code, email)` | Magic link code exchange | `AuthenticationResponse` |
| `send_magic_auth_code(email)` | Send magic link | `None` |
| `enroll_auth_factor(user_id, type="totp")` | Enroll MFA factor | `EnrollAuthFactorResponse` |
| `verify_auth_factor(auth_factor_id, code)` | Verify MFA code | `VerifyAuthFactorResponse` |

### `Session` object methods

| Method | Description | Returns |
|--------|-------------|---------|
| `session.authenticate()` | Validate and return auth info | `SessionAuthentication` |
| `session.refresh()` | Refresh tokens, return new sealed session | `RefreshSessionResponse` |
| `session.get_logout_url()` | Get WorkOS logout URL | `str` |

### `AuthenticationResponse` fields

```python
auth_response.user              # User object
auth_response.organization_id   # str | None
auth_response.access_token      # str (raw JWT)
auth_response.refresh_token     # str (raw refresh)
auth_response.sealed_session    # str (encrypted; store as cookie)
```

### `User` object fields

```python
user.id                   # "user_01ARZ..."
user.email                # "alice@example.com"
user.email_verified       # bool
user.first_name           # str | None
user.last_name            # str | None
user.profile_picture_url  # str | None
user.created_at           # datetime
user.updated_at           # datetime
user.external_id          # str | None (SCIM or external mapping)
```

---

## SSO (SAML / OIDC) Integration

### SSO Authorization URL

```python
# For org-specific SSO (SAML/OIDC IdP)
authorization_url = workos.user_management.get_authorization_url(
    provider="authkit",
    redirect_uri="http://localhost:3000/callback",
    organization_id="org_01ARZ...",  # Required for SSO
)
```

WorkOS automatically routes to the correct IdP (SAML/OIDC) based on the organization's SSO connection. After SAML assertion, WorkOS creates/updates the WorkOS user and issues tokens.

### SSO Connection Management

```python
# List SSO connections for an org
connections = workos.sso.list_connections(
    organization_id="org_01ARZ...",
    limit=20,
)
for conn in connections.data:
    print(conn.id, conn.provider, conn.status)  # "active" | "inactive" | "draft"
```

---

## Webhook Events

WorkOS sends webhooks for auth events. Register webhook endpoint in the WorkOS dashboard.

### Webhook Verification

```python
from workos import WorkOSClient

workos = WorkOSClient(api_key=os.getenv("WORKOS_API_KEY"))

@app.route("/webhooks/workos", methods=["POST"])
def handle_webhook():
    payload = request.data.decode("utf-8")
    signature = request.headers.get("WorkOS-Signature")
    webhook_secret = os.getenv("WORKOS_WEBHOOK_SECRET")

    try:
        event = workos.webhooks.construct_event(
            payload=payload,
            sig_header=signature,
            secret=webhook_secret,
            tolerance=180,  # seconds
        )
    except Exception as e:
        return {"error": str(e)}, 400

    # event.event: str (event type)
    # event.data: dict (payload)
    handle_event(event)
    return {"received": True}, 200
```

### Key Webhook Events

| Event | Trigger |
|-------|---------|
| `user.created` | New user registered |
| `user.updated` | User profile changed |
| `user.deleted` | User removed |
| `session.created` | New session started |
| `connection.activated` | SSO connection enabled |
| `dsync.user.created` | SCIM-provisioned user |
| `dsync.user.updated` | SCIM user attribute change |
| `invitation.accepted` | User accepted org invite |

---

## Admin Portal

The Admin Portal is a WorkOS-hosted UI for end customers (org admins) to configure their own SSO, Directory Sync, and Audit Log settings without code.

```python
# Generate Admin Portal link for an organization
portal_link = workos.portal.generate_link(
    organization="org_01ARZ...",
    intent="sso",           # "sso" | "dsync" | "audit_logs" | "log_streams"
    return_url="https://app.example.com/settings",
    success_url="https://app.example.com/settings/success",
)
# portal_link.link → URL to redirect org admin to
```

---

## Node.js / Next.js SDK (authkit-nextjs)

### Setup

```typescript
// lib/auth.ts
import { authkit } from '@workos-inc/authkit-nextjs';

export const { getSession, withAuth } = authkit({
    clientId: process.env.WORKOS_CLIENT_ID!,
    clientSecret: process.env.WORKOS_CLIENT_SECRET!,
    apiKeySecret: process.env.WORKOS_API_KEY!,
    redirectUri: process.env.WORKOS_REDIRECT_URI!,
    cookiePassword: process.env.WORKOS_COOKIE_PASSWORD!,
    cookieMaxAge: 60 * 60 * 24 * 7,  // 7 days (default)
});
```

### Middleware Protection

```typescript
// middleware.ts
import { authkitMiddleware } from '@workos-inc/authkit-nextjs';

export default authkitMiddleware({
    publicRoutes: ['/', '/login', '/signup', '/api/public/*'],
});

export const config = {
    matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
};
```

### Server Components

```typescript
// app/dashboard/page.tsx
import { getSession } from '@/lib/auth';
import { redirect } from 'next/navigation';

export default async function Dashboard() {
    const session = await getSession();
    if (!session) redirect('/login');

    return <h1>Hello {session.user.email}</h1>;
}
```

### React Embedded Components

```tsx
// Embedded sign-in form (no redirect to WorkOS UI)
import { SignIn } from '@workos-inc/authkit-react';

export function LoginPage() {
    return <SignIn />;
}
```

---

## Authentication

WorkOS API uses Bearer token authentication on all server-side calls:

```
Authorization: Bearer sk_live_...
```

Rate limits: Not publicly documented; contact WorkOS for enterprise limits. Use exponential backoff on 429 responses.

---

## 2026 Beta / Recent Features (as of 2026-02-20)

- **Python AuthKit example app** — Official sample at `github.com/workos/python-authkit-example` using Flask + sealed sessions
- **Composable Middleware (Node)** — `authkitMiddleware` supports custom proxy helpers for auth composition
- **TokenRefreshError Enhancement** — Now includes `userId` and `sessionId` fields for debugging
- **Next.js 15 parity** — Full App Router, Server Actions, and React 19 support
- **Python SDK v5.40+** — Latest stable; `workos >= 5.40.0` in trace project

---

## thegent / trace Integration

- **trace project**: `workos>=5.40.0` in `pyproject.toml`; `@workos-inc/authkit-react@^0.16.0` in web app frontend
- **thegent**: WorkOS manages dashboard user auth and org-level access isolation
- **Pattern**: Python backend uses `WorkOSClient` + sealed sessions; Next.js frontend uses `authkit-nextjs` with middleware

---

## Known Issues / Gotchas

1. **Cookie password length**: Must be exactly 32+ characters; shorter values cause silent decryption failures at runtime.
2. **Sealed session expiry**: `session.authenticate()` returns `authenticated=False` with reason `"session_expired"` when the session has expired; always check `auth_result.reason`.
3. **SSO requires organization_id**: `get_authorization_url()` without `organization_id` shows generic AuthKit UI; SSO routing only activates when org is specified.
4. **Webhook tolerance**: Default tolerance is 180 seconds; clock skew > 3 minutes causes webhook rejections.
5. **Multiple org memberships**: A user can belong to multiple organizations; `session.authenticate()` returns the active session's org only — use `list_organization_memberships()` to get all.
6. **Python SDK vs Node SDK parity**: Python SDK `authenticate_with_code()` is the equivalent of Node's `handleAuth()`; both produce sealed sessions.

---

## Sources & References

- **WorkOS AuthKit (Python)**: https://workos.com/docs/authkit/vanilla/python (fetched 2026-02-20)
- **WorkOS User Management (Python)**: https://workos.com/docs/user-management/vanilla/python (fetched 2026-02-20)
- **WorkOS Python SDK Docs**: https://workos.com/docs/sdks/python (fetched 2026-02-20)
- **WorkOS API Reference**: https://workos.com/docs/reference (fetched 2026-02-20)
- **authkit-nextjs GitHub**: https://github.com/workos/authkit-nextjs (fetched 2026-02-20)
- **python-authkit-example**: https://github.com/workos/python-authkit-example (fetched 2026-02-20)
- **authkit-react npm**: `@workos-inc/authkit-react@^0.16.0`
- **Last Verified**: 2026-02-20

See also: `docs/context/workos.md` (enterprise SSO/SCIM reference)

---

## Quick Reference

| Item | Value |
|------|-------|
| Python package | `workos >= 5.40.0` |
| Node package | `@workos-inc/authkit-nextjs` |
| React package | `@workos-inc/authkit-react` |
| Auth pattern | Authorization Code + Sealed Session Cookie |
| Cookie encryption | HMAC-SHA256 with 32+ char `WORKOS_COOKIE_PASSWORD` |
| Session TTL | 7 days default (configurable) |
| Base API URL | `https://api.workos.com` |
| Auth header | `Authorization: Bearer $WORKOS_API_KEY` |
| Webhook header | `WorkOS-Signature` |

### Quick Python Session Flow

```python
# 1. Redirect to AuthKit
url = workos.user_management.get_authorization_url(
    provider="authkit", redirect_uri=REDIRECT_URI)
redirect(url)

# 2. Exchange code (in /callback)
auth = workos.user_management.authenticate_with_code(
    code=code, session={"seal_session": True, "cookie_password": COOKIE_PWD})
set_cookie("wos-session", auth.sealed_session)

# 3. Validate on each request
session = workos.user_management.load_sealed_session(
    sealed_session=cookie, cookie_password=COOKIE_PWD)
result = session.authenticate()
if not result.authenticated:
    redirect("/login")
user = result.user
```

### Common Patterns

- **SSO**: Pass `organization_id` to `get_authorization_url()`; WorkOS routes to correct IdP
- **Refresh**: Call `session.refresh()` when `auth_result.reason == "session_expired"`
- **Logout**: `session.get_logout_url()` → redirect → delete cookie
- **Webhooks**: Verify with `workos.webhooks.construct_event(payload, sig, secret, tolerance=180)`

---

## Source: context/workos.md

# WorkOS API Context

> Definitive reference for implementing WorkOS enterprise auth and directory features for thegent multi-tenant deployments.
> Sources: workos.com/docs (fetched 2026-02-20).

---

## What is WorkOS

WorkOS is an enterprise-focused authentication and identity management platform providing single sign-on (SSO), directory sync, admin portals, audit logs, and user management—enabling applications to become enterprise-ready without building custom enterprise IAM.

**Key capabilities:**
- **Single Sign-On (SSO):** SAML and OIDC support for any organization's identity provider
- **Directory Sync:** Provision users/groups from Google Workspace, Microsoft Entra ID, and other SCIM providers
- **Admin Portal:** Hosted UI for IT admins to configure SSO/Directory Sync without vendor support
- **User Management:** AuthKit for password and magic link authentication
- **Audit Logs:** Track identity and access events for compliance
- **Organizations:** Multi-tenant organization management with domain verification

**Pricing (2026):** $125/month per SSO connection; $125/month per Directory Sync connection.

---

## Core Concepts

### Organizations

An **organization** represents a customer/tenant in your application. WorkOS associates connections, users, and domains with organizations.

```
Organization
├── Domains (verified)
├── Connections
│   ├── SSO (SAML/OIDC)
│   ├── Directory Sync (SCIM)
│   └── OAuth (User Management)
└── Users & Groups
```

### Connections

A **connection** links an organization to an identity provider:
- **SSO Connection:** Maps to a customer's SAML IdP or OIDC provider
- **Directory Sync Connection:** Syncs users/groups from a SCIM provider (Google Workspace, Entra ID)
- **OAuth Connection:** Enables password and magic link login via AuthKit

### Authentication Flows

| Type | Protocol | Use Case |
|------|----------|----------|
| **SSO** | SAML 2.0, OIDC | Enterprise users authenticate via corporate IdP |
| **Directory Sync** | SCIM | Automated user/group provisioning from HR/directory |
| **AuthKit** | OAuth 2.0 | App-native password/magic link auth for smaller orgs |

### Authentication Credentials

Two credentials identify your application to WorkOS:

| Credential | Purpose | Example |
|----------|---------|---------|
| **client_id** | Public application identifier | `default_organization_01ARZ3NDEKTSV4RRFFQ6WQ4` |
| **client_secret** / **API Key** | Secret authentication token | `sk_live_...` (API key) |

Obtain from WorkOS dashboard: `https://dashboard.workos.com/api-keys`

---

## Authentication & API Keys

### API Key Header

All WorkOS API requests require the `Authorization` header with API key:

```
Authorization: Bearer <API_KEY>
```

**Example:**
```bash
curl -H "Authorization: Bearer sk_live_..." \
  https://api.workos.com/organizations
```

### Environment Variables

Recommended setup for thegent integrations:

```bash
# Required
WORKOS_API_KEY=sk_live_...           # API key for server-side requests
WORKOS_CLIENT_ID=default_organization_...

# Optional (for AuthKit)
WORKOS_CLIENT_SECRET=...             # For OAuth code exchange
WORKOS_REDIRECT_URI=https://app.example.com/auth/callback
```

### API Key Introspection

Check API key status and rate limits:

```
GET https://api.workos.com/keys/{key_id}
Authorization: Bearer <API_KEY>

Response:
{
  "id": "api_key_01ARZ...",
  "name": "Production API Key",
  "created_at": "2024-01-15T10:00:00Z",
  "active": true,
  "rate_limit": {
    "requests_per_minute": 600,
    "requests_per_second": 10
  }
}
```

---

## Base URL

```
https://api.workos.com
```

All endpoints are relative to this base.

---

## Organizations Endpoint

### GET /organizations

List all organizations.

```
GET https://api.workos.com/organizations
Authorization: Bearer <API_KEY>
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `limit` | integer | Max results (default 10, max 100) |
| `before` / `after` | string | Cursor for pagination |

**Response:**

```json
{
  "object": "list",
  "data": [
    {
      "id": "org_01ARZ3NDEKTSV4RRFFQ6WQ4",
      "object": "organization",
      "name": "Acme Corp",
      "domains": [
        {
          "id": "org_domain_01ARZ...",
          "object": "organization_domain",
          "domain": "acme.com",
          "verified_at": "2024-01-15T10:00:00Z"
        }
      ],
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "list_metadata": {
    "before": null,
    "after": "org_01ARZ3ND..."
  }
}
```

### POST /organizations

Create a new organization.

```
POST https://api.workos.com/organizations
Authorization: Bearer <API_KEY>
Content-Type: application/json

{
  "name": "Acme Corp",
  "domain_data": {
    "domain": "acme.com"
  }
}
```

**Response:** Same structure as GET single organization.

### GET /organizations/{id}

Get organization details.

```
GET https://api.workos.com/organizations/org_01ARZ3NDEKTSV4RRFFQ6WQ4
Authorization: Bearer <API_KEY>
```

---

## Single Sign-On (SSO)

### SSO Authorization Endpoints

#### 1. Create Authorization URL

Direct users to WorkOS SSO:

```
GET https://api.workos.com/sso/authorize
  ?client_id=<client_id>
  &organization_id=<org_id>  [or domain=<domain>]
  &redirect_uri=<callback_url>
  &response_type=code
  &state=<random_state>
```

**Parameters:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `client_id` | Yes | Your WorkOS client_id |
| `organization_id` | One of | Organization ID |
| `domain` | One of | Organization domain (alternative) |
| `redirect_uri` | Yes | Callback URL (must match registered) |
| `response_type` | Yes | Always `code` |
| `state` | Recommended | CSRF protection token |

**Redirect Flow:**
```
User → Your App → /authorize
       Your App → WorkOS SSO
       WorkOS → User authenticates with IdP
       WorkOS → Redirect to your callback with code + state
       Your App → Exchange code for session
```

#### 2. Authorization Code Exchange

Exchange code for session:

```
POST https://api.workos.com/sso/code
Authorization: Bearer <API_KEY>
Content-Type: application/json

{
  "client_id": "<client_id>",
  "code": "<authorization_code>"
}
```

**Response:**

```json
{
  "id": "ses_01ARZ3NDEKTSV4RRFFQ6WQ4",
  "object": "sso_session",
  "user": {
    "id": "user_01ARZ3NDEKTSV4RRFFQ6WQ4",
    "object": "user",
    "email": "john@acme.com",
    "first_name": "John",
    "last_name": "Doe",
    "email_verified": true
  },
  "organization_id": "org_01ARZ3NDEKTSV4RRFFQ6WQ4",
  "authentication_method": "SAML"
}
```

### SSO Connections

#### GET /sso_connections

List SSO connections for an organization.

```
GET https://api.workos.com/sso_connections
  ?organization_id=org_01ARZ3NDEKTSV4RRFFQ6WQ4
Authorization: Bearer <API_KEY>
```

**Response:**

```json
{
  "object": "list",
  "data": [
    {
      "id": "conn_01ARZ3NDEKTSV4RRFFQ6WQ4",
      "object": "sso_connection",
      "organization_id": "org_01ARZ3NDEKTSV4RRFFQ6WQ4",
      "connection_type": "SAML",
      "name": "Acme SAML",
      "created_at": "2024-01-15T10:00:00Z",
      "status": "established"
    }
  ]
}
```

---

## Directory Sync

### Directory Sync Connections

#### GET /directory_sync_connections

List Directory Sync connections.

```
GET https://api.workos.com/directory_sync_connections
  ?organization_id=org_01ARZ3NDEKTSV4RRFFQ6WQ4
Authorization: Bearer <API_KEY>
```

**Response:**

```json
{
  "object": "list",
  "data": [
    {
      "id": "dir_conn_01ARZ...",
      "object": "directory_sync_connection",
      "organization_id": "org_01ARZ...",
      "name": "Google Workspace",
      "directory_provider": "google_workspace",
      "status": "linked",
      "created_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

### Directory Sync Users

#### GET /directory_users

List provisioned users from Directory Sync.

```
GET https://api.workos.com/directory_users
  ?directory_id=dir_conn_01ARZ...
Authorization: Bearer <API_KEY>
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `directory_id` | string | Directory connection ID |
| `limit` | integer | Pagination (default 10, max 100) |
| `before` / `after` | string | Cursor |

**Response:**

```json
{
  "object": "list",
  "data": [
    {
      "id": "dir_usr_01ARZ...",
      "object": "directory_user",
      "directory_id": "dir_conn_01ARZ...",
      "external_id": "goog_01ARZ...",
      "emails": [
        { "address": "john@acme.com", "primary": true }
      ],
      "first_name": "John",
      "last_name": "Doe",
      "idp_metadata": {
        "title": "Engineer",
        "department": "Engineering"
      },
      "state": "active",
      "created_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

### Directory Sync Groups

#### GET /directory_groups

List provisioned groups.

```
GET https://api.workos.com/directory_groups
  ?directory_id=dir_conn_01ARZ...
Authorization: Bearer <API_KEY>
```

**Response:**

```json
{
  "object": "list",
  "data": [
    {
      "id": "dir_grp_01ARZ...",
      "object": "directory_group",
      "directory_id": "dir_conn_01ARZ...",
      "external_id": "goog_grp_01ARZ...",
      "name": "Engineering",
      "display_name": "Engineering Team",
      "created_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

### Directory Sync Webhooks

WorkOS sends webhook events for user/group changes:

```json
{
  "id": "evt_01ARZ...",
  "type": "dsync.user.created",
  "created_at": "2024-01-15T10:00:00Z",
  "data": {
    "object": "directory_user",
    "id": "dir_usr_01ARZ...",
    "directory_id": "dir_conn_01ARZ...",
    "emails": [{ "address": "new@acme.com", "primary": true }],
    "first_name": "New",
    "last_name": "User",
    "state": "active"
  }
}
```

**Event Types:**
- `dsync.user.created`
- `dsync.user.updated`
- `dsync.user.deleted`
- `dsync.group.created`
- `dsync.group.updated`
- `dsync.group.deleted`

---

## Admin Portal

### Admin Portal Links

The Admin Portal provides a hosted UI for IT admins to configure SSO/Directory Sync without vendor support.

#### POST /admin_portal_authorizations

Create an authorization link for the Admin Portal (5-minute expiration).

```
POST https://api.workos.com/admin_portal_authorizations
Authorization: Bearer <API_KEY>
Content-Type: application/json

{
  "organization_id": "org_01ARZ3NDEKTSV4RRFFQ6WQ4",
  "environment_id": "env_..."  [optional]
}
```

**Response:**

```json
{
  "object": "admin_portal_authorization",
  "id": "auth_01ARZ...",
  "organization_id": "org_01ARZ...",
  "authorization_url": "https://admin.workos.com/authorize?code=auth_01ARZ...",
  "created_at": "2024-01-15T10:00:00Z",
  "expires_at": "2024-01-15T10:05:00Z"
}
```

**Use Cases:**
- Embed in customer dashboard: `<a href="{authorization_url}">Configure SSO</a>`
- Expires in 5 minutes; generate fresh link per request

### Admin Portal Features

From within the portal, IT admins can:

| Feature | Capability |
|---------|-----------|
| **Domain Verification** | Add DNS records proving organizational domain ownership |
| **SSO Management** | Test connections, view session details, edit configuration, reset connections |
| **Directory Sync** | Monitor sync status, manage attribute mappings, select groups, review synced users |
| **User Management** | Manage users, set roles, configure email domains |

---

## Audit Logs

### GET /audit_logs

Retrieve audit log events for compliance tracking.

```
GET https://api.workos.com/audit_logs
  ?organization_id=org_01ARZ3NDEKTSV4RRFFQ6WQ4
  &limit=10
  &after=audit_log_01ARZ...
Authorization: Bearer <API_KEY>
```

**Response:**

```json
{
  "object": "list",
  "data": [
    {
      "object": "audit_log",
      "id": "audit_log_01ARZ...",
      "organization_id": "org_01ARZ...",
      "action": "sso.user.authenticated",
      "actor": {
        "type": "user",
        "id": "user_01ARZ..."
      },
      "targets": [
        {
          "type": "organization",
          "id": "org_01ARZ..."
        }
      ],
      "result": "success",
      "occurred_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

---

## User Management (AuthKit)

WorkOS provides user creation, password management, and magic link authentication.

### POST /users

Create a user.

```
POST https://api.workos.com/users
Authorization: Bearer <API_KEY>
Content-Type: application/json

{
  "organization_id": "org_01ARZ3NDEKTSV4RRFFQ6WQ4",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "password_hash": "bcrypt_hash_...",  [optional]
  "email_verified": false
}
```

### GET /users

List users in an organization.

```
GET https://api.workos.com/users
  ?organization_id=org_01ARZ3NDEKTSV4RRFFQ6WQ4
Authorization: Bearer <API_KEY>
```

---

## SDK Support

WorkOS provides official SDKs:

| Language | Package | Installation |
|----------|---------|--------------|
| **Python** | `workos` | `pip install workos` |
| **Node.js** | `@workos-inc/node` | `npm install @workos-inc/node` |
| **Go** | `github.com/workos/workos-go` | Import from Go modules |
| **Java** | `com.workos:workos` | Maven/Gradle dependency |
| **.NET** | `WorkOS.Net` | NuGet package |

### Python Example

```python
from workos import WorkOS

workos = WorkOS(api_key="sk_live_...")

# Create organization
org = workos.organizations.create(
    name="Acme Corp",
    domain_data={"domain": "acme.com"}
)

# Create SSO authorization URL
auth_url = workos.sso.authorization_url(
    client_id="default_organization_...",
    organization_id=org.id,
    redirect_uri="https://app.example.com/auth/callback"
)

# Exchange code for session
session = workos.sso.get_profile(code=auth_code)
print(f"User: {session.user.email}")

# List Directory Sync connections
connections = workos.directory_sync.list_connections(
    organization_id=org.id
)

# List provisioned users
users = workos.directory_sync.list_users(
    directory_id=connections[0].id
)
```

### Node.js Example

```typescript
import { WorkOS } from '@workos-inc/node';

const client = new WorkOS(process.env.WORKOS_API_KEY);

// Get organization
const org = await client.organizations.getOrganization('org_...');

// Create SSO authorization URL
const authUrl = client.sso.getAuthorizationUrl({
  clientId: process.env.WORKOS_CLIENT_ID,
  organizationId: org.id,
  redirectUri: 'https://app.example.com/auth/callback'
});

// Exchange code
const session = await client.sso.getProfile({ code: authCode });

// List Directory Sync users
const users = await client.dirSync.listUsers({
  directoryId: 'dir_conn_...'
});
```

---

## Error Codes

WorkOS API errors return standard HTTP codes with structured error responses:

| Code | Meaning | Details |
|------|---------|---------|
| 200 | Success | Request succeeded |
| 201 | Created | Resource created |
| 204 | No Content | Successful but no response body |
| 400 | Bad Request | Invalid parameters or validation error |
| 401 | Unauthorized | Invalid or missing API key |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource does not exist |
| 409 | Conflict | Resource already exists or state conflict |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Server Error | Internal WorkOS error |
| 503 | Service Unavailable | Service temporarily down |

**Error Response Format:**

```json
{
  "object": "error",
  "code": "invalid_request",
  "message": "Invalid organization_id",
  "request_id": "req_..."
}
```

---

## Rate Limits

Default rate limits per API key:

| Limit | Value |
|-------|-------|
| **Requests per minute** | 600 |
| **Requests per second** | 10 |
| **Concurrent requests** | 100 |

Check rate limit status in response headers:

```
X-RateLimit-Limit: 600
X-RateLimit-Remaining: 599
X-RateLimit-Reset: 1705329600
```

---

## Relevance to thegent

WorkOS enables thegent deployments to support enterprise customers requiring:

1. **Multi-tenant SSO:** Each customer organization authenticates via their corporate IdP (Okta, Azure AD, etc.)
2. **Directory Sync:** Automated user provisioning from SCIM providers; eliminates manual user management
3. **Admin Portal:** Customers self-configure SSO/Directory Sync without vendor support
4. **Audit Logs:** Track authentication and authorization events for compliance
5. **User Management:** Fallback password/magic link auth for non-enterprise tiers

**Integration Points:**
- Web dashboard: Use WorkOS AuthKit (covered in `workos-authkit.md`)
- CLI server: Validate organization from JWT; route requests per organization
- Webhook handlers: Sync Directory Sync users to thegent user database
- Multi-org routing: Use organization_id to isolate data

---

## Sources

- [WorkOS API Reference](https://workos.com/docs/reference)
- [Single Sign-On Documentation](https://workos.com/docs/sso)
- [Directory Sync Documentation](https://workos.com/docs/directory-sync)
- [Admin Portal Documentation](https://workos.com/docs/admin-portal)
- [User Management (AuthKit)](https://workos.com/docs/user-management)
- [Audit Logs](https://workos.com/docs/audit-logs)
- [GitHub: workos-python](https://github.com/workos/python-sdk)
- [GitHub: workos-node](https://github.com/workos/workos-node)

---
