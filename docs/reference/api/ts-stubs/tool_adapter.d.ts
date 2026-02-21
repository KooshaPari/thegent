// Auto-generated TypeScript declarations for tool_adapter
// Source: generate-api-docs.py

export declare class ToolAdapter {
  constructor(agent_id: string);
  discover_tools(target_path: string): void;
  generate_binding(tool_id: string): void;
  wrap_tool(tool_id: string): void;
}

export declare class ToolDefinition extends BaseModel {
}

export declare function discover_tools(target_path: string): void;
export declare function generate_binding(tool_id: string): void;
export declare function wrap_tool(tool_id: string): void;
