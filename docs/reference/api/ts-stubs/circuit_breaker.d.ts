// Auto-generated TypeScript declarations for circuit_breaker
// Source: generate-api-docs.py

export declare function is_open(session_dir: string, target: string, category: string): void;
export declare function should_allow(session_dir: string, target: string, category: string): void;
export declare function trip(session_dir: string, target: string, category: string): void;
