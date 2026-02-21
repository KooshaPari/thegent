// Auto-generated usage examples for parser
// Source: generate-api-docs.py

import { TaskParseError, detect_task_format, extract_markdown_sections, parse_legacy_task, parse_list_from_markdown, parse_markdown_sections_to_fields, parse_steps_from_markdown, parse_task_file, parse_yaml_frontmatter } from "./parser";

// Create a TaskParseError instance
const taskparseerror = new TaskParseError();

// Call detect_task_format
detect_task_format("example_content");
// Call extract_markdown_sections
extract_markdown_sections("example_body");
// Call parse_legacy_task
parse_legacy_task("example_content");
// Call parse_list_from_markdown
parse_list_from_markdown("example_content");
// Call parse_markdown_sections_to_fields
parse_markdown_sections_to_fields("example_body", undefined as unknown as Record<(str, Any)>);
// Call parse_steps_from_markdown
parse_steps_from_markdown("example_content");
// Call parse_task_file
parse_task_file("example_file_path");
// Call parse_yaml_frontmatter
parse_yaml_frontmatter("example_content");
