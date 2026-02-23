<<<<<<< HEAD
# Worklog Wave 81 - Lane D (Bugs 28-36)

## 1) Covered items table

| Issue | Title | Status |
|---|---|---|
| CLIProxyAPI#1306 | Claude Opus 4.5 returns "Internal server error" in response body via Anthropic OAuth (Sonnet works) | open |
| CLIProxyAPI#1299 | fix(logging): request and API response timestamps are inaccurate in error logs | open |
| CLIProxyAPI#1293 | Gemini API error: empty text content causes 'required oneof field data must have one initialized field' | open |
| CLIProxyAPIPlus#145 | [Bug] Further improve OpenAI compatibility mode support for Claude models (protocol conversion) | open |
| CLIProxyAPI#1269 | Tool Error on Antigravity Gemini 3 Flash | open |
| CLIProxyAPI#1215 | tool_use_error InputValidationError: EnterPlanMode failed due to unexpected parameter `reason` | open |
| CLIProxyAPI#1214 | Error 403 | open |
| CLIProxyAPIPlus#125 | Error 403 | open |
| CLIProxyAPI#1119 | Error code: 400 - {'detail': 'Unsupported parameter: user'} | open |

## 2) thegent impact classification (direct/indirect/external)

| Issue | Classification | Basis |
|---|---|---|
| CLIProxyAPI#1306 | indirect | Upstream proxy/provider behavior can break thegent model routes using Anthropic OAuth-backed paths. |
| CLIProxyAPI#1299 | indirect | Logging correctness affects thegent incident triage when proxy logs are used for diagnosis. |
| CLIProxyAPI#1293 | indirect | Payload-shape mismatch in upstream translation can surface as failures in thegent CLI workflows. |
| CLIProxyAPIPlus#145 | indirect | Protocol conversion gaps can impact thegent compatibility when routed through OpenAI-compatible mode. |
| CLIProxyAPI#1269 | indirect | Tool call translation/runtime failures can break thegent tool-using sessions on Gemini routes. |
| CLIProxyAPI#1215 | direct | `EnterPlanMode` parameter validation error can directly affect thegent plan-mode tool invocation contracts. |
| CLIProxyAPI#1214 | external | 403 authorization failures are typically provider/account/policy-side unless local auth mapping is wrong. |
| CLIProxyAPIPlus#125 | external | 403 authorization failures are typically provider/account/policy-side unless local auth mapping is wrong. |
| CLIProxyAPI#1119 | direct | Unsupported `user` parameter is a request-shape contract issue that can originate from thegent request assembly. |

## 3) Proposed local actions (tests/docs/code touchpoints in this repo) with priority P0/P1/P2

| Priority | Action | Touchpoints |
|---|---|---|
| P0 | Add/extend contract tests asserting plan-mode tool payload excludes unexpected `reason` field and fails loudly on unknown fields. | tests around plan-mode/tool-use request serialization; request contract validators; docs for plan-mode payload contract. |
| P0 | Add request-shape tests and normalization checks to ensure unsupported OpenAI `user` parameter is either mapped correctly per route or hard-rejected with explicit error. | request translation layer for OpenAI-compatible inputs; route-specific schema validation tests; troubleshooting docs. |
| P1 | Add regression tests for empty text/content blocks in Gemini translation paths, with explicit non-empty content validation before provider call. | Gemini translator/adapter tests; provider payload builder checks; error taxonomy docs. |
| P1 | Add integration test coverage for tool invocation on Gemini/Antigravity routes (including failure signatures from issue #1269). | tool-call integration tests; provider adapter fixtures; docs/reference for known failure signatures. |
| P2 | Improve internal diagnostics docs/runbook for timestamp trustworthiness and external 403 triage boundaries (what is local vs provider-side). | docs/reports or docs/reference troubleshooting pages; logging field documentation; incident triage checklist. |

## 4) Blockers/unknowns

- Missing reproducible request/response artifacts for #1306, #1269, #1214, #125 to determine whether failures originate in thegent request shaping vs upstream proxy/provider.
- Unknown current parity between thegent plan-mode parameter schema and upstream accepted fields for #1215.
- Unknown whether this repo currently emits OpenAI `user` field on affected paths (#1119) or only forwards from clients.
- No linked commit/fix references in the source list to confirm already-resolved behavior in newer proxy versions.

## 5) Next 3 executable tasks for this lane

1. Implement and run a focused failing test for `EnterPlanMode` rejecting unexpected `reason` in current request builder, then patch builder/validator to enforce contract.
2. Add a failing regression test for unsupported `user` parameter on OpenAI-compatible route and implement explicit route-aware handling (map or hard-fail with actionable error).
3. Create a Gemini payload regression test set for empty content/tool-call edge cases (#1293/#1269) and document expected fail-fast errors in local troubleshooting docs.
=======
# Wave 81 Lane D Worklog (2026-02-23)

- Scope: analyze WL-327 (Connector policy initiative) and WL-328 (Connector checkpoint initiative) to surface the available evidence about connector reliability/retry-resume hardening and determine what follow-up work is needed.
- Constraint: this lane is producing a report-only snapshot—no code or policy changes were authored in this pass.

## Findings
- `docs/reference/WORK_STREAM.md:26821-26845` records WL-327 and WL-328 as BACKLOG items that ask for “deterministic behavior and traceable outputs” for connector reliability, retry, and resume hardening, and it asserts the evidence lives in `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_I_2026-02-22.md` even though that file is absent from the worktree right now.
- `docs/reports/bulk-wi-b1-lane-c.md:631-804` consolidates WL-327x/328x backlog markers that cite `docs/AUDIT_MODERNIZATION_PLAN.md:80-103` as the source; those markers are still describing stub removal without connector-specific acceptance criteria, so the lane still lacks the concrete signal paths or verification that WL-327/328 are supposed to cover.
- `docs/AUDIT_MODERNIZATION_PLAN.md:60-103` is a high-level modernization checklist (security + observability + data-processing chunks) and does not document the deterministic connector retry/resume behavior the workstream items allude to, leaving a gap between the WL-327/328 statements in `WORK_STREAM.md` and any actionable steps.

## Recommendations
- Restore or link the promised `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_I_2026-02-22.md` artifact (or replace the evidence pointer in `WORK_STREAM.md`) so the lane can read the detailed connector policy/checkpoint specs referenced in WL-327/328.
- Expand the `docs/AUDIT_MODERNIZATION_PLAN.md` section that backs WL-327x/328x (lines 80-103) with concrete connector policy/checkpoint work (deterministic inputs, recovery story, tracing expectations) to make those backlog markers actionable.
- Once the evidence doc exists, revisit WL-327/328 and capture the deterministic behavior expectations, the verification approach, and any required code/test surfaces.

## Verification
- `rg -n "WL-327" docs/reference/WORK_STREAM.md`
- `rg -n "WL-328" docs/reference/WORK_STREAM.md`
- `nl -ba docs/reports/bulk-wi-b1-lane-c.md | sed -n '610,820p'`
- `sed -n '60,140p' docs/AUDIT_MODERNIZATION_PLAN.md`
- `find docs -iname 'WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_I_2026-02-22.md' -print`
>>>>>>> 58ccbe31e72efd07558be54d6a129ce6d984487d
