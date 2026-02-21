// Auto-generated TypeScript declarations for kill_switch
// Source: generate-api-docs.py

export declare class SafetyKillSwitch {
  constructor(workspace_root: string);
  activate(reason: string): void;
  check_status(): void;
  verify_alignment_drift(self_improvement_rate: number): void;
}

export declare function activate(reason: string): void;
export declare function check_status(): void;
export declare function verify_alignment_drift(self_improvement_rate: number): void;
