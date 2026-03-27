# ADR: Foundation-First Layered Template Repos

## Status
Accepted

## Decision
Use separate repositories for:

1. Commons shared layer
2. Language layers
3. Domain layers (follow-up)

Control and orchestration lives in `template-program-ops` with Spec Kitty artifacts.

## Rationale

1. Isolates ownership by concern.
2. Enables independent semver and release cadence.
3. Reduces duplication while preserving composition flexibility.

## Consequences

1. Requires strict manifest compatibility validation.
2. Requires clear dependency graph and upgrade guidance.
