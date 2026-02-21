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
