// Auto-generated TypeScript declarations for provider_model_manager
// Source: generate-api-docs.py

export declare function add_api_key(provider: string, api_key: string): void;
export declare function add_common_alias(alias: string): void;
export declare function add_custom_benchmark(provider: string, model: string, benchmark_name: string, score: number, category: string, description: string): void;
export declare function add_model_alias(provider: string, model: string, alias: string): void;
export declare function add_model_index(provider: string, model: string, context_limit: any, output_limit: any, cost_per_1m_input: any, cost_per_1m_output: any, tps: any, latency_first_token: any, reasoning: any, vision: any, swebench: any, termbench: any, notes: any): void;
export declare function add_model_modality(provider: string, model: string, modality: string, value: any): void;
export declare function add_provider(name: string, base_url: string, model: string, login_url: any, login_instructions: any, display_name: any, extra_aliases: any, api_key: any, base_url_env: any): void;
export declare function calculate_composite_score(benchmarks: Record<(str, float)>, weights: any): void;
export declare function delete_provider(name: string, remove_credentials: boolean): void;
export declare function discover_models(provider: any): void;
export declare function fuzzy_search_models(query: string, fields: any, provider: any, limit: number): void;
export declare function get_model_indices(provider: any, model: any): void;
export declare function get_model_modalities(provider: any, model: any): void;
export declare function get_provider(name: string): void;
export declare function list_available_modalities(): void;
export declare function list_credentials(): void;
export declare function list_model_indices(provider: any, sort_by: string, include_all: boolean): void;
export declare function list_models(provider: any): void;
export declare function list_models_with_scores(provider: any, min_score: any, modality: any, sort_by: string): void;
export declare function list_providers(include_credentials: boolean): void;
export declare function remove_api_key(provider: string): void;
export declare function remove_common_alias(alias: string): void;
export declare function remove_model_alias(provider: string, alias: string): void;
export declare function remove_model_index(provider: string, model: string): void;
export declare function run_provider_form(): void;
export declare function search_by_modalities(required_modalities: Array<string>, excluded_modalities: any, provider: any, sort_by: string): void;
export declare function search_models_by_capability(capability: string, min_context: any, max_cost_per_1m: any, min_tps: any): void;
export declare function update_provider(name: string, base_url: any, model: any, login_url: any, login_instructions: any, display_name: any, extra_aliases: any, api_key: any, base_url_env: any): void;
export declare function validate_provider(name: string): void;
