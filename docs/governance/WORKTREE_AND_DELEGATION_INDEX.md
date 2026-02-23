# Worktree and Delegation Governance Index

Use this index as the entrypoint for multi-agent worktree/commit/delegation governance.

## Documents

1. `docs/governance/WORKTREE_SCALE_COMMIT_VERSION_PR_POLICY.md`
2. `docs/governance/DELEGATION_ARCHITECTURE_LN.md`
3. `docs/governance/TASK_CLASSIFIER_SCHEMA.yaml`
4. `docs/governance/DOMAIN_PLAYBOOKS.md`
5. `docs/governance/GOVERNANCE_ROADMAP_DAG.md`
6. `docs/governance/MCP_A2A_CONTROL_PLANE_BOUNDARY.md`
7. `docs/governance/ROLLOUT_PHASES_CHECKLIST.md`

## Adoption Order

1. Read and approve policy matrix.
2. Adopt classifier schema and delegation contracts.
3. Implement scheduler placement and conflict controls.
4. Enforce in hooks and CI.
5. Roll out by lane percentages.

## Enforced Commands

1. `./scripts/worktree_governance.sh new <branch> [start-point]`
2. `./scripts/worktree_governance.sh check`
