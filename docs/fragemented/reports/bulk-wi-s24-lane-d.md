### [WL-6750]
**Title:** Convert alias-probe exception swallowing in `shell doctor` into visible diagnostics.
**Source Path+Line:** [thegent/src/thegent/shell_cli.py:177]
**Acceptance Checklist:**
- [ ] Replace blanket exception suppression in the alias probe with targeted handling for subprocess timeout and launch failures.
- [ ] Add a doctor issue or warning entry when alias probing fails so output does not appear falsely healthy.
- [ ] Add tests covering both successful alias detection and probe-failure visibility.
**Notes:** The current bare `except` path drops probe failures and can mask shell-environment regressions.

### [WL-6751]
**Title:** Split zsh-version detection failures into actionable platform statuses.
**Source Path+Line:** [thegent/src/thegent/shell_cli.py:479]
**Acceptance Checklist:**
- [ ] Distinguish missing binary, timeout, and execution failure when collecting zsh version.
- [ ] Preserve non-fatal behavior while surfacing failure cause in platform output.
- [ ] Add tests for success and each degraded status path.
**Notes:** Collapsing all errors into `Not available` removes useful environment-triage detail.

### [WL-6752]
**Title:** Prevent incorrect Nix success fallback when version command fails unexpectedly.
**Source Path+Line:** [thegent/src/thegent/doctor_shell_nix.py:148]
**Acceptance Checklist:**
- [ ] Replace broad fallback handling with typed exception branches for timeout, execution errors, and missing binary.
- [ ] Avoid marking status `ok` on generic invocation errors without evidence of a healthy binary.
- [ ] Add tests covering timeout, permission, and non-zero invocation outcomes.
**Notes:** Current fallback logic can report Nix as found even when command execution is broken.

### [WL-6753]
**Title:** Attach failure cause context to MCP health-check warnings.
**Source Path+Line:** [thegent/src/thegent/doctor.py:1501]
**Acceptance Checklist:**
- [ ] Capture bounded error category/message when MCP `/health` probing fails.
- [ ] Preserve warning semantics but include reason context in result details.
- [ ] Add tests for connection-refused and timeout scenarios.
**Notes:** Generic `not reachable` messaging obscures remediation for different outage modes.

### [WL-6754]
**Title:** Differentiate git-log command failure from true zero-commit windows.
**Source Path+Line:** [thegent/src/thegent/summary.py:61]
**Acceptance Checklist:**
- [ ] Replace blanket exception-to-empty-list fallback with structured failure metadata.
- [ ] Include bounded stderr/exit code context for failed git invocation.
- [ ] Update callers/tests to handle `no commits` versus `query failed` as distinct states.
**Notes:** Returning `[]` for all failures can under-report activity in generated summaries.

### [WL-6755]
**Title:** Track malformed JSONL lines during session log parsing.
**Source Path+Line:** [thegent/src/thegent/summary.py:79]
**Acceptance Checklist:**
- [ ] Record parse-failure counts and optionally sampled line context while continuing ingestion.
- [ ] Keep per-line fault tolerance without silent data-quality loss.
- [ ] Add tests for mixed valid/invalid log files and malformed timestamps.
**Notes:** The current `except ... pass` path hides parsing drift and makes audit confidence weaker.

### [WL-6756]
**Title:** Emit telemetry when `sendfile` optimization falls back to standard copy.
**Source Path+Line:** [thegent/src/thegent/infra/fast_file_ops.py:66]
**Acceptance Checklist:**
- [ ] Capture fallback reason category when the `sendfile` branch fails.
- [ ] Preserve existing copy correctness and metadata behavior across fallback.
- [ ] Add tests that force `sendfile` failure and assert fallback plus diagnostic emission.
**Notes:** Silent fallback obscures performance regressions in large file copy workflows.

### [WL-6757]
**Title:** Surface provider-discovery probe failures in model listing.
**Source Path+Line:** [thegent/src/thegent/provider_model_manager.py:507]
**Acceptance Checklist:**
- [ ] Replace broad exception swallowing with warning-level diagnostics including provider context.
- [ ] Return discovery status metadata so callers can distinguish `no models` from probe failure.
- [ ] Add tests for transport failure and malformed model payload handling.
**Notes:** Silent failure conflates connectivity issues with legitimately empty model catalogs.

### [WL-6758]
**Title:** Preserve subagent enumeration failure signals in session TUI.
**Source Path+Line:** [thegent/src/thegent/ux/session_tui.py:103]
**Acceptance Checklist:**
- [ ] Replace `except Exception: return []` with structured degraded-state signaling.
- [ ] Keep UI resilient while exposing an explicit warning for enumeration errors.
- [ ] Add tests for psutil/process-tree failure paths.
**Notes:** Returning an empty list silently can misrepresent active subagents as absent.

### [WL-6759]
**Title:** Separate network-interface query errors from true empty-interface state.
**Source Path+Line:** [thegent/src/thegent/resources/network.py:159]
**Acceptance Checklist:**
- [ ] Return a result shape that distinguishes psutil query failure from zero discovered interfaces.
- [ ] Preserve exception logging while exposing machine-readable error context.
- [ ] Add tests for psutil exceptions and empty-interface hosts.
**Notes:** A bare `[]` on both paths masks telemetry failures during runtime diagnostics.
