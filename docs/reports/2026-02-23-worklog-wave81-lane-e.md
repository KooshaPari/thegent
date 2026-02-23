# Lane E Report - Wave 81 (Bugs 37-43)

Source: `docs/reference/WORK_STREAM_CLIPROXY_ALL.md`
Scope: Bugs items 37..43 only

## 1) Covered items

| Issue | Title | Status |
|---|---|---|
| CLIProxyAPI#1085 | Streaming Response Translation Fails to Emit Completion Events on `[DONE]` Marker | open |
| CLIProxyAPI#1078 | Extended thinking model fails with "Expected thinking or redacted_thinking, but found tool_use" on multi-turn conversations | open |
| CLIProxyAPIPlus#111 | Antigravity authentication failed | open |
| CLIProxyAPIPlus#99 | GitHub Copilot Model Call Failure | open |
| CLIProxyAPI#999 | Codex Responses API: `item_reference` in `input` not cleaned, causing 404 and incorrect client suspension | open |
| CLIProxyAPI#983 | 400 Error: Unsupported `max_tokens` Parameter When Using OpenAI Base URL | open |
| CLIProxyAPI#949 | Internal Server Error: `auth_unavailable: no auth available` | open |

## 2) thegent impact classification

| Issue | Impact | Rationale |
|---|---|---|
| CLIProxyAPI#1085 | indirect | Affects stream termination semantics from upstream proxy; thegent may observe hangs/missing completion states in client flows. |
| CLIProxyAPI#1078 | external | Provider/proxy-side message-shape + thinking-chain handling; no clear thegent-owned transform in this repo. |
| CLIProxyAPIPlus#111 | external | Authentication failure is upstream account/provider path, outside this repo. |
| CLIProxyAPIPlus#99 | indirect | Model-call failures can surface through thegent integrations, but root cause is proxy/provider routing. |
| CLIProxyAPI#999 | direct | Codex Responses `item_reference` handling maps to thegent runtime behavior and request hygiene expectations. |
| CLIProxyAPI#983 | indirect | Parameter compatibility mismatch at proxy boundary can be mitigated by request-shape tests/docs in this repo. |
| CLIProxyAPI#949 | external | Upstream auth availability/outage class; local code can only improve error surfacing and retry messaging. |

## 3) Proposed local actions (this repo)

| Priority | Action | Touchpoints |
|---|---|---|
| P0 | Add regression tests for response lifecycle completeness when upstream stream ends with done marker semantics (no silent hang). | `tests/` stream/response lifecycle tests; runtime adapter test fixtures |
| P0 | Add request-sanitization tests for Codex Responses payloads to reject/strip unsupported `item_reference` shapes before outbound requests. | `tests/` codex responses adapter/unit tests; request-building modules under `src/` |
| P1 | Add compatibility guard tests for OpenAI-base URL parameter shaping (`max_tokens` vs accepted fields) and fail-fast error messaging. | `tests/` provider compatibility tests; request normalization modules under `src/` |
| P1 | Improve docs/runbook for upstream auth failures (`auth_unavailable`, antigravity auth fail) with explicit operator triage steps and non-fallback handling. | `docs/guides/` or `docs/reference/` operational troubleshooting docs |
| P2 | Add smoke matrix entries for Copilot/Antigravity paths to detect upstream regression earlier in CI diagnostics. | provider smoke test matrix docs/tests in this repo |

## 4) Blockers/unknowns

- Issue bodies, reproducer payloads, and exact failing traces are not present in the source index; precision of fixes is blocked until issue-level details are pulled.
- Ownership boundary is split across `CLIProxyAPI` and `CLIProxyAPIPlus`; patch location for root-cause fixes may be outside this repo.
- Current thegent code paths tied to Codex Responses and stream-finalization need targeted mapping before assigning exact files.

## 5) Next 3 executable tasks for lane E

1. Extract failing payload/trace details for #1085, #999, #983 and convert each into a minimal reproducible test case draft for this repo.
2. Map current thegent request/stream adapter surfaces to concrete files, then open a focused test-first patch plan (P0 items first).
3. Draft a short operator troubleshooting doc for auth outage class errors (#111, #949) with explicit fail-fast expectations and no fallback behavior.
