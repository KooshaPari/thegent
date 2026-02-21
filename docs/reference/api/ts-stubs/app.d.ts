// Auto-generated TypeScript declarations for app
// Source: generate-api-docs.py

export declare class CompositApp extends App {
  constructor(session_state: SessionState | None);
  action_close_pane(): void;
  action_focus_next(): void;
  action_new_pane(): void;
  action_quit(): void;
  action_retry_pane(): void;
  action_split_horizontal(): void;
  action_split_vertical(): void;
  compose(): void;
  on_mount(): void;
  on_panel_mounted(message: PanelMounted): void;
  on_panel_unmounted(message: PanelUnmounted): void;
  on_unmount(): void;
}

export declare class ErrorBoundary extends Static {
  constructor(error_message: string, error_type: string, stack_trace: string, pane_id: string);
  render(): void;
}

export declare class Statusbar extends Static {
  render(): void;
}

export declare function action_close_pane(): void;
export declare function action_focus_next(): void;
export declare function action_new_pane(): void;
export declare function action_quit(): void;
export declare function action_retry_pane(): void;
export declare function action_split_horizontal(): void;
export declare function action_split_vertical(): void;
export declare function compose(): void;
export declare function on_mount(): void;
export declare function on_panel_mounted(message: PanelMounted): void;
export declare function on_panel_unmounted(message: PanelUnmounted): void;
export declare function on_unmount(): void;
export declare function render(): void;
