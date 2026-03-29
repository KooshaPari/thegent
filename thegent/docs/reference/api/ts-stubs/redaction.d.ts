// Auto-generated TypeScript declarations for redaction
// Source: generate-api-docs.py

export declare class PIIRedactor {
  constructor(custom_patterns: any);
  contains_pii(text: string): void;
  redact(text: string, mode: string): void;
}

export declare function contains_pii(text: string): void;
export declare function redact(text: string, mode: string): void;
