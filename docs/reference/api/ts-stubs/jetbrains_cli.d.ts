// Auto-generated TypeScript declarations for jetbrains_cli
// Source: generate-api-docs.py

export declare class JetBrainsCLI {
  constructor(ide_path: any);
  diff(file1: string, file2: string): void;
  format(files: Array<string>, project_root: any): void;
  inspect(project_root: string, profile: any): void;
  merge(file1: string, file2: string, base: string, output: string): void;
}

export declare function diff(file1: string, file2: string): void;
export declare function format(files: Array<string>, project_root: any): void;
export declare function inspect(project_root: string, profile: any): void;
export declare function merge(file1: string, file2: string, base: string, output: string): void;
