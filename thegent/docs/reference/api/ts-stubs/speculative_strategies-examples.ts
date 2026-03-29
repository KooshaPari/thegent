// Auto-generated usage examples for speculative_strategies
// Source: generate-api-docs.py

import { SpeculativeConfig, SpeculativeStrategy, compute_adaptive_timeout, select_speculative_providers, should_terminate_early } from "./speculative_strategies";

// Create a SpeculativeConfig instance
const speculativeconfig = new SpeculativeConfig();

// Create a SpeculativeStrategy instance
const speculativestrategy = new SpeculativeStrategy();

// Call compute_adaptive_timeout
compute_adaptive_timeout(0, 0, 0);
// Call select_speculative_providers
select_speculative_providers(undefined as unknown as Array<string>, undefined as unknown as SpeculativeStrategy, 0);
// Call should_terminate_early
should_terminate_early(0, 0, undefined as unknown as Array<any>, undefined as unknown as SpeculativeStrategy);
