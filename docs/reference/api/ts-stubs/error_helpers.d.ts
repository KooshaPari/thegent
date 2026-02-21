// Auto-generated TypeScript declarations for error_helpers
// Source: generate-api-docs.py

export declare class ActionableError extends Exception {
  constructor(message: string, suggestion: any, docs_url: any, context: any);
}

export declare function handle_error_actionable(error: Exception, custom_message: any, suggestion: any, docs_url: any): void;
