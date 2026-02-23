# Worklog Wave 81 Master (2026-02-23)

Scope: next 50 backlog items from `docs/reference/WORK_STREAM_CLIPROXY_ALL.md` Bugs 1..50.

## Lane Assignment

| Lane | Item range | Report |
|---|---|---|
| A | Bugs 1..9 | `docs/reports/2026-02-23-worklog-wave81-lane-a.md` |
| B | Bugs 10..18 | `docs/reports/2026-02-23-worklog-wave81-lane-b.md` |
| C | Bugs 19..27 | `docs/reports/2026-02-23-worklog-wave81-lane-c.md` |
| D | Bugs 28..36 | `docs/reports/2026-02-23-worklog-wave81-lane-d.md` |
| E | Bugs 37..43 | `docs/reports/2026-02-23-worklog-wave81-lane-e.md` |
| F | Bugs 44..50 | `docs/reports/2026-02-23-worklog-wave81-lane-f.md` |

## Consolidated Outcome

- 50 items were triaged in parallel across 6 child agents.
- Dominant classification pattern: `indirect` or `external` root causes in upstream proxy/providers, with a smaller subset of `direct` local contract/test work in `thegent`.
- Recurrent local themes:
  - request-shape normalization and schema sanitization
  - streaming completion/lifecycle regression coverage
  - auth/config fail-fast checks and clearer diagnostics
  - explicit no-fallback error handling contracts

## Top Priority Local Execution Queue (P0 first)

1. Add/expand request-shape regressions for tool-name parity and unsupported field stripping across provider translators.
2. Add streaming lifecycle regressions to enforce completion semantics and prevent hangs/silent terminal loss.
3. Add payload sanitization coverage for Gemini/Claude/Codex edge fields (`thought_signature`, nullable arrays, metadata leakage, unsupported fields).
4. Add strict config/auth fail-fast checks for malformed or missing auth/config paths with actionable errors.
5. Add plan-mode contract tests for unexpected parameters and explicit schema rejection.
6. Add sequential-thinking and tool-argument compatibility regressions on adapter paths.

## Immediate Next 10 Implementable Tasks

1. Write failing test: tool name parity (`tool_choice.name` vs `tools[].name`) and enforce fail-fast validation.
2. Write failing test: streaming done-marker completion event contract on proxied routes.
3. Write failing test: Gemini payload excludes unsupported metadata fields in `contents[]`.
4. Write failing test: nullable type array tool schema normalization for proxy compatibility.
5. Write failing test: unsupported OpenAI `user` parameter handling is explicit and deterministic.
6. Write failing test: config path type guard rejects directory-where-file-expected for cliproxy config.
7. Write failing test: empty-content message handling for Kiro/Gemini request conversion paths.
8. Write failing test: Codex Responses payload sanitization for disallowed `item_reference` shapes.
9. Write failing test: sequential-thinking required parameter normalization (no dropped required fields).
10. Add concise operator runbook section for upstream auth/rate-limit failures and local-vs-external triage boundaries.

