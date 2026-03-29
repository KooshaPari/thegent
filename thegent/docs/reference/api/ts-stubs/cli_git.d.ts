// Auto-generated TypeScript declarations for cli_git
// Source: generate-api-docs.py

export declare function add(files: Array<string>, agent_id: string, project_root: string): void;
export declare function callback(ctx: typer.Context): void;
export declare function commit(message: string, agent_id: string, ref: string, project_root: string): void;
export declare function diff(project_root: string, agent_id: string, use_delta: boolean): void;
export declare function get_agent_id(): void;
export declare function lock_cleanup_main(ctx: typer.Context, path: Array<string>, max_age: number, dry_run: boolean): void;
export declare function lock_cleanup_service(action: string): void;
export declare function log(project_root: string, limit: number): void;
export declare function merge(base: string, ours: string, theirs: string, output: string): void;
export declare function run_system_git(args: Array<string>): void;
export declare function status(agent_id: string, project_root: string, short: boolean): void;
