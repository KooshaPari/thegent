---
layout: home

hero:
  name: thegent
  text: AI Agent Governance & MCP Server
  tagline: Comprehensive agent lifecycle management and quality governance
  actions:
    - theme: brand
      text: Get Started
      link: /ARCHITECTURE_LAYERS.md
    - theme: alt
      text: View on GitHub
      link: https://github.com

features:
  - title: Agent Governance
    details: Define agent personas, dispatch hooks, enforce quality gates
  - title: MCP Integration
    details: Expose agent capabilities via Model Context Protocol
  - title: Hook System
    details: Lifecycle hooks for pre/post tool execution
  - title: Operator Runbooks
    details: Health checks, incident guides, and verification command packs
  - title: Structured Docs
    details: Tutorials, How-to, Reference, and Explanation lanes for predictable navigation
---

## Who This Documentation Is For

- Operators running shared agent infrastructure.
- Platform engineers integrating multi-agent workflows.
- Internal developers extending core routing and governance.
- Contributors improving reliability, docs, and tooling.

## Start Here

1. [Start Here](/start-here.md) for first-run onboarding.
2. [Tutorials](/tutorials/) for step-by-step first outcomes.
3. [How-to Guides](/how-to/) for task-oriented procedures.
4. [Operations](/operations/) for runbooks and on-call workflows.
5. [API](/api/) and [Reference](/reference/) for command and interface details.

## Fast Verification Commands

```bash
# health
curl -sS http://localhost:8317/health

# model inventory
curl -sS http://localhost:8317/v1/models -H "Authorization: Bearer YOUR_CLIENT_KEY" | jq '.data[:5]'

# provider metrics
curl -sS http://localhost:8317/v1/metrics/providers -H "Authorization: Bearer YOUR_CLIENT_KEY" | jq
```

## See also

- [WORK_STREAM.md](reference/WORK_STREAM.md) — canonical backlog
- [00-MASTER-INDEX.md](plans/00-MASTER-INDEX.md) — plan index
