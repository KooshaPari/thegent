// Auto-generated TypeScript declarations for autonomous_learning
// Source: generate-api-docs.py

export declare class AutonomousLearningSurface {
  constructor();
  add_learning_point(context: string, action: string, outcome: any): void;
  get_recommendation(context: string): void;
}

export declare function add_learning_point(context: string, action: string, outcome: any): void;
export declare function get_recommendation(context: string): void;
