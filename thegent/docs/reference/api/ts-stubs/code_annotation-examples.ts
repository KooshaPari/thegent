// Auto-generated usage examples for code_annotation
// Source: generate-api-docs.py

import { CodeAnnotationGenerator, generate_annotation_component, parse_annotations } from "./code_annotation";

// Create a CodeAnnotationGenerator instance
const codeannotationgenerator = new CodeAnnotationGenerator("example_annotation_format");
codeannotationgenerator.generate_annotation_component(undefined as unknown as Array<Record<(str, Any)>>);
codeannotationgenerator.parse_annotations("example_code");

// Call generate_annotation_component
generate_annotation_component(undefined as unknown as any, undefined as unknown as Array<Record<(str, Any)>>);
// Call parse_annotations
parse_annotations(undefined as unknown as any, "example_code");
