// Auto-generated TypeScript declarations for link_checker
// Source: generate-api-docs.py

export declare class LinkChecker {
  constructor(base_dir: any);
  check_directory(dir_path: string, pattern: string): void;
  check_file(file_path: string): void;
  check_link(url: string, base_path: string): void;
  find_links(file_path: string): void;
}

export declare function check_directory(dir_path: string, pattern: string): void;
export declare function check_file(file_path: string): void;
export declare function check_link(url: string, base_path: string): void;
export declare function find_links(file_path: string): void;
