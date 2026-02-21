// Auto-generated TypeScript declarations for input_sanitizer
// Source: generate-api-docs.py

export declare class InputSanitizer {
  detect_command_injection(value: string): void;
  detect_sql_injection(value: string): void;
  detect_xss(value: string): void;
  sanitize_input(value: any, input_type: string): void;
  sanitize_string(value: string, max_length: any): void;
  validate_filename(filename: string): void;
}

export declare function detect_command_injection(value: string): void;
export declare function detect_sql_injection(value: string): void;
export declare function detect_xss(value: string): void;
export declare function sanitize_input(value: any, input_type: string): void;
export declare function sanitize_string(value: string, max_length: any): void;
export declare function validate_filename(filename: string): void;
