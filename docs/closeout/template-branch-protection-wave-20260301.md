# Template Branch-Protection Wave Closeout

Date: 2026-03-01T14:08:46Z

## Scope
- template-lang-python
- template-lang-zig
- template-lang-go
- template-lang-elixir-hex
- template-lang-kotlin
- template-lang-mojo
- template-lang-rust
- template-lang-swift
- template-lang-typescript
- template-domain-service-api
- template-domain-webapp
- template-program-ops
- template-commons

## Result Summary
| repo | merged PR | merged URL | merged at | branch protection checks | approving reviews | req. conversation resolution |
|---|---:|---|---|---|---:|---:|
| template-lang-python | #4 | [chore: enforce branch protection checks contract](https://github.com/KooshaPari/template-lang-python/pull/4) | 2026-03-01T14:06:41Z | policy-gate,validate | 0 | false |
| template-lang-zig | #4 | [chore: enforce branch protection checks contract](https://github.com/KooshaPari/template-lang-zig/pull/4) | 2026-03-01T14:06:45Z | policy-gate,validate | 0 | false |
| template-lang-go | #4 | [chore: enforce branch protection checks contract](https://github.com/KooshaPari/template-lang-go/pull/4) | 2026-03-01T14:06:48Z | policy-gate,validate | 0 | false |
| template-lang-elixir-hex | #4 | [chore: enforce branch protection checks contract](https://github.com/KooshaPari/template-lang-elixir-hex/pull/4) | 2026-03-01T14:06:51Z | policy-gate,validate | 0 | false |
| template-lang-kotlin | #4 | [chore: enforce branch protection checks contract](https://github.com/KooshaPari/template-lang-kotlin/pull/4) | 2026-03-01T14:06:54Z | policy-gate,validate | 0 | false |
| template-lang-mojo | #4 | [chore: enforce branch protection checks contract](https://github.com/KooshaPari/template-lang-mojo/pull/4) | 2026-03-01T14:06:56Z | policy-gate,validate | 0 | false |
| template-lang-rust | #4 | [chore: enforce branch protection checks contract](https://github.com/KooshaPari/template-lang-rust/pull/4) | 2026-03-01T14:06:59Z | policy-gate,validate | 0 | false |
| template-lang-swift | #4 | [chore: enforce branch protection checks contract](https://github.com/KooshaPari/template-lang-swift/pull/4) | 2026-03-01T14:07:03Z | policy-gate,validate | 0 | false |
| template-lang-typescript | #4 | [chore: enforce branch protection checks contract](https://github.com/KooshaPari/template-lang-typescript/pull/4) | 2026-03-01T14:07:05Z | policy-gate,validate | 0 | false |
| template-domain-service-api | #4 | [chore: enforce branch protection checks contract](https://github.com/KooshaPari/template-domain-service-api/pull/4) | 2026-03-01T14:07:08Z | policy-gate,validate | 0 | false |
| template-domain-webapp | #4 | [chore: enforce branch protection checks contract](https://github.com/KooshaPari/template-domain-webapp/pull/4) | 2026-03-01T14:07:11Z | policy-gate,validate | 0 | false |
| template-program-ops | #4 | [chore: enforce branch protection checks contract](https://github.com/KooshaPari/template-program-ops/pull/4) | 2026-03-01T14:07:14Z | policy-gate,validate | 0 | false |
| template-commons | #4 | [chore: enforce branch protection checks contract](https://github.com/KooshaPari/template-commons/pull/4) | 2026-03-01T13:13:41Z | policy-gate,validate | 0 | false |

## template-commons state
- `template-commons` shows PR #4 merged and aligned with the same branch protection contract after this wave.

## Notes
- All listed PR #4 entries are in `MERGED` state with zero unresolved review threads.
- Branch protection now requires `policy-gate` and `validate` checks.
- `required_conversation_resolution` is set to `false` across these repos to remove external review thread blocking.

## Follow-on: Workflow reuse and drift pass
- `policy-gate.yml` is now fully identical across all 13 template repos (hash-aligned).
- `branch-protection-audit.yml` is now aligned for `EXPECTED_CONVERSATION_RESOLUTION=false` across all 13 repos.
- `template-commons` hosts the canonical reusable workflows for both policy gate and branch-protection audit.
- `ci.yml` remains split by template stack:
  - Core stack (8 repos): `template-domain-service-api`, `template-domain-webapp`, `template-lang-elixir-hex`, `template-lang-kotlin`, `template-lang-mojo`, `template-lang-rust`, `template-lang-swift`, `template-lang-zig`
  - JS/Go stack (4 repos): `template-commons`, `template-lang-go`, `template-lang-python`, `template-lang-typescript`
  - Ops stack: `template-program-ops`
- New follow-on hardening pass:
  - Added `CODEOWNERS` to all 13 template repositories.
  - Extended reusable `policy-gate` to enforce presence of `CODEOWNERS`.
  - Removed stray untracked artifacts from the `template-commons` working checkout and archived them to:
    - `/tmp/template-commons-cleanup-archive-20260301/template-commons-wtrees`
    - `/tmp/template-commons-cleanup-archive-20260301/templates`
    - `/tmp/template-commons-cleanup-archive-20260301/phenotype-go-kit`
- Recommended reusable workflow target:
  - Share `policy-gate.yml` and standardized `branch-protection-audit.yml` via a reusable workflow template in `template-commons` (or a dedicated composite actions module), then have all language repos `workflow_call` these workflows.
