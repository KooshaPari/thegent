// Auto-generated usage examples for edit_links
// Source: generate-api-docs.py

import { EditLinksGenerator, add_edit_link_to_file, add_edit_links_batch, generate_edit_link } from "./edit_links";

// Create a EditLinksGenerator instance
const editlinksgenerator = new EditLinksGenerator("example_repo_url", "example_branch", undefined as unknown as any);
editlinksgenerator.add_edit_link_to_file("example_file_path", "example_position");
editlinksgenerator.add_edit_links_batch(undefined as unknown as Array<string>, "example_position");
editlinksgenerator.generate_edit_link("example_file_path");

// Call add_edit_link_to_file
add_edit_link_to_file(undefined as unknown as any, "example_file_path", "example_position");
// Call add_edit_links_batch
add_edit_links_batch(undefined as unknown as any, undefined as unknown as Array<string>, "example_position");
// Call generate_edit_link
generate_edit_link(undefined as unknown as any, "example_file_path");
