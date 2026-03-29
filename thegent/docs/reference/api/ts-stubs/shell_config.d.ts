// Auto-generated TypeScript declarations for shell_config
// Source: generate-api-docs.py

export declare class ShellConfigAuditor {
  audit(search_dirs: Array<string>): void;
  check_sourcing_order(configs: Array<ShellConfigFile>): void;
  find_duplicate_aliases(configs: Array<ShellConfigFile>): void;
  find_duplicates(configs: Array<ShellConfigFile>): void;
  generate_consolidated(configs: Array<ShellConfigFile>): void;
  sourcing_graph(configs: Array<ShellConfigFile>): void;
}

export declare class ShellConfigFile {
  parse(path: string): void;
}

export declare function audit(search_dirs: Array<string>): void;
export declare function check_sourcing_order(configs: Array<ShellConfigFile>): void;
export declare function find_duplicate_aliases(configs: Array<ShellConfigFile>): void;
export declare function find_duplicates(configs: Array<ShellConfigFile>): void;
export declare function generate_consolidated(configs: Array<ShellConfigFile>): void;
export declare function parse(path: string): void;
export declare function sourcing_graph(configs: Array<ShellConfigFile>): void;
