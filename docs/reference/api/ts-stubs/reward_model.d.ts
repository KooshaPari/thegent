// Auto-generated TypeScript declarations for reward_model
// Source: generate-api-docs.py

export declare class RecursiveRewardModel {
  constructor();
  get_reward_statistics(): void;
  optimize(): void;
  record_reward(agent_id: string, task_id: string, reward_value: number, metadata: any): void;
}

export declare class RewardSignal {
}

export declare function get_reward_statistics(): void;
export declare function optimize(): void;
export declare function record_reward(agent_id: string, task_id: string, reward_value: number, metadata: any): void;
