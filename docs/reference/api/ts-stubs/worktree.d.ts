// Auto-generated TypeScript declarations for worktree
// Source: generate-api-docs.py

export declare class BranchCoordinator {
  get_safe_branch_name(base: string): void;
}

export declare class WorktreeManager {
  constructor(project_root: string, mesh_dir: string);
  cleanup_worktree(agent_id: string): void;
  create_worktree(agent_id: string, branch_name: any): void;
  list_active_worktrees(): void;
}

export declare function cleanup_worktree(agent_id: string): void;
export declare function create_worktree(agent_id: string, branch_name: any): void;
export declare function get_safe_branch_name(base: string): string;
export declare function list_active_worktrees(): void;
