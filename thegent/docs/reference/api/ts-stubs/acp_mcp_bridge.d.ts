// Auto-generated TypeScript declarations for acp_mcp_bridge
// Source: generate-api-docs.py

export declare class ACPAgentCallError extends BridgeError {
  constructor(agent_url: string, detail: string);
}

export declare class ACPToolDescriptor {
  to_dict(): void;
}

export declare class AcpMcpBridge {
  constructor(acp_client: ACPClient, mcp_app: any, mcp_server_url: any);
  get_mcp_tool_manifest(): void;
}

export declare class BridgeError extends Exception {
}

export declare class MCPToolNotFoundError extends BridgeError {
  constructor(tool_name: string);
}

export declare function get_mcp_tool_manifest(): void;
export declare function to_dict(): void;
