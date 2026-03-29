// Auto-generated TypeScript declarations for workstream_db
// Source: generate-api-docs.py

export declare class WorkstreamDB {
  constructor(db_path: any, settings: any);
  execute_query(query: string, params: [(Any, Ellipsis)]): void;
  generate_work_stream_md(output_path: string): void;
  get_active_items(): void;
  get_dependency_graph(): void;
  get_next_items(limit: number, completed_ids: any): void;
  get_ready_items(max_retries: number, base_backoff_sec: number): void;
  get_recent_costs(limit: number): void;
  get_running_count(): void;
  get_running_count_by_lane(): void;
  get_running_sessions(): void;
  get_session(session_id: string): void;
  get_statistics(): void;
  get_top_agents(limit: number): void;
  mark_session_complete(session_id: string, exit_code: number): void;
  record_constitutional_violation(item_id: string, session_id: any, violation: any): void;
  record_cost(session_id: string, cost_usd: number, tokens_total: number, model: any): void;
  record_launch(item_id: string, session_id: string, lane: string, model: string, estimated_cost: number, trigger_type: string, pid: any): void;
  record_resource_usage(session_id: string, usage: Record<(str, Any)>): void;
  record_session(session_id: string, agent: string, prompt: string, status: string, workstream_item_id: any, lane: any, model: any, owner_tag: any, team_id: any, task_id: any): void;
  sync_from_agileplus(session_dir: string): void;
  sync_from_queues(session_dir: string): void;
  sync_with_markdown(work_stream_path: string): void;
  sync_workstream(workstream_data: Record<(str, Any)>): void;
  upsert_canonical_item(item_id: string, title: string, source: string, source_system: string, priority: string, status: string, metadata: any, depends: any): void;
}

export declare function execute_query(query: string, params: [(Any, Ellipsis)]): void;
export declare function generate_work_stream_md(output_path: string): void;
export declare function get_active_items(): void;
export declare function get_dependency_graph(): void;
export declare function get_next_items(limit: number, completed_ids: any): void;
export declare function get_ready_items(max_retries: number, base_backoff_sec: number): void;
export declare function get_recent_costs(limit: number): void;
export declare function get_running_count(): void;
export declare function get_running_count_by_lane(): void;
export declare function get_running_sessions(): void;
export declare function get_session(session_id: string): void;
export declare function get_statistics(): void;
export declare function get_top_agents(limit: number): void;
export declare function mark_session_complete(session_id: string, exit_code: number): void;
export declare function record_constitutional_violation(item_id: string, session_id: any, violation: any): void;
export declare function record_cost(session_id: string, cost_usd: number, tokens_total: number, model: any): void;
export declare function record_launch(item_id: string, session_id: string, lane: string, model: string, estimated_cost: number, trigger_type: string, pid: any): void;
export declare function record_resource_usage(session_id: string, usage: Record<(str, Any)>): void;
export declare function record_session(session_id: string, agent: string, prompt: string, status: string, workstream_item_id: any, lane: any, model: any, owner_tag: any, team_id: any, task_id: any): void;
export declare function sync_from_agileplus(session_dir: string): void;
export declare function sync_from_queues(session_dir: string): void;
export declare function sync_with_markdown(work_stream_path: string): void;
export declare function sync_workstream(workstream_data: Record<(str, Any)>): void;
export declare function upsert_canonical_item(item_id: string, title: string, source: string, source_system: string, priority: string, status: string, metadata: any, depends: any): void;
