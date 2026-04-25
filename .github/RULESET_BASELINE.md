# thegent Ruleset Baseline

This repository uses a stacked-PR-friendly protected-main baseline and repo-local governance
workflows for layered branch policy.

## Enforced Branch Protection Baseline

- require pull requests before merge on the default branch
- block force pushes and branch deletion
- require at least 1 approval
- dismiss stale approvals on new pushes
- require resolved review threads before merge
- allow merge methods: `merge`, `squash`
- enable GitHub `code_quality`
- enable GitHub `copilot_code_review`

## Repo-Local Governance Gates

The repo complements the branch ruleset with workflow-based gates:

- `policy-gate`
- `pr-governance-gate`
- `sast-quick`
- `codeql`
- `security-guard`

Required status check mapping is still a follow-up item and should be encoded once the stable job
names are locked.

## Branch Policy

- stacked PR lanes such as `stack/*`, `layer/*`, `preview/*`, `feat/*`, and `release/*` are valid
  and preferred for multi-step work
- `fix/*` must not target `main` or `master` unless the PR carries `layered-pr-exception`
- merge commits in PR branches are disallowed by the repo-local governance workflow
- local `--no-verify` usage is not accepted as a reason to bypass server-side workflow checks

## Exception Policy

- only documented billing or quota failures may be excluded from CI blocking review
- billing-only exceptions must be documented in the PR body and carry the
  `ci-billing-exception` label
- review threads and blocking comments must be resolved before merge
