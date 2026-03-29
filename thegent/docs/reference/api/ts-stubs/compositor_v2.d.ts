// Auto-generated TypeScript declarations for compositor_v2
// Source: generate-api-docs.py

export declare class CompositorApp extends App {
  constructor(context: any);
  action_close_pane(): void;
  action_focus_next(): void;
  action_focus_prev(): void;
  action_new_pane(): void;
  action_quit(): void;
  action_restore_layout(): void;
  action_save_layout(): void;
  action_show_help(): void;
  action_split_horizontal(): void;
  action_split_vertical(): void;
  action_toggle_maximize(): void;
  action_toggle_sidebar(): void;
  append_output(text: string): void;
  compose(): void;
  on_mount(): void;
  set_agent_status(status: string, agent: string): void;
  update_status(): void;
  update_title(): void;
  write_output(text: string): void;
}

export declare class TUIContext {
  constructor(session_id: any, agent_name: any, cwd: any);
}

export declare function action_close_pane(): void;
export declare function action_focus_next(): void;
export declare function action_focus_prev(): void;
export declare function action_new_pane(): void;
export declare function action_quit(): void;
export declare function action_restore_layout(): void;
export declare function action_save_layout(): void;
export declare function action_show_help(): void;
export declare function action_split_horizontal(): void;
export declare function action_split_vertical(): void;
export declare function action_toggle_maximize(): void;
export declare function action_toggle_sidebar(): void;
export declare function append_output(text: string): void;
export declare function compose(): void;
export declare function on_mount(): void;
export declare function set_agent_status(status: string, agent: string): void;
export declare function update_status(): void;
export declare function update_title(): void;
export declare function write_output(text: string): void;
