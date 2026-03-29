// Auto-generated TypeScript declarations for egress
// Source: generate-api-docs.py

export declare class EgressEvent {
}

export declare class SIEMEgress {
  constructor(endpoint_url: any);
  format_for_syslog(event: EgressEvent): void;
  push_event(event: EgressEvent): void;
}

export declare function format_for_syslog(event: EgressEvent): void;
export declare function push_event(event: EgressEvent): void;
