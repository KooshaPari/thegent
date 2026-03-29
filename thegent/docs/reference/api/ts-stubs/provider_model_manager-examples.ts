// Auto-generated usage examples for provider_model_manager
// Source: generate-api-docs.py

import { add_api_key, add_common_alias, add_custom_benchmark, add_model_alias, add_model_index, add_model_modality, add_provider, calculate_composite_score, delete_provider, discover_models, fuzzy_search_models, get_model_indices, get_model_modalities, get_provider, list_available_modalities, list_credentials, list_model_indices, list_models, list_models_with_scores, list_providers, remove_api_key, remove_common_alias, remove_model_alias, remove_model_index, run_provider_form, search_by_modalities, search_models_by_capability, update_provider, validate_provider } from "./provider_model_manager";

// Call add_api_key
add_api_key("example_provider", "example_api_key");
// Call add_common_alias
add_common_alias("example_alias");
// Call add_custom_benchmark
add_custom_benchmark("example_provider", "example_model", "example_benchmark_name", 0, "example_category", "example_description");
// Call add_model_alias
add_model_alias("example_provider", "example_model", "example_alias");
// Call add_model_index
add_model_index("example_provider", "example_model", undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any);
// Call add_model_modality
add_model_modality("example_provider", "example_model", "example_modality", undefined as unknown as any);
// Call add_provider
add_provider("example_name", "example_base_url", "example_model", undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any);
// Call calculate_composite_score
calculate_composite_score(undefined as unknown as Record<(str, float)>, undefined as unknown as any);
// Call delete_provider
delete_provider("example_name", false);
// Call discover_models
discover_models(undefined as unknown as any);
// Call fuzzy_search_models
fuzzy_search_models("example_query", undefined as unknown as any, undefined as unknown as any, 0);
// Call get_model_indices
get_model_indices(undefined as unknown as any, undefined as unknown as any);
// Call get_model_modalities
get_model_modalities(undefined as unknown as any, undefined as unknown as any);
// Call get_provider
get_provider("example_name");
// Call list_available_modalities
list_available_modalities();
// Call list_credentials
list_credentials();
// Call list_model_indices
list_model_indices(undefined as unknown as any, "example_sort_by", false);
// Call list_models
list_models(undefined as unknown as any);
// Call list_models_with_scores
list_models_with_scores(undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, "example_sort_by");
// Call list_providers
list_providers(false);
// Call remove_api_key
remove_api_key("example_provider");
// Call remove_common_alias
remove_common_alias("example_alias");
// Call remove_model_alias
remove_model_alias("example_provider", "example_alias");
// Call remove_model_index
remove_model_index("example_provider", "example_model");
// Call run_provider_form
run_provider_form();
// Call search_by_modalities
search_by_modalities(undefined as unknown as Array<string>, undefined as unknown as any, undefined as unknown as any, "example_sort_by");
// Call search_models_by_capability
search_models_by_capability("example_capability", undefined as unknown as any, undefined as unknown as any, undefined as unknown as any);
// Call update_provider
update_provider("example_name", undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any);
// Call validate_provider
validate_provider("example_name");
