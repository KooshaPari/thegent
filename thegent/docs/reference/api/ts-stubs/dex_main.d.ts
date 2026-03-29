// Auto-generated TypeScript declarations for dex_main
// Source: generate-api-docs.py

export declare class LazyConsole {
}

export declare function default_dex(ctx: typer.Context, force: boolean, native: boolean): void;
export declare function dex_bg(model_alias: string, prompt: string, cd: any, mode: string, timeout: number, owner: any): void;
export declare function dex_composer(dangerously_bypass: boolean, resume: any, cd: any, print_mode: boolean, debug: boolean, add_dir: Array<string>, sandbox: any, full_auto: boolean, search: boolean, no_alt_screen: boolean, prompt: any): void;
export declare function dex_doctor(fix: boolean): void;
export declare function dex_flash(dangerously_bypass: boolean, resume: any, cd: any, print_mode: boolean, debug: boolean, add_dir: Array<string>, sandbox: any, full_auto: boolean, search: boolean, no_alt_screen: boolean, continue_session: boolean, prompt: any): void;
export declare function dex_free(dangerously_bypass: boolean, resume: any, cd: any, print_mode: boolean, debug: boolean, add_dir: Array<string>, sandbox: any, full_auto: boolean, search: boolean, no_alt_screen: boolean, continue_session: boolean, prompt: any): void;
export declare function dex_glm(dangerously_bypass: boolean, resume: any, cd: any, print_mode: boolean, debug: boolean, add_dir: Array<string>, sandbox: any, full_auto: boolean, search: boolean, no_alt_screen: boolean, continue_session: boolean, prompt: any): void;
export declare function dex_haiku(dangerously_bypass: boolean, resume: any, cd: any, print_mode: boolean, debug: boolean, add_dir: Array<string>, sandbox: any, full_auto: boolean, search: boolean, no_alt_screen: boolean, continue_session: boolean, prompt: any): void;
export declare function dex_history(limit: number, format: any): void;
export declare function dex_inspect(session_ids: Array<string>, owner: any, tail: number, stderr: boolean, format: any, include_contract: boolean): void;
export declare function dex_logs(session_id: string, follow: boolean, stderr: boolean, tail: number, timeout: number): void;
export declare function dex_max(dangerously_bypass: boolean, resume: any, cd: any, print_mode: boolean, debug: boolean, add_dir: Array<string>, sandbox: any, full_auto: boolean, search: boolean, no_alt_screen: boolean, continue_session: boolean, prompt: any): void;
export declare function dex_mini(dangerously_bypass: boolean, resume: any, cd: any, print_mode: boolean, debug: boolean, add_dir: Array<string>, sandbox: any, full_auto: boolean, search: boolean, no_alt_screen: boolean, continue_session: boolean, prompt: any): void;
export declare function dex_opus(dangerously_bypass: boolean, resume: any, cd: any, print_mode: boolean, debug: boolean, add_dir: Array<string>, sandbox: any, full_auto: boolean, search: boolean, no_alt_screen: boolean, continue_session: boolean, prompt: any): void;
export declare function dex_ps(all_sessions: boolean, owner: any, format: any, include_contract: boolean): void;
export declare function dex_run(model_alias: string, prompt: string, cd: any, mode: string, timeout: number): void;
export declare function dex_sonnet(dangerously_bypass: boolean, resume: any, cd: any, print_mode: boolean, debug: boolean, add_dir: Array<string>, sandbox: any, full_auto: boolean, search: boolean, no_alt_screen: boolean, continue_session: boolean, prompt: any): void;
export declare function dex_status(session_id: string, format: any, include_contract: boolean): void;
export declare function dex_stop(session_id: string, force: boolean, wind_down: boolean, grace: number): void;
export declare function dex_ultra(dangerously_bypass: boolean, resume: any, cd: any, print_mode: boolean, debug: boolean, add_dir: Array<string>, sandbox: any, full_auto: boolean, search: boolean, no_alt_screen: boolean, continue_session: boolean, prompt: any): void;
export declare function dex_wait(session_id: string, timeout: number): void;
export declare function install_links(bin_dir: string, force: boolean): void;
