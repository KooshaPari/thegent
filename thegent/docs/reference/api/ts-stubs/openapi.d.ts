// Auto-generated TypeScript declarations for openapi
// Source: generate-api-docs.py

export declare class OpenAPIGenerator {
  constructor(output_format: string);
  generate_swagger_ui_html(spec_url: string): void;
  parse_openapi_spec(file_path: string): void;
}

export declare function generate_swagger_ui_html(spec_url: string): void;
export declare function parse_openapi_spec(file_path: string): void;
