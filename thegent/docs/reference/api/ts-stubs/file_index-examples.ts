// Auto-generated usage examples for file_index
// Source: generate-api-docs.py

import { FileIndex, build, find, find_by_ext, find_by_name, invalidate, is_cached } from "./file_index";

// Create a FileIndex instance
const fileindex = new FileIndex(undefined as unknown as any);
fileindex.build("example_root", undefined as unknown as any);
fileindex.find("example_pattern", undefined as unknown as any);
fileindex.find_by_ext("example_ext", undefined as unknown as any);
fileindex.find_by_name("example_name", undefined as unknown as any);
fileindex.invalidate(undefined as unknown as any);
fileindex.is_cached("example_root");

// Call build
build(undefined as unknown as any, "example_root", undefined as unknown as any);
// Call find
find(undefined as unknown as any, "example_pattern", undefined as unknown as any);
// Call find_by_ext
find_by_ext(undefined as unknown as any, "example_ext", undefined as unknown as any);
// Call find_by_name
find_by_name(undefined as unknown as any, "example_name", undefined as unknown as any);
// Call invalidate
invalidate(undefined as unknown as any, undefined as unknown as any);
// Call is_cached
is_cached(undefined as unknown as any, "example_root");
