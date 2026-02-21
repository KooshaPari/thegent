// Auto-generated TypeScript declarations for versioning
// Source: generate-api-docs.py

export declare class VersioningManager {
  constructor(versions: Array<string>);
  generate_version_manifest(): void;
  generate_version_switcher_html(current_version: string): void;
}

export declare function generate_version_manifest(): void;
export declare function generate_version_switcher_html(current_version: string): void;
