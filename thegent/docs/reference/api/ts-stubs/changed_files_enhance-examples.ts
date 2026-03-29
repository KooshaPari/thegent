// Auto-generated usage examples for changed_files_enhance
// Source: generate-api-docs.py

import { ChangedFilesEnhance, get_changed_files, get_shared_files, integrate_ls_files } from "./changed_files_enhance";

// Create a ChangedFilesEnhance instance
const changedfilesenhance = new ChangedFilesEnhance();
changedfilesenhance.get_changed_files("example_repo_path", undefined as unknown as any);
changedfilesenhance.get_shared_files("example_repo_path");
changedfilesenhance.integrate_ls_files("example_repo_path");

// Call get_changed_files
get_changed_files(undefined as unknown as any, "example_repo_path", undefined as unknown as any);
// Call get_shared_files
get_shared_files(undefined as unknown as any, "example_repo_path");
// Call integrate_ls_files
integrate_ls_files(undefined as unknown as any, "example_repo_path");
