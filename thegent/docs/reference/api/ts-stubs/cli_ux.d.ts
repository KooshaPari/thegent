// Auto-generated TypeScript declarations for cli_ux
// Source: generate-api-docs.py

export declare function display_command_examples(command: string, examples: Array<Record<(str, str)>>): void;
export declare function display_command_suggestion(command: string, suggestions: Array<string>): void;
export declare function format_command_help(command: string, description: string, examples: any): void;
export declare function format_error_with_suggestion(error: Exception, command: any): void;
export declare function interactive_confirm(message: string, default: boolean): void;
export declare function print_command_header(command: string, description: string): void;
export declare function print_section_header(title: string): void;
export declare function suggest_command(command: string, commands: any): void;
