// Auto-generated TypeScript declarations for seed_storage
// Source: generate-api-docs.py

export declare class SeedStorage {
  constructor(storage_path: any);
  archive_seed(seed_id: string): void;
  delete_seed(seed_id: string): void;
  export_markdown(output_path: any): void;
  find_by_id(seed_id: string): void;
  find_by_source(source: SeedSource): void;
  find_by_status(status: string): void;
  find_by_tag(tag: string): void;
  find_by_text(text: string): void;
  get_stats(): void;
  load_seeds(): void;
  store_seed(seed: Seed): void;
  update_seed(seed_id: string): void;
}

export declare function archive_seed(seed_id: string): void;
export declare function delete_seed(seed_id: string): void;
export declare function export_markdown(output_path: any): void;
export declare function find_by_id(seed_id: string): void;
export declare function find_by_source(source: SeedSource): void;
export declare function find_by_status(status: string): void;
export declare function find_by_tag(tag: string): void;
export declare function find_by_text(text: string): void;
export declare function get_stats(): void;
export declare function load_seeds(): void;
export declare function store_seed(seed: Seed): void;
export declare function update_seed(seed_id: string): void;
