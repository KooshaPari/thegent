// Auto-generated TypeScript declarations for themes
// Source: generate-api-docs.py

export declare class ThemeColors {
  from_dict(data: Record<(str, str)>): void;
  to_dict(): void;
}

export declare class ThemeDefinition {
  from_dict(data: Record<(str, Any)>): void;
  to_dict(): void;
  to_textual_theme(): void;
}

export declare class ThemeManager {
  constructor(storage_dir: any);
  add_theme(theme: ThemeDefinition): void;
  apply_to_app(app: any): void;
  create_theme(name: string, colors: ThemeColors, dark: boolean, author: string, description: string): void;
  delete_theme(name: string): void;
  duplicate_theme(source: string, new_name: string): void;
  export_theme(name: string, path: string): void;
  get_current(): void;
  get_styles(): void;
  get_theme(name: string): void;
  import_theme(path: string): void;
  list_themes(): void;
  set_theme(name: string): void;
}

export declare function add_theme(theme: ThemeDefinition): void;
export declare function apply_to_app(app: any): void;
export declare function create_theme(name: string, colors: ThemeColors, dark: boolean, author: string, description: string): void;
export declare function delete_theme(name: string): void;
export declare function duplicate_theme(source: string, new_name: string): void;
export declare function export_theme(name: string, path: string): void;
export declare function from_dict(data: Record<(str, Any)>): ThemeDefinition;
export declare function get_builtin_themes(): void;
export declare function get_current(): void;
export declare function get_styles(): void;
export declare function get_theme(name: string): void;
export declare function import_theme(path: string): void;
export declare function list_themes(): void;
export declare function set_theme(name: string): void;
export declare function to_dict(): Record<(str, Any)>;
export declare function to_textual_theme(): void;
