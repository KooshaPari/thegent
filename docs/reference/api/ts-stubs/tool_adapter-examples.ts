// Auto-generated usage examples for tool_adapter
// Source: generate-api-docs.py

import { ToolAdapter, ToolDefinition, discover_tools, generate_binding, wrap_tool } from "./tool_adapter";

// Create a ToolAdapter instance
const tooladapter = new ToolAdapter("example_agent_id");
tooladapter.discover_tools("example_target_path");
tooladapter.generate_binding("example_tool_id");
tooladapter.wrap_tool("example_tool_id");

// Create a ToolDefinition instance
const tooldefinition = new ToolDefinition();

// Call discover_tools
discover_tools(undefined as unknown as any, "example_target_path");
// Call generate_binding
generate_binding(undefined as unknown as any, "example_tool_id");
// Call wrap_tool
wrap_tool(undefined as unknown as any, "example_tool_id");
