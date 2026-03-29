// Auto-generated TypeScript declarations for code_annotation
// Source: generate-api-docs.py

export declare class CodeAnnotationGenerator {
  constructor(annotation_format: string);
  generate_annotation_component(annotations: Array<Record<(str, Any)>>): void;
  parse_annotations(code: string): void;
}

export declare function generate_annotation_component(annotations: Array<Record<(str, Any)>>): void;
export declare function parse_annotations(code: string): void;
