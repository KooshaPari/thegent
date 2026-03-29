// Auto-generated usage examples for shell_injection
// Source: generate-api-docs.py

import { AgentReadinessDetector, TmuxInjector, get_agent_state, inject_command, is_ready, list_agent_sessions, wait_for_ready } from "./shell_injection";

// Create a AgentReadinessDetector instance
const agentreadinessdetector = new AgentReadinessDetector();
agentreadinessdetector.get_agent_state(0);

// Create a TmuxInjector instance
const tmuxinjector = new TmuxInjector("example_session_prefix");
tmuxinjector.inject_command("example_session_id", "example_command", false);
tmuxinjector.is_ready("example_session_id");
tmuxinjector.list_agent_sessions();
tmuxinjector.wait_for_ready("example_session_id", 0);

// Call get_agent_state
get_agent_state(0);
// Call inject_command
inject_command(undefined as unknown as any, "example_session_id", "example_command", false);
// Call is_ready
is_ready(undefined as unknown as any, "example_session_id");
// Call list_agent_sessions
list_agent_sessions(undefined as unknown as any);
// Call wait_for_ready
wait_for_ready(undefined as unknown as any, "example_session_id", 0);
