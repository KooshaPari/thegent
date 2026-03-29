// Auto-generated TypeScript declarations for orchestration_modes
// Source: generate-api-docs.py

export declare class ConflictArbitrator {
  constructor(quorum_threshold: number);
  arbitrate(results: Array<any>): void;
  detect_conflicts(results: Array<any>): void;
}

export declare class ModeEntry {
}

export declare class MultiAgentMode extends StrEnum {
}

export declare function arbitrate(results: Array<any>): void;
export declare function calculate_risk_score(prompt: string, lane: string): void;
export declare function detect_conflicts(results: Array<any>): void;
export declare function get_mode(mode_id: string): void;
export declare function list_modes(): void;
export declare function suggest_mode(risk: string, urgency: string, confidence: number): void;
