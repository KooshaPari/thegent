### [WL-6610]
**Title:** Replace simulated neural synthesis output with provider-backed code generation pipeline
**Source Path+Line:** [thegent/src/thegent/agents/synthesis.py:40]
**Acceptance Checklist:**
- [ ] Replace `_mock_llm_generation` call path with real provider invocation that accepts prompt and optional formal spec context.
- [ ] Capture generation metadata (provider/model/latency/token usage) alongside synthesized source for downstream verification.
- [ ] Add tests covering successful generation, provider failure propagation, and deterministic fallback prevention.
**Notes:** The current synthesis flow still calls a mock generator, so verification runs on synthetic code instead of model-produced output.

### [WL-6611]
**Title:** Implement real protocol adapters for discovered tools instead of mock adapted output
**Source Path+Line:** [thegent/src/thegent/agents/tool_adapter.py:69]
**Acceptance Checklist:**
- [ ] Replace mock `adapted_call` body with protocol-specific execution for `mcp`, `rest`, `python`, and `cli` tool definitions.
- [ ] Validate kwargs against declared parameters before execution and return typed error payloads for contract violations.
- [ ] Add tests for one successful invocation per supported protocol plus unsupported-protocol failure handling.
**Notes:** `wrap_tool` currently returns a static success payload and never executes the discovered tool.

### [WL-6612]
**Title:** Compute throughput KPI from run telemetry instead of fixed placeholder values
**Source Path+Line:** [thegent/src/thegent/ux/kpis.py:22]
**Acceptance Checklist:**
- [ ] Derive `throughput` from concrete session/run artifacts rather than hardcoded constants.
- [ ] Keep metric timestamps and existing schema stable while populating live values for reliability/availability when sources exist.
- [ ] Add tests proving KPI values change with input telemetry and remain bounded when telemetry is absent.
**Notes:** The KPI dashboard currently emits placeholder throughput and mostly static health numbers.

### [WL-6613]
**Title:** Replace harness status placeholder with explicit health probe and error classification
**Source Path+Line:** [thegent/src/thegent/sitback_plugins.py:136]
**Acceptance Checklist:**
- [ ] Rename and implement the status provider as a concrete harness probe that reports `available`, `unavailable`, and `error` states.
- [ ] Distinguish missing dependency, runtime failure, and disabled-by-config outcomes in structured fields.
- [ ] Add tests for harness present, harness missing, and probe exception scenarios.
**Notes:** The current helper is explicitly placeholder-oriented and returns ambiguous fallback states.

### [WL-6614]
**Title:** Generate module/function-targeted Mojo dispatch scripts instead of generic placeholder main()
**Source Path+Line:** [thegent/src/thegent/infra/mojo_bridge.py:414]
**Acceptance Checklist:**
- [ ] Build Mojo script bodies that call the requested `task.module` and `task.function` with decoded args.
- [ ] Validate task contract before script generation and surface actionable errors for missing symbols/signature mismatches.
- [ ] Add tests for successful dispatch, unknown module/function, and malformed args payloads.
**Notes:** The default script path still prints raw args and does not invoke the requested kernel function.

### [WL-6615]
**Title:** Add structured parse-failure accounting for native checkpoint parser exceptions
**Source Path+Line:** [thegent/src/thegent/execution_jsonl_parsers.py:38]
**Acceptance Checklist:**
- [ ] Replace silent exception swallow in native parse path with structured diagnostics counters/logging.
- [ ] Preserve fallback-to-Python behavior while exposing parse failure reasons to observability surfaces.
- [ ] Add tests ensuring native exceptions increment diagnostics and still return correct fallback parse results.
**Notes:** Native parser failures are currently dropped silently, obscuring parser reliability issues.

### [WL-6616]
**Title:** Harden config load failures with explicit error surfacing instead of empty-config fallback
**Source Path+Line:** [thegent/src/thegent/config/manager.py:34]
**Acceptance Checklist:**
- [ ] Replace bare `except` fallback with explicit error classification for invalid JSON vs I/O failures.
- [ ] Preserve startup behavior while exposing parse/load failures through logger and/or typed exception pathway.
- [ ] Add tests for malformed config, unreadable file, and successful load scenarios.
**Notes:** Returning `{}` on all errors hides broken user config and makes diagnosis difficult.

### [WL-6617]
**Title:** Improve shim detection error handling in native Claude binary discovery path
**Source Path+Line:** [thegent/src/thegent/clode_binary_discovery.py:16]
**Acceptance Checklist:**
- [ ] Replace silent `OSError` swallow with traceable diagnostics for symlink resolution failures.
- [ ] Ensure shim detection still returns deterministic booleans for non-existent paths and permission-restricted links.
- [ ] Add tests for direct shim path, non-shim path, broken symlink, and permission error conditions.
**Notes:** Current behavior suppresses symlink read failures, making native binary resolution failures opaque.

### [WL-6618]
**Title:** Return explicit bottleneck status payload when detector is unavailable
**Source Path+Line:** [thegent/src/thegent/execution.py:463]
**Acceptance Checklist:**
- [ ] Replace empty-dict return with stable schema that indicates detector availability and why data is missing.
- [ ] Keep existing populated payload contract unchanged when detector is present.
- [ ] Add tests for detector-missing and detector-present branches.
**Notes:** The current empty response is ambiguous for callers that need to distinguish "no bottlenecks" from "no detector configured".

### [WL-6619]
**Title:** Add strict provider-definition validation for cliproxy JSON loading path
**Source Path+Line:** [thegent/src/thegent/agents/cliproxy_manager.py:37]
**Acceptance Checklist:**
- [ ] Replace generic `{}` fallback with validation errors that identify missing file, invalid JSON, and non-object payloads.
- [ ] Keep downstream call sites resilient by returning typed validation results or raising controlled exceptions.
- [ ] Add tests for valid definitions, malformed JSON, missing files, and array/scalar JSON payloads.
**Notes:** `_load_json` currently collapses all load/parse problems into empty dicts, masking configuration defects.
