// Auto-generated TypeScript declarations for frecency
// Source: generate-api-docs.py

export declare class FrecencyCache {
  constructor(maxsize: number, half_life_seconds: number, storage: any);
  access(key: string): void;
  clear(): void;
  evict_lowest(n: number): void;
  get_entry(key: string): void;
  half_life(): void;
  maxsize(): void;
  score(key: string): void;
  top_n(n: number): void;
}

export declare class FrecencyEntry {
  age_seconds(now: any): void;
  recalculate_score(half_life: number, now: any): void;
}

export declare class FrecencyModelSelector {
  constructor(maxsize: number, half_life_seconds: number, storage: any);
  cache(): void;
  preferred_model(candidates: Array<string>): void;
  record_use(model_id: string): void;
  score(model_id: string): void;
  top_models(n: number): void;
}

export declare function access(key: string): void;
export declare function age_seconds(now: any): void;
export declare function cache(): void;
export declare function clear(): void;
export declare function evict_lowest(n: number): void;
export declare function get_entry(key: string): void;
export declare function half_life(): void;
export declare function maxsize(): void;
export declare function preferred_model(candidates: Array<string>): void;
export declare function recalculate_score(half_life: number, now: any): void;
export declare function record_use(model_id: string): void;
export declare function score(model_id: string): void;
export declare function top_models(n: number): void;
export declare function top_n(n: number): void;
