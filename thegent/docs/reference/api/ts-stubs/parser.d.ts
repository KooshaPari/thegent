// Auto-generated TypeScript declarations for parser
// Source: generate-api-docs.py

export declare class TaskParseError extends Exception {
}

export declare function detect_task_format(content: string): void;
export declare function extract_markdown_sections(body: string): void;
export declare function parse_legacy_task(content: string): void;
export declare function parse_list_from_markdown(content: string): void;
export declare function parse_markdown_sections_to_fields(body: string, frontmatter: Record<(str, Any)>): void;
export declare function parse_steps_from_markdown(content: string): void;
export declare function parse_task_file(file_path: string): void;
export declare function parse_yaml_frontmatter(content: string): void;
