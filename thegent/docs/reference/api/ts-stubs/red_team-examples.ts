// Auto-generated usage examples for red_team
// Source: generate-api-docs.py

import { RedTeamAgent, RedTeamScenario, evaluate_resilience, generate_attack } from "./red_team";

// Create a RedTeamAgent instance
const redteamagent = new RedTeamAgent(undefined as unknown as any);
redteamagent.evaluate_resilience(undefined as unknown as RedTeamScenario, undefined as unknown as Record<(str, Any)>);
redteamagent.generate_attack("example_target_agent");

// Create a RedTeamScenario instance
const redteamscenario = new RedTeamScenario();

// Call evaluate_resilience
evaluate_resilience(undefined as unknown as any, undefined as unknown as RedTeamScenario, undefined as unknown as Record<(str, Any)>);
// Call generate_attack
generate_attack(undefined as unknown as any, "example_target_agent");
