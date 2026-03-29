// Auto-generated TypeScript declarations for git_enhance
// Source: generate-api-docs.py

export declare class GitEnhance {
  constructor(ttl_seconds: number);
  detect_lock(repo_path: string): void;
  git_status(repo_path: string, use_cache: boolean): void;
  passthrough_to_agent(command: string, args: Array<string>): void;
}

export declare function detect_lock(repo_path: string): void;
export declare function git_status(repo_path: string, use_cache: boolean): void;
export declare function passthrough_to_agent(command: string, args: Array<string>): void;
