// Auto-generated TypeScript declarations for prune
// Source: generate-api-docs.py

export declare function kill_process(pid: number): void;
export declare function mcp_prune(force: boolean, dry_run: boolean, parent_pid: any, interactive: boolean, caller_info: any): void;
export declare function prompt_tty_kill(pid: number, cmd: string, tty: string): void;
export declare function show_interactive_prune_menu(pid: number, cmd: string, tty: string, pane: any): void;
