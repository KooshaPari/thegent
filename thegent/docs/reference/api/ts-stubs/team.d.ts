// Auto-generated TypeScript declarations for team
// Source: generate-api-docs.py

export declare function team_create(name: string, agents: Array<string>, objective: string): void;
export declare function team_crew(format: string): void;
export declare function team_delegate(prompt: string, teammate: string): void;
export declare function team_hierarchy(format: string): void;
export declare function team_list(format: string): void;
export declare function team_status(run_id: string): void;
export declare function teammates_delegate(teammate: string, task: string, parent_run_id: string): void;
export declare function teammates_list(): void;
export declare function teammates_show(req_id: string): void;
export declare function teammates_status(run_id: string): void;
