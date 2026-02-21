// Auto-generated TypeScript declarations for slo
// Source: generate-api-docs.py

export declare class SLORegulator {
  constructor(latency_slo_ms: number, error_slo_rate: number);
  is_compliant(): void;
  record_execution(latency_ms: number, success: boolean): void;
}

export declare function is_compliant(): void;
export declare function record_execution(latency_ms: number, success: boolean): void;
