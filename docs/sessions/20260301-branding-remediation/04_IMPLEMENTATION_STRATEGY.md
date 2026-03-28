# Implementation Strategy

- Use direct textual normalization for owner handle variants.
- Keep edits to human-authored docs/config/workflows and avoid generated artifacts.
- Preserve forward-only migration: no revert operations, no compatibility shims added.
