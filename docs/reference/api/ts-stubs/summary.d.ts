// Auto-generated TypeScript declarations for summary
// Source: generate-api-docs.py

export declare function get_chat_logs(session_dir: string, project_key: string, start_dt: datetime, end_dt: datetime): void;
export declare function get_git_commits(project_path: string, start_dt: datetime, end_dt: datetime): void;
export declare function get_project_key(project_path: string): void;
export declare function get_time_range(period: string): void;
export declare function summary_impl(period: string, project_path: any, summarize: boolean, agent: string): void;
