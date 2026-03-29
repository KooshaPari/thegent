// Auto-generated TypeScript declarations for cliproxy_manager
// Source: generate-api-docs.py

export declare function ensure_proxy_running(settings: ThegentSettings): void;
export declare function fetch_provider_metrics(settings: any): void;
export declare function kill_proxy(settings: ThegentSettings): void;
export declare function proxy_service_install(settings: ThegentSettings): void;
export declare function proxy_service_start(): void;
export declare function proxy_service_stop(): void;
export declare function proxy_service_uninstall(): void;
export declare function run_login(settings: ThegentSettings, provider: string, prompt_func: any, force: boolean): void;
export declare function run_login_unified(settings: ThegentSettings, provider: string, prompt_func: any, skip_if_configured: boolean): void;
export declare function start_proxy_managed(settings: ThegentSettings): void;
