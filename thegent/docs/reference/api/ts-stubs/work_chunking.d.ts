// Auto-generated TypeScript declarations for work_chunking
// Source: generate-api-docs.py

export declare class ChunkConfig {
}

export declare function chunk_work_items(items: Array<any>, chunk_size: number): void;
export declare function compute_optimal_chunk_size(total_items: number, available_resources: Record<(str, Any)>, config: any): void;
