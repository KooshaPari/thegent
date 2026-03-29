// Auto-generated TypeScript declarations for test_seed_storage
// Source: generate-api-docs.py

export declare class TestSeedStorageArchive {
  test_archive_seed(storage: any, sample_seed: any): void;
  test_delete_nonexistent_seed(storage: any): void;
  test_delete_seed(storage: any, sample_seed: any): void;
}

export declare class TestSeedStorageExport {
  populated_storage(storage: any): void;
  test_export_markdown_by_status(populated_storage: any): void;
  test_export_markdown_content(populated_storage: any): void;
  test_export_to_file(storage: any, populated_storage: any, temp_storage_dir: any): void;
}

export declare class TestSeedStorageQuery {
  populated_storage(storage: any): void;
  test_find_by_id(populated_storage: any): void;
  test_find_by_id_not_found(populated_storage: any): void;
  test_find_by_source(populated_storage: any): void;
  test_find_by_status(populated_storage: any): void;
  test_find_by_tag(populated_storage: any): void;
  test_find_by_text(populated_storage: any): void;
  test_find_by_text_not_found(populated_storage: any): void;
}

export declare class TestSeedStorageRead {
  test_load_empty_storage(storage: any): void;
  test_load_multiple_seeds(storage: any): void;
  test_load_preserves_metadata(storage: any): void;
  test_load_single_seed(storage: any, sample_seed: any): void;
}

export declare class TestSeedStorageStats {
  populated_storage(storage: any): void;
  test_stats_avg_confidence(populated_storage: any): void;
  test_stats_by_confidence(populated_storage: any): void;
  test_stats_by_source(populated_storage: any): void;
  test_stats_by_status(populated_storage: any): void;
  test_stats_total_count(populated_storage: any): void;
}

export declare class TestSeedStorageUpdate {
  test_update_context(storage: any, sample_seed: any): void;
  test_update_multiple_fields(storage: any, sample_seed: any): void;
  test_update_nonexistent_seed(storage: any): void;
  test_update_status(storage: any, sample_seed: any): void;
  test_update_tags(storage: any, sample_seed: any): void;
}

export declare class TestSeedStorageWrite {
  test_duplicate_seed_prevention(storage: any, sample_seed: any): void;
  test_jsonl_format(storage: any, sample_seed: any): void;
  test_store_multiple_seeds(storage: any): void;
  test_store_seed(storage: any, sample_seed: any): void;
  test_store_seed_creates_directory(temp_storage_dir: any): void;
}

export declare function populated_storage(storage: any): void;
export declare function sample_seed(): void;
export declare function storage(temp_storage_dir: any): void;
export declare function temp_storage_dir(): void;
export declare function test_archive_seed(storage: any, sample_seed: any): void;
export declare function test_delete_nonexistent_seed(storage: any): void;
export declare function test_delete_seed(storage: any, sample_seed: any): void;
export declare function test_duplicate_seed_prevention(storage: any, sample_seed: any): void;
export declare function test_export_markdown_by_status(populated_storage: any): void;
export declare function test_export_markdown_content(populated_storage: any): void;
export declare function test_export_to_file(storage: any, populated_storage: any, temp_storage_dir: any): void;
export declare function test_find_by_id(populated_storage: any): void;
export declare function test_find_by_id_not_found(populated_storage: any): void;
export declare function test_find_by_source(populated_storage: any): void;
export declare function test_find_by_status(populated_storage: any): void;
export declare function test_find_by_tag(populated_storage: any): void;
export declare function test_find_by_text(populated_storage: any): void;
export declare function test_find_by_text_not_found(populated_storage: any): void;
export declare function test_jsonl_format(storage: any, sample_seed: any): void;
export declare function test_load_empty_storage(storage: any): void;
export declare function test_load_multiple_seeds(storage: any): void;
export declare function test_load_preserves_metadata(storage: any): void;
export declare function test_load_single_seed(storage: any, sample_seed: any): void;
export declare function test_stats_avg_confidence(populated_storage: any): void;
export declare function test_stats_by_confidence(populated_storage: any): void;
export declare function test_stats_by_source(populated_storage: any): void;
export declare function test_stats_by_status(populated_storage: any): void;
export declare function test_stats_total_count(populated_storage: any): void;
export declare function test_store_multiple_seeds(storage: any): void;
export declare function test_store_seed(storage: any, sample_seed: any): void;
export declare function test_store_seed_creates_directory(temp_storage_dir: any): void;
export declare function test_update_context(storage: any, sample_seed: any): void;
export declare function test_update_multiple_fields(storage: any, sample_seed: any): void;
export declare function test_update_nonexistent_seed(storage: any): void;
export declare function test_update_status(storage: any, sample_seed: any): void;
export declare function test_update_tags(storage: any, sample_seed: any): void;
