// Auto-generated TypeScript declarations for health_score
// Source: generate-api-docs.py

export declare class DimensionScore extends BaseModel {
}

export declare class HealthBand extends StrEnum {
}

export declare class HealthScore extends BaseModel {
}

export declare class HealthScoreComputer {
  constructor(health_targets_path: string);
  compute(dimension_values: Record<(str, float)>): void;
  compute_with_trend(dimension_values: Record<(str, float)>, previous_score: any): void;
}

export declare function compute(dimension_values: Record<(str, float)>): void;
export declare function compute_with_trend(dimension_values: Record<(str, float)>, previous_score: any): void;
export declare function get_band(score: number): void;
