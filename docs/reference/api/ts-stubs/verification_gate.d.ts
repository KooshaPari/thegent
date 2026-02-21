// Auto-generated TypeScript declarations for verification_gate
// Source: generate-api-docs.py

export declare class DimensionScanResult extends Protocol {
}

export declare class HealthComputerProtocol extends Protocol {
  compute(scan_result: any): void;
}

export declare class RemediationTaskProtocol extends Protocol {
}

export declare class ScanResultProtocol extends Protocol {
  get_dimension(dimension: string): void;
}

export declare class ScannerProtocol extends Protocol {
  scan(): void;
  scan_dimension(dimension: string): void;
}

export declare class TaskExecutionProtocol extends Protocol {
}

export declare class TaskVerification extends BaseModel {
}

export declare class VerificationGate {
  constructor(scanner: ScannerProtocol, health_computer: HealthComputerProtocol, max_rerolls: number);
  get_escalated_tier(current_tier: string): void;
  should_reroll(attempts: number): void;
  verify_task(task: RemediationTaskProtocol, execution: TaskExecutionProtocol, pre_scan: ScanResultProtocol): void;
}

export declare class VerificationVerdict extends StrEnum {
}

export declare function compute(scan_result: any): any;
export declare function get_dimension(dimension: string): any;
export declare function get_escalated_tier(current_tier: string): void;
export declare function scan(): ScanResultProtocol;
export declare function scan_dimension(dimension: string): DimensionScanResult;
export declare function should_reroll(attempts: number): void;
export declare function verify_task(task: RemediationTaskProtocol, execution: TaskExecutionProtocol, pre_scan: ScanResultProtocol): void;
