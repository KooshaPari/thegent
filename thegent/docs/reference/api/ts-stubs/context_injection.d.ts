// Auto-generated TypeScript declarations for context_injection
// Source: generate-api-docs.py

export declare class ContextInjector {
  constructor(project_root: string);
  render_agent_md(agent_info: Record<(str, Any)>, mesh_state: Record<(str, Any)>): void;
  setup_tool_context(agent_dir: string, agent_type: string): void;
  update_context(agent_id: string, agent_dir: string, mesh_state: Record<(str, Any)>): void;
}

export declare function render_agent_md(agent_info: Record<(str, Any)>, mesh_state: Record<(str, Any)>): void;
export declare function setup_tool_context(agent_dir: string, agent_type: string): void;
export declare function update_context(agent_id: string, agent_dir: string, mesh_state: Record<(str, Any)>): void;
