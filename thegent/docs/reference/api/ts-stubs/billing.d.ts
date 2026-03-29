// Auto-generated TypeScript declarations for billing
// Source: generate-api-docs.py

export declare class TeamBillingManager {
  constructor(session_dir: string);
  check_quota(team_id: string, resource: string, cost: number): void;
  get_billing_report(team_id: string): void;
  record_usage(team_id: string, resource: string, amount: number): void;
}

export declare function check_quota(team_id: string, resource: string, cost: number): void;
export declare function get_billing_report(team_id: string): void;
export declare function record_usage(team_id: string, resource: string, amount: number): void;
