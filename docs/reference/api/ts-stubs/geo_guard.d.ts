// Auto-generated TypeScript declarations for geo_guard
// Source: generate-api-docs.py

export declare class DataLocationCheck extends BaseModel {
}

export declare class GeoGuard {
  constructor();
  add_rule(rule: SovereigntyRule): void;
  validate_location(data_id: string, category: string, region: string): void;
}

export declare class SovereigntyRule extends BaseModel {
}

export declare function add_rule(rule: SovereigntyRule): void;
export declare function validate_location(data_id: string, category: string, region: string): void;
