// Auto-generated usage examples for enhanced_errors
// Source: generate-api-docs.py

import { ConfigurationError, DependencyError, EnhancedError, ErrorContext, NetworkError, RuntimeError, create_config_error, create_dependency_error, create_network_error, create_runtime_error, display, error_report, format_error_with_context } from "./enhanced_errors";

// Create a ConfigurationError instance
const configurationerror = new ConfigurationError();

// Create a DependencyError instance
const dependencyerror = new DependencyError();

// Create a EnhancedError instance
const enhancederror = new EnhancedError("example_message", undefined as unknown as any, undefined as unknown as any);
enhancederror.display();

// Create a ErrorContext instance
const errorcontext = new ErrorContext();

// Create a NetworkError instance
const networkerror = new NetworkError();

// Create a RuntimeError instance
const runtimeerror = new RuntimeError();

// Call create_config_error
create_config_error("example_message", "example_config_file", undefined as unknown as any);
// Call create_dependency_error
create_dependency_error("example_message", "example_dependency", undefined as unknown as any);
// Call create_network_error
create_network_error("example_message", undefined as unknown as any, undefined as unknown as any);
// Call create_runtime_error
create_runtime_error("example_message", "example_runtime", undefined as unknown as Array<string>, undefined as unknown as any);
// Call display
display(undefined as unknown as any);
// Call error_report
error_report(undefined as unknown as Exception, false);
// Call format_error_with_context
format_error_with_context(undefined as unknown as Exception, undefined as unknown as any);
