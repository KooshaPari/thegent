// Auto-generated usage examples for seed_storage
// Source: generate-api-docs.py

import { SeedStorage, archive_seed, delete_seed, export_markdown, find_by_id, find_by_source, find_by_status, find_by_tag, find_by_text, get_stats, load_seeds, store_seed, update_seed } from "./seed_storage";

// Create a SeedStorage instance
const seedstorage = new SeedStorage(undefined as unknown as any);
seedstorage.archive_seed("example_seed_id");
seedstorage.delete_seed("example_seed_id");
seedstorage.export_markdown(undefined as unknown as any);
seedstorage.find_by_id("example_seed_id");
seedstorage.find_by_source(undefined as unknown as SeedSource);
seedstorage.find_by_status("example_status");
seedstorage.find_by_tag("example_tag");
seedstorage.find_by_text("example_text");
seedstorage.get_stats();
seedstorage.load_seeds();
seedstorage.store_seed(undefined as unknown as Seed);
seedstorage.update_seed("example_seed_id");

// Call archive_seed
archive_seed(undefined as unknown as any, "example_seed_id");
// Call delete_seed
delete_seed(undefined as unknown as any, "example_seed_id");
// Call export_markdown
export_markdown(undefined as unknown as any, undefined as unknown as any);
// Call find_by_id
find_by_id(undefined as unknown as any, "example_seed_id");
// Call find_by_source
find_by_source(undefined as unknown as any, undefined as unknown as SeedSource);
// Call find_by_status
find_by_status(undefined as unknown as any, "example_status");
// Call find_by_tag
find_by_tag(undefined as unknown as any, "example_tag");
// Call find_by_text
find_by_text(undefined as unknown as any, "example_text");
// Call get_stats
get_stats(undefined as unknown as any);
// Call load_seeds
load_seeds(undefined as unknown as any);
// Call store_seed
store_seed(undefined as unknown as any, undefined as unknown as Seed);
// Call update_seed
update_seed(undefined as unknown as any, "example_seed_id");
