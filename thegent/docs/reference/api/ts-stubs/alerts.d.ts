// Auto-generated TypeScript declarations for alerts
// Source: generate-api-docs.py

export declare class AlertFatigueController {
  constructor(settings: ThegentSettings);
  get_fatigue_level(): void;
  record_alert(kind: InterruptionKind): void;
}

export declare class InterruptionKind extends enum.StrEnum {
}

export declare function get_fatigue_level(): void;
export declare function record_alert(kind: InterruptionKind): void;
