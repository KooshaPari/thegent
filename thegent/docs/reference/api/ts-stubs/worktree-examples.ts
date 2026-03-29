// Auto-generated usage examples for worktree
// Source: generate-api-docs.py

import { BranchCoordinator, WorktreeManager, cleanup_worktree, create_worktree, get_safe_branch_name, list_active_worktrees } from "./worktree";

// Create a BranchCoordinator instance
const branchcoordinator = new BranchCoordinator();
branchcoordinator.get_safe_branch_name("example_base");

// Create a WorktreeManager instance
const worktreemanager = new WorktreeManager("example_project_root", "example_mesh_dir");
worktreemanager.cleanup_worktree("example_agent_id");
worktreemanager.create_worktree("example_agent_id", undefined as unknown as any);
worktreemanager.list_active_worktrees();

// Call cleanup_worktree
cleanup_worktree(undefined as unknown as any, "example_agent_id");
// Call create_worktree
create_worktree(undefined as unknown as any, "example_agent_id", undefined as unknown as any);
// Call get_safe_branch_name
get_safe_branch_name("example_base");
// Call list_active_worktrees
list_active_worktrees(undefined as unknown as any);
