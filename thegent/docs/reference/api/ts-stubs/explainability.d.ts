// Auto-generated TypeScript declarations for explainability
// Source: generate-api-docs.py

export declare class DetailLevel extends StrEnum {
}

export declare class ExplainabilityEngine {
  constructor();
  get_explanation(decision_id: string, level: DetailLevel): void;
  record_decision(decision_id: string, explanation: Explanation): void;
  render_all(decision_id: string): void;
}

export declare class Explanation {
}

export declare function get_explanation(decision_id: string, level: DetailLevel): void;
export declare function record_decision(decision_id: string, explanation: Explanation): void;
export declare function render_all(decision_id: string): void;
