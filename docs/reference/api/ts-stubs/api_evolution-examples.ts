// Auto-generated usage examples for api_evolution
// Source: generate-api-docs.py

import { APIEvolutionManager, is_feature_enabled, negotiate_version } from "./api_evolution";

// Create a APIEvolutionManager instance
const apievolutionmanager = new APIEvolutionManager("example_current_version");
apievolutionmanager.is_feature_enabled("example_flag");
apievolutionmanager.negotiate_version("example_client_version");

// Call is_feature_enabled
is_feature_enabled(undefined as unknown as any, "example_flag");
// Call negotiate_version
negotiate_version(undefined as unknown as any, "example_client_version");
