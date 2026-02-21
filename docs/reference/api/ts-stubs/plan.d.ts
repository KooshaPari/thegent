// Auto-generated TypeScript declarations for plan
// Source: generate-api-docs.py

export declare function milestone_create(name: Annotated<(str, Any)>, product_id: Annotated<(Any, Any)>): void;
export declare function milestone_list(output_json: Annotated<(bool, Any)>): void;
export declare function plan_add(task_id: string, agent: string, prompt: string, depends_on: any): void;
export declare function plan_analyze(cd: any, format: string): void;
export declare function plan_checkpoint(reason: string): void;
export declare function plan_claim(item_id: string, agent_id: any, cd: any): void;
export declare function plan_complete(item_id: string, agent_id: any, cd: any): void;
export declare function plan_incorporate(dry_run: boolean): void;
export declare function plan_next(format: string): void;
export declare function plan_progress(limit: number, format: string): void;
export declare function plan_remove(task_id: string): void;
export declare function plan_roadmap(format: string): void;
export declare function plan_rollback(checkpoint_id: string): void;
export declare function plan_status(format: string): void;
export declare function plan_work_stream(limit: number, format: string, cd: any): void;
export declare function sprint_create(name: Annotated<(str, Any)>, milestone_id: Annotated<(Any, Any)>): void;
export declare function sprint_list(output_json: Annotated<(bool, Any)>): void;
