# Phenotype `repos/` hub

**Deployment:** This file is the **canonical, versioned** copy of the on-disk index at `Phenotype/repos/README.md` (the hub folder is not its own git repository). After editing here, **sync** the same body to `repos/README.md` on the filesystem so local navigation and agent policy stay aligned.

---

# Phenotype `repos/` hub

This directory is the **Phenotype multi-repository worktree hub**: many project checkouts and feature branches live here alongside shared scripts and policy. It is not a single application repo; treat each subdirectory as its own Git project unless documented otherwise.

**Agent and workflow policy:** see [AGENTS.md](../../../AGENTS.md) for canonical `main` vs worktree layout, quality gates, and migration notes. (Path is relative to this file inside the `thegent` checkout; when copied to `repos/README.md`, use `./AGENTS.md`.)

**Naming note (cliproxy):** you may see **`cliproxy-wtrees`** (intended worktrees path) and a typo symlink or path like **`cliproxy-wtress`**. Prefer the structured layout under `repos/worktrees/<project>/...` as described in [AGENTS.md](../../../AGENTS.md). Do not perform mass moves or bulk renames here without an explicit, reviewed plan—compatibility symlinks and incremental migration are preferred.
