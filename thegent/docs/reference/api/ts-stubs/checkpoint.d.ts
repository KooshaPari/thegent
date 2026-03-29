// Auto-generated TypeScript declarations for checkpoint
// Source: generate-api-docs.py

export declare function create(session_dir: string, reason: string, dag_content: string, owner: string): void;
export declare function get(session_dir: string, checkpoint_id: string): void;
export declare function list_checkpoints(session_dir: string, limit: number): void;
