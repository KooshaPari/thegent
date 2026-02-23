### [WL-6760]
**Title:** Distinguish tmux session probe failures from empty session state in native discovery fallback
**Source:** [thegent/src/thegent/native/discovery_native.py:61]
**Acceptance checklist:**
- [ ] Replace blanket exception handling in `_fallback_sessions` with targeted handling for timeout, command launch, and parse failures.
- [ ] Return structured fallback metadata so callers can distinguish probe failure from a true zero-session result.
- [ ] Add tests for `tmux` missing, timeout, and malformed output cases.
**Notes:**
- Current `except Exception: return []` path hides discovery regressions behind an empty sessions list.

### [WL-6761]
**Title:** Surface native discovery binary invocation errors in `DiscoveryClient._run`
**Source:** [thegent/src/thegent/native/discovery_native.py:143]
**Acceptance checklist:**
- [ ] Replace generic exception swallowing in `_run` with explicit handling that captures invocation failure categories.
- [ ] Emit bounded diagnostics for non-timeout failures while preserving `None` return behavior for callers.
- [ ] Add tests covering subprocess launch failure, timeout, and non-JSON stdout paths.
**Notes:**
- Returning `None` for every exception class conflates transport failure with normal fallback behavior.

### [WL-6762]
**Title:** Expose diskcache initialization failure reasons in `MultiLevelCache`
**Source:** [thegent/src/thegent/cache/multi_level.py:67]
**Acceptance checklist:**
- [ ] Replace broad initialization suppression with targeted exception handling and warning-level context.
- [ ] Preserve L1-only degradation semantics while recording why L2 cache was disabled.
- [ ] Add tests for permission-denied, invalid path, and diskcache open failures.
**Notes:**
- Silent downgrade to L1-only mode makes persistent cache outages hard to diagnose.

### [WL-6763]
**Title:** Add dropped-event telemetry for async observability queue saturation
**Source:** [thegent/src/thegent/observability/async_logger.py:68]
**Acceptance checklist:**
- [ ] Track queue-full drops with counters and periodic structured diagnostics.
- [ ] Keep non-blocking enqueue semantics while making drop rates observable.
- [ ] Add tests that force `queue.Full` and assert counter/diagnostic behavior.
**Notes:**
- The current silent drop path obscures data loss during high-throughput runs.

### [WL-6764]
**Title:** Report handler execution failures in observability worker loop without crashing the thread
**Source:** [thegent/src/thegent/observability/async_logger.py:109]
**Acceptance checklist:**
- [ ] Replace silent handler exception suppression with bounded warning diagnostics including handler identity.
- [ ] Keep worker resiliency guarantees so one handler failure does not stop processing.
- [ ] Add tests for failing handlers to verify continued event processing plus diagnostics emission.
**Notes:**
- Hidden handler failures can disable observability sinks with no operator signal.

### [WL-6765]
**Title:** Differentiate provider metrics fetch failure classes in `fetch_provider_metrics`
**Source:** [thegent/src/thegent/agents/cliproxy_manager.py:686]
**Acceptance checklist:**
- [ ] Narrow exception handling to network/timeouts/parsing and capture bounded failure detail.
- [ ] Return structured status metadata so callers can distinguish "endpoint unavailable" from "empty metrics".
- [ ] Add tests for connection refused, timeout, invalid JSON, and non-dict payloads.
**Notes:**
- Generic `None` return on all exceptions masks whether proxy health or payload schema is broken.

### [WL-6766]
**Title:** Surface guardrail evaluation failures in `enforce_input_guardrails`
**Source:** [thegent/src/thegent/cli/services/run_guard_helpers.py:62]
**Acceptance checklist:**
- [ ] Replace blanket exception fallback with typed handling for import, initialization, and evaluation failures.
- [ ] Preserve non-blocking behavior while returning machine-readable diagnostics for guardrail subsystem errors.
- [ ] Add tests for missing guardrail module and runtime evaluation exceptions.
**Notes:**
- Returning `None` for all failures can unintentionally bypass configured prompt guardrails without visibility.

### [WL-6767]
**Title:** Preserve persona registry load errors in `_load_registry` instead of collapsing to empty registry
**Source:** [thegent/src/thegent/cross_project/registry.py:33]
**Acceptance checklist:**
- [ ] Replace generic parse/read suppression with structured error reporting for IO and JSON decode failures.
- [ ] Distinguish "registry not found" from "registry unreadable/corrupt" in return metadata.
- [ ] Add tests for malformed JSON, permission errors, and truncated files.
**Notes:**
- Falling back to `{}` for all exceptions can silently discard existing persona state.

### [WL-6768]
**Title:** Report linter-unavailable state explicitly in unified lint fast path
**Source:** [thegent/src/thegent/tools/linting_accelerator.py:187]
**Acceptance checklist:**
- [ ] Replace bare empty-list fallback when neither oxlint nor eslint is available with a structured unavailable result.
- [ ] Preserve compatibility for existing callers by providing clear status metadata alongside lint results.
- [ ] Add tests covering fast path with no lint engines installed.
**Notes:**
- Returning `[]` currently conflates “clean code” with “no linter executed.”

### [WL-6769]
**Title:** Distinguish message-registry lookup errors from no-pending state in execution helpers
**Source:** [thegent/src/thegent/execution.py:1806]
**Acceptance checklist:**
- [ ] Replace broad exception fallback in pending-message retrieval with typed failure metadata.
- [ ] Preserve empty-list behavior for true no-pending cases while exposing session/meta resolution failures.
- [ ] Add tests for missing meta file, unreadable message log, and parser failures.
**Notes:**
- Current `except Exception: return []` can hide operational breakage as an apparent empty queue.
