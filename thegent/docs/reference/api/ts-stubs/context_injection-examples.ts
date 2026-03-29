// Auto-generated usage examples for context_injection
// Source: generate-api-docs.py

import { ContextInjector, render_agent_md, setup_tool_context, update_context } from "./context_injection";

// Create a ContextInjector instance
const contextinjector = new ContextInjector("example_project_root");
contextinjector.render_agent_md(undefined as unknown as Record<(str, Any)>, undefined as unknown as Record<(str, Any)>);
contextinjector.setup_tool_context("example_agent_dir", "example_agent_type");
contextinjector.update_context("example_agent_id", "example_agent_dir", undefined as unknown as Record<(str, Any)>);

// Call render_agent_md
render_agent_md(undefined as unknown as any, undefined as unknown as Record<(str, Any)>, undefined as unknown as Record<(str, Any)>);
// Call setup_tool_context
setup_tool_context(undefined as unknown as any, "example_agent_dir", "example_agent_type");
// Call update_context
update_context(undefined as unknown as any, "example_agent_id", "example_agent_dir", undefined as unknown as Record<(str, Any)>);
