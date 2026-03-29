// Auto-generated TypeScript declarations for health_scorer
// Source: generate-api-docs.py

export declare class DimensionScore extends TypedDict {
}

export declare class HealthReport extends TypedDict {
}

export declare class HealthScorer {
  constructor(targets_file: any);
  calculate_overall(scores: Array<DimensionScore>): void;
  dimension_status(score: number): void;
  generate_report(measurements: Record<(str, float)>): void;
  normalize_score(actual: number, target: number, direction: string): void;
  score_dimension(dimension_key: string, actual: number): void;
}

export declare function calculate_overall(scores: Array<DimensionScore>): void;
export declare function dimension_status(score: number): void;
export declare function generate_report(measurements: Record<(str, float)>): void;
export declare function normalize_score(actual: number, target: number, direction: string): void;
export declare function score_dimension(dimension_key: string, actual: number): void;
