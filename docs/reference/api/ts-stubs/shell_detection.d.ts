// Auto-generated TypeScript declarations for shell_detection
// Source: generate-api-docs.py

export declare class ShellType extends str, Enum {
}

export declare function get_fast_command_prefix(shell_type: ShellType): void;
export declare function get_preferred_shell(performance: boolean): void;
export declare function get_shell_executable(shell_type: ShellType): void;
