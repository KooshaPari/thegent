# PRD: Layered Template Platform Foundation

## Problem

Template setup is repeated across repos, causing drift and maintenance overhead.

## Goal

Create a reusable layered template platform with shared commons, language baselines, and domain overlays.

## Success Criteria

1. Four foundation repos exist with contracts and CI.
2. Reconcile behavior is codified and testable.
3. Existing repos can adopt through non-destructive diff-based reconciliation.
4. Domain wave planning is grounded in current repo inventory.

## Non-Goals

1. Full domain rollout in wave 1.
2. Forced overwrite migration of existing repos.
