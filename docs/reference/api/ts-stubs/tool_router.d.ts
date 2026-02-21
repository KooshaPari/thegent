// Auto-generated TypeScript declarations for tool_router
// Source: generate-api-docs.py

export declare class ToolDefinition extends BaseModel {
}

export declare class ToolRouter {
  constructor(registry_path: any);
  get_tool_prompt_injection(prompt: string): void;
  register_tool(tool: ToolDefinition): void;
  route(prompt: string, limit: number): void;
  save_registry(): void;
}

export declare function get_tool_prompt_injection(prompt: string): void;
export declare function register_tool(tool: ToolDefinition): void;
export declare function route(prompt: string, limit: number): void;
export declare function save_registry(): void;
