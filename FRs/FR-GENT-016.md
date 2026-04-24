# FR-GENT-016: Provider Adapter Registry

## ID
- **FR-ID**: FR-GENT-016
- **Repository**: thegent
- **Domain**: CTR (Contracts)

## Description

The system SHALL maintain an `ADAPTER_REGISTRY` mapping provider names to OutputAdapter instances, register default XML adapters for common providers (copilot, gemini, claude, codex, cursor, antigravity), and provide a `normalize_output()` function that attempts the registered adapter first, falls back to plain text extraction with reduced confidence (0.3-0.5), or raises SemanticValidationError when fallback is disabled.

## Acceptance Criteria

- [ ] Maintains `ADAPTER_REGISTRY`
- [ ] Registers XML adapters for providers
- [ ] `normalize_output()` uses adapters
- [ ] Falls back to plain text with low confidence

## Test References

| Test File | Function | FR Reference |
|-----------|----------|--------------|
| `tests/adapter_tests.rs` | `test_adapter_registry` | `// @trace FR-GENT-016` |

## Code References

| File | Function/Struct | FR Reference |
|------|-----------------|--------------|
| `src/adapters/registry.py` | `ADAPTER_REGISTRY` | `@trace FR-GENT-016` |

## Related FRs

- FR-GENT-015: Incremental XML Parser

## Status

- **Current**: implemented
- **Since**: 2026-01-25
