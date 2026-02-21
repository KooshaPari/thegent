// Auto-generated TypeScript declarations for cli_examples
// Source: generate-api-docs.py

export declare class CLIExamplesGenerator {
  constructor(command: string);
  generate_examples(command: string): void;
  get_all_commands(): void;
  render_markdown(examples: Array<Record<(str, Any)>>): void;
}

export declare function generate_examples(command: string): void;
export declare function get_all_commands(): void;
export declare function render_markdown(examples: Array<Record<(str, Any)>>): void;
