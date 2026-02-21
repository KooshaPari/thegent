// Auto-generated TypeScript declarations for project_registry
// Source: generate-api-docs.py

export declare class EpisodeRecord extends BaseModel {
}

export declare class EpisodeStatus extends StrEnum {
}

export declare class ProjectRecord extends BaseModel {
}

export declare class ProjectRegistry {
  constructor(db_path: any);
  create_episode(project_id: string, agent_id: string, metadata: any): void;
  get_episodes_for_project(project_id: string): void;
  get_project(project_id: string): void;
  list_projects(): void;
  register_project(name: string, path: string, metadata: any): void;
  update_episode(episode_id: string, status: any, metadata: any): void;
  update_project_metadata(project_id: string, metadata: Record<(str, Any)>): void;
}

export declare function create_episode(project_id: string, agent_id: string, metadata: any): void;
export declare function get_episodes_for_project(project_id: string): void;
export declare function get_project(project_id: string): void;
export declare function list_projects(): void;
export declare function register_project(name: string, path: string, metadata: any): void;
export declare function update_episode(episode_id: string, status: any, metadata: any): void;
export declare function update_project_metadata(project_id: string, metadata: Record<(str, Any)>): void;
