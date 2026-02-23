# Wave 81 Lane C Report (2026-02-23)

## 1) Covered items table (issue id/title/status)

| Issue | Title | Status |
|---|---|---|
| CLIProxyAPI#1455 | Missing auth file returns 500 instead of using configured provider | open |
| CLIProxyAPI#1445 | API Error | open |
| CLIProxyAPIPlus#178 | Claude `thought_signature` forwarded to Gemini causes Base64 decode error | open |
| CLIProxyAPI#1424 | Claude -> Gemini translation fails on unsupported JSON Schema fields (`$id`, `patternProperties`) | open |
| CLIProxyAPI#1394 | Session title generation fails for Claude via Antigravity provider (OpenCode) | open |
| CLIProxyAPI#1392 | Automatic account rotation on `VALIDATION_REQUIRED` errors | open |
| CLIProxyAPIPlus#163 | Kiro: empty content in messages causes Bad Request | open |
| CLIProxyAPI#1375 | Gemini 400: unsupported `defer_loading` in `ToolSearch` | open |
| CLIProxyAPI#1325 | Gemini 3 returns 404 "Requested entity was not found" | open |

## 2) thegent impact classification (direct/indirect/external)

| Issue | Classification | Basis |
|---|---|---|
| #1455 | indirect | thegent wraps/diagnoses cliproxy auth flow; 500 behavior is primarily upstream proxy runtime behavior. |
| #1445 | external | title-only signal; no actionable local repro detail in tracker entry. |
| #178 | direct | local adapter/translator tests already assert `thought_signature` stripping behavior. |
| #1424 | direct | local adapter/translator tests already assert schema-field sanitization (`patternProperties` removal). |
| #1394 | external | session title generation path appears upstream/provider-side from issue framing. |
| #1392 | indirect | rotation policy is upstream feature; local prechecks/failure surfacing can be improved. |
| #163 | direct | empty-content normalization is request-shaping logic applicable to local adapter layer. |
| #1375 | direct | unsupported-field stripping is local request translation concern. |
| #1325 | external | model availability/404 is provider catalog/runtime side; local handling is secondary. |

## 3) Proposed local actions (tests/docs/code touchpoints) with priority P0/P1/P2

| Priority | Action | Local touchpoints |
|---|---|---|
| P0 | Add/expand regressions for translation sanitization covering `thought_signature`, unsupported schema keys, unsupported tool fields, and empty content normalization. | `tests/test_unit_cliproxy_adapter.py`, `tests/routing/test_litellm_responses_handler.py`, `src/thegent/cliproxy_adapter.py`, `src/thegent/utils/routing_impl/litellm_responses_handler.py` |
| P0 | Ensure local request-transform path strips/normalizes Gemini-incompatible payload fields (`$id`, `patternProperties`, `defer_loading`) and preserves fail-loud errors when still invalid. | `src/thegent/cliproxy_request_transform.py`, `src/thegent/cliproxy_adapter.py`, `src/thegent/utils/routing_impl/transforms.py` |
| P1 | Improve auth-missing/user-action guidance in doctor/cliproxy manager to reduce opaque "500-like" user experience. | `src/thegent/doctor.py`, `src/thegent/agents/cliproxy_manager.py`, `tests/test_unit_cliproxy_manager.py` |
| P1 | Add deterministic integration parity coverage for known cliproxy incompatibility signatures (Gemini 400/404 classes) to classify upstream vs local transform failures quickly. | `tests/integration/test_parity_legacy_vs_cliproxy_migration.py`, `tests/auth/test_parity_oauth_vs_cliproxy.py` |
| P2 | Add concise operator note mapping these issue IDs to local mitigations/diagnostics and explicit upstream ownership boundaries. | `docs/reference/WORK_STREAM_CLIPROXY_ALL.md` (reference only), lane reports in `docs/reports/` |

## 4) Blockers/unknowns

- #1445 lacks concrete repro payload, provider, and endpoint; cannot assign local root cause.
- #1394 and #1325 likely depend on upstream provider/model lifecycle behavior; local fixes may be limited to validation and messaging.
- #1392 is framed as feature work in upstream proxy; local lane cannot implement true account rotation behavior inside thegent alone.

## 5) Next 3 executable tasks for this lane

1. Add one focused regression file covering #163 and #1375 payload sanitation/normalization edge cases in local adapter/transform logic.
2. Harden `cliproxy_request_transform`/adapter sanitization for Gemini-incompatible fields and run targeted pytest selection for touched tests.
3. Add doctor/cliproxy manager diagnostics path that turns missing/invalid auth prerequisites into explicit actionable guidance, then validate with unit tests.
