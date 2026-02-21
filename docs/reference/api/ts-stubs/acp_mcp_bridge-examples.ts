// Auto-generated usage examples for acp_mcp_bridge
// Source: generate-api-docs.py

import { ACPAgentCallError, ACPToolDescriptor, AcpMcpBridge, BridgeError, MCPToolNotFoundError, get_mcp_tool_manifest, to_dict } from "./acp_mcp_bridge";

// Create a ACPAgentCallError instance
const acpagentcallerror = new ACPAgentCallError("example_agent_url", "example_detail");

// Create a ACPToolDescriptor instance
const acptooldescriptor = new ACPToolDescriptor();
acptooldescriptor.to_dict();

// Create a AcpMcpBridge instance
const acpmcpbridge = new AcpMcpBridge(undefined as unknown as ACPClient, undefined as unknown as any, undefined as unknown as any);
acpmcpbridge.get_mcp_tool_manifest();

// Create a BridgeError instance
const bridgeerror = new BridgeError();

// Create a MCPToolNotFoundError instance
const mcptoolnotfounderror = new MCPToolNotFoundError("example_tool_name");

// Call get_mcp_tool_manifest
get_mcp_tool_manifest(undefined as unknown as any);
// Call to_dict
to_dict(undefined as unknown as any);
