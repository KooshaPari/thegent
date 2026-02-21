// Auto-generated usage examples for fallback_ui
// Source: generate-api-docs.py

import { FallbackOption, FallbackRegistry, get_recommendations } from "./fallback_ui";

// Create a FallbackOption instance
const fallbackoption = new FallbackOption("example_id", "example_label", "example_description", "example_command");

// Create a FallbackRegistry instance
const fallbackregistry = new FallbackRegistry(undefined as unknown as ThegentSettings);
fallbackregistry.get_recommendations("example_failure_kind");

// Call get_recommendations
get_recommendations(undefined as unknown as any, "example_failure_kind");
