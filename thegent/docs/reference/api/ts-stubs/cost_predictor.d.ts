// Auto-generated TypeScript declarations for cost_predictor
// Source: generate-api-docs.py

export declare class CostPredictor {
  constructor();
  predict_cost(model: string, tokens_estimate: number, action_type: string): void;
}

export declare function predict_cost(model: string, tokens_estimate: number, action_type: string): void;
