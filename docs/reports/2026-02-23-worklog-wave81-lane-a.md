# Worklog Wave 81 - Lane A (2026-02-23)

Source: `docs/reference/WORK_STREAM_CLIPROXY_ALL.md` (Bugs 1..9 only).

## 1) Covered items table

| Issue | Title | Status |
|---|---|---|
| CLIProxyAPI#1671 | BUG: Cannot use Claude Models in Codex CLI | open |
| CLIProxyAPI#1658 | Qwen Oauth fails | open |
| CLIProxyAPIPlus#251 | Bug thinking | open |
| CLIProxyAPI#1641 | Docker Image Error | open |
| CLIProxyAPI#1620 | Claude output not streaming in cliproxyapi usage | open |
| CLIProxyAPI#1584 | Invalid thinking block signature after Gemini CLI -> Claude OAuth switch | open |
| CLIProxyAPI#1535 | INVALID_ARGUMENT on antigravity claude-opus-4-6 | open |
| CLIProxyAPI#1533 | Persistent 400 INVALID_ARGUMENT on claude-opus-4-6-thinking | open |
| CLIProxyAPI#1530 | `proxy_` prefix mismatch between `tool_choice.name` and `tools[].name` causing 400 | open |

## 2) thegent impact classification

| Issue | Classification | Basis |
|---|---|---|
| CLIProxyAPI#1671 | indirect | Affects Codex + Claude path through external CLIProxy translation/auth behavior that thegent consumes. |
| CLIProxyAPI#1658 | external | Qwen OAuth failure appears provider/proxy-side with no explicit thegent-owned surface in issue title. |
| CLIProxyAPIPlus#251 | external | "Bug thinking" is underspecified and in CLIProxyAPIPlus; cannot map to a concrete thegent defect yet. |
| CLIProxyAPI#1641 | external | Docker image packaging/runtime issue is outside thegent codebase. |
| CLIProxyAPI#1620 | indirect | Streaming behavior mismatch can affect thegent UX when routed through cliproxy, but root likely proxy translator/transport. |
| CLIProxyAPI#1584 | indirect | Cross-provider conversation state/signature handling can surface via thegent sessions, but root likely in cliproxy adapter/translator. |
| CLIProxyAPI#1535 | indirect | INVALID_ARGUMENT on specific upstream model is proxy/provider contract handling that impacts thegent integrations. |
| CLIProxyAPI#1533 | indirect | Same as #1535; request-shape/model-contract issue external to thegent core. |
| CLIProxyAPI#1530 | direct | Tool name consistency is a request-construction contract that thegent can pre-validate in local adapter/tests. |

## 3) Proposed local actions (tests/docs/code touchpoints)

| Priority | Action | Type | Local touchpoints |
|---|---|---|---|
| P0 | Add regression tests asserting tool name parity (`tool_choice.name` vs `tools[].name`) and fail-fast validation before proxy dispatch. | tests+code | `tests/protocols/`, `src/thegent/protocols/` |
| P0 | Add streaming contract tests that require incremental chunk emission and completion markers for proxied Claude routes. | tests | `tests/streaming/` or existing stream translator test modules |
| P1 | Add conversation-state transition tests for provider switch (Gemini -> Claude OAuth) ensuring signature/state reset semantics are explicit. | tests | `tests/protocols/` and session/translator test modules |
| P1 | Add request-shape guards for known INVALID_ARGUMENT patterns (model/argument combinations) with explicit error classification. | code+tests | request validation/translation modules in `src/thegent/` and companion tests |
| P2 | Document cliproxy integration guardrails for lane triage (streaming, tool names, model-arg compatibility, provider-switch behavior). | docs | `docs/reference/` integration docs |

## 4) Blockers/unknowns

- Issue entries provide only title+status; no payload samples, logs, or reproducer steps.
- No confirmed mapping from each issue to a specific thegent module/function without upstream traces.
- For #1658, #251, #1641 root cause appears external; local mitigation scope is uncertain until concrete failure artifacts are attached.

## 5) Next 3 executable tasks for this lane

1. Add a focused failing test for tool-name parity contract (`proxy_` mismatch path) and implement fail-fast validator if absent.
2. Add/extend streaming regression test to assert chunked emission (not single flush) for cliproxy-routed Claude responses.
3. Build a minimal issue-evidence matrix (issue -> required artifacts/log fields/repro command) and request missing artifacts to unblock direct fixes.
