// Auto-generated usage examples for reward_model
// Source: generate-api-docs.py

import { RecursiveRewardModel, RewardSignal, get_reward_statistics, optimize, record_reward } from "./reward_model";

// Create a RecursiveRewardModel instance
const recursiverewardmodel = new RecursiveRewardModel();
recursiverewardmodel.get_reward_statistics();
recursiverewardmodel.optimize();
recursiverewardmodel.record_reward("example_agent_id", "example_task_id", 0, undefined as unknown as any);

// Create a RewardSignal instance
const rewardsignal = new RewardSignal();

// Call get_reward_statistics
get_reward_statistics(undefined as unknown as any);
// Call optimize
optimize(undefined as unknown as any);
// Call record_reward
record_reward(undefined as unknown as any, "example_agent_id", "example_task_id", 0, undefined as unknown as any);
