// Auto-generated TypeScript declarations for calibration
// Source: generate-api-docs.py

export declare class ConfidenceCalibrator {
  constructor(settings: ThegentSettings);
  calibrate(agent_name: string, raw_confidence: number): void;
  record_feedback(agent_name: string, provided_confidence: number, actual_success: boolean): void;
}

export declare function calibrate(agent_name: string, raw_confidence: number): void;
export declare function record_feedback(agent_name: string, provided_confidence: number, actual_success: boolean): void;
