// Auto-generated TypeScript declarations for manager
// Source: generate-api-docs.py

export declare class LayoutManager {
  constructor(storage_dir: any);
  create_layout(name: string, root: any): void;
  delete_layout(name: string): void;
  duplicate_layout(source_name: string, new_name: string): void;
  get_current(): void;
  get_layout(name: string): void;
  list_layouts(): void;
  rename_layout(old_name: string, new_name: string): void;
  switch_layout(name: string): void;
}

export declare class LayoutState {
}

export declare class PaneConfig {
}

export declare class SplitConfig {
}

export declare function create_default_layout(): void;
export declare function create_full_output_layout(): void;
export declare function create_horizontal_split(left_pane: PaneConfig, right_pane: PaneConfig, left_weight: number, right_weight: number): void;
export declare function create_layout(name: string, root: any): void;
export declare function create_main_sidebar(main_pane: PaneConfig, sidebar_pane: PaneConfig, sidebar_width: number): void;
export declare function create_terminal_layout(): void;
export declare function create_three_column(left: PaneConfig, center: PaneConfig, right: PaneConfig, weights: any): void;
export declare function create_vertical_split(top_pane: PaneConfig, bottom_pane: PaneConfig, top_weight: number, bottom_weight: number): void;
export declare function delete_layout(name: string): void;
export declare function duplicate_layout(source_name: string, new_name: string): void;
export declare function get_current(): void;
export declare function get_layout(name: string): void;
export declare function list_layouts(): void;
export declare function rename_layout(old_name: string, new_name: string): void;
export declare function switch_layout(name: string): void;
