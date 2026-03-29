// Auto-generated TypeScript declarations for projects
// Source: generate-api-docs.py

export declare class ContextBridger {
  constructor(registry: ProjectRegistry);
  get_peer_context(project_name: string, file_pattern: string): void;
}

export declare class ProjectRegistry {
  constructor(global_config_dir: string);
  list_projects(): void;
  register_project(path: string, name: string): void;
  update_activity(path: string): void;
}

export declare function get_peer_context(project_name: string, file_pattern: string): void;
export declare function list_projects(): void;
export declare function register_project(path: string, name: string): void;
export declare function update_activity(path: string): void;
