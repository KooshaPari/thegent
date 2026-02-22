### [WL-6600]
**Title:** Make `shell reload` fail on unsuccessful `source ~/.zshrc` execution instead of always printing success.
**Source Path+Line:** [thegent/src/thegent/shell_cli.py:136]
**Acceptance Checklist:**
- [ ] Capture `subprocess.run` result and gate success messaging on return code.
- [ ] Print stderr-derived diagnostics when sourcing fails.
- [ ] Add a CLI test that simulates non-zero exit and asserts failure output.
**Notes:** Current `check=False` path reports success even when `.zshrc` sourcing fails.

### [WL-6601]
**Title:** Replace swallowed alias-detection failures in `shell doctor` with actionable diagnostics.
**Source Path+Line:** [thegent/src/thegent/shell_cli.py:176]
**Acceptance Checklist:**
- [ ] Catch `TimeoutExpired` and subprocess errors explicitly in alias inspection.
- [ ] Record a doctor issue entry when the alias probe itself fails.
- [ ] Add coverage for timeout/error branches so failures are visible in doctor output.
**Notes:** Bare exception suppression can hide broken diagnostics and produce false "healthy" reports.

### [WL-6602]
**Title:** Harden git commit collection error reporting in summary generation.
**Source Path+Line:** [thegent/src/thegent/summary.py:60]
**Acceptance Checklist:**
- [ ] Replace broad exception swallowing in `get_git_commits` with typed error handling.
- [ ] Include command/context diagnostics in a structured warning path.
- [ ] Add tests for git command failures and non-repo paths.
**Notes:** Silent `[]` fallback obscures whether there were no commits or command execution failed.

### [WL-6603]
**Title:** Expose malformed telemetry lines instead of silently suppressing all parse exceptions.
**Source Path+Line:** [thegent/src/thegent/contracts/telemetry.py:29]
**Acceptance Checklist:**
- [ ] Replace `contextlib.suppress(Exception)` with explicit JSON decode handling.
- [ ] Track malformed-line count or emit debug diagnostics during telemetry reads.
- [ ] Add tests for mixed valid/invalid JSONL lines.
**Notes:** Full exception suppression makes telemetry corruption invisible during drift analysis.

### [WL-6604]
**Title:** Add structured parse-failure accounting in `ContractTelemetry.get_stats` event ingestion.
**Source Path+Line:** [thegent/src/thegent/contracts/telemetry.py:133]
**Acceptance Checklist:**
- [ ] Separate parse failures from provider-filter skips while reading events.
- [ ] Return parse-error counters alongside existing aggregate metrics.
- [ ] Add regression tests for malformed events within otherwise valid telemetry streams.
**Notes:** Current `except ... continue` drops bad rows silently and can skew confidence/fallback metrics.

### [WL-6605]
**Title:** Make native parser extraction fallback observable when Rust extension invocation fails.
**Source Path+Line:** [thegent/src/thegent/contracts/parser.py:224]
**Acceptance Checklist:**
- [ ] Catch and log native parser invocation failures with exception context.
- [ ] Preserve Python parser fallback behavior without silent failure.
- [ ] Add tests asserting fallback is triggered and diagnostics are emitted on native errors.
**Notes:** The current silent pass masks native parser regressions and complicates troubleshooting.

### [WL-6606]
**Title:** Instrument native `<think>` stripping fallback path in output parser.
**Source Path+Line:** [thegent/src/thegent/output_parser.py:277]
**Acceptance Checklist:**
- [ ] Replace silent native-strip failure handling with debug-level diagnostics.
- [ ] Keep regex fallback result parity for normal text and nested think blocks.
- [ ] Add tests for native failure simulation plus fallback correctness.
**Notes:** Observability gap prevents operators from detecting degraded parsing performance.

### [WL-6607]
**Title:** Remove silent scoring-path degradation when model quality/speed lookup imports fail.
**Source Path+Line:** [thegent/src/thegent/planning/selector.py:81]
**Acceptance Checklist:**
- [ ] Replace broad import/lookup exception suppression with explicit diagnostics.
- [ ] Define deterministic fallback scoring behavior when lookup modules are unavailable.
- [ ] Add tests for successful lookup and forced-import-failure scenarios.
**Notes:** Today the selector quietly reverts to metadata defaults with no signal that enrichment failed.

### [WL-6608]
**Title:** Validate calibration file schema instead of defaulting silently on load errors.
**Source Path+Line:** [thegent/src/thegent/ux/calibration.py:42]
**Acceptance Checklist:**
- [ ] Distinguish JSON parse errors from wrong-shape payloads in `_load_calibration`.
- [ ] Emit diagnostics before returning an empty bias map.
- [ ] Add tests for corrupt JSON, non-dict payloads, and valid calibration maps.
**Notes:** Returning `{}` on all errors can silently reset learned calibration behavior.

### [WL-6609]
**Title:** Prevent partial-state contamination when board artifact JSON loading fails.
**Source Path+Line:** [thegent/src/thegent/planning/board_artifact_loader.py:65]
**Acceptance Checklist:**
- [ ] Ensure `load_all` rolls back or isolates partial `items/slices/metadata` mutations when `_load_json` raises.
- [ ] Surface file-specific error details while preserving deterministic loader result schema.
- [ ] Add tests for malformed JSON and mixed-artifact load sequences.
**Notes:** Failed JSON load currently records an error but may leave in-memory loader state inconsistent for subsequent steps.
