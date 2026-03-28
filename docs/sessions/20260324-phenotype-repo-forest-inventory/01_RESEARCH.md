# Research Notes: Repo Forest Inventory

## Top-level git checkouts reviewed

- `agentops-policy-federation` - clean, on `main`
- `trace` - clean, on `main`
- `portage` - clean, on `main`
- `tokenledger` - clean, on `main`
- `bifrost-extensions` - clean, on `main`
- `agentapi-plusplus` - clean, on `main`
- `phenotype-go-kit` - clean, on `main`
- `heliosApp` - dirty, on `main...upstream/main [ahead 8]`
- `heliosCLI` - dirty, on `main...origin/main [ahead 15, behind 112]`
- `phenotypeActions` - dirty, on `main...origin/main [ahead 2]`
- `phenotype-config` - dirty, on `main...upstream/main [ahead 1]`
- `phenotype-design` - dirty, on `main...origin/main [ahead 1]`
- `AgilePlus` - dirty, on `release-turn-202603240347`
- `phenodocs` - dirty, on `feat/planning-next50-linear-20260326`
- `thegent` - dirty, on `main...upstream/main [ahead 21]`
- `trash-cli` - dirty, on `master...origin/master [ahead 10]`
- `agent-devops-setups` - clean, on `agentops/policy-federation-rollout...origin/agentops/policy-federation-rollout [ahead 6]`
- `phenotype-shared` - clean, on `feat/create-state-machine-crate`

## Initial diff classification

- `heliosApp`: real runtime changes in `apps/runtime/src/audit/sink.ts`, `apps/runtime/src/index.ts`, and `apps/runtime/src/protocol/validator.ts`, plus the `worktrees/heliosApp/dotagents` pointer change.
- `heliosCLI`: only the `worktrees/heliosCLI/dotagents` pointer change showed up in the first status pass.
- `phenotypeActions`: untracked `.github/CODEOWNERS`.
- `phenotype-config`: generated `spec-kitty.*` command/prompt scaffolding across `.claude`, `.codex`, and `.cursor`.
- `phenotype-design`: theme/config docs edits plus new docs/governance files and workspace metadata.
- `AgilePlus`: generated `agileplus.*` scaffolding and route edits in `crates/agileplus-api/src/routes/*.rs`.
- `phenodocs`: `.vitepress/.temp` deletions, likely generated cache churn.
- `thegent`: current working tree snapshot only shows the untracked `worktrees/thegent/dotagents/` pointer.
- `trash-cli`: one untracked workflow file, `.github/workflows/security-scan-schedule.yml`.

## Intent classification

- `phenotype-config` appears to be intentional bootstrap scaffolding: large generated command/prompt/template sets, not random churn.
- `AgilePlus` appears intentional and validated: the branch carries substantive API/state refactors plus generated command scaffolding.
- `phenodocs` current dirty state is pointer churn only in the latest snapshot.

## Validation results

- `cargo check -p agileplus-api -p agileplus-sqlite -p agileplus-git` passed in `AgilePlus`.
- `npm run docs:build` passed in `phenotype-design`.
- `thegent` staged-state check did not show the previously suspected secret deletions in the current snapshot.
- `thegent` policy-federation run metadata enrichment now has a dedicated integration module and
  repo-name resolver that treats both canonical roots and `worktrees/<repo>/...` lanes as the same
  owning repo.

## Notes

- The child-agent delegation path in this session repeatedly hit a model usage ceiling and is not reliable for this pass.
- Direct shell inventory is the current source of truth.
