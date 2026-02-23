# Internal Architecture Guide

## Core Layers

1. CLI + entrypoints (`src/thegent/main.py`, `src/thegent/cli/`)
2. Governance + policy (`src/thegent/governance/`)
3. Orchestration + execution (`src/thegent/orchestration/`, `src/thegent/execution.py`)
4. Performance accelerators (`crates/thegent-*`)
5. Hooks and lifecycle automation (`hooks/`)

## Engineering Priorities

- Deterministic behavior over implicit fallback behavior.
- Explicit governance checks for critical pathways.
- Rust acceleration for hot paths and shell shim dispatch.
