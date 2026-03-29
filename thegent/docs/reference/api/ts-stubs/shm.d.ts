// Auto-generated TypeScript declarations for shm
// Source: generate-api-docs.py

export declare class SHMSystem {
  award_xp(amount: number): void;
  get_xp_state(): void;
  is_native_active(): void;
  is_open(target: string, category: string, threshold: number, window_s: number, recovery_s: number): void;
  record_failure(target: string, category: string): void;
  set_level(level: number): void;
}

export declare function award_xp(amount: number): void;
export declare function get_shm_system(session_dir: string): SHMSystem;
export declare function get_xp_state(): Record<(str, Any)>;
export declare function is_native_active(): boolean;
export declare function is_open(target: string, category: string, threshold: number, window_s: number, recovery_s: number): boolean;
export declare function record_failure(target: string, category: string): void;
export declare function set_level(level: number): void;
