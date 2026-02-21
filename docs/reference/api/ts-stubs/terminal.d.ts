// Auto-generated TypeScript declarations for terminal
// Source: generate-api-docs.py

export declare class TmuxPane {
}

export declare function capture_tmux_pane(pane_id: string, last_lines: number): void;
export declare function heliosShield_status(): void;
export declare function is_claude_code_pane(pane: TmuxPane): void;
export declare function list_tmux_panes(): void;
export declare function send_to_tmux_pane(pane_id: string, text: string, enter: boolean): void;
