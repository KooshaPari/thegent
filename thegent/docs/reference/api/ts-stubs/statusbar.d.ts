// Auto-generated TypeScript declarations for statusbar
// Source: generate-api-docs.py

export declare class StatusItem {
  constructor(label: string, value: string, active: boolean, color: string);
}

export declare class StatusbarWidget extends Widget {
  constructor();
  add_item(item: StatusItem): void;
  clear_items(): void;
  compose(): void;
  on_mount(): void;
  remove_item(label: string): void;
  set_status(status: string, message: string): void;
  watch_agent_name(value: any): void;
  watch_agent_status(value: string): void;
  watch_cwd(value: string): void;
  watch_session_id(value: any): void;
}

export declare function add_item(item: StatusItem): void;
export declare function clear_items(): void;
export declare function compose(): void;
export declare function on_mount(): void;
export declare function remove_item(label: string): void;
export declare function set_status(status: string, message: string): void;
export declare function watch_agent_name(value: any): void;
export declare function watch_agent_status(value: string): void;
export declare function watch_cwd(value: string): void;
export declare function watch_session_id(value: any): void;
