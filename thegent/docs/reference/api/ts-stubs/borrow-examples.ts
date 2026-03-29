// Auto-generated usage examples for borrow
// Source: generate-api-docs.py

import { BorrowConfig, ToolBorrower, ToolManifest, export_tool_config, generate_claude_md_snippet, generate_mcp_json, get_tool, list_available_tools, list_available_tools_by_category, to_dict, url, validate_server_reachable } from "./borrow";

// Create a BorrowConfig instance
const borrowconfig = new BorrowConfig();
borrowconfig.url();

// Create a ToolBorrower instance
const toolborrower = new ToolBorrower(undefined as unknown as any);
toolborrower.export_tool_config(undefined as unknown as Array<string>);
toolborrower.generate_claude_md_snippet(undefined as unknown as Array<string>);
toolborrower.generate_mcp_json(undefined as unknown as Array<string>, "example_output_path");
toolborrower.get_tool("example_name");
toolborrower.list_available_tools();
toolborrower.list_available_tools_by_category();
toolborrower.validate_server_reachable();

// Create a ToolManifest instance
const toolmanifest = new ToolManifest();
toolmanifest.to_dict();

// Call export_tool_config
export_tool_config(undefined as unknown as any, undefined as unknown as Array<string>);
// Call generate_claude_md_snippet
generate_claude_md_snippet(undefined as unknown as any, undefined as unknown as Array<string>);
// Call generate_mcp_json
generate_mcp_json(undefined as unknown as any, undefined as unknown as Array<string>, "example_output_path");
// Call get_tool
get_tool(undefined as unknown as any, "example_name");
// Call list_available_tools
list_available_tools(undefined as unknown as any);
// Call list_available_tools_by_category
list_available_tools_by_category(undefined as unknown as any);
// Call to_dict
to_dict(undefined as unknown as any);
// Call url
url(undefined as unknown as any);
// Call validate_server_reachable
validate_server_reachable(undefined as unknown as any);
