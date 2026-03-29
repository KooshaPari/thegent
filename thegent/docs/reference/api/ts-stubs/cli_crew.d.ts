// Auto-generated TypeScript declarations for cli_crew
// Source: generate-api-docs.py

export declare function crew_add_agent_cmd(crew_id: string, role: string, name: string, description: string, capabilities: string, model: string): void;
export declare function crew_add_task_cmd(crew_id: string, description: string, dependencies: string, agent_id: string): void;
export declare function crew_create_cmd(name: string, description: string, execution_mode: string, output: string): void;
export declare function crew_execute_cmd(crew_file: string, cwd: string, mode: string, timeout: number, model: string): void;
export declare function crew_list_cmd(): void;
export declare function crew_show_cmd(crew_id: string): void;
export declare function crew_status_cmd(crew_id: string): void;
