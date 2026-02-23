### [WL-6810]
**Title:** Implement conflict-aware `sync_configs` merge flow in unified config manager
**Source:** [thegent/src/thegent/integration/unified_config.py:163]
**Acceptance checklist:**
- [ ] Detect key conflicts across managed config sources using explicit precedence rules.
- [ ] Apply deterministic merge logic and persist reconciled values to source files.
- [ ] Add tests for no-conflict sync, merge conflicts, and idempotent re-sync behavior.
**Notes:** Line 162 is still a placeholder comment and does not execute real merge/conflict handling.

### [WL-6811]
**Title:** Replace mocked local-state collection with registry-backed sync payload construction
**Source:** [thegent/src/thegent/discovery/sync.py:69]
**Acceptance checklist:**
- [ ] Load `active_teams` and `recent_handoffs` from real project state files instead of static empty lists.
- [ ] Validate generated sync payload schema before writing peer inbox artifacts.
- [ ] Add tests for successful extraction and malformed source-file handling.
**Notes:** Line 69 explicitly marks local state collection as mocked file-read behavior.

### [WL-6812]
**Title:** Upgrade ZK verifier from mock response checks to deterministic proof validation
**Source:** [thegent/src/thegent/verification/zkp.py:60]
**Acceptance checklist:**
- [ ] Replace response-shape-only logic with deterministic challenge-response proof verification.
- [ ] Enforce freshness and replay constraints before accepting proofs.
- [ ] Add tests for valid proof, stale proof, commitment mismatch, and tampered response cases.
**Notes:** Line 59 is marked as mock verification logic and is not cryptographically authoritative.

### [WL-6813]
**Title:** Implement real remote transport in sync push path instead of stub-only reporting
**Source:** [thegent/src/thegent/commands/sync.py:655]
**Acceptance checklist:**
- [ ] Replace `files_would_push` stub behavior with concrete upload/publish execution.
- [ ] Return per-file transfer outcomes in `OperationResult.details` with actionable error metadata.
- [ ] Add tests for successful push, partial failure, and unreachable target handling.
**Notes:** Line 654 labels the branch as a stub that reports what would be pushed.

### [WL-6814]
**Title:** Replace MCP gateway placeholder executor with real server tool invocation
**Source:** [thegent/src/thegent/mcp/gateway.py:99]
**Acceptance checklist:**
- [ ] Dispatch calls through registered MCP server configuration rather than synthetic results.
- [ ] Preserve duration and normalize errors for unknown servers/tools and transport failures.
- [ ] Add tests for successful invocation, unknown server ID, and downstream execution failure.
**Notes:** Line 98 documents `execute` as a stub that currently returns placeholder output.

### [WL-6815]
**Title:** Integrate dispatcher `_execute_task` with concrete runner execution path
**Source:** [thegent/src/thegent/orchestration/dispatcher.py:386]
**Acceptance checklist:**
- [ ] Replace placeholder output generation with real runner invocation from selected `runner_name`.
- [ ] Propagate non-success execution state and captured error details to callers.
- [ ] Add tests for success, runner failure propagation, and approval-blocked execution.
**Notes:** Line 385 is explicitly marked as placeholder behavior and does not run real workload logic.

### [WL-6816]
**Title:** Implement Rich style/token wiring in `apply_to_cli` for runtime design language
**Source:** [thegent/src/thegent/design/design_language.py:101]
**Acceptance checklist:**
- [ ] Map design tokens to concrete Rich theme/style configuration consumed by CLI surfaces.
- [ ] Support platform-specific token overrides while preserving deterministic defaults.
- [ ] Add tests asserting style application and missing-token fallback behavior.
**Notes:** Line 101 indicates this path is placeholder-only and does not configure CLI styles.

### [WL-6817]
**Title:** Replace KPI placeholder constants with telemetry-derived calculations
**Source:** [thegent/src/thegent/execution.py:1047]
**Acceptance checklist:**
- [ ] Compute KPI fields from run registry and contract telemetry instead of hardcoded constants.
- [ ] Define explicit behavior for sparse datasets, including confidence/data-availability indicators.
- [ ] Add deterministic tests for populated and empty telemetry fixtures.
**Notes:** Line 1047 contains placeholder KPI values that can diverge from real runtime behavior.

### [WL-6818]
**Title:** Implement persistent model-tier mutation in `ModelPromoter._update_model_tier`
**Source:** [thegent/src/thegent/learning/promotion.py:23]
**Acceptance checklist:**
- [ ] Implement catalog persistence for tier updates with validation that `model_id` exists.
- [ ] Record promotion metadata (old tier, new tier, trigger metrics, timestamp) for auditability.
- [ ] Add tests for successful promotion, unknown IDs, and idempotent repeated updates.
**Notes:** Line 24 is currently a `pass`, so promotion decisions are not persisted.

### [WL-6819]
**Title:** Add tier-2 bind-mount enforcement in Linux sandbox wrapper
**Source:** [thegent/src/thegent/security/sandboxing.py:39]
**Acceptance checklist:**
- [ ] Replace the tier-2 `pass` branch with explicit worktree-only bind mounts and allowed scopes.
- [ ] Block unintended filesystem traversal outside permitted bind targets.
- [ ] Add tests for tier-2 wrapper arguments and regression coverage for other tiers.
**Notes:** Line 36 is an unimplemented tier-2 branch, leaving isolation behavior undefined.
