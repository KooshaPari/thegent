// Auto-generated usage examples for openapi
// Source: generate-api-docs.py

import { OpenAPIGenerator, generate_swagger_ui_html, parse_openapi_spec } from "./openapi";

// Create a OpenAPIGenerator instance
const openapigenerator = new OpenAPIGenerator("example_output_format");
openapigenerator.generate_swagger_ui_html("example_spec_url");
openapigenerator.parse_openapi_spec("example_file_path");

// Call generate_swagger_ui_html
generate_swagger_ui_html(undefined as unknown as any, "example_spec_url");
// Call parse_openapi_spec
parse_openapi_spec(undefined as unknown as any, "example_file_path");
