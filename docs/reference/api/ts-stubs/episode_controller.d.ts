// Auto-generated TypeScript declarations for episode_controller
// Source: generate-api-docs.py

export declare class EpisodeController {
  constructor(project_id: string, agent_id: string, registry: ProjectRegistry, shadow: ShadowAuditGit, metadata: any);
  end(): void;
  episode(): void;
  resume(): void;
  start(): void;
  suspend(): void;
}

export declare function end(): void;
export declare function episode(): void;
export declare function resume(): void;
export declare function start(): void;
export declare function suspend(): void;
