// Auto-generated TypeScript declarations for quality_values
// Source: generate-api-docs.py

export declare function get_all_model_quality_indices(settings: any, benchmarks_path: any): void;
export declare function get_model_provider_quality_index(model_id: string, provider: string, settings: any): void;
export declare function get_model_provider_quality_indices(settings: any, benchmarks_path: any, use_cache: boolean): void;
export declare function get_model_quality_for_role(model_id: string, role_benchmark_weights: any, settings: any, benchmarks_path: any): void;
export declare function get_model_quality_index(model_id: string, settings: any, benchmarks_path: any): void;
export declare function invalidate_quality_index_cache(): void;
