// Auto-generated TypeScript declarations for scoring
// Source: generate-api-docs.py

export declare class ProviderScorer {
  constructor(settings: ThegentSettings);
  get_score(provider_id: string): void;
  update_score(provider_id: string, latency_s: number, success: boolean): void;
}

export declare function get_score(provider_id: string): void;
export declare function update_score(provider_id: string, latency_s: number, success: boolean): void;
