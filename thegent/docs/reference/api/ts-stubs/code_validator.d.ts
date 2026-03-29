// Auto-generated TypeScript declarations for code_validator
// Source: generate-api-docs.py

export declare class CodeExampleValidator {
  constructor(check_syntax: boolean, run_tests: boolean);
  validate_code_snippet(code: string, language: string): void;
  validate_doc_file(file_path: string): void;
}

export declare function validate_code_snippet(code: string, language: string): void;
export declare function validate_doc_file(file_path: string): void;
