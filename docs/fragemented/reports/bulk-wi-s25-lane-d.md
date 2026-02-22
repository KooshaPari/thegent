### [WL-6800]
**Title:** Make alias-probe failures visible in `shell doctor` output.
**Source Path+Line:** [thegent/src/thegent/shell_cli.py:177]
**Acceptance Checklist:**
- [ ] Replace blanket alias-probe exception swallowing with targeted timeout/launch handling.
- [ ] Emit a doctor warning or issue entry when probing fails.
- [ ] Add tests for successful probe and failure visibility paths.
**Notes:** Silent probe failure can produce a false healthy shell diagnosis.

### [WL-6801]
**Title:** Report actionable zsh-version detection degradation states.
**Source Path+Line:** [thegent/src/thegent/shell_cli.py:479]
**Acceptance Checklist:**
- [ ] Distinguish missing binary, timeout, and execution failure when checking zsh version.
- [ ] Preserve non-fatal doctor flow while surfacing failure cause.
- [ ] Add tests for success and each degraded status path.
**Notes:** Collapsing all failures to `Not available` removes triage detail.

### [WL-6802]
**Title:** Prevent optimistic Nix health on failed version invocations.
**Source Path+Line:** [thegent/src/thegent/doctor_shell_nix.py:148]
**Acceptance Checklist:**
- [ ] Replace broad fallback handling with typed exception branches.
- [ ] Avoid `ok` status on generic invocation failure without verified output.
- [ ] Add tests for timeout, execution failure, and non-zero outcomes.
**Notes:** Current fallback can misclassify broken Nix setups as healthy.

### [WL-6803]
**Title:** Include MCP health-check failure cause in warning details.
**Source Path+Line:** [thegent/src/thegent/doctor.py:1501]
**Acceptance Checklist:**
- [ ] Capture bounded error category/message when `/health` probe fails.
- [ ] Preserve warning semantics while adding remediation context.
- [ ] Add tests for timeout and connection-refused scenarios.
**Notes:** Generic `not reachable` warnings are insufficient for rapid diagnosis.

### [WL-6804]
**Title:** Separate git-log execution failure from true no-commit windows.
**Source Path+Line:** [thegent/src/thegent/summary.py:61]
**Acceptance Checklist:**
- [ ] Replace blanket exception-to-empty fallback with structured failure metadata.
- [ ] Capture bounded stderr/exit code context for failed git invocations.
- [ ] Update callers/tests to distinguish query failure from no-commit results.
**Notes:** Returning `[]` for both paths can under-report activity in summaries.

### [WL-6805]
**Title:** Track malformed JSONL records during summary ingestion.
**Source Path+Line:** [thegent/src/thegent/summary.py:79]
**Acceptance Checklist:**
- [ ] Record parse-failure counts while continuing line-by-line ingestion.
- [ ] Optionally retain bounded sampled context for bad lines.
- [ ] Add tests for mixed valid/invalid JSONL and malformed timestamps.
**Notes:** Silent parse skips hide data-quality degradation.

### [WL-6806]
**Title:** Emit diagnostics when `sendfile` path degrades to copy fallback.
**Source Path+Line:** [thegent/src/thegent/infra/fast_file_ops.py:66]
**Acceptance Checklist:**
- [ ] Capture fallback reason when `sendfile` branch fails.
- [ ] Preserve correctness and metadata behavior across fallback.
- [ ] Add tests forcing `sendfile` failure and asserting diagnostic emission.
**Notes:** Silent fallback obscures large-file performance regressions.

### [WL-6807]
**Title:** Surface provider discovery probe failures in model listing.
**Source Path+Line:** [thegent/src/thegent/provider_model_manager.py:507]
**Acceptance Checklist:**
- [ ] Replace broad exception swallowing with warning-level diagnostics.
- [ ] Return status metadata to distinguish probe failure from empty model catalogs.
- [ ] Add tests for transport failure and malformed payload handling.
**Notes:** Silent failure conflates outages with legitimate empty results.

### [WL-6808]
**Title:** Preserve subagent enumeration failure signals in session TUI.
**Source Path+Line:** [thegent/src/thegent/ux/session_tui.py:103]
**Acceptance Checklist:**
- [ ] Replace `except Exception: return []` with structured degraded-state signaling.
- [ ] Keep UI resilient while surfacing explicit warnings.
- [ ] Add tests for process-tree enumeration failure paths.
**Notes:** Returning empty lists silently can misrepresent active subagents.

### [WL-6809]
**Title:** Distinguish network-interface query errors from true empty state.
**Source Path+Line:** [thegent/src/thegent/resources/network.py:159]
**Acceptance Checklist:**
- [ ] Return a shape that differentiates psutil query failure from zero interfaces.
- [ ] Preserve logging while exposing machine-readable error context.
- [ ] Add tests for psutil exceptions and genuine empty-interface hosts.
**Notes:** Shared `[]` output masks telemetry failure during diagnostics.
