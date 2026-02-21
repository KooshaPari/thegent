// Auto-generated TypeScript declarations for shadow
// Source: generate-api-docs.py

export declare class ShadowWorkspace {
  constructor(project_root: string, shadow_id: string);
  create(branch: any): void;
  destroy(): void;
  get_env(): void;
  merge_back(): void;
  run(cmd: Array<string>): void;
}

export declare function create(branch: any): void;
export declare function destroy(): void;
export declare function get_env(): void;
export declare function merge_back(): void;
export declare function run(cmd: Array<string>): void;
