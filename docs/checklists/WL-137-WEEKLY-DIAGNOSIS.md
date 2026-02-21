# WL-137 Weekly LOC/Refactor Diagnosis Checklist

Use this checklist once per week to keep LOC/refactor drift visible across active codebases.

## Run

- [ ] Run `task diag:wl137`.
- [ ] Confirm the command exits zero (or explicitly triage non-zero alerts).
- [ ] Verify `var/wl137/history.json` has a new run entry.
- [ ] Verify a report exists at `docs/reports/WL-137-weekly-YYYY-MM-DD.md`.

## Review

- [ ] Check total LOC drift by target (`thegent`, `trace`).
- [ ] Check hotspot growth (`files > 500`, `files > 1000`).
- [ ] Review top-file table for new monolith candidates.
- [ ] Confirm alerts are either addressed or tracked.

## Follow-up

- [ ] If thresholds regressed, open or update decomposition work items in `docs/reference/WORK_STREAM.md`.
- [ ] Link the generated report from the relevant active plan/worklog item.
- [ ] Keep report filenames date-stamped and immutable for trend history.
