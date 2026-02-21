// Auto-generated usage examples for scanner
// Source: generate-api-docs.py

import { MarkdownScanner, ScanConfig, get_file_date, get_summary, save_results, scan, scan_directory, should_exclude } from "./scanner";

// Create a MarkdownScanner instance
const markdownscanner = new MarkdownScanner(undefined as unknown as ScanConfig);
markdownscanner.get_file_date("example_filepath");
markdownscanner.get_summary();
markdownscanner.save_results(undefined as unknown as any);
markdownscanner.scan();
markdownscanner.scan_directory("example_base_path", false, undefined as unknown as any);
markdownscanner.should_exclude("example_filepath");

// Create a ScanConfig instance
const scanconfig = new ScanConfig();

// Call get_file_date
get_file_date(undefined as unknown as any, "example_filepath");
// Call get_summary
get_summary(undefined as unknown as any);
// Call save_results
save_results(undefined as unknown as any, undefined as unknown as any);
// Call scan
scan(undefined as unknown as any);
// Call scan_directory
scan_directory(undefined as unknown as any, "example_base_path", false, undefined as unknown as any);
// Call should_exclude
should_exclude(undefined as unknown as any, "example_filepath");
