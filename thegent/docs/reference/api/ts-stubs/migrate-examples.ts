// Auto-generated usage examples for migrate
// Source: generate-api-docs.py

import { migrate_legacy_task_to_yaml_frontmatter, migrate_work_stream_entry_to_task, migrate_work_stream_to_tasks } from "./migrate";

// Call migrate_legacy_task_to_yaml_frontmatter
migrate_legacy_task_to_yaml_frontmatter("example_content");
// Call migrate_work_stream_entry_to_task
migrate_work_stream_entry_to_task("example_task_id", "example_title", "example_source", "example_priority", "example_depends", undefined as unknown as any);
// Call migrate_work_stream_to_tasks
migrate_work_stream_to_tasks("example_work_stream_path", "example_tasks_dir", false);
