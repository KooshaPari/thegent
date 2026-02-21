// Auto-generated TypeScript declarations for context
// Source: generate-api-docs.py

export declare class ContextCompressor {
  constructor(session_dir: string, threshold_pct: number);
  generate_continuity_packet(intent: string, decisions: Array<string>, risks: Array<string>, context_files: Array<string>): void;
  prune_context(conversation: Array<Record<(str, Any)>>): void;
  should_compress(current_tokens: number, max_tokens: number): void;
}

export declare function generate_continuity_packet(intent: string, decisions: Array<string>, risks: Array<string>, context_files: Array<string>): void;
export declare function prune_context(conversation: Array<Record<(str, Any)>>): void;
export declare function should_compress(current_tokens: number, max_tokens: number): void;
