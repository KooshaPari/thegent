# Specification Draft

## Problem statement

AgilePlus is close to a coherent local development engine, but the operator experience is fragmented:

- CLI supports several core workflows.
- MCP exposes a smaller and partly stubbed set of wrappers.
- API mutations are incomplete for modules and cycles.
- Batch import and migration workflows are missing.
- Release governance is partially aligned to a 5-tier channel model, but the live workflow language is inconsistent.

The target state is a single intuitive workflow surface for:

- specs
- research
- plans
- work packages
- modules
- cycles
- queues/backlogs
- audits/governance
- import/migration
- release promotion
- CI/CD and branch automation

## Scope

### In scope

- CLI, MCP, and API parity for the core AgilePlus entity model.
- Batch import and migration flows for specs and work items.
- Module and cycle write support in the API.
- Real backlog persistence instead of placeholder queue behavior.
- Release-channel normalization to `alpha/canary/beta/rc/prod`.
- Worktree-friendly development and PR flow documentation.
- Org-wide rollout planning for migrating projects into AgilePlus tracking.

### Out of scope for this planning pass

- Implementing every repo migration immediately.
- Rewriting the underlying storage engine.
- Seed SQL as the primary operator path.
- Destructive cleanup of existing worktrees or histories.

## Assumptions

- Existing specs 001-004 remain the canonical feature containers for core platform work.
- The current CLI command model remains the starting point.
- The HTTP API should become the canonical automation surface for batch operations.
- MCP should be a user-facing thin orchestration layer, not a separate source of truth.
- Local worktree development should remain the default authoring environment.

## ARUs

### Assumptions

- The current repo already has enough domain model and workflow scaffolding to support the next layer of automation.
- GH branch structure and reusable workflows can support channel-aware promotion.

### Risks

- MCP and API parity work may expose more stubbed or placeholder code than the initial audit shows.
- Batch imports may require schema and validation changes across multiple crates/packages.
- Canary/high-extreme branch semantics may be inconsistent across repo conventions.
- The existing queue/backlog abstraction may need a storage rewrite rather than a patch.

### Uncertainties

- Which exact import format should be canonical for first release: JSON, YAML, or both.
- Whether the org-wide rollout should be orchestrated through one repo or a dedicated control-plane package.
- How much branch naming policy should be standardized versus adapted per repo.

### Mitigations

- Start with a single canonical import schema and add adapters after the core flow is stable.
- Keep API batch endpoints thin and validation-heavy.
- Document branch/channel policy before changing workflow automation.
- Preserve backward-read compatibility where needed, but do not keep legacy operator paths as the primary UX.

## Desired end state

- A user can create or migrate a project through a CLI, MCP, or HTTP API workflow without touching seed SQL.
- A user can import a backlog/spec bundle, validate it, and apply it with auditability.
- A user can manage modules and cycles through all three surfaces.
- A user can work from a canary/high-extreme local branch and keep pulling the latest branch/package stream while developing in a worktree.
- A user can generate past/present/future state views from the same data model.

