// Auto-generated TypeScript declarations for injection
// Source: generate-api-docs.py

export declare class ContextInjection {
  constructor(project_root: string, mesh_root: string);
  create_tool_symlinks(agent_id: string): void;
  update_agent_md(mesh_state: Record<string, unknown>): void;
}

export declare class ShellInjection {
  constructor(agent_id: string);
  find_session(): void;
  is_ready(prompt_pattern: string): void;
  send_command(command: string, wait: number): void;
}

export declare function create_tool_symlinks(agent_id: string): void;
export declare function find_session(): void;
export declare function is_ready(prompt_pattern: string): void;
export declare function send_command(command: string, wait: number): void;
export declare function update_agent_md(mesh_state: Record<string, unknown>): void;
