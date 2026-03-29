// Auto-generated usage examples for probing
// Source: generate-api-docs.py

import { AgentFingerprint, AgentProber, identify_deviations, probe_agent } from "./probing";

// Create a AgentFingerprint instance
const agentfingerprint = new AgentFingerprint();

// Create a AgentProber instance
const agentprober = new AgentProber("example_agent_id");
agentprober.identify_deviations(undefined as unknown as AgentFingerprint, undefined as unknown as AgentFingerprint);
agentprober.probe_agent(undefined as unknown as any);

// Call identify_deviations
identify_deviations(undefined as unknown as any, undefined as unknown as AgentFingerprint, undefined as unknown as AgentFingerprint);
// Call probe_agent
probe_agent(undefined as unknown as any, undefined as unknown as any);
