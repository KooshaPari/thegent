// Auto-generated TypeScript declarations for manage
// Source: generate-api-docs.py

export declare function install_to_claude_code(url: string): void;
export declare function install_to_claude_desktop(url: string): void;
export declare function install_to_client(client: string, url: string, workspace: any, replace_all: boolean, force_http: boolean): void;
export declare function install_to_codex(url: string): void;
export declare function install_to_cursor(url: string, workspace: any): void;
export declare function install_to_droid(url: string, workspace: any): void;
export declare function mcp_down(): void;
export declare function mcp_restart(): void;
export declare function mcp_up(reload: boolean): void;
export declare function migrate_to_unimount(client: string, mcp_url: string, workspace: any): void;
export declare function prune_periodic_install(): void;
export declare function prune_periodic_start(): void;
export declare function prune_periodic_status(): void;
export declare function prune_periodic_stop(): void;
export declare function prune_periodic_uninstall(): void;
export declare function remove_playwright_from_client(client: string, workspace: any): void;
export declare function remove_servers_from_client(client: string, server_names: Array<string>, workspace: any): void;
export declare function serve_delegate_or_run(settings: any): void;
export declare function service_install(): void;
export declare function service_start(): void;
export declare function service_status(settings: any): void;
export declare function service_stop(): void;
export declare function service_uninstall(): void;
