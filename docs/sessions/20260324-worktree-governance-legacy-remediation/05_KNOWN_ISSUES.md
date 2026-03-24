# 05_KNOWN_ISSUES

- `task quality:pre-push:strict-governance` continues to fail while any legacy worktrees remain.
- Dirty legacy worktrees must be cleaned or pruned before migration is allowed.
- `lane-split-modules-bootstrap-v2` previously had a real `DU src/thegent/native/git_native.py`
  delete/modify conflict in `/Users/kooshapari/CodeProjects/Phenotype/repos/.worktrees/thegent--lane-split-modules-bootstrap-v2`.
  That conflict is now resolved, but the worktree is still dirty and detached, so it is not
  migratable yet.
