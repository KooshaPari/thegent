// Auto-generated TypeScript declarations for registry_tui
// Source: generate-api-docs.py

export declare class RegistryTUI extends App {
  constructor();
  action_refresh(): void;
  action_toggle_all(): void;
  compose(): void;
  on_mount(): void;
  on_session_selected(event: DataTable.RowSelected): void;
}

export declare class SessionDetails extends Static {
  update_details(session: Record<(str, Any)>): void;
}

export declare function action_refresh(): void;
export declare function action_toggle_all(): void;
export declare function compose(): ComposeResult;
export declare function on_mount(): void;
export declare function on_session_selected(event: DataTable.RowSelected): void;
export declare function update_details(session: Record<(str, Any)>): void;
