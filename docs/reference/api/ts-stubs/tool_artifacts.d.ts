// Auto-generated TypeScript declarations for tool_artifacts
// Source: generate-api-docs.py

export declare class MCPCallArtifact extends BaseArtifact {
  create(maif: MAIFArtifact, mcp_server: string, mcp_tool: string, call_status: ToolResultStatus): void;
}

export declare class ToolInvocationArtifact extends BaseArtifact {
  create(maif: MAIFArtifact, tool_type: ToolType, tool_name: string, arguments: Record<(str, Any)>, result_status: ToolResultStatus): void;
}

export declare class ToolResultStatus extends str, Enum {
}

export declare class ToolType extends str, Enum {
}

export declare function create(maif: MAIFArtifact, mcp_server: string, mcp_tool: string, call_status: ToolResultStatus): void;
