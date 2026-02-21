// Auto-generated TypeScript declarations for teammates
// Source: generate-api-docs.py

export declare class DelegationRequest {
}

export declare class TeammateManager {
  constructor(storage_path: string, hierarchy_manager: any);
  create_team(team_id: string, name: string, description: string, team_type: TeamType, coordination_mode: CoordinationMode, lead_id: string): void;
  delegate(teammate_id: string, parent_run_id: string, prompt: string, team_id: any, relationship_type: RelationshipType): void;
  get_delegations(parent_run_id: any): void;
  list_personas(): void;
  update_status(req_id: string, status: string, summary: any): void;
}

export declare class TeammatePersona {
}

export declare function create_team(team_id: string, name: string, description: string, team_type: TeamType, coordination_mode: CoordinationMode, lead_id: string): void;
export declare function delegate(teammate_id: string, parent_run_id: string, prompt: string, team_id: any, relationship_type: RelationshipType): void;
export declare function get_delegations(parent_run_id: any): void;
export declare function list_personas(): void;
export declare function update_status(req_id: string, status: string, summary: any): void;
