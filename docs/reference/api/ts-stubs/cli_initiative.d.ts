// Auto-generated TypeScript declarations for cli_initiative
// Source: generate-api-docs.py

export declare class Initiative {
  constructor(id: string, title: string, status: string, deliverables: string, effort: string);
}

export declare function initiative_audit_cmd(): void;
export declare function initiative_list_cmd(): void;
export declare function parse_plan_initiatives(plan_path: string): void;
