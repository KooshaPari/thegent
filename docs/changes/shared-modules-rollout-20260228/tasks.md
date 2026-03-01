# Tasks: Shared Modules Rollout 2026-02-28

## Phased WBS + DAG

| Phase | Task ID | Description | Depends On | Branch | Worktree |
|---|---|---|---|---|---|
| A | WT-01 | Extract reusable policy gate module and validate in `helios-cli` | none | `mod/policy-gate-v1` | `/Users/kooshapari/CodeProjects/Phenotype/repos/.worktrees/helios-cli--mod-policy-gate-v1` |
| A | WT-03 | Extract polyglot config core contract from `phenotype-config` | none | `mod/polyglot-config-core-v1` | `/Users/kooshapari/CodeProjects/Phenotype/repos/.worktrees/phenotype-config--mod-polyglot-config-core-v1` |
| B | WT-02 | Normalize CLI task surface module (`lint/test/build/release`) | WT-01 | `mod/cli-task-surface-v1` | `/Users/kooshapari/CodeProjects/Phenotype/repos/.worktrees/helios-cli--mod-cli-task-surface-v1` |
| B | WT-04 | Extract provider ledger schema + tooling | WT-03 | `mod/provider-ledger-schema-v1` | `/Users/kooshapari/CodeProjects/Phenotype/repos/.worktrees/tokenledger--mod-provider-ledger-schema-v1` |
| B | WT-05 | Extract proxy auth/access SDK module | WT-03 | `mod/proxy-auth-access-sdk-v1` | `/Users/kooshapari/CodeProjects/Phenotype/repos/.worktrees/cliproxyapi-plusplus--mod-proxy-auth-access-sdk-v1` |
| C | WT-06 | Extract queue orchestrator as reusable module | WT-02 | `mod/queue-orchestrator-v1` | `/Users/kooshapari/CodeProjects/Phenotype/repos/.worktrees/portage--mod-queue-orchestrator-v1` |
| C | WT-07 | Extract OpenAPI+SSE agent client module | WT-05 | `mod/openapi-agent-client-v1` | `/Users/kooshapari/CodeProjects/Phenotype/repos/.worktrees/agentapi-plusplus--mod-openapi-agent-client-v1` |
| D | WT-08 | `thegent` app-composition cutover (orchestration-only) | WT-01,WT-02,WT-03,WT-04,WT-05,WT-06,WT-07 | `mod/thegent-app-composition-v1` | `/Users/kooshapari/CodeProjects/Phenotype/repos/.worktrees/thegent--mod-app-composition-v1` |

## Lane Acceptance Checklist (applies to every WT-XX)
1. Module package metadata and versioning are present.
2. Public interface contract is documented.
3. Module-local tests pass.
4. At least one consumer integration test passes.
5. Lint/type/security checks pass in host repo.
6. Migration note identifies removed duplicate code paths.

## Stop Rules
1. If a lane changes files owned by another active lane, stop and split scope.
2. If contract tests fail in more than two consumer repos, open a contract-fix lane first.
3. If governance gate state is red in host repo, pause feature extraction and repair gates.
4. If merge-base drift causes replay conflicts, rebase lane and restage atomic commits before PR.
