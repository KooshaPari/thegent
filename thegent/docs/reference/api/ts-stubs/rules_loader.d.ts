// Auto-generated TypeScript declarations for rules_loader
// Source: generate-api-docs.py

export declare class Rule {
  key(): void;
}

export declare class RulesLoader {
  constructor(rules_path: any);
  get_rule(command: string, subcommand: any): void;
  load(force: boolean): void;
}

export declare function get_rule(command: string, subcommand: any): void;
export declare function key(): string;
export declare function load(force: boolean): void;
