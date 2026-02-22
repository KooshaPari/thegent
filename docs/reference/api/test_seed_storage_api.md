# test_seed_storage API Reference

> **Source**: `src/thegent/memory/test_seed_storage.py`

Tests for seed storage with JSONL persistence.

---

## TestSeedStorageArchive

Test archiving seeds.

### Methods

#### TestSeedStorageArchive.test_archive_seed

```python
test_archive_seed(self: Any, storage: Any, sample_seed: Any)
```

Test archiving a seed.

---

#### TestSeedStorageArchive.test_delete_nonexistent_seed

```python
test_delete_nonexistent_seed(self: Any, storage: Any)
```

Test deleting non-existent seed.

---

#### TestSeedStorageArchive.test_delete_seed

```python
test_delete_seed(self: Any, storage: Any, sample_seed: Any)
```

Test deleting (archiving) a seed.

---

---

## TestSeedStorageExport

Test exporting seeds to markdown.

### Methods

#### TestSeedStorageExport.populated_storage

```python
populated_storage(self: Any, storage: Any)
```

Create storage with multiple seeds.

---

#### TestSeedStorageExport.test_export_markdown_by_status

```python
test_export_markdown_by_status(self: Any, populated_storage: Any)
```

Test markdown export groups by status.

---

#### TestSeedStorageExport.test_export_markdown_content

```python
test_export_markdown_content(self: Any, populated_storage: Any)
```

Test markdown export content.

---

#### TestSeedStorageExport.test_export_to_file

```python
test_export_to_file(self: Any, storage: Any, populated_storage: Any, temp_storage_dir: Any)
```

Test exporting markdown to file.

---

---

## TestSeedStorageQuery

Test querying seeds.

### Methods

#### TestSeedStorageQuery.populated_storage

```python
populated_storage(self: Any, storage: Any)
```

Create storage with multiple seeds.

---

#### TestSeedStorageQuery.test_find_by_id

```python
test_find_by_id(self: Any, populated_storage: Any)
```

Test finding seed by ID.

---

#### TestSeedStorageQuery.test_find_by_id_not_found

```python
test_find_by_id_not_found(self: Any, populated_storage: Any)
```

Test finding non-existent seed by ID.

---

#### TestSeedStorageQuery.test_find_by_source

```python
test_find_by_source(self: Any, populated_storage: Any)
```

Test finding seeds by source.

---

#### TestSeedStorageQuery.test_find_by_status

```python
test_find_by_status(self: Any, populated_storage: Any)
```

Test finding seeds by status.

---

#### TestSeedStorageQuery.test_find_by_tag

```python
test_find_by_tag(self: Any, populated_storage: Any)
```

Test finding seeds by tag.

---

#### TestSeedStorageQuery.test_find_by_text

```python
test_find_by_text(self: Any, populated_storage: Any)
```

Test finding seed by text.

---

#### TestSeedStorageQuery.test_find_by_text_not_found

```python
test_find_by_text_not_found(self: Any, populated_storage: Any)
```

Test finding non-existent seed by text.

---

---

## TestSeedStorageRead

Test reading seeds from storage.

### Methods

#### TestSeedStorageRead.test_load_empty_storage

```python
test_load_empty_storage(self: Any, storage: Any)
```

Test loading from non-existent file.

---

#### TestSeedStorageRead.test_load_multiple_seeds

```python
test_load_multiple_seeds(self: Any, storage: Any)
```

Test loading multiple seeds.

---

#### TestSeedStorageRead.test_load_preserves_metadata

```python
test_load_preserves_metadata(self: Any, storage: Any)
```

Test that loading preserves seed metadata.

---

#### TestSeedStorageRead.test_load_single_seed

```python
test_load_single_seed(self: Any, storage: Any, sample_seed: Any)
```

Test loading a single seed.

---

---

## TestSeedStorageStats

Test statistics generation.

### Methods

#### TestSeedStorageStats.populated_storage

```python
populated_storage(self: Any, storage: Any)
```

Create storage with seeds of various statuses.

---

#### TestSeedStorageStats.test_stats_avg_confidence

```python
test_stats_avg_confidence(self: Any, populated_storage: Any)
```

Test average confidence calculation.

---

#### TestSeedStorageStats.test_stats_by_confidence

```python
test_stats_by_confidence(self: Any, populated_storage: Any)
```

Test stats breakdown by confidence level.

---

#### TestSeedStorageStats.test_stats_by_source

```python
test_stats_by_source(self: Any, populated_storage: Any)
```

Test stats breakdown by source.

---

#### TestSeedStorageStats.test_stats_by_status

```python
test_stats_by_status(self: Any, populated_storage: Any)
```

Test stats breakdown by status.

---

#### TestSeedStorageStats.test_stats_total_count

```python
test_stats_total_count(self: Any, populated_storage: Any)
```

Test total seed count in stats.

---

---

## TestSeedStorageUpdate

Test updating seeds.

### Methods

#### TestSeedStorageUpdate.test_update_context

```python
test_update_context(self: Any, storage: Any, sample_seed: Any)
```

Test updating seed context.

---

#### TestSeedStorageUpdate.test_update_multiple_fields

```python
test_update_multiple_fields(self: Any, storage: Any, sample_seed: Any)
```

Test updating multiple fields at once.

---

#### TestSeedStorageUpdate.test_update_nonexistent_seed

```python
test_update_nonexistent_seed(self: Any, storage: Any)
```

Test updating non-existent seed.

---

#### TestSeedStorageUpdate.test_update_status

```python
test_update_status(self: Any, storage: Any, sample_seed: Any)
```

Test updating seed status.

---

#### TestSeedStorageUpdate.test_update_tags

```python
test_update_tags(self: Any, storage: Any, sample_seed: Any)
```

Test updating seed tags.

---

---

## TestSeedStorageWrite

Test writing seeds to storage.

### Methods

#### TestSeedStorageWrite.test_duplicate_seed_prevention

```python
test_duplicate_seed_prevention(self: Any, storage: Any, sample_seed: Any)
```

Test that duplicate seeds are not stored.

---

#### TestSeedStorageWrite.test_jsonl_format

```python
test_jsonl_format(self: Any, storage: Any, sample_seed: Any)
```

Test that seeds are stored in JSONL format.

---

#### TestSeedStorageWrite.test_store_multiple_seeds

```python
test_store_multiple_seeds(self: Any, storage: Any)
```

Test storing multiple seeds.

---

#### TestSeedStorageWrite.test_store_seed

```python
test_store_seed(self: Any, storage: Any, sample_seed: Any)
```

Test storing a single seed.

---

#### TestSeedStorageWrite.test_store_seed_creates_directory

```python
test_store_seed_creates_directory(self: Any, temp_storage_dir: Any)
```

Test that storing seed creates necessary directories.

---

---

## populated_storage

```python
populated_storage(self: Any, storage: Any)
```

Create storage with multiple seeds.

---

## sample_seed

Create sample seed for testing.

---

## storage

```python
storage(temp_storage_dir: Any)
```

Create SeedStorage instance with temp directory.

---

## temp_storage_dir

Create temporary directory for storage tests.

---

## test_archive_seed

```python
test_archive_seed(self: Any, storage: Any, sample_seed: Any)
```

Test archiving a seed.

---

## test_delete_nonexistent_seed

```python
test_delete_nonexistent_seed(self: Any, storage: Any)
```

Test deleting non-existent seed.

---

## test_delete_seed

```python
test_delete_seed(self: Any, storage: Any, sample_seed: Any)
```

Test deleting (archiving) a seed.

---

## test_duplicate_seed_prevention

```python
test_duplicate_seed_prevention(self: Any, storage: Any, sample_seed: Any)
```

Test that duplicate seeds are not stored.

---

## test_export_markdown_by_status

```python
test_export_markdown_by_status(self: Any, populated_storage: Any)
```

Test markdown export groups by status.

---

## test_export_markdown_content

```python
test_export_markdown_content(self: Any, populated_storage: Any)
```

Test markdown export content.

---

## test_export_to_file

```python
test_export_to_file(self: Any, storage: Any, populated_storage: Any, temp_storage_dir: Any)
```

Test exporting markdown to file.

---

## test_find_by_id

```python
test_find_by_id(self: Any, populated_storage: Any)
```

Test finding seed by ID.

---

## test_find_by_id_not_found

```python
test_find_by_id_not_found(self: Any, populated_storage: Any)
```

Test finding non-existent seed by ID.

---

## test_find_by_source

```python
test_find_by_source(self: Any, populated_storage: Any)
```

Test finding seeds by source.

---

## test_find_by_status

```python
test_find_by_status(self: Any, populated_storage: Any)
```

Test finding seeds by status.

---

## test_find_by_tag

```python
test_find_by_tag(self: Any, populated_storage: Any)
```

Test finding seeds by tag.

---

## test_find_by_text

```python
test_find_by_text(self: Any, populated_storage: Any)
```

Test finding seed by text.

---

## test_find_by_text_not_found

```python
test_find_by_text_not_found(self: Any, populated_storage: Any)
```

Test finding non-existent seed by text.

---

## test_jsonl_format

```python
test_jsonl_format(self: Any, storage: Any, sample_seed: Any)
```

Test that seeds are stored in JSONL format.

---

## test_load_empty_storage

```python
test_load_empty_storage(self: Any, storage: Any)
```

Test loading from non-existent file.

---

## test_load_multiple_seeds

```python
test_load_multiple_seeds(self: Any, storage: Any)
```

Test loading multiple seeds.

---

## test_load_preserves_metadata

```python
test_load_preserves_metadata(self: Any, storage: Any)
```

Test that loading preserves seed metadata.

---

## test_load_single_seed

```python
test_load_single_seed(self: Any, storage: Any, sample_seed: Any)
```

Test loading a single seed.

---

## test_stats_avg_confidence

```python
test_stats_avg_confidence(self: Any, populated_storage: Any)
```

Test average confidence calculation.

---

## test_stats_by_confidence

```python
test_stats_by_confidence(self: Any, populated_storage: Any)
```

Test stats breakdown by confidence level.

---

## test_stats_by_source

```python
test_stats_by_source(self: Any, populated_storage: Any)
```

Test stats breakdown by source.

---

## test_stats_by_status

```python
test_stats_by_status(self: Any, populated_storage: Any)
```

Test stats breakdown by status.

---

## test_stats_total_count

```python
test_stats_total_count(self: Any, populated_storage: Any)
```

Test total seed count in stats.

---

## test_store_multiple_seeds

```python
test_store_multiple_seeds(self: Any, storage: Any)
```

Test storing multiple seeds.

---

## test_store_seed

```python
test_store_seed(self: Any, storage: Any, sample_seed: Any)
```

Test storing a single seed.

---

## test_store_seed_creates_directory

```python
test_store_seed_creates_directory(self: Any, temp_storage_dir: Any)
```

Test that storing seed creates necessary directories.

---

## test_update_context

```python
test_update_context(self: Any, storage: Any, sample_seed: Any)
```

Test updating seed context.

---

## test_update_multiple_fields

```python
test_update_multiple_fields(self: Any, storage: Any, sample_seed: Any)
```

Test updating multiple fields at once.

---

## test_update_nonexistent_seed

```python
test_update_nonexistent_seed(self: Any, storage: Any)
```

Test updating non-existent seed.

---

## test_update_status

```python
test_update_status(self: Any, storage: Any, sample_seed: Any)
```

Test updating seed status.

---

## test_update_tags

```python
test_update_tags(self: Any, storage: Any, sample_seed: Any)
```

Test updating seed tags.

---
