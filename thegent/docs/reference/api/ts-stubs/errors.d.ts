// Auto-generated TypeScript declarations for errors
// Source: generate-api-docs.py

export declare class ConfigError extends ThegentError {
  constructor(message: string, remediation_hint: any);
}

export declare class MCPError extends ThegentError {
  constructor(message: string, remediation_hint: any);
}

export declare class ProviderError extends ThegentError {
  constructor(message: string, remediation_hint: any);
}

export declare class ThegentError extends Exception {
  constructor(message: string, remediation_hint: any);
}

export declare function get_hint_for_message(message: string): void;
export declare function get_install_hint(tool: string): void;
export declare function print_error(message: string, hint: any, console: any): void;
