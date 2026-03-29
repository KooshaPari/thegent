// Auto-generated TypeScript declarations for changed_files_enhance
// Source: generate-api-docs.py

export declare class ChangedFilesEnhance {
  constructor();
  get_changed_files(repo_path: string, filter_patterns: any): void;
  get_shared_files(repo_path: string): void;
  integrate_ls_files(repo_path: string): void;
}

export declare function get_changed_files(repo_path: string, filter_patterns: any): void;
export declare function get_shared_files(repo_path: string): void;
export declare function integrate_ls_files(repo_path: string): void;
