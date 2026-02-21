// Auto-generated TypeScript declarations for aggregator
// Source: generate-api-docs.py

export declare class CostAggregator {
  daily_total(owner: string): void;
  get_all_categories_mtd(): void;
  get_category_mtd_total(category: string): void;
  get_mtd_total(): void;
}

export declare class CostEstimator {
  estimate(model: any, tokens_total: number, prompt_length: number): void;
}

export declare function daily_total(owner: string): void;
export declare function estimate(model: any, tokens_total: number, prompt_length: number): void;
export declare function get_all_categories_mtd(): void;
export declare function get_category_mtd_total(category: string): void;
export declare function get_mtd_total(): void;
