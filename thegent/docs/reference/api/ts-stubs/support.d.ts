// Auto-generated TypeScript declarations for support
// Source: generate-api-docs.py

export declare class SupportModeSession {
  constructor(engineer_id: string);
  get_view(raw_output: string): void;
}

export declare class SupportRedactor {
  constructor();
  redact_payload(payload: Record<(str, Any)>): void;
  redact_text(text: string): void;
}

export declare function get_view(raw_output: string): void;
export declare function redact_payload(payload: Record<(str, Any)>): void;
export declare function redact_text(text: string): void;
