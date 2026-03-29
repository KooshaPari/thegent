// Auto-generated TypeScript declarations for terminal_pane
// Source: generate-api-docs.py

export declare class TerminalConfig {
}

export declare class TerminalManager {
  constructor();
  add_pane(pane_id: string, pane: TerminalPane): void;
  get_active(): void;
  get_pane(pane_id: string): void;
  list_panes(): void;
  set_active(pane_id: string): void;
}

export declare class TerminalPane extends Widget {
  constructor();
  clear(): void;
  get_output(): void;
  on_resize(event: Resize): void;
}

export declare class TerminalSize {
}

export declare function add_pane(pane_id: string, pane: TerminalPane): void;
export declare function clear(): void;
export declare function get_active(): void;
export declare function get_output(): void;
export declare function get_pane(pane_id: string): void;
export declare function list_panes(): void;
export declare function on_resize(event: Resize): void;
export declare function set_active(pane_id: string): void;
