// Auto-generated TypeScript declarations for menubar
// Source: generate-api-docs.py

export declare class MenuDropdown extends Static {
  constructor(items: Array<[(str, Any)]>);
  compose(): void;
}

export declare class MenubarWidget extends Widget {
  action_toggle_menu(menu_name: string): void;
  compose(): void;
  on_click(event: Click): void;
  on_mount(): void;
}

export declare function action_toggle_menu(menu_name: string): void;
export declare function compose(): void;
export declare function on_click(event: Click): void;
export declare function on_mount(): void;
