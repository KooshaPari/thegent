// Auto-generated TypeScript declarations for modes
// Source: generate-api-docs.py

export declare function register_modes(mcp: FastMCP): void;
export declare function thegent_dag_ready(cd: any): void;
export declare function thegent_dag_recover(cd: any, action: string): void;
export declare function thegent_dag_sync(cd: any, auto_run_next: boolean): void;
export declare function thegent_discussion_add_question(session_id: string, question: string, answer: any): void;
export declare function thegent_discussion_finalize(brief_content: string, brief_id: any, cd: any): void;
export declare function thegent_discussion_start(topic: string, cd: any): void;
export declare function thegent_plan_approve(plan_id: string, cd: any): void;
export declare function thegent_plan_create(prompt: string, plan_id: any, brief_path: any, cd: any): void;
export declare function thegent_plan_get(plan_id: any, cd: any): void;
export declare function thegent_plan_save(content: string, plan_id: any, cd: any): void;
export declare function thegent_plan_status(cd: any): void;
export declare function thegent_protocol_get(mode: any, name: any, cd: any): void;
export declare function thegent_protocol_list(cd: any): void;
export declare function thegent_research_finalize(report_content: string, report_id: any, cd: any): void;
export declare function thegent_team_create(prompt: string, mode: string, teammates: number, cd: any): void;
export declare function thegent_team_delegate(teammate_id: string, prompt: string, parent_run_id: any): void;
export declare function thegent_team_list(cd: any): void;
export declare function thegent_validation_report(cd: any, protocol: any): void;
