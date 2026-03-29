// Auto-generated TypeScript declarations for migrate
// Source: generate-api-docs.py

export declare function migrate_legacy_task_to_yaml_frontmatter(content: string): void;
export declare function migrate_work_stream_entry_to_task(task_id: string, title: string, source: string, priority: string, depends: string, work_stream_path: any): void;
export declare function migrate_work_stream_to_tasks(work_stream_path: string, tasks_dir: string, dry_run: boolean): void;
