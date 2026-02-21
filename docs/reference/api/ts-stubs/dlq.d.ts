// Auto-generated TypeScript declarations for dlq
// Source: generate-api-docs.py

export declare function is_poison_pill(session_dir: string, run_id: string, threshold: number): void;
export declare function list_pending(session_dir: string, limit: number): void;
export declare function resolve(session_dir: string, run_id: string, resolution: string): void;
