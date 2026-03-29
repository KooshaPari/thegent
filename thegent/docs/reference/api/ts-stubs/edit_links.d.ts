// Auto-generated TypeScript declarations for edit_links
// Source: generate-api-docs.py

export declare class EditLinksGenerator {
  constructor(repo_url: string, branch: string, base_dir: any);
  add_edit_link_to_file(file_path: string, position: string): void;
  add_edit_links_batch(files: Array<string>, position: string): void;
  generate_edit_link(file_path: string): void;
}

export declare function add_edit_link_to_file(file_path: string, position: string): void;
export declare function add_edit_links_batch(files: Array<string>, position: string): void;
export declare function generate_edit_link(file_path: string): void;
