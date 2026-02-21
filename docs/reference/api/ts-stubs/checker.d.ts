// Auto-generated TypeScript declarations for checker
// Source: generate-api-docs.py

export declare class CheckerAgent {
  constructor(settings: ThegentSettings, agent_name: string);
  decide(governance_report: Record<(str, Any, str)>, todo_spec: string, wbs_status: Record<(str, Any, str)>, agent_response: string): void;
}

export declare class CheckerDecision extends StrEnum {
}

export declare class CheckerResult extends BaseModel {
}

export declare function decide(governance_report: Record<(str, Any, str)>, todo_spec: string, wbs_status: Record<(str, Any, str)>, agent_response: string): void;
