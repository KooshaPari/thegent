// Auto-generated TypeScript declarations for schema_formal
// Source: generate-api-docs.py

export declare class SchemaEvolutionVerifier {
  check_liveness_impact(evolution_report: Record<(str, Any)>): void;
  verify_compatibility(old_schema: Record<(str, Any)>, new_schema: Record<(str, Any)>): void;
  verify_tag_evolution(old_tags: Array<string>, new_tags: Array<string>): void;
}

export declare function check_liveness_impact(evolution_report: Record<(str, Any)>): void;
export declare function verify_compatibility(old_schema: Record<(str, Any)>, new_schema: Record<(str, Any)>): void;
export declare function verify_tag_evolution(old_tags: Array<string>, new_tags: Array<string>): void;
