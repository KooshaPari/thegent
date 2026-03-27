## Phenotype Long-Term Stability and Non-Destructive Change Protocol <!-- PHENOTYPE_LONGTERM_STABILITY_PROTOCOL -->

- Optimize for long-term platform value over short-term convenience; choose durable solutions even when implementation complexity is higher.
- Classify proposed changes as `quick_fix` or `stable_solution`; prefer `stable_solution` unless an incident response explicitly requires a temporary fix.
- Do not use deletions/reversions as the default strategy; prefer targeted edits, forward fixes, and incremental hardening.
- Prefer moving obsolete or superseded material into `.archive/` over destructive removal when retention is operationally useful.
- Prefer clean manual merges, explicit conflict resolution, and auditable history over forceful rewrites, force merges, or history-destructive workflows.
- Prefer completing unused stubs into production-quality implementations when they represent intended product direction; avoid leaving stubs ignored indefinitely.
- Do not merge any PR while any check is failing, including non-required checks, unless the user gives explicit exception approval.
- When proposing a quick fix, include a scheduled follow-up path to a stable solution in the same plan.
