// Auto-generated TypeScript declarations for macos_desktop
// Source: generate-api-docs.py

export declare class AutomationError extends Exception {
}

export declare class AutomationResult {
}

export declare class MacOSDesktopAutomation {
  click_menu_item(app: string, menu: string, item: string): void;
  get_frontmost_app(): void;
  is_available(): void;
  open_application(name: string): void;
  run_applescript(script: string, timeout_s: number): void;
  run_jxa(script: string, timeout_s: number): void;
}

export declare function click_menu_item(app: string, menu: string, item: string): void;
export declare function get_frontmost_app(): void;
export declare function is_available(): void;
export declare function open_application(name: string): void;
export declare function run_applescript(script: string, timeout_s: number): void;
export declare function run_jxa(script: string, timeout_s: number): void;
