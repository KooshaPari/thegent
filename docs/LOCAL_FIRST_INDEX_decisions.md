# LOCAL_FIRST_INDEX Decisions

Canonical home for the local-first CLI index decisions, integration checklist,
performance targets, and production-readiness checklist.

## Scope

This doc consolidates the actionable recommendations from the Rust CLI
libraries research set into a single root reference.

## Design decisions

- Use `clap` as the default parser/runtime baseline for new Rust CLIs.
- Keep interactive terminal UX optional and only add `ratatui`, `skim`, or
  `jnv` when the workflow explicitly needs selection/search affordances.
- Treat `atuin` and `pueue` as the primary workflow orchestration candidates
  for shell productivity and queued execution.
- Restrict heavier diagnostics and inspection tools such as `websocat`,
  `bandwhich`, and `ripgrep-all` to audited workflows, trusted directories, or
  explicit runbooks.
- Favor a small number of high-signal, production-ready primitives over a
  broad default install set.
- Re-evaluate the shortlist on a 90-day cadence so the decision set tracks
  upstream activity and maintenance drift.

## Integration checklist

- Verify shell compatibility before broader rollout for any tool that depends
  on hooks, shell state, or profile integration.
- Require explicit history retention, sync, and redaction policy before
  enabling command-capture tooling such as `atuin`.
- Add allow-lists or audited-directory constraints before allowing broad file
  search or network diagnostics tooling.
- Pin versions and keep lockfiles under review for tools that make operational
  decisions based on shell state or network capture.
- Document rollback steps for each pilot tool, including how to disable sync,
  clear local profile state, or remove a tool from the default path.
- Keep user-facing guidance aligned with the guarded rollout model: pilot
  first, then expand only after one team has verified the workflow end-to-end.

## Performance targets

These are selection and rollout targets, not runtime benchmarks:

- Maintain a fixed Rust CLI reference set of 100 packages for parity.
- Score candidates on a 100-point rubric with explicit gates for adoption.
- Use the following tiering:
  - Tier A: 90+ for first-class dependencies
  - Tier B: 75-89 for controlled adoption with notes
  - Tier C: below 75 for exclusion from the default catalog
- Refresh the shortlist when the source set is older than 90 days or when
  upstream release cadence materially changes the top candidates.
- Require at least two metadata signals for fragmented ecosystems before
  promoting a package into the reference set.

## Production readiness checklist

- Maintenance: recent commits, active maintainers, and a healthy issue trend.
- Tests: CI signal, visible test coverage, or documented verification steps.
- Docs: clear README, examples, and stable API or usage documentation.
- Security: security policy, explicit handling of sensitive operations, and
  release/distribution controls.
- Release cadence: tags, changelog, and predictable compatibility guidance.

## Recommendations preserved

- Adopt `clap`, `ratatui`, `pueue`, `skim`, `dust`, `miniserve`, and `grex`
  as the default high-confidence Rust CLI candidates.
- Adopt `atuin` with guardrails because its productivity gains are strong but
  its shell capture model requires policy controls.
- Treat `websocat`, `ripgrep-all`, `monolith`, and `bandwhich` as guarded or
  avoid-by-default depending on the security posture of the deployment.
- Re-score the catalog on a 90-day cadence and after any major upstream
  release or operational incident drill.

## Source reports moved here

- `docs/reports/cli-libraries-100-packages-2026-02-26/cli-libraries-100-rust-value-breakdown.md`
- `docs/reports/cli-libraries-100-packages-2026-02-26/cli-libraries-100-rust-production-readiness.md`
