// Auto-generated TypeScript declarations for policy
// Source: generate-api-docs.py

export declare class LearningSession {
  constructor(policy_manager: PolicyManager);
  is_valid(): void;
  start(): void;
}

export declare class PolicyManager {
  constructor(initial_policies: any);
  get_policy(key: string): void;
  update(new_policies: Record<(str, Any)>): void;
}

export declare function get_policy(key: string): void;
export declare function is_valid(): void;
export declare function start(): void;
export declare function update(new_policies: Record<(str, Any)>): void;
