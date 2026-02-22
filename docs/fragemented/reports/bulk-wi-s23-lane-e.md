### [WL-6710]
**Title:** Expose alias-audit probe failures in `shell doctor` instead of suppressing them
**Source:** [thegent/src/thegent/shell_cli.py:178]
**Acceptance checklist:**
- [ ] Replace blanket exception suppression around the alias probe with targeted handling for timeout and command-launch errors.
- [ ] Emit a warning entry in doctor output when alias checks are skipped due to probe failure.
- [ ] Add tests that assert normal alias detection still works and failure paths remain non-fatal but visible.
**Notes:**
- The current `except Exception: pass` can hide shell-level regressions and produce false "healthy" output.

### [WL-6711]
**Title:** Differentiate zsh absence from execution failure in platform reporting
**Source:** [thegent/src/thegent/shell_cli.py:479]
**Acceptance checklist:**
- [ ] Split error handling so missing `zsh`, timeout, and malformed version output are reported as distinct platform statuses.
- [ ] Keep command execution non-blocking while preserving actionable diagnostics for each failure class.
- [ ] Add CLI tests for success and each fallback status row in the platform table.
**Notes:**
- Collapsing all exceptions into "Not available" reduces operator visibility during environment triage.

### [WL-6712]
**Title:** Harden Nix version detection fallback to avoid incorrect success states
**Source:** [thegent/src/thegent/doctor_shell_nix.py:148]
**Acceptance checklist:**
- [ ] Narrow exception handling around `nix --version` and preserve error details for non-timeout failures.
- [ ] Distinguish "binary exists but invocation failed" from true positive detection in check results.
- [ ] Add tests for timeout, permission, and execution-error cases covering expected status/message transitions.
**Notes:**
- The current fallback may report Nix as found even when command execution is broken.

### [WL-6713]
**Title:** Report MCP health-check failure causes in `_check_mcp_tools`
**Source:** [thegent/src/thegent/doctor.py:1501]
**Acceptance checklist:**
- [ ] Capture exception category and bounded message context when MCP `/health` probing fails.
- [ ] Preserve warning semantics but include failure reason in `r.details` for diagnostics tooling.
- [ ] Add tests for connection refused, timeout, and malformed response scenarios.
**Notes:**
- A generic "not reachable" message obscures the remediation path for different outage modes.

### [WL-6714]
**Title:** Preserve git-log invocation errors in `get_git_commits` with structured outcomes
**Source:** [thegent/src/thegent/summary.py:61]
**Acceptance checklist:**
- [ ] Replace bare `return []` on exception with a typed result that distinguishes "no commits" from "query failure".
- [ ] Include command stderr/exit-code metadata (bounded) for failed git-log calls.
- [ ] Update summary callers/tests to handle failure metadata without breaking existing output generation.
**Notes:**
- Silent fallback to empty commits can under-report work activity and mislead audit consumers.

### [WL-6715]
**Title:** Surface JSONL parse failures in `_parse_log_entry` without aborting log ingestion
**Source:** [thegent/src/thegent/summary.py:79]
**Acceptance checklist:**
- [ ] Track parse-error counters and optionally sample malformed lines for diagnostics.
- [ ] Keep per-line fault tolerance while exposing aggregate parse quality to callers.
- [ ] Add tests for invalid JSON, bad timestamps, and mixed valid/invalid log files.
**Notes:**
- Current suppression (`except Exception: pass`) hides data-quality drift in session audit logs.

### [WL-6716]
**Title:** Add observable fallback telemetry for Linux `sendfile` copy path
**Source:** [thegent/src/thegent/infra/fast_file_ops.py:65]
**Acceptance checklist:**
- [ ] Log or meter when `sendfile` fails and the code falls back to standard copy.
- [ ] Preserve existing functional fallback while recording failure reason categories.
- [ ] Add tests that force `sendfile` failure and assert fallback correctness plus telemetry emission.
**Notes:**
- Silent fallback makes performance regressions difficult to detect in large-file workflows.

### [WL-6717]
**Title:** Return explicit discovery failure metadata in `discover_models`
**Source:** [thegent/src/thegent/provider_model_manager.py:507]
**Acceptance checklist:**
- [ ] Replace silent exception swallowing around CLIProxy model discovery with warning-level diagnostics.
- [ ] Return provider discovery status metadata alongside model list so callers can distinguish empty results from probe failures.
- [ ] Add tests for connection failure and invalid payload schema.
**Notes:**
- The current behavior conflates "no models" with "discovery failed," weakening provider onboarding UX.

### [WL-6718]
**Title:** Emit recoverable diagnostics when subagent enumeration fails in session TUI
**Source:** [thegent/src/thegent/ux/session_tui.py:103]
**Acceptance checklist:**
- [ ] Replace broad exception-to-empty-list fallback with structured warning context tied to session ID.
- [ ] Keep UI rendering resilient while displaying a degraded-state indicator in the session view.
- [ ] Add tests covering psutil errors and unexpected process-tree failures.
**Notes:**
- Returning `[]` silently can misrepresent active subagents as absent.

### [WL-6719]
**Title:** Distinguish interface-query errors from zero-interface state in `list_interfaces`
**Source:** [thegent/src/thegent/resources/network.py:159]
**Acceptance checklist:**
- [ ] Return a result shape that separates "no interfaces" from psutil query failure.
- [ ] Preserve existing exception logging while exposing machine-readable error context to callers.
- [ ] Add unit tests for psutil exceptions and empty-interface hosts.
**Notes:**
- Returning a bare empty list for both paths can mask runtime telemetry pipeline failures.
