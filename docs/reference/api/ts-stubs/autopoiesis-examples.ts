// Auto-generated usage examples for autopoiesis
// Source: generate-api-docs.py

import { AgentPersonaSpec, AutopoiesisManager, author_persona, deploy_persona } from "./autopoiesis";

// Create a AgentPersonaSpec instance
const agentpersonaspec = new AgentPersonaSpec();

// Create a AutopoiesisManager instance
const autopoiesismanager = new AutopoiesisManager("example_run_id");
autopoiesismanager.author_persona(undefined as unknown as AgentPersonaSpec);
autopoiesismanager.deploy_persona(undefined as unknown as SynthesisResult);

// Call author_persona
author_persona(undefined as unknown as any, undefined as unknown as AgentPersonaSpec);
// Call deploy_persona
deploy_persona(undefined as unknown as any, undefined as unknown as SynthesisResult);
