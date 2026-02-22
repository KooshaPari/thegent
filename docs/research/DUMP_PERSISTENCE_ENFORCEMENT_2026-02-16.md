# Dump Persistence Enforcement — 2026-02-16

Status: ENFORCEMENT SPEC (2026-02-22)
Scope: Operational rules to guarantee conversation/research dump persistence

## Enforcement Rules
1. Every research or architecture session MUST end with a persisted dump artifact in `docs/research/`.
2. Dump updates MUST include `Purpose`, `Date`, and at least one actionable `Next Steps` block.
3. If chronology or decisions change, dependent dump files MUST be cross-linked in the same edit.

## Trigger Points
| Trigger | Required Action | Failure Condition |
| --- | --- | --- |
| Session start | Declare target dump artifact for this lane/workstream. | No target file declared. |
| Mid-session handoff | Write incremental findings before switching tasks. | Context exists only in terminal output. |
| Session close | Confirm dump file saved and backlinks updated. | Work completed with no persisted artifact links. |

## Enforcement Command Matrix
| Checkpoint | Command | Expected Signal | On Failure |
| --- | --- | --- | --- |
| Artifact presence | `ls docs/research/CONVERSATION_DUMP_*.md` | Target dated dump file exists | Stop closeout and create/update dump |
| Required metadata | `rg -n \"\\*\\*Purpose:\\*\\*|\\*\\*Date:\\*\\*|Next Steps\" docs/research/CONVERSATION_DUMP_*.md` | `Purpose`, `Date`, and `Next Steps` are present | Patch missing sections before completion |
| Cross-link integrity | `rg -n \"CONVERSATION_DUMP_2026-02-16_COMPLETE|ARCH_DECISIONS_2026-02-16|RECOVERY_TRANSCRIPT_GAP_REPORT_2026-02-16\" docs/research/*.md` | Required backlinks resolve in research docs | Add missing backlinks in same lane pass |

## Failure Handling
- **Hard fail:** Stop lane completion if required dump artifacts are missing.
- **Recovery action:** Reconstruct from available sources and record missing evidence in a gap report.
- **Escalation:** Mark unresolved evidence explicitly as `Unrecoverable`; do not silently omit.

## Operator Checklist
- [ ] Dump file exists for the session date/workstream.
- [ ] Cross-links to chronology/decisions are present where applicable.
- [ ] Open evidence gaps are tracked in `RECOVERY_TRANSCRIPT_GAP_REPORT_2026-02-16.md`.

## Automation Hooks
| Hook Point | Hook Action | Fail Message |
| --- | --- | --- |
| `UserPromptSubmit` | Require explicit target dump file path for active lane/work item. | `DUMP_ENFORCEMENT_FAIL: target dump artifact not declared` |
| `PostToolUse` (write/edit) | Detect research/architecture edits and confirm required metadata fields remain present. | `DUMP_ENFORCEMENT_FAIL: required dump metadata missing` |
| `Stop` / session close | Run backlink + artifact presence checks before lane completion. | `DUMP_ENFORCEMENT_FAIL: dump artifact/backlink validation failed` |

## Compliance Signals
- **Pre-close signal:** `ls docs/research/CONVERSATION_DUMP_*.md | tail -n 1` returns the active dated dump artifact.
- **Metadata signal:** `rg -n "\\*\\*Purpose:\\*\\*|\\*\\*Date:\\*\\*|Next Steps" docs/research/CONVERSATION_DUMP_*.md` shows all required fields.
- **Backlink signal:** `rg -n "CONVERSATION_DUMP_|ARCH_DECISIONS_|RECOVERY_TRANSCRIPT_GAP_REPORT_" docs/research/*.md` confirms linked recovery context exists.

## Recovery Drills
- **Drill 1 — Missing artifact:** Temporarily move target dump, run artifact check, then restore and re-run until pass.
- **Drill 2 — Missing metadata:** Remove one required field in a local scratch edit, run metadata check, then patch and verify clean output.
- **Drill 3 — Broken backlink:** Replace one expected reference token, run backlink check, then restore canonical token and confirm pass.

## Failure Taxonomy
| Class | Detection Command | Operator Action |
| --- | --- | --- |
| Artifact missing | `ls docs/research/CONVERSATION_DUMP_*.md` | Create/update target dump before any closeout. |
| Metadata incomplete | `rg -n "\\*\\*Purpose:\\*\\*|\\*\\*Date:\\*\\*|Next Steps" docs/research/CONVERSATION_DUMP_*.md` | Patch required fields in the same lane pass. |
| Backlink broken | `rg -n "CONVERSATION_DUMP_|ARCH_DECISIONS_|RECOVERY_TRANSCRIPT_GAP_REPORT_" docs/research/*.md` | Restore canonical link tokens before handoff. |
| Evidence unrecoverable | `rg -n "Unrecoverable|GAP" docs/research/RECOVERY_TRANSCRIPT_GAP_REPORT_2026-02-16.md` | Record gap explicitly and escalate for sign-off. |

## Enforcement Escalation Matrix
| Severity | Condition | Immediate Command | Escalation Action |
| --- | --- | --- | --- |
| SEV-1 Blocker | No dump artifact for active session | `ls docs/research/CONVERSATION_DUMP_*.md` | Halt completion; assign owner to restore artifact now. |
| SEV-2 Major | Required metadata missing | `rg -n "\\*\\*Purpose:\\*\\*|\\*\\*Date:\\*\\*|Next Steps" docs/research/CONVERSATION_DUMP_*.md` | Patch immediately; re-run checks before resume. |
| SEV-3 Moderate | Backlinks incomplete or stale | `rg -n "CONVERSATION_DUMP_|ARCH_DECISIONS_|RECOVERY_TRANSCRIPT_GAP_REPORT_" docs/research/*.md` | Queue same-pass fix and confirm clean grep output. |
| SEV-4 Advisory | Marked unrecoverable evidence gap | `rg -n "Unrecoverable" docs/research/RECOVERY_TRANSCRIPT_GAP_REPORT_2026-02-16.md` | Notify lane lead and track resolution owner/date. |
