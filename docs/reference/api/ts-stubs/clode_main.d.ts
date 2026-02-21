// Auto-generated TypeScript declarations for clode_main
// Source: generate-api-docs.py

export declare class LazyConsole {
}

export declare function clode_bg(prompt: string, cd: any, mode: string, timeout: number, owner: any, model: string): void;
export declare function clode_bg_global(model_alias: string, prompt: string, cd: any, mode: string, timeout: number, owner: any): void;
export declare function clode_comp(provider: any, resume: any, cd: any, print_mode: boolean, debug: boolean, add_dir: Array<string>, output_format: any, continue_session: boolean, prompt: any): void;
export declare function clode_composer(provider: any, resume: any, cd: any, print_mode: boolean, debug: boolean, add_dir: Array<string>, output_format: any, continue_session: boolean, prompt: any): void;
export declare function clode_doctor(fix: boolean): void;
export declare function clode_flash(provider: any, resume: any, cd: any, print_mode: boolean, debug: boolean, add_dir: Array<string>, output_format: any, continue_session: boolean, prompt: any): void;
export declare function clode_free(resume: any, cd: any, print_mode: boolean, debug: boolean, add_dir: Array<string>, output_format: any, continue_session: boolean, prompt: any): void;
export declare function clode_glm(policy: string, prefer: string, dangerously_skip_permissions: boolean, resume: any, cd: any, print_mode: boolean, debug: boolean, add_dir: Array<string>, output_format: any, continue_session: boolean, model: any, prompt: any): void;
export declare function clode_haiku(provider: any, resume: any, cd: any, print_mode: boolean, debug: boolean, add_dir: Array<string>, output_format: any, continue_session: boolean, prompt: any): void;
export declare function clode_history(limit: number, format: any): void;
export declare function clode_inspect(session_ids: Array<string>, owner: any, tail: number, stderr: boolean, format: any, include_contract: boolean): void;
export declare function clode_logs(session_id: string, follow: boolean, stderr: boolean, tail: number, timeout: number): void;
export declare function clode_max(provider: any, resume: any, cd: any, print_mode: boolean, debug: boolean, add_dir: Array<string>, output_format: any, continue_session: boolean, prompt: any): void;
export declare function clode_mini(resume: any, cd: any, print_mode: boolean, debug: boolean, add_dir: Array<string>, output_format: any, continue_session: boolean, prompt: any): void;
export declare function clode_opus(provider: any, resume: any, cd: any, print_mode: boolean, debug: boolean, add_dir: Array<string>, output_format: any, continue_session: boolean, prompt: any): void;
export declare function clode_opus1m(provider: any, resume: any, cd: any, print_mode: boolean, debug: boolean, add_dir: Array<string>, output_format: any, continue_session: boolean, prompt: any): void;
export declare function clode_ps(all_sessions: boolean, owner: any, format: any, include_contract: boolean): void;
export declare function clode_run(prompt: string, cd: any, mode: string, timeout: number, model: string): void;
export declare function clode_run_global(model_alias: string, prompt: string, cd: any, mode: string, timeout: number): void;
export declare function clode_sonnet(provider: any, resume: any, cd: any, print_mode: boolean, debug: boolean, add_dir: Array<string>, output_format: any, continue_session: boolean, prompt: any): void;
export declare function clode_status(session_id: string, format: any, include_contract: boolean): void;
export declare function clode_step(provider: any, resume: any, cd: any, print_mode: boolean, debug: boolean, add_dir: Array<string>, output_format: any, continue_session: boolean, prompt: any): void;
export declare function clode_stop(session_id: string, force: boolean, wind_down: boolean, grace: number): void;
export declare function clode_wait(session_id: string, timeout: number): void;
export declare function cost_key(b: string): [(float, number, str)];
export declare function create_provider_app(provider: string): void;
export declare function default_clode(ctx: typer.Context, native: boolean): void;
export declare function install_links(bin_dir: string, force: boolean): void;
export declare function main(ctx: typer.Context): void;
export declare function sitback_cmd(agent: string, provider: any, model: any, dex: boolean, cd: any, skill: any, profile: string, tmux: boolean, no_dashboard: boolean, tui: boolean): void;
