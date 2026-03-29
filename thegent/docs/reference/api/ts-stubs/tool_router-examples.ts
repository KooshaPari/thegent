// Auto-generated usage examples for tool_router
// Source: generate-api-docs.py

import { ToolDefinition, ToolRouter, get_tool_prompt_injection, register_tool, route, save_registry } from "./tool_router";

// Create a ToolDefinition instance
const tooldefinition = new ToolDefinition();

// Create a ToolRouter instance
const toolrouter = new ToolRouter(undefined as unknown as any);
toolrouter.get_tool_prompt_injection("example_prompt");
toolrouter.register_tool(undefined as unknown as ToolDefinition);
toolrouter.route("example_prompt", 0);
toolrouter.save_registry();

// Call get_tool_prompt_injection
get_tool_prompt_injection(undefined as unknown as any, "example_prompt");
// Call register_tool
register_tool(undefined as unknown as any, undefined as unknown as ToolDefinition);
// Call route
route(undefined as unknown as any, "example_prompt", 0);
// Call save_registry
save_registry(undefined as unknown as any);
