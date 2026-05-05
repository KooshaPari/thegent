# Plan: two-surface-architecture

## Objective

Design a two-surface architecture for Thegent that separates the internal implementation surface from the external public API surface, establishing clear stability contracts for what is stable, transitional, or experimental.

## Approach

1. Inventory all current public interfaces and classify by intended stability (stable, transitional, experimental)
2. Define the two-surface boundary: stable APIs are versioned and backward-compatible; internal surfaces may change freely
3. Introduce a stability marker annotation and API surface audit tooling
4. Implement a deprecation pathway for transitional interfaces with migration guides
5. Validate by running the full test suite under both surfaces with surface-specific linting rules
