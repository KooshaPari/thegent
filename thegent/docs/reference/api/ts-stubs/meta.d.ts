// Auto-generated TypeScript declarations for meta
// Source: generate-api-docs.py

export declare class ConstitutionalPrinciple extends StrEnum {
}

export declare class MetaGovernance {
  constructor(constitution_path: any);
  get_constitution_summary(): void;
  save_constitution(): void;
  validate_action(action_description: string, tags: set<string>): void;
}

export declare class Rule {
}

export declare function get_constitution_summary(): void;
export declare function save_constitution(): void;
export declare function validate_action(action_description: string, tags: set<string>): void;
