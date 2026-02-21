// Auto-generated usage examples for link_checker
// Source: generate-api-docs.py

import { LinkChecker, check_directory, check_file, check_link, find_links } from "./link_checker";

// Create a LinkChecker instance
const linkchecker = new LinkChecker(undefined as unknown as any);
linkchecker.check_directory("example_dir_path", "example_pattern");
linkchecker.check_file("example_file_path");
linkchecker.check_link("example_url", "example_base_path");
linkchecker.find_links("example_file_path");

// Call check_directory
check_directory(undefined as unknown as any, "example_dir_path", "example_pattern");
// Call check_file
check_file(undefined as unknown as any, "example_file_path");
// Call check_link
check_link(undefined as unknown as any, "example_url", "example_base_path");
// Call find_links
find_links(undefined as unknown as any, "example_file_path");
