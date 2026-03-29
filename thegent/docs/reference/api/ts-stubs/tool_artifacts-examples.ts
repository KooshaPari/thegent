// Auto-generated usage examples for tool_artifacts
// Source: generate-api-docs.py

import { MCPCallArtifact, ToolInvocationArtifact, ToolResultStatus, ToolType, create } from "./tool_artifacts";

// Create a MCPCallArtifact instance
const mcpcallartifact = new MCPCallArtifact();
mcpcallartifact.create(undefined as unknown as MAIFArtifact, "example_mcp_server", "example_mcp_tool", undefined as unknown as ToolResultStatus);

// Create a ToolInvocationArtifact instance
const toolinvocationartifact = new ToolInvocationArtifact();
toolinvocationartifact.create(undefined as unknown as MAIFArtifact, undefined as unknown as ToolType, "example_tool_name", undefined as unknown as Record<(str, Any)>, undefined as unknown as ToolResultStatus);

// Create a ToolResultStatus instance
const toolresultstatus = new ToolResultStatus();

// Create a ToolType instance
const tooltype = new ToolType();

// Call create
create(undefined as unknown as any, undefined as unknown as MAIFArtifact, "example_mcp_server", "example_mcp_tool", undefined as unknown as ToolResultStatus);
