# Evidence Bundle Rollout

## Overview
Bring the phenotype-nexus docs into compliance with the evidence-bundle mandate by planning the rollout in discrete milestones, tracking each chunk inside AgilePlus, and recording the WBS details back into the docs/sessions worklog.

## WBS Milestones
1. *Phase 1 – Coverage Mapping*: Identify every tutorial/how-to/API/reference/CLI leaf that needs `type`/`evidence_bundle` metadata and a bundle assignment.
2. *Phase 2 – Bundle Generation*: Produce placeholder or real evidence artifacts (manifest, GIF, VHS, API simulation) per bundle and verify the gate for each doc family.
3. *Phase 3 – Validation & Automation*: Run the `docs:evidence` check, capture the results, and bake a regression guard (CI/Playwright) that prevents regressions for future bundles.

## Work Packages
- `WP01-document-evidence-classification`: blueprint of doc families, frontmatter standardization, and onboarding instructions for future contributors.
- `WP02-evidence-bundle-creation`: artifact generation, naming conventions, drop-in resources, and translation-specific bundles.
- `WP03-validation-and-automation`: gating checks, release notes, and CI guard configuration.

## Success Criteria
- Each targeted doc either has a dedicated bundle or falls under a documented exemption, and the evidence gate passes (`npm run docs:evidence`).
- AgilePlus tasks capture lane movement for each work package and the worklog documents the chunked progress.
