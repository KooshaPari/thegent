// Auto-generated usage examples for injection
// Source: generate-api-docs.py

import { ContextInjection, ShellInjection, create_tool_symlinks, find_session, is_ready, send_command, update_agent_md } from "./injection";

// Create a ContextInjection instance
const contextinjection = new ContextInjection("example_project_root", "example_mesh_root");
contextinjection.create_tool_symlinks("example_agent_id");
contextinjection.update_agent_md(undefined as unknown as Record<string, unknown>);

// Create a ShellInjection instance
const shellinjection = new ShellInjection("example_agent_id");
shellinjection.find_session();
shellinjection.is_ready("example_prompt_pattern");
shellinjection.send_command("example_command", 0);

// Call create_tool_symlinks
create_tool_symlinks(undefined as unknown as any, "example_agent_id");
// Call find_session
find_session(undefined as unknown as any);
// Call is_ready
is_ready(undefined as unknown as any, "example_prompt_pattern");
// Call send_command
send_command(undefined as unknown as any, "example_command", 0);
// Call update_agent_md
update_agent_md(undefined as unknown as any, undefined as unknown as Record<string, unknown>);
