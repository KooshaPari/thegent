# Worklog Wave 81 - Lane B (2026-02-23)

## 1) Covered items table (issue id/title/status)

| Issue | Title | Status |
|---|---|---|
| CLIProxyAPIPlus#210 | [Bug] Kiro 与 Ampcode 的 Bash 工具参数不兼容 | open |
| CLIProxyAPI#1521 | The account has available credit, but a 503 or 429 error is occurring. | open |
| CLIProxyAPIPlus#206 | bug: Nullable type arrays in tool schemas cause 400 error on Antigravity/Droid Factory | open |
| CLIProxyAPI#1514 | Token refresh logic fails with generic 500 error ("server busy") from iflow provider | open |
| CLIProxyAPI#1513 | bug: Nullable type arrays in tool schemas cause 400 error on Antigravity/Droid Factory | open |
| CLIProxyAPI#1508 | Feature: Per-OAuth-Account Outbound Proxy Enforcement for Google (Gemini/Antigravity) + OpenAI Codex (incl. token refresh and strict/fail-closed mode) | open |
| CLIProxyAPI#1507 | [BUG] 反重力 Opus-4.5 在 OpenCode 上搭配 DCP 插件使用时会报错 | open |
| CLIProxyAPI#1477 | bug: request-level metadata fields injected into contents[] causing Gemini API rejection (v6.8.4) | open |
| CLIProxyAPIPlus#201 | failed to save config: open /CLIProxyAPI/config.yaml: read-only file system | open |

## 2) thegent impact classification (direct/indirect/external)

| Issue | Classification | Rationale |
|---|---|---|
| CLIProxyAPIPlus#210 | indirect | CLI tool-parameter translation mismatch is upstream in proxy adapter behavior; affects thegent via routed tool calls. |
| CLIProxyAPI#1521 | external | Provider/quota/rate-limit behavior (503/429) is external to this repo. |
| CLIProxyAPIPlus#206 | indirect | Schema normalization/translation bug in proxy stack; thegent can add guards/tests for compatibility expectations. |
| CLIProxyAPI#1514 | external | Token refresh failure occurs in upstream provider integration layer. |
| CLIProxyAPI#1513 | indirect | Same class as #206; translation/schema compatibility issue upstream. |
| CLIProxyAPI#1508 | external | Feature request centered on proxy enforcement policy outside this repo. |
| CLIProxyAPI#1507 | indirect | OpenCode + DCP plugin interop likely at route/translation boundary; can be captured by regression fixtures here. |
| CLIProxyAPI#1477 | indirect | Request metadata contamination into Gemini payload is translator-layer bug; thegent can assert outbound payload contracts in tests. |
| CLIProxyAPIPlus#201 | external | Filesystem mount/read-only write failure is deployment/runtime environment concern. |

## 3) Proposed local actions (tests/docs/code touchpoints) with priority P0/P1/P2

- P0: Add translator regression tests to ensure request-level metadata never enters Gemini `contents[]` payloads (targets #1477).
  - Touchpoints: `tests/` translator/proxy payload tests; request-shaping fixtures under existing protocol/translator test suites.
- P0: Add schema-compat tests for nullable array tool params to prevent 400 regressions (targets #206/#1513).
  - Touchpoints: `tests/` tool-schema conversion tests; fixtures covering `type: ["array", "null"]` and normalized output expectations.
- P1: Add integration-style tests for Bash tool argument serialization compatibility for Kiro/Ampcode-style invocations (targets #210).
  - Touchpoints: `tests/` tool-call argument mapping suite; docs note in relevant compatibility report.
- P1: Add error-surface tests that preserve explicit upstream 429/503 and token-refresh failures without masking (targets #1521/#1514).
  - Touchpoints: `tests/` provider error translation; ensure fail-loud mapping in current error wrapper paths.
- P2: Document known external/runtime-only classes (read-only config path, per-account outbound proxy policy) as non-repo-owned with escalation route (targets #201/#1508).
  - Touchpoints: `docs/reports/` lane report follow-up or `docs/reference/` issue triage notes.

## 4) Blockers/unknowns

- No reproducible payload samples are included in `WORK_STREAM_CLIPROXY_ALL.md` for #210/#1477/#206/#1513, so exact failing request shapes are unknown.
- Ownership boundary is unclear between `CLIProxyAPI` and `CLIProxyAPIPlus` for shared schema/translator code paths; may affect where fixes belong.
- #1507 includes OpenCode + DCP plugin context not represented in this repo’s current local fixtures.
- #1521 and #1514 may require provider telemetry unavailable from this repository.

## 5) Next 3 executable tasks for this lane

1. Create failing regression tests for metadata leakage into Gemini `contents[]` and nullable array tool schemas, scoped to existing translator/protocol test modules.
2. Add compatibility tests for Bash tool argument mapping (Kiro/Ampcode shape) and verify expected normalized request body.
3. Draft a short triage addendum mapping #1521/#1514/#1508/#201 as external dependencies with explicit escalation owner and evidence needed for handoff.
