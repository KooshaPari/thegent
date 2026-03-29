// Auto-generated TypeScript declarations for symbolic
// Source: generate-api-docs.py

export declare class RiskPath {
}

export declare class SymbolicRiskExplorer {
  constructor(dag: Record<(str, Any)>);
  explore(start_node: string): void;
  get_highest_risk_path(): void;
}

export declare function explore(start_node: string): void;
export declare function get_highest_risk_path(): void;
