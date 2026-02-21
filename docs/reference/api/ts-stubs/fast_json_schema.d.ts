// Auto-generated TypeScript declarations for fast_json_schema
// Source: generate-api-docs.py

export declare class FastJSONSchemaValidator {
  constructor(schema: Record<(str, Any)>);
  backend(): void;
  is_valid(instance: any): void;
  validate(instance: any): void;
}

export declare function backend(): void;
export declare function get_schema_validator(schema: Record<(str, Any)>, cache_key: any): void;
export declare function is_valid(instance: any): void;
export declare function is_valid_json_schema(instance: any, schema: Record<(str, Any)>, cache_key: any): void;
export declare function validate(instance: any): void;
export declare function validate_json_schema(instance: any, schema: Record<(str, Any)>, cache_key: any): void;
