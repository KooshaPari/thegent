// Auto-generated TypeScript declarations for run
// Source: generate-api-docs.py

export declare function run_agent(prompt: string, agent: any, model: any, bg: boolean, loop: boolean, cd: any, timeout: number, full: boolean, owner: any, run_id: any, task_id: any, lane: string, routing: any, failover: boolean, contract_version: any, domain: any, speculative: boolean, idempotency_token: any, remote: boolean): void;
export declare function run_history(limit: number, format: string): void;
export declare function run_logs(session_id: any, follow: boolean): void;
export declare function run_ps(all_sessions: boolean, owner: any, format: string, include_contract: boolean): void;
export declare function run_stop(session_id: any): void;
