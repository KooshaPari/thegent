// Auto-generated TypeScript declarations for coordination
// Source: generate-api-docs.py

export declare class TeamCoordinator {
  constructor(session_dir: string);
  broadcast_message(team_id: string, sender: string, message: string): void;
  call_vote(team_id: string, caller: string, subject: string, options: Array<string>): void;
  cast_vote(team_id: string, vote_id: string, voter: string, option: string): void;
  detect_idle(stdout: string): void;
  get_vote_result(team_id: string, vote_id: string): void;
  handle_task_completed(team_id: string, task_id: string, result: string): void;
  wait_for_task(team_id: string, task_id: string, timeout: number): void;
}

export declare function broadcast_message(team_id: string, sender: string, message: string): void;
export declare function call_vote(team_id: string, caller: string, subject: string, options: Array<string>): void;
export declare function cast_vote(team_id: string, vote_id: string, voter: string, option: string): void;
export declare function detect_idle(stdout: string): void;
export declare function get_vote_result(team_id: string, vote_id: string): void;
export declare function handle_task_completed(team_id: string, task_id: string, result: string): void;
export declare function wait_for_task(team_id: string, task_id: string, timeout: number): void;
