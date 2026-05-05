# Plan: hexagonal-split-track-1

## Objective

Migrate ~30K LOC of Thegent's LLM routing, provider adapters, and auth integrations from Python to Go (CLIProxy), maintaining full functional parity through a strict TDD implementation plan with bite-sized, verifiable tasks.

## Approach

1. Review TRACK1_ARCHITECTURE_DECISIONS.md and TRACK1_TDD_IMPLEMENTATION_PLAN.md to establish the implementation baseline
2. Scaffold the Go module alongside the existing Python code with a clear package boundary
3. Implement routing, adapter, and auth domains using test-first development, starting with the smallest units
4. Build a Python/Go interop layer (IPC or FFI) that allows thegent agent runner to route through the Go implementation
5. Enable via feature flag and validate with the full test suite before deprecating the Python implementations
