# 07_NEXT_WAVE — 24 items (6 slices × 4)

Session-end queue for **worktree / runtime hygiene**. Re-verify lane state before executing (see `04_QUEUE_CADENCE.md`). **Snapshot:** 2026-03-24.

## Slice 1 — heliosApp (4)

1. Confirm `heliosApp/heliosApp-wtrees/decomp-20260314`: `git status`, branch intent, no stray `.tmp/runtime-secrets-tests` commits.
2. Run full runtime gates from that worktree: `bun run typecheck`, `bun test` (or repo `task`/`package.json` equivalent).
3. Open or update PR for decomp lane; resolve CI; request review per team process.
4. After merge: return canonical `heliosApp` to `main` and prune/remove finished worktree per governance.

## Slice 2 — heliosCLI (4)

5. Repair or park dirty `heliosCLI` canonical root (tracked in family matrix).
6. Resolve **detached** `heliosCLI-composite-actions` (register, remove, or repoint).
7. Burn down next dirty lane in `heliosCLI-wtrees` (e.g. governance/Bazel lanes) — one lane at a time.
8. Re-run `git worktree list` from `heliosCLI` repo root; fix broken entries.

## Slice 3 — helios-cli / colab / helMo (4)

9. `helios-cli` root: clear untracked nested worktree paths or add to `.gitignore` with rationale.
10. `colab` canonical root: commit or revert dirty `main` drift; align with upstream.
11. `colab-wtrees/stabilize` and `colab-wtrees/helios-integration`: repair or symlink decision.
12. Leave clean lanes untouched: `helios-cli/.worktrees/*` mod lanes, `colab-wtrees/parity-*`, `colab-wtrees/ts-debt-*`, `helMo-wtrees/stability-audit` — verify still clean.

## Slice 4 — cliproxy (4)

13. Canonicalize **`cliproxy-wtrees` vs `cliproxy-wtress`** (typo duplicate): one symlink or rename policy; document.
14. Triage detached lanes under `cliproxy-wtress` / `cliproxyapi++` forests (state check each).
15. Prune **gone** or safe-to-remove lanes after explicit confirmation.
16. Avoid duplicating large parallel forests; align with `migrate-legacy` / `worktree_governance.sh` when ready.

## Slice 5 — portage (4)

17. Decision pass: **detached** `portage-wtrees/agentops-policy-federation`, `oxc-consolidated-fix`, `oxc-governance-fix`, `oxc-migration-fix`, `.worktrees/portage-policy-federation-onboard`.
18. Prune **prune-safe** `/private/tmp/portage-*` and `wt-portage-*` temp worktrees after `git worktree list` confirms.
19. Prune `PROJECT-wtrees/codex-mlx-eval` if still marked prunable and no unique commits.
20. Fix broken `gitdir` pointers if any remain after prune.

## Slice 6 — trace / trash-cli / ralph-codex-loop (4)

21. **Resolved** `trace-wtrees/codex-required-gates*` — locks cleared 2026-03-28; `git worktree list --porcelain` now only reports the three canonical lanes (`trace` @ `b81e00522e2ae559eb308de8f4a2d7959717ccde` on `fix/tracertm-types-react`, `trace-wtrees/spec-docs` @ `ecfab33f92bb717df72a5dc1217b402cf3fdee58` on `docs/add-adr`, `trace-wtrees/ui-overhaul` @ `3eabc971ed5aa0943013f264fa75565bd8a44f7d` on `fix/ts4111-build-v2`); no `codex-required-gates*` entries remain to unlock or prune.
22. Retain visibility on `codex-required-gates*` history before reusing the names; ensure no additional locked refs exist prior to future migrations.
23. **Detached** `trash-cli/PROJECT-wtrees/pr1-rust-put-fix` — repair attachment or explicit abandon.
24. **Unborn** `ralph-codex-loop` / child lane — init repo or remove worktree entry.

---

**Note:** The automatic “full Phenotype repos + GitHub account” inventory is **out of band** for this wave; refresh counts only when running a dedicated inventory session.
