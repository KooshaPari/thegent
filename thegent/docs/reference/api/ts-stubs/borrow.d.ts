// Auto-generated TypeScript declarations for borrow
// Source: generate-api-docs.py

export declare class BorrowConfig {
  url(): void;
}

export declare class ToolBorrower {
  constructor(config: any);
  export_tool_config(tool_names: Array<string>): void;
  generate_claude_md_snippet(tool_names: Array<string>): void;
  generate_mcp_json(tool_names: Array<string>, output_path: string): void;
  get_tool(name: string): void;
  list_available_tools(): void;
  list_available_tools_by_category(): void;
  validate_server_reachable(): void;
}

export declare class ToolManifest {
  to_dict(): void;
}

export declare function export_tool_config(tool_names: Array<string>): void;
export declare function generate_claude_md_snippet(tool_names: Array<string>): void;
export declare function generate_mcp_json(tool_names: Array<string>, output_path: string): void;
export declare function get_tool(name: string): void;
export declare function list_available_tools(): void;
export declare function list_available_tools_by_category(): void;
export declare function to_dict(): void;
export declare function url(): string;
export declare function validate_server_reachable(): void;
