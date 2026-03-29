// Auto-generated usage examples for fr_index
// Source: generate-api-docs.py

import { FRIndexSubcommands, extract_fr_ids, get_fr_references, index_file } from "./fr_index";

// Create a FRIndexSubcommands instance
const frindexsubcommands = new FRIndexSubcommands();
frindexsubcommands.extract_fr_ids("example_content");
frindexsubcommands.get_fr_references("example_fr_id");
frindexsubcommands.index_file("example_file_path");

// Call extract_fr_ids
extract_fr_ids(undefined as unknown as any, "example_content");
// Call get_fr_references
get_fr_references(undefined as unknown as any, "example_fr_id");
// Call index_file
index_file(undefined as unknown as any, "example_file_path");
