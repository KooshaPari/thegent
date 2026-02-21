// Auto-generated usage examples for scoring
// Source: generate-api-docs.py

import { ProviderScorer, get_score, update_score } from "./scoring";

// Create a ProviderScorer instance
const providerscorer = new ProviderScorer(undefined as unknown as ThegentSettings);
providerscorer.get_score("example_provider_id");
providerscorer.update_score("example_provider_id", 0, false);

// Call get_score
get_score(undefined as unknown as any, "example_provider_id");
// Call update_score
update_score(undefined as unknown as any, "example_provider_id", 0, false);
