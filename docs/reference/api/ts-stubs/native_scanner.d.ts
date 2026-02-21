// Auto-generated TypeScript declarations for native_scanner
// Source: generate-api-docs.py

export declare class NativeGovernanceScanner {
  constructor();
  add_trigger(trigger: string, obfuscated: boolean): void;
  scan(content: string): void;
}

export declare function add_trigger(trigger: string, obfuscated: boolean): void;
export declare function scan(content: string): void;
