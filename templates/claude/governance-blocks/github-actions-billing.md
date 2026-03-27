## GitHub Actions Billing Constraint

- The KooshaPari GitHub account has a persistent Actions billing/spending-limit issue.
- GitHub Actions CI workflows will NOT run on any repo — jobs fail immediately with a billing error.
- Do NOT wait for CI checks to pass, do NOT try to "fix" CI failures caused by this, and do NOT block PRs on CI status.
- When merging PRs: remove required status checks from branch protection if needed, or use `gh pr merge --admin`.
- When creating PRs: expect CI to fail; verify quality locally (build, lint, test) instead.
- To remove required checks: `gh api repos/KooshaPari/<repo>/branches/main/protection/required_status_checks -X DELETE`
