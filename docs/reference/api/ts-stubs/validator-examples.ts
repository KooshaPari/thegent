// Auto-generated usage examples for validator
// Source: generate-api-docs.py

import { TaskValidator, ValidationError, ValidationResult, format_errors, validate, validate_file, validate_task, validate_task_file } from "./validator";

// Create a TaskValidator instance
const taskvalidator = new TaskValidator(undefined as unknown as any);
taskvalidator.validate(undefined as unknown as Record<(str, Any)>);
taskvalidator.validate_file("example_file_path");

// Create a ValidationError instance
const validationerror = new ValidationError();

// Create a ValidationResult instance
const validationresult = new ValidationResult();
validationresult.format_errors();

// Call format_errors
format_errors(undefined as unknown as any);
// Call validate
validate(undefined as unknown as any, undefined as unknown as Record<(str, Any)>);
// Call validate_file
validate_file(undefined as unknown as any, "example_file_path");
// Call validate_task
validate_task(undefined as unknown as Record<(str, Any)>, undefined as unknown as any);
// Call validate_task_file
validate_task_file("example_file_path", undefined as unknown as any);
