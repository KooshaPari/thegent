// Auto-generated TypeScript declarations for pane_manager
// Source: generate-api-docs.py

export declare class PaneManager {
  constructor();
  close_pane(): void;
  create_root_pane(pane_id: string): void;
  focus_next(): void;
  restore_layout(layout_data: Record<string, unknown>): void;
  save_layout(): void;
  split_pane(direction: string): void;
}

export declare class PaneNode {
}

export declare function close_pane(): void;
export declare function create_root_pane(pane_id: string): void;
export declare function focus_next(): void;
export declare function restore_layout(layout_data: Record<string, unknown>): void;
export declare function save_layout(): void;
export declare function split_pane(direction: string): void;
