// Auto-generated TypeScript declarations for reputation
// Source: generate-api-docs.py

export declare class ReputationEntry extends BaseModel {
}

export declare class ReputationManager {
  constructor(db_path: any);
  get_all_scores(): void;
  get_reputation_report(agent_id: string): void;
  get_trust_score(agent_id: string): void;
  submit_rating(agent_id: string, reviewer_id: string, task_id: string, rating: number, feedback: string): void;
}

export declare function get_all_scores(): void;
export declare function get_reputation_report(agent_id: string): void;
export declare function get_trust_score(agent_id: string): void;
export declare function submit_rating(agent_id: string, reviewer_id: string, task_id: string, rating: number, feedback: string): void;
