// Auto-generated TypeScript declarations for validator
// Source: generate-api-docs.py

export declare class TaskValidator {
  constructor(schema_path: any);
  validate(task: Record<(str, Any)>): void;
  validate_file(file_path: string): void;
}

export declare class ValidationError {
}

export declare class ValidationResult {
  format_errors(): void;
}

export declare function format_errors(): void;
export declare function validate(task: Record<(str, Any)>): void;
export declare function validate_file(file_path: string): void;
export declare function validate_task(task: Record<(str, Any)>, schema_path: any): void;
export declare function validate_task_file(file_path: string, schema_path: any): void;
