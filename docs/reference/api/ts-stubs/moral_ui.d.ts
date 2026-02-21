// Auto-generated TypeScript declarations for moral_ui
// Source: generate-api-docs.py

export declare class ArbitrationResult extends BaseModel {
}

export declare class MoralDilemma extends BaseModel {
}

export declare class MoralUI {
  constructor();
  present_dilemma(dilemma: MoralDilemma): void;
  resolve_dilemma(result: ArbitrationResult): void;
}

export declare function present_dilemma(dilemma: MoralDilemma): void;
export declare function resolve_dilemma(result: ArbitrationResult): void;
