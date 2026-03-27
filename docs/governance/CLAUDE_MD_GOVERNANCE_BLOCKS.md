# CLAUDE.md Governance Blocks — Centralization Guide

## Overview

Six governance policy blocks appear identically in 30+ Phenotype repository `CLAUDE.md` files.
This document describes how they are centralized in `thegent` and how to keep repos in sync.

## Canonical Block Locations

All canonical block files live at:

```
thegent/templates/claude/governance-blocks/
  README.md                    — This system, usage guide, sync script
  shared-reuse-protocol.md     — PHENOTYPE_SHARED_REUSE_PROTOCOL
  git-delivery-protocol.md     — PHENOTYPE_GIT_DELIVERY_PROTOCOL
  longterm-stability.md        — PHENOTYPE_LONGTERM_STABILITY_PROTOCOL
  github-actions-billing.md    — GitHub Actions Billing Constraint
  ci-completeness.md           — CI Completeness Policy
  child-agent-delegation.md    — Child-Agent and Delegation Policy
```

A fully-assembled `CLAUDE.md` template for new repos is at:

```
thegent/templates/claude/repo-claude-md.template.md
```

## Block Descriptions

### PHENOTYPE_SHARED_REUSE_PROTOCOL (`shared-reuse-protocol.md`)

Instructs agents to treat all repos as part of a shared org, identify cross-repo reuse
opportunities, prefer extraction over duplication, and execute forward-only migrations.

### PHENOTYPE_GIT_DELIVERY_PROTOCOL (`git-delivery-protocol.md`)

Mandates branch-based delivery, stacked PRs, linear scoped PRs, CI enforcement before merge,
review thread resolution, and rebasing to keep branches current.

### PHENOTYPE_LONGTERM_STABILITY_PROTOCOL (`longterm-stability.md`)

Requires durable solutions over quick fixes, no deletions without archiving, clean merge
history, completion of stubs, no merges with failing checks, and follow-up plans for any
quick fix.

### GitHub Actions Billing Constraint (`github-actions-billing.md`)

Informs agents that CI will fail due to account billing limits; they must not block on CI,
must verify quality locally, and may remove required checks or use `--admin` merge when needed.

### CI Completeness Policy (`ci-completeness.md`)

Requires agents to fix ALL CI failures on a PR including pre-existing ones, with the sole
exception of GitHub Actions billing failures.

### Child-Agent and Delegation Policy (`child-agent-delegation.md`)

Requires liberal use of child agents for discovery and high-context work; parent agent focuses
on integration and finalization only.

## Repo CLAUDE.md Structure

Project-specific content occupies the top of `CLAUDE.md`. Shared governance blocks appear
at the bottom after a clearly labelled divider:

```
---
<!-- Shared governance blocks — source: thegent/templates/claude/governance-blocks/ -->
<!-- Do not edit below this line in individual repos. Update the source and re-sync. -->
```

## Sync Procedure

When a governance block changes:

1. Edit the canonical file in `thegent/templates/claude/governance-blocks/`.
2. Commit and merge to `thegent` main.
3. For each affected repo, replace the corresponding section in its `CLAUDE.md` with the
   updated content from the canonical file.

The sync script in `templates/claude/governance-blocks/README.md` can append the full
governance footer to a repo's `CLAUDE.md` in one step.

## Which Repos Have These Blocks

As of 2026-03-26, at least 32 repos under
`/Users/kooshapari/CodeProjects/Phenotype/repos/` contain one or more of these blocks.
Key repos confirmed:

- `agent-devops-setups`, `agentapi-plusplus`, `agentops-policy-federation`
- `bifrost-extensions`, `civ`, `cliproxyapi-plusplus`, `crates`, `docs`
- `heliosApp-colab`, `helMo`, and ~22 more

Run this to enumerate all:

```bash
grep -rl "PHENOTYPE_SHARED_REUSE_PROTOCOL\|PHENOTYPE_GIT_DELIVERY_PROTOCOL\|PHENOTYPE_LONGTERM_STABILITY_PROTOCOL" \
  /Users/kooshapari/CodeProjects/Phenotype/repos/*/CLAUDE.md
```
