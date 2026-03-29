// Auto-generated TypeScript declarations for enhanced_errors
// Source: generate-api-docs.py

export declare class ConfigurationError extends EnhancedError {
}

export declare class DependencyError extends EnhancedError {
}

export declare class EnhancedError extends Exception {
  constructor(message: string, context: any, cause: any);
  display(): void;
}

export declare class ErrorContext {
}

export declare class NetworkError extends EnhancedError {
}

export declare class RuntimeError extends EnhancedError {
}

export declare function create_config_error(message: string, config_file: string, suggestion: any): void;
export declare function create_dependency_error(message: string, dependency: string, install_command: any): void;
export declare function create_network_error(message: string, endpoint: any, suggestion: any): void;
export declare function create_runtime_error(message: string, runtime: string, available_runtimes: Array<string>, suggestion: any): void;
export declare function display(): void;
export declare function error_report(error: Exception, include_traceback: boolean): void;
export declare function format_error_with_context(error: Exception, context: any): void;
