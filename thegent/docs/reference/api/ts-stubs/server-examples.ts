// Auto-generated usage examples for server
// Source: generate-api-docs.py

import { ACPServerAdapter, AgentSession, add_message, stop } from "./server";

// Create a ACPServerAdapter instance
const acpserveradapter = new ACPServerAdapter();

// Create a AgentSession instance
const agentsession = new AgentSession("example_agent_id", undefined as unknown as AgentRunner, undefined as unknown as any);
agentsession.add_message("example_role", "example_content");
agentsession.stop();

// Call add_message
add_message(undefined as unknown as any, "example_role", "example_content");
// Call stop
stop(undefined as unknown as any);
