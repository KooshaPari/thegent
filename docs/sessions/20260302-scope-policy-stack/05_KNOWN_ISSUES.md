# 05_KNOWN_ISSUES

- Current schema file is intentionally strict; unknown extensions fail fast.
- No JSON-Schema runtime validation is performed in `resolve.py` yet, only structural checks.
- Harness integration is currently documented but not yet enforced in all harness launchers.

## Workaround
- Keep this as canonical baseline and update harness entrypoints in the next step.

