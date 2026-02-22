# Architecture Decisions — 2026-02-16

Status: ACTIVE (2026-02-22)
Scope: Executable decision record for recovery and architecture direction captured on 2026-02-16

## ADR Register
| ADR ID | Title | Status | Primary Evidence |
| --- | --- | --- | --- |
| ADR-2026-02-16-01 | Standardize Shell/Shim Recovery Flow | Accepted | `docs/research/CURSOR_AGENT_RECOVERY_2026-02-16.md` |
| ADR-2026-02-16-02 | Promote GUI/TUI Notes into Planned Work | Accepted | `docs/research/PROMPTS_LAST_12H.md` |
| ADR-2026-02-16-03 | Adopt Hybrid Compute Offloading | Accepted | `docs/research/CONVERSATION_DUMP_2026-02-16.md` |
| ADR-2026-02-16-04 | Enforce Conversation Dump Persistence by Default | Accepted | `docs/research/CONVERSATION_DUMP_2026-02-18.md` |

## ADR-2026-02-16-01 — Standardize Shell/Shim Recovery Flow
- **Context:** Recovery work was inconsistent across shell configs and typing conventions.
- **Decision:** Use a single typed recovery flow and one auditable procedure.
- **Execution Effect:** Recovery tasks must follow one documented path before escalation.
- **Evidence:** `docs/research/CURSOR_AGENT_RECOVERY_2026-02-16.md`

## ADR-2026-02-16-02 — Promote GUI/TUI Notes into Planned Work
- **Context:** Desktop interaction strategy existed as fragmented exploratory notes.
- **Decision:** Treat GUI/TUI direction as implementation planning input, not passive notes.
- **Execution Effect:** Convert design statements into backlog-ready implementation slices.
- **Evidence:** `docs/research/PROMPTS_LAST_12H.md`

## ADR-2026-02-16-03 — Adopt Hybrid Compute Offloading
- **Context:** Pure local or pure remote execution created responsiveness and reliability trade-offs.
- **Decision:** Use a hybrid local/remote model with explicit transport/sync assumptions.
- **Execution Effect:** New compute-path work must declare local/remote boundaries up front.
- **Evidence:** `docs/research/CONVERSATION_DUMP_2026-02-16.md`

## ADR-2026-02-16-04 — Enforce Conversation Dump Persistence by Default
- **Context:** Missing dump evidence increased incident reconstruction cost.
- **Decision:** Make dump persistence a baseline operating requirement.
- **Execution Effect:** Session workflows must include explicit dump-write checkpoints.
- **Evidence:** `docs/research/CONVERSATION_DUMP_2026-02-18.md`

## Immediate Implementation Hooks
- Add dump checkpoint validation to session-close workflow.
- Keep chronology and decision backlinks synchronized between 2026-02-16 and 2026-02-18 dumps.
- Re-open this file only when a decision changes, not for routine status updates.

## Implementation Ticket Seeds
| Seed ID | Derived From ADR | Ticket Seed | Done Signal |
| --- | --- | --- | --- |
| TSEED-01 | ADR-2026-02-16-01 | Standardize and lint shell/shim recovery procedure docs + command sequence. | Recovery runbook executes in one deterministic order. |
| TSEED-02 | ADR-2026-02-16-02 | Split GUI/TUI design statements into small backlog slices with owner and artifact path. | Each slice has a concrete file target and verification command. |
| TSEED-03 | ADR-2026-02-16-03 | Add compute-path declaration checklist (local/remote boundary) to implementation planning docs. | New compute work includes explicit boundary declaration. |
| TSEED-04 | ADR-2026-02-16-04 | Enforce dump persistence checks at session close with fail-fast output. | Session close fails when required dump metadata/backlinks are missing. |

## Decision Validation Matrix
| ADR ID | Validation Check | Cadence | Pass Signal |
| --- | --- | --- | --- |
| ADR-2026-02-16-01 | Recovery drill follows one shell/shim sequence without branch-specific variants. | Weekly | One runbook path succeeds end-to-end. |
| ADR-2026-02-16-02 | GUI/TUI notes are converted into backlog slices with owner + verification command. | Per planning cycle | No net-new design note remains untracked. |
| ADR-2026-02-16-03 | New compute work declares local/remote boundary and transport assumptions. | Per proposal | Boundary declaration is present before implementation starts. |
| ADR-2026-02-16-04 | Session close writes dump metadata and required backlinks before completion. | Per session close | Close step fails fast when persistence evidence is missing. |

## Revisit Triggers
- **ADR-2026-02-16-01:** Revisit when recovery incidents require ad hoc shell-specific exceptions more than once in a sprint.
- **ADR-2026-02-16-02:** Revisit when GUI/TUI backlog conversion lags by one planning cycle or ownership is consistently missing.
- **ADR-2026-02-16-03:** Revisit when hybrid handoff failures or latency regressions breach agreed operating thresholds.
- **ADR-2026-02-16-04:** Revisit when dump persistence checks are bypassed or incident reconstruction lacks required session evidence.

## Decision Debt Register
| Debt ID | Linked ADR | Current Decision Debt | Retirement Condition |
| --- | --- | --- | --- |
| DDEBT-01 | ADR-2026-02-16-01 | Recovery flow is standardized, but exception-rate thresholds are narrative-only. | Promote exception threshold to an enforced checklist gate in recovery runbook execution. |
| DDEBT-02 | ADR-2026-02-16-02 | GUI/TUI note-to-backlog conversion is required, but conversion latency is not instrumented. | Add cycle-level latency tracking for note conversion with owner accountability. |
| DDEBT-03 | ADR-2026-02-16-03 | Hybrid boundaries are required, but boundary declarations are not schema-validated. | Enforce required local/remote boundary fields in proposal templates before implementation starts. |
| DDEBT-04 | ADR-2026-02-16-04 | Dump persistence is mandatory, but backlink completeness checks are runtime-only. | Add pre-close static validation for dump metadata and backlink integrity. |

## Supersession Protocol
- A superseding ADR must reference the replaced ADR ID(s) from this file and state one explicit reason category: reliability, operability, or evidence quality.
- Any supersession proposal must include updated entries for `Implementation Ticket Seeds`, `Decision Validation Matrix`, and `Revisit Triggers` before status changes.
- Status transition order is strict: `Accepted` (new ADR) → `Superseded` (old ADR) in the same edit, with no intermediate ambiguity.
- Supersession is valid only when the new ADR defines a tighter or equivalent pass signal than the old one and preserves evidence paths.
