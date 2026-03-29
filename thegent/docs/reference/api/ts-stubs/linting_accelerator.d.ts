// Auto-generated TypeScript declarations for linting_accelerator
// Source: generate-api-docs.py

export declare class LintResult {
}

export declare class LintingAccelerator {
  is_eslint_available(): void;
  is_oxlint_available(): void;
  is_ruff_available(): void;
  lint(paths: Array<string>, fast: boolean, oxlint_config: any, eslint_config: any): void;
  run_eslint(paths: Array<string>, config: any): void;
  run_oxlint(paths: Array<string>, config: any): void;
  run_ruff(paths: Array<string>): void;
}

export declare function is_eslint_available(): void;
export declare function is_oxlint_available(): void;
export declare function is_ruff_available(): void;
export declare function lint(paths: Array<string>, fast: boolean, oxlint_config: any, eslint_config: any): void;
export declare function run_eslint(paths: Array<string>, config: any): void;
export declare function run_oxlint(paths: Array<string>, config: any): void;
export declare function run_ruff(paths: Array<string>): void;
